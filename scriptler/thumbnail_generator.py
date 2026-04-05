from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import THUMBNAIL_DIR, VIDEO_GENISLIK, VIDEO_YUKSEKLIK

THUMBNAIL_W = 1280
THUMBNAIL_H = 720

RENKLER = {
    "ninni_mavi": {"bg": [(20, 20, 80), (60, 60, 160)], "yazi": (255, 255, 255), "vurgu": (255, 215, 0)},
    "ninni_mor": {"bg": [(60, 20, 80), (120, 60, 160)], "yazi": (255, 255, 255), "vurgu": (255, 200, 50)},
    "neseli_sari": {"bg": [(255, 200, 0), (255, 150, 0)], "yazi": (50, 50, 50), "vurgu": (255, 50, 50)},
    "neseli_yesil": {"bg": [(50, 180, 50), (20, 140, 20)], "yazi": (255, 255, 255), "vurgu": (255, 255, 0)},
}

def gradyan_arkaplan(draw, w, h, renk1, renk2):
    for y in range(h):
        oran = y / h
        r = int(renk1[0] + (renk2[0] - renk1[0]) * oran)
        g = int(renk1[1] + (renk2[1] - renk1[1]) * oran)
        b = int(renk1[2] + (renk2[2] - renk1[2]) * oran)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

def yildiz_ekle(draw, w, h, renk, sayi=20):
    import random
    random.seed(42)
    for _ in range(sayi):
        x = random.randint(0, w)
        y = random.randint(0, h // 2)
        boyut = random.randint(2, 8)
        draw.ellipse([x-boyut, y-boyut, x+boyut, y+boyut], fill=renk)

def ay_ekle(draw, x, y, boyut, renk):
    # Dolgu daire
    draw.ellipse([x, y, x+boyut, y+boyut], fill=renk)
    # Kesim dairesi (hilal efekti)
    draw.ellipse([x+boyut//4, y-boyut//6, x+boyut+boyut//4, y+boyut-boyut//6], fill=(0, 0, 0, 0))

def thumbnail_olustur(baslik, sure_metni, tur="ninni", dosya_adi=None, renk_sema=None):
    img = Image.new("RGB", (THUMBNAIL_W, THUMBNAIL_H))
    draw = ImageDraw.Draw(img)

    if renk_sema is None:
        renk_sema = "ninni_mavi" if tur == "ninni" else "neseli_sari"

    renkler = RENKLER[renk_sema]
    gradyan_arkaplan(draw, THUMBNAIL_W, THUMBNAIL_H, renkler["bg"][0], renkler["bg"][1])

    if tur == "ninni":
        yildiz_ekle(draw, THUMBNAIL_W, THUMBNAIL_H, renkler["vurgu"])

    # Dekoratif daireler
    draw.ellipse([-100, -100, 200, 200], outline=(*renkler["vurgu"], 80), width=3)
    draw.ellipse([THUMBNAIL_W-200, THUMBNAIL_H-200, THUMBNAIL_W+100, THUMBNAIL_H+100],
                 outline=(*renkler["vurgu"], 80), width=3)

    # Başlık metni
    try:
        font_buyuk = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 80)
        font_orta = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 55)
        font_kucuk = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
    except:
        font_buyuk = ImageFont.load_default()
        font_orta = font_buyuk
        font_kucuk = font_buyuk

    # Başlık - gölge efekti
    x_merkez = THUMBNAIL_W // 2
    y_baslik = THUMBNAIL_H // 3

    # Gölge
    draw.text((x_merkez+3, y_baslik+3), baslik, font=font_buyuk, fill=(0,0,0,128), anchor="mm")
    # Asıl metin
    draw.text((x_merkez, y_baslik), baslik, font=font_buyuk, fill=renkler["yazi"], anchor="mm")

    # Süre kutusu
    kutu_w, kutu_h = 300, 70
    kutu_x = x_merkez - kutu_w // 2
    kutu_y = THUMBNAIL_H * 2 // 3
    draw.rounded_rectangle([kutu_x, kutu_y, kutu_x+kutu_w, kutu_y+kutu_h],
                           radius=35, fill=renkler["vurgu"])
    draw.text((x_merkez, kutu_y + kutu_h//2), sure_metni,
              font=font_orta, fill=(50,50,50), anchor="mm")

    # Emoji/simge alanı
    if tur == "ninni":
        draw.text((100, THUMBNAIL_H//2), "🌙", font=font_buyuk, anchor="mm")
        draw.text((THUMBNAIL_W-100, THUMBNAIL_H//2), "⭐", font=font_buyuk, anchor="mm")

    # Kanal adı
    draw.text((x_merkez, THUMBNAIL_H - 50), "@iyiuykularcocuklar00",
              font=font_kucuk, fill=(*renkler["yazi"][:3], 180), anchor="mm")

    # Kaydet
    if dosya_adi is None:
        dosya_adi = baslik.replace(" ", "_").lower()[:30] + ".jpg"

    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    tam_yol = os.path.join(THUMBNAIL_DIR, dosya_adi)
    img.save(tam_yol, "JPEG", quality=95)
    print(f"Thumbnail oluşturuldu: {tam_yol}")
    return tam_yol


if __name__ == "__main__":
    thumbnail_olustur("Bebek Ninnileri", "1 Saat", tur="ninni", dosya_adi="test_ninni.jpg")
    thumbnail_olustur("Çocuk Şarkıları", "30 Dakika", tur="cocuk_sarki", renk_sema="neseli_sari", dosya_adi="test_sarki.jpg")
    print("Test thumbnaillar oluşturuldu!")
