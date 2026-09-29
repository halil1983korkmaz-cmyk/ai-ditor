"""Validated, portable journal preferences shared by the UI and formatter.

These presets describe journal typography, not a licence for journal articles.
The application itself is distributed under the MIT licence.
"""
import math
import re
from page_furniture import RUNNING_DEFAULTS, normalize_running
from urllib.parse import urlsplit


TEMPLATES = [
    {'id': 'classic', 'name': 'Klasik akademik',
     'description': 'Solda logo, sağda dergi künyesi; özetlerin yanında makale bilgileri.',
     'settings': {'template_id': 'classic', 'header_layout': 'classic', 'footer_layout': 'full',
                  'font_family': 'texgyrepagella', 'accent_color': '#244E63', 'body_size': '10', 'logo_height_cm': 2.0}},
    {'id': 'contemporary', 'name': 'Çağdaş editoryal',
     'description': 'Renkli dergi başlığı, sağda logo ve yan yana iki dilde özet.',
     'settings': {'template_id': 'contemporary', 'header_layout': 'contemporary', 'footer_layout': 'compact',
                  'font_family': 'texgyreheros', 'accent_color': '#176B68', 'body_size': '10', 'logo_height_cm': 1.7}},
    {'id': 'centered', 'name': 'Ortalanmış kapak',
     'description': 'Ortalanmış logo, dergi adı ve makale başlığı; tam genişlikte özetler.',
     'settings': {'template_id': 'centered', 'header_layout': 'centered', 'footer_layout': 'full',
                  'font_family': 'texgyretermes', 'accent_color': '#603F63', 'body_size': '11', 'logo_height_cm': 1.5}},
    {'id': 'minimal', 'name': 'Yalın araştırma',
     'description': 'Kompakt üst künye, soldan hizalı başlıklar ve sade dipnot alanı.',
     'settings': {'template_id': 'minimal', 'header_layout': 'minimal', 'footer_layout': 'minimal',
                  'font_family': 'latinmodern', 'accent_color': '#333F48', 'body_size': '10', 'logo_height_cm': 1.0}},
    {'id': 'scholarly', 'name': 'Sosyal bilimler',
     'description': 'Gri dergi künyesi, ortalanmış başlık, ayrı sayfada İngilizce özet ve tek/çift sayfa üst bilgileri.',
     'settings': {'template_id': 'scholarly', 'header_layout': 'scholarly', 'footer_layout': 'full',
                  'font_family': 'texgyretermes', 'accent_color': '#222222', 'body_size': '11',
                  'logo_height_cm': 3.0, 'doi_position': 'top', 'english_abstract_heading': 'Extended Summary',
                  'header_mode': 'odd_even', 'header_left': '{yazarlar}', 'header_center': '', 'header_right': '{sayfa}',
                  'header_even_left': '{dergi} {yil} {cilt}({sayi}) {sayfa_araligi}',
                  'header_even_center': '', 'header_even_right': '{sayfa}', 'header_font_size': '10', 'header_rule': 'line',
                  'header_first_mode': 'custom', 'header_first_left': '',
                  'header_first_center': '{dergi} {yil} {cilt}({sayi})', 'header_first_right': '',
                  'footer_mode': 'none', 'footer_first_mode': 'none', 'footer_rule': 'none'}},
]

_DEFAULTS = {
    'journal_name_tr': '', 'journal_name_en': '', 'issn_print': '', 'issn_online': '',
    'journal_url': '', 'font_family': 'texgyrepagella', 'body_size': '10',
    'accent_color': '#244E63', 'logo_height_cm': 2.0, 'corresponding_marker': '*',
    'english_only': False, 'doi_position': 'bottom', 'logo_stem': 'journal_logo',
    'cc_logo_stem': 'license_logo', 'footer_text': '', 'first_page_fit': 'auto',
    'template_id': 'classic', 'header_layout': 'classic', 'footer_layout': 'full',
    'show_logo': True, 'show_cc_logo': True, 'link_citations': True,
    'english_abstract_heading': 'Abstract',
    'frontmatter_text': '',
    'frontmatter_line': 'E-ISSN: {issn} | Cilt/Volume: {cilt} | Sayı/Issue: {sayi} | Ay/Month: {ay} | Yıl/Year: {yil}',
    'frontmatter_toc_heading': 'İÇİNDEKİLER / TABLE OF CONTENTS',
    'frontmatter_cover_line': 'E-ISSN: {issn}   Cilt | Volume: {cilt}   Sayı | Issue: {sayi}   Yıl | Year: {yil}',
}

# Page, paragraph and APA 7 preferences. They are inert until `layout_mode` is
# 'custom' (page/paragraph values) so every built-in template renders exactly as
# before; APA options default to the behaviour that predates them.
LAYOUT_DEFAULTS = {
    'layout_mode': 'template',
    'margin_top_cm': 2.5, 'margin_bottom_cm': 2.5, 'margin_left_cm': 2.5, 'margin_right_cm': 2.5,
    'header_distance_cm': 1.25, 'footer_distance_cm': 1.25,
    'body_align': 'justify', 'body_space_before_pt': 0.0, 'body_space_after_pt': 6.0,
    'body_line_spacing': 1.15, 'body_first_line_indent_cm': 0.0,
    'heading_size_pt': 11.0, 'heading_space_before_pt': 12.0, 'heading_space_after_pt': 6.0,
    'heading1_align': 'left',
    'caption_size_pt': 9.0, 'table_size_pt': 9.0, 'footnote_size_pt': 8.0,
    'ref_align': 'left', 'ref_hanging_cm': 1.25, 'ref_space_before_pt': 0.0,
    'ref_space_after_pt': 6.0, 'ref_line_spacing': 1.0, 'ref_size_pt': 0.0,
    'logo_mode': 'side', 'logo_width_cm': 0.0,
    'frontmatter_cover': 'yes', 'frontmatter_toc': 'yes', 'toc_show_authors': 'yes', 'frontmatter_font': 'sans',
    'cover_text_top_cm': 26.4, 'cover_text_size_pt': 12.0, 'cover_text_color': '#FFFFFF',
}
APA_DEFAULTS = {
    'apa_and': '&', 'apa_et_al': 'et al.', 'apa_page_style': 'auto', 'apa_no_date': 'auto',
    'apa_max_ref_authors': 20.0, 'apa_sort_references': 'yes', 'apa_check': 'warn',
}
# key: (minimum, maximum). Values arrive as numbers or numeric strings from the UI.
_LAYOUT_RANGES = {
    'margin_top_cm': (0.3, 6), 'margin_bottom_cm': (0.3, 6), 'margin_left_cm': (0.5, 6),
    'margin_right_cm': (0.5, 6), 'header_distance_cm': (0.2, 4), 'footer_distance_cm': (0.2, 4),
    'body_space_before_pt': (0, 48), 'body_space_after_pt': (0, 48), 'body_line_spacing': (0.8, 3),
    'body_first_line_indent_cm': (0, 4), 'heading_size_pt': (8, 24), 'heading_space_before_pt': (0, 48),
    'heading_space_after_pt': (0, 48), 'caption_size_pt': (7, 14), 'table_size_pt': (7, 14),
    'footnote_size_pt': (6, 14), 'ref_hanging_cm': (0, 3), 'ref_space_before_pt': (0, 48),
    'ref_space_after_pt': (0, 48), 'ref_line_spacing': (0.8, 3), 'ref_size_pt': (0, 14),
    'apa_max_ref_authors': (1, 50), 'logo_width_cm': (0, 19), 'cover_text_top_cm': (1, 29),
    'cover_text_size_pt': (6, 40),
}
_LAYOUT_CHOICES = {
    'layout_mode': {'template', 'custom'}, 'body_align': {'left', 'justify'},
    'heading1_align': {'left', 'center'}, 'ref_align': {'left', 'justify'},
    'apa_and': {'&', 've', 'and'}, 'apa_et_al': {'et al.', 'vd.', 'auto'},
    'apa_page_style': {'auto', 'tr', 'en'}, 'apa_no_date': {'auto', 't.y.', 'n.d.'},
    'apa_sort_references': {'yes', 'no'}, 'apa_check': {'warn', 'off'},
    'logo_mode': {'side', 'banner'}, 'frontmatter_cover': {'yes', 'no'}, 'frontmatter_toc': {'yes', 'no'},
    'toc_show_authors': {'yes', 'no'}, 'frontmatter_font': {'sans', 'journal'},
}
_FONT_ALIASES = {
    'palatino linotype': 'texgyrepagella', 'palatino': 'texgyrepagella',
    'tex gyre pagella': 'texgyrepagella', 'times new roman': 'texgyretermes',
    'times': 'texgyretermes', 'tex gyre termes': 'texgyretermes',
    'century': 'texgyrebonum', 'century schoolbook': 'texgyrebonum',
    'calibri': 'carlito', 'arial': 'texgyreheros', 'sans serif': 'texgyreheros',
    'sans-serif': 'texgyreheros', 'latin modern': 'latinmodern',
}


def default_settings():
    return {**_DEFAULTS, **RUNNING_DEFAULTS, **LAYOUT_DEFAULTS, **APA_DEFAULTS}


def _normalize_layout(result):
    for key, choices in _LAYOUT_CHOICES.items():
        value = str(result[key]).strip().lower()
        if value not in choices:
            raise ValueError(f'Geçersiz {key} seçeneği.')
        result[key] = value
    for key, (low, high) in _LAYOUT_RANGES.items():
        raw = result[key]
        if isinstance(raw, str) and not raw.strip():
            raw = (LAYOUT_DEFAULTS | APA_DEFAULTS)[key]
        try:
            number = float(str(raw).replace(',', '.')) if isinstance(raw, str) else float(raw)
        except (TypeError, ValueError):
            raise ValueError(f'{key} bir sayı olmalıdır.') from None
        if isinstance(raw, bool) or not math.isfinite(number) or not low <= number <= high:
            raise ValueError(f'{key} değeri {low:g}–{high:g} arasında olmalıdır.')
        result[key] = round(number, 2)
    if not re.fullmatch(r'#[0-9a-fA-F]{6}', str(result['cover_text_color'])):
        raise ValueError('Kapak yazı rengi #RRGGBB biçiminde olmalıdır.')
    result['cover_text_color'] = str(result['cover_text_color']).upper()
    if result['ref_size_pt'] and result['ref_size_pt'] < 7:
        raise ValueError('ref_size_pt değeri 0 (gövde puntosu) veya 7–14 olmalıdır.')
    result['apa_max_ref_authors'] = int(result['apa_max_ref_authors'])


def normalize_settings(raw):
    """Return complete safe settings; reject malformed user supplied values.

    Unknown keys are ignored, so exported preferences can evolve compatibly.
    Legacy `font` and `header_layout` names remain accepted.
    """
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError('Dergi ayarları bir nesne olmalıdır.')
    incoming = dict(raw)
    if 'font_family' not in incoming and 'font' in incoming:
        incoming['font_family'] = incoming['font']
    if 'template_id' not in incoming and 'header_layout' in incoming:
        incoming['template_id'] = incoming['header_layout']
    result = default_settings()
    result.update({k: v for k, v in incoming.items() if k in result})
    for key, choices in {
        'template_id': {template['id'] for template in TEMPLATES},
        'header_layout': {template['id'] for template in TEMPLATES},
        'footer_layout': {'full', 'compact', 'minimal'},
        'doi_position': {'top', 'bottom'}, 'first_page_fit': {'auto', 'compact', 'dense'},
        'body_size': {'10', '11', '12'},
    }.items():
        value = str(result[key]).strip().lower()
        if value not in choices:
            raise ValueError(f'Geçersiz {key} seçeneği.')
        result[key] = value
    result['header_layout'] = result['template_id']
    font = str(result['font_family']).strip().lower()
    font = _FONT_ALIASES.get(font, font)
    if font not in {'texgyrepagella', 'texgyretermes', 'texgyrebonum', 'texgyreheros', 'carlito', 'latinmodern'}:
        raise ValueError('Desteklenmeyen yazı tipi.')
    result['font_family'] = font
    for key in ('english_only', 'show_logo', 'show_cc_logo', 'link_citations'):
        if not isinstance(result[key], bool):
            raise ValueError(f'{key} doğru/yanlış değeri olmalıdır.')
    for key, maximum in {'journal_name_tr': 250, 'journal_name_en': 250, 'issn_print': 30,
                         'issn_online': 30, 'footer_text': 3000, 'journal_url': 500,
                         'corresponding_marker': 4, 'logo_stem': 80, 'cc_logo_stem': 80,
                         'english_abstract_heading': 80, 'frontmatter_text': 20000, 'frontmatter_line': 200,
                         'frontmatter_toc_heading': 100, 'frontmatter_cover_line': 200}.items():
        value = result[key]
        if not isinstance(value, str) or len(value) > maximum or any(ord(c) < 32 and c not in '\n\t' for c in value):
            raise ValueError(f'{key} alanı geçerli bir metin olmalıdır (en çok {maximum} karakter).')
        result[key] = value.strip()
    result['english_abstract_heading'] = result['english_abstract_heading'] or 'Abstract'
    color = result['accent_color']
    if not isinstance(color, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
        raise ValueError('Vurgu rengi #RRGGBB biçiminde olmalıdır.')
    result['accent_color'] = color.upper()
    try:
        height = float(result['logo_height_cm'])
    except (TypeError, ValueError):
        raise ValueError('Logo yüksekliği bir sayı olmalıdır.') from None
    if isinstance(result['logo_height_cm'], bool) or not math.isfinite(height) or not 0.5 <= height <= 3.5:
        raise ValueError('Logo yüksekliği 0,5–3,5 cm arasında olmalıdır.')
    result['logo_height_cm'] = height
    url = result['journal_url']
    if url:
        try:
            parsed = urlsplit(url)
            if parsed.scheme not in {'https', 'http'} or not parsed.netloc or parsed.username or parsed.password or any(c.isspace() for c in url):
                raise ValueError
        except ValueError:
            raise ValueError('Dergi adresi geçerli bir http/https adresi olmalıdır.') from None
    for key in ('logo_stem', 'cc_logo_stem'):
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}', result[key]):
            raise ValueError('Logo dosyası için güvenli bir ad gereklidir.')
    if result['corresponding_marker'] not in {'*', '†', '‡', '§', '¶', '#', '★', '✉'}:
        raise ValueError('Desteklenmeyen sorumlu yazar işareti.')
    _normalize_layout(result)
    result.update(normalize_running(raw))
    return result
