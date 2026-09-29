"""APA 7 preferences: reference order and a conservative, read-only consistency check.

The checker never rewrites author text or reference data. It only reports where
the manuscript departs from the journal's own APA 7 options (ampersand, "vd."/
"et al.", page prefixes, "t.y."/"n.d.", author limit, DOI form), so the editor
decides what to change.
"""
import re

from citation_links import CitationIndex, YEAR

_NAME = r"[A-ZÇĞİÖŞÜ][\w'’\-]+"
_NAMES = _NAME + r"(?:\s+" + _NAME + r")?"
_LEAD = r"(?<![\w'’\-])"
_TAIL = r"\s*(?:,\s*|\(\s*)\(?" + YEAR
_PAIR = re.compile(_LEAD + '(' + _NAMES + r')\s+(ve|and|&)\s+(' + _NAMES + ')' + _TAIL)
_ET_AL = re.compile(_LEAD + '(' + _NAMES + r')\s+(et\s+al\.|vd\.|ve\s+ark\.)' + _TAIL)
_PAGE = re.compile(r'(?:,|\()\s*(ss?|pp?)\.\s*(\d+)(\s*[-–—]\s*\d+)?')
_NO_DATE = re.compile(r'[^\s(;]+,\s*(t\.y\.|n\.d\.)(?=[\s;)])|\((t\.y\.|n\.d\.)\)')
_REF_AUTHOR = re.compile(r"(?:^|[,;&]\s*|\s)([^,;&\d()]+?),\s*(?:[A-ZÇĞİÖŞÜ]\.(?:\s*[-–]?\s*[A-ZÇĞİÖŞÜ]\.)*)")


def ordered_references(data, settings, key):
    """Reference lines in output order. `key` is the Turkish collation key."""
    lines = [line.strip() for line in data.get('references', '').splitlines() if line.strip()]
    return sorted(lines, key=key) if settings.get('apa_sort_references', 'yes') == 'yes' else lines


def _language(settings):
    return 'en' if settings.get('english_only') else 'tr'


def expected_et_al(settings):
    value = settings.get('apa_et_al', 'et al.')
    return ('et al.' if _language(settings) == 'en' else 'vd.') if value == 'auto' else value


def expected_page_style(settings):
    value = settings.get('apa_page_style', 'auto')
    return _language(settings) if value == 'auto' else value


def expected_no_date(settings):
    value = settings.get('apa_no_date', 'auto')
    return ('n.d.' if _language(settings) == 'en' else 't.y.') if value == 'auto' else value


def _item(code, message, examples=None, count=None):
    examples = list(dict.fromkeys(examples or []))
    return {'code': code, 'message': message, 'count': count if count is not None else len(examples),
            'examples': examples[:3]}


def _body_texts(data):
    for section in data.get('sections', []):
        yield section.get('content', '')
    for key in ('tr_abs', 'en_abs'):
        yield data.get('abstract', {}).get(key, '')


def check_article(data, settings):
    """Return {'enabled', 'warnings'}; warnings are plain data safe for JSON/UI."""
    if settings.get('apa_check', 'warn') == 'off':
        return {'enabled': False, 'warnings': []}
    texts = [t for t in _body_texts(data) if t.strip()]
    refs = [line.strip() for line in data.get('references', '').splitlines() if line.strip()]
    warnings = []

    joiner, wrong_join = settings.get('apa_and', '&'), []
    et_al, wrong_et_al = expected_et_al(settings), []
    for text in texts:
        for match in _PAIR.finditer(text):
            if match.group(2) != joiner:
                wrong_join.append(match.group(0).strip())
        for match in _ET_AL.finditer(text):
            found = re.sub(r'\s+', ' ', match.group(2))
            if found != et_al:
                wrong_et_al.append(match.group(0).strip())
    if wrong_join:
        warnings.append(_item('citation_joiner', f'İki yazarlı atıflarda “{joiner}” kullanılmalıdır.', wrong_join))
    if wrong_et_al:
        warnings.append(_item('citation_et_al', f'Üç ve daha fazla yazarlı atıflarda “{et_al}” kullanılmalıdır.', wrong_et_al))

    style, wrong_pages = expected_page_style(settings), []
    single, multiple = ('s.', 'ss.') if style == 'tr' else ('p.', 'pp.')
    for text in texts:
        for match in _PAGE.finditer(text):
            prefix, is_range = match.group(1) + '.', bool(match.group(3))
            if prefix != (multiple if is_range else single):
                wrong_pages.append(match.group(0).lstrip(',( ').strip())
    if wrong_pages:
        warnings.append(_item('citation_pages', f'Sayfa göstergesi “{single}” (tek sayfa) ve “{multiple}” (sayfa aralığı) biçiminde olmalıdır.', wrong_pages))

    no_date, wrong_dates = expected_no_date(settings), []
    for text in texts + refs:
        wrong_dates += [m.group(0) for m in _NO_DATE.finditer(text) if (m.group(1) or m.group(2)) != no_date]
    if wrong_dates:
        warnings.append(_item('no_date', f'Tarihsiz kaynaklarda “{no_date}” kullanılmalıdır.', wrong_dates))

    limit = settings.get('apa_max_ref_authors', 20)
    missing_year, long_lists, wrong_ampersand, doi_form = [], [], [], []
    for ref in refs:
        year = re.search(r'\((?:' + YEAR + r'|t\.y\.|n\.d\.)[^)]*\)', ref)
        if not year:
            missing_year.append(ref[:80])
            continue
        prefix = ref[:year.start()]
        authors = len(_REF_AUTHOR.findall(prefix))
        if authors > limit and '…' not in prefix and '...' not in prefix:
            long_lists.append(ref[:80])
        if joiner == '&' and re.search(r'[A-ZÇĞİÖŞÜ]\.\s+(?:ve|and)\s+[^\d,]+,\s*[A-ZÇĞİÖŞÜ]\.', prefix):
            wrong_ampersand.append(ref[:80])
        if re.search(r'\bdoi\s*:\s*10\.|(?<!https://)doi\.org/10\.|https?://dx\.doi\.org/', ref, re.I):
            doi_form.append(ref[:80])
    if missing_year:
        warnings.append(_item('reference_year', 'Kaynakça kaydında (Yıl) veya (t.y.) bilgisi bulunamadı.', missing_year))
    if long_lists:
        warnings.append(_item('reference_authors', f'{limit} yazardan uzun kaynaklarda ilk {limit - 1} yazardan sonra “…” ve son yazar verilmelidir.', long_lists))
    if wrong_ampersand:
        warnings.append(_item('reference_joiner', 'Kaynakçada yazarlar arasında “&” kullanılmalıdır.', wrong_ampersand))
    if doi_form:
        warnings.append(_item('doi_form', 'DOI, https://doi.org/10… biçiminde yazılmalıdır.', doi_form))

    index = CitationIndex(refs)
    cited = {i for text in texts for _, _, i in index.spans(text)}
    ambiguous = set(index.ambiguous)
    uncited = [refs[i][:80] for i in range(len(refs)) if i not in cited and i not in ambiguous and i not in index.unsupported]
    if uncited:
        warnings.append(_item('uncited_reference', 'Metinde eşleşen atıf bulunamayan olası kaynaklar (tek yazarlı/yıllı biçimler denetlenir).', uncited))
    if ambiguous:
        warnings.append(_item('same_author_year', 'Aynı yazar ve yıla ait kayıtlar için yıla a, b… eki verilmelidir (ör. 2026a, 2026b).',
                              [refs[i][:80] for i in sorted(ambiguous)]))
    return {'enabled': True, 'warnings': warnings}
