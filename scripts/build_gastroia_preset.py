"""Build presets/gastroia-journal-preset.json for Ayarlar → Dergi ayarlarını içe aktar.

The values come from the GASTROIA article template (Makale Şablonu), the writing
guide (Yazım Kılavuzu, APA 7) and the cover/title-page documents:
A4, top 0.58 cm / other margins 2 cm, Times New Roman 11 pt, paragraph spacing
12 pt before and after, 1.15 line spacing, no first-line indent, footnotes 10 pt.

Run from the repository root:  python scripts/build_gastroia_preset.py
"""
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from journal_templates import normalize_settings  # noqa: E402

SETTINGS = {
    # Identity. Add the Turkish journal title and website in the app if they should appear.
    'journal_name_tr': 'GASTROIA',
    'journal_name_en': 'GASTROIA Journal of Gastronomy and Travel Research',
    'issn_print': '', 'issn_online': '2602-4144', 'journal_url': '',
    # Closest built-in cover: grey masthead, centred title, separate English summary page.
    'template_id': 'scholarly', 'header_layout': 'scholarly', 'footer_layout': 'full',
    'font_family': 'texgyretermes', 'body_size': '11', 'accent_color': '#9EC53C',
    'logo_height_cm': 3.0, 'corresponding_marker': '*', 'doi_position': 'top',
    'english_abstract_heading': 'Extended Summary', 'english_only': False,
    'show_logo': True, 'show_cc_logo': True, 'link_citations': True,
    'footer_text': ('Bu makale Creative Commons Atıf-GayriTicari-Türetilemez 4.0 (CC BY-NC-ND 4.0) '
                    'lisansı ile yayımlanmaktadır. / This article is published under the '
                    'CC BY-NC-ND 4.0 licence.'),
    # Running heads: cover line "E-ISSN, cilt(sayı), yıl"; later pages "başlık · Cilt, Sayı, yıl, sayfalar".
    'header_mode': 'same', 'header_left': '', 'header_right': '',
    'header_center': '{kisa_baslik} · Cilt. {cilt}, Sayı. {sayi}, {yil}, {sayfa_araligi}',
    'header_first_mode': 'custom', 'header_first_left': '', 'header_first_right': '',
    'header_first_center': 'E-ISSN: {issn}, {cilt}({sayi}), {yil}',
    'header_font_size': '9', 'header_rule': 'line',
    'footer_mode': 'none', 'footer_first_mode': 'none', 'footer_rule': 'none',
    # Page and paragraph layout (Yazım Kılavuzu → Sayfa Yapısı ve Yazım Kriterleri).
    'layout_mode': 'custom',
    'margin_top_cm': 0.58, 'margin_bottom_cm': 2.0, 'margin_left_cm': 2.0, 'margin_right_cm': 2.0,
    'header_distance_cm': 0.6, 'footer_distance_cm': 1.5,
    'body_align': 'justify', 'body_space_before_pt': 12, 'body_space_after_pt': 12,
    'body_line_spacing': 1.15, 'body_first_line_indent_cm': 0,
    'heading_size_pt': 11, 'heading_space_before_pt': 12, 'heading_space_after_pt': 6, 'heading1_align': 'left',
    'caption_size_pt': 11, 'table_size_pt': 11, 'footnote_size_pt': 10,
    'ref_align': 'justify', 'ref_hanging_cm': 1.25, 'ref_space_before_pt': 6, 'ref_space_after_pt': 0,
    'ref_line_spacing': 1.0, 'ref_size_pt': 0,
    # APA 7 as required by the guide: "&", "vd."/"et al." by language, s./ss. and p./pp., t.y./n.d., 20 authors.
    'apa_and': '&', 'apa_et_al': 'auto', 'apa_page_style': 'auto', 'apa_no_date': 'auto',
    'apa_max_ref_authors': 20, 'apa_sort_references': 'yes', 'apa_check': 'warn',
}


def asset(path, mime='image/png'):
    return {'name': path.name, 'data': f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')}


def build():
    settings = normalize_settings(SETTINGS)  # fail here, not in the app, if a value is invalid
    return {'format': 'aiditor-journal-preset', 'version': 1, 'settings': settings,
            'assets': {'logo': asset(ROOT / 'presets/assets/gastroia-logo.png'),
                       'license': asset(ROOT / 'presets/assets/cc-by-nc-nd.png')}}


if __name__ == '__main__':
    target = ROOT / 'presets' / 'gastroia-journal-preset.json'
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('yazıldı:', target.relative_to(ROOT))
