"""Journal settings UI: GASTROIA preset import, margin/paragraph fields and APA 7 report (real Chromium)."""
import json
import os
from pathlib import Path
import sys
import tempfile

from playwright.sync_api import sync_playwright, expect

sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_workflow import ROOT, QA, Server, login, preset_saved, api  # noqa: E402

PRESET = ROOT / 'presets' / 'gastroia-journal-preset.json'


def run():
    with tempfile.TemporaryDirectory(prefix='aiditor-browser-layout-') as data, sync_playwright() as p:
        server = Server(data)
        try:
            url = server.start()
            browser = p.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM_PATH') or None)
            page = browser.new_context(viewport={'width': 1440, 'height': 1200}).new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('dialog', lambda dialog: dialog.accept())
            login(page, url, 'journal_gastroia', True, 'GASTROIA')
            page.locator('#journal-tab').click()

            # Template mode: custom fields are locked and defaults do not change any template.
            expect(page.locator('#js-layout_mode')).to_have_value('template')
            assert page.locator('#layout-custom-fields').evaluate('el => el.disabled')

            page.locator('#import-preset').set_input_files(str(PRESET))
            page.wait_for_function('document.getElementById("js-margin_top_cm").value === "0.58"')
            preset_saved(page)
            expect(page.locator('#js-layout_mode')).to_have_value('custom')
            assert not page.locator('#layout-custom-fields').evaluate('el => el.disabled')
            for field, value in {'js-margin_bottom_cm': '2', 'js-margin_left_cm': '2', 'js-body_space_before_pt': '12',
                                 'js-body_line_spacing': '1.15', 'js-ref_hanging_cm': '1.25', 'js-footnote_size_pt': '10',
                                 'js-apa_and': '&', 'js-apa_et_al': 'auto', 'js-apa_max_ref_authors': '20',
                                 'js-name-en': 'GASTROIA Journal of Gastronomy and Travel Research', 'js-issn-online': '2602-4144'}.items():
                expect(page.locator('#' + field)).to_have_value(value)
            saved = api(page, '/api/journal')['settings']
            assert saved['margin_top_cm'] == 0.58 and saved['apa_et_al'] == 'auto' and saved['body_size'] == '11', saved

            # Editing a value persists through the normal autosave path.
            page.locator('#js-margin_top_cm').fill('1.2')
            page.locator('#js-apa_and').select_option('ve')
            preset_saved(page)
            saved = api(page, '/api/journal')['settings']
            assert saved['margin_top_cm'] == 1.2 and saved['apa_and'] == 've', saved
            page.locator('#layout-settings').scroll_into_view_if_needed()
            page.locator('#layout-settings').screenshot(path=str(QA / 'layout-settings.png'))
            page.locator('#apa-settings').screenshot(path=str(QA / 'apa-settings.png'))

            # Out-of-range values are refused by the server and reported, not silently stored.
            page.locator('#js-margin_left_cm').fill('99')
            page.wait_for_function('document.getElementById("journal-save-status").dataset.state === "error"')
            assert api(page, '/api/journal')['settings']['margin_left_cm'] == 2.0
            page.locator('#js-margin_left_cm').fill('2')
            preset_saved(page)

            page.locator('#js-layout_mode').select_option('template')
            assert page.locator('#layout-custom-fields').evaluate('el => el.disabled')

            # The APA report is built with text nodes only.
            page.evaluate('''() => renderApaReport({enabled:true,warnings:[{code:'x',message:'Mesaj',count:3,examples:['<img src=x onerror=alert(1)>']}]})''')
            text = page.locator('#apa-result').text_content()
            assert '1 uyarı' in text and '<img src=x' in text and 'toplam 3' in text, text
            assert page.locator('#apa-result img').count() == 0
            assert not errors, errors
            print('browser layout/APA checks passed')
        finally:
            server.stop()


if __name__ == '__main__':
    run()
