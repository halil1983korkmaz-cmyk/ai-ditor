"""Word -> PDF conversion through a locally installed LibreOffice, plus PDF merging.

The PDF is rendered from the very same editable .docx the application produces, so
Word and PDF outputs match. LibreOffice is an optional system component; when it is
missing the caller receives a Turkish, actionable message instead of a stack trace.
"""
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

_LOCK = threading.Lock()
_CANDIDATES = {
    'darwin': ['/Applications/LibreOffice.app/Contents/MacOS/soffice'],
    'win32': [r'C:\Program Files\LibreOffice\program\soffice.exe',
              r'C:\Program Files (x86)\LibreOffice\program\soffice.exe'],
}


class PdfUnavailable(ValueError):
    """LibreOffice is missing or failed; the message is shown to the editor."""


def find_office():
    override = os.environ.get('AIDITOR_SOFFICE')
    if override and Path(override).is_file():
        return override
    for name in ('soffice', 'libreoffice'):
        found = shutil.which(name)
        if found:
            return found
    for candidate in _CANDIDATES.get(sys.platform, []):
        if Path(candidate).is_file():
            return candidate
    return None


def pdf_available():
    return find_office() is not None


def docx_to_pdf(blob: bytes, timeout: int = 240) -> bytes:
    office = find_office()
    if not office:
        raise PdfUnavailable('PDF çıktısı için bilgisayarda LibreOffice kurulu olmalıdır (libreoffice.org). '
                             'Kurulumdan sonra uygulamayı yeniden açın; Word çıktısı LibreOffice olmadan da alınabilir.')
    with _LOCK, tempfile.TemporaryDirectory(prefix='aiditor-pdf-') as directory:
        work = Path(directory)
        source = work / 'document.docx'
        source.write_bytes(blob)
        profile = (work / 'profile').as_uri()
        try:
            subprocess.run([office, f'-env:UserInstallation={profile}', '--headless', '--norestore',
                            '--convert-to', 'pdf', '--outdir', str(work), str(source)],
                           capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise PdfUnavailable('PDF dönüştürme zaman aşımına uğradı. Belgeyi küçültüp yeniden deneyin.') from exc
        except OSError as exc:
            raise PdfUnavailable('LibreOffice başlatılamadı. Kurulumu kontrol edin.') from exc
        target = work / 'document.pdf'
        if not target.is_file() or target.stat().st_size < 100:
            raise PdfUnavailable('Word belgesi PDF’e dönüştürülemedi. LibreOffice’in başka bir pencerede açık olmadığından emin olun.')
        return target.read_bytes()


def page_count(pdf: bytes) -> int:
    from pypdf import PdfReader
    return len(PdfReader(io.BytesIO(pdf)).pages)


def merge_pdfs(parts):
    """Merge [(title, pdf_bytes)] and add one outline entry per part."""
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    for title, pdf in parts:
        start = len(writer.pages)
        for page in PdfReader(io.BytesIO(pdf)).pages:
            writer.add_page(page)
        if title and len(writer.pages) > start:
            writer.add_outline_item(title[:200], start)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()
