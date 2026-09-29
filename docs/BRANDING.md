# GASTROIA Editor görsel kimliği

GASTROIA yeşili zemin üzerinde beyaz serifli bir G harfi ve altında ince bir çizgi. Simge arayüzde, macOS ve Windows paketlerinde aynıdır.

| Kullanım | Renk |
|---|---|
| Zemin | GASTROIA yeşili `#9EC53C` |
| G harfi ve çizgi | Beyaz `#FFFFFF` |

Ana kaynak: [`static/brand.svg`](../static/brand.svg). SVG içindeki G harfi sistem serif yazı tipiyle çizilir; PNG/ICO/ICNS dosyaları `scripts/export_brand.py` ile üretilir. Kenarlar dışında gerçek saydamlık vardır. Gölge, doku ve degrade kullanılmaz. Simgedeki boşluğu koruyun; yatay veya dikey esnetmeyin.

Üretim dosyaları: `gastroia_editor_icon.png` (1024 px), `icon_gastroia.icns` (macOS), `icon_gastroia.ico` (Windows). SVG değiştirildiğinde bu dosyaları yeniden üretin:

```sh
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/export_brand.py
```

Logo taslağı yerleşik görsel üretim aracıyla hazırlandı; uygulamanın son varlıkları aynı tasarımın düzenlenebilir SVG kaynağından oluşturuldu. Tasarım özeti: lacivert yuvarlatılmış kare üzerinde kırık beyaz, akademik tipografiyle çizilmiş A ve küçük yeşil artı; sade, düz renkli, küçük boyutlarda okunabilir; ek yazı, doku veya üç boyutlu efekt yok.

Bu varlıklar da deponun MIT lisansı kapsamındadır.
