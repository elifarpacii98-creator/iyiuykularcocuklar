"""
Günlük otomatik video üretim ve yükleme pipeline'ı

Kullanım:
  python3 scriptler/gunluk_pipeline.py              # Bugünkü videoları üret ve yükle
  python3 scriptler/gunluk_pipeline.py --sadece-uret  # Sadece video üret, yükleme yapma
  python3 scriptler/gunluk_pipeline.py --sadece-yukle # Hazır videoları yükle
"""
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *
from thumbnail_generator import thumbnail_olustur
from video_compiler import uzun_video_olustur, short_video_olustur, resimden_video_olustur
from youtube_upload import youtube_baglan, video_yukle, aciklama_olustur

# ─── Günlük Video Planı ────────────────────────────────────────────────────────

HAFTALIK_PLAN = {
    0: [  # Pazartesi
        {"tur": "ninni", "sure": 3600, "baslik": "Bebek Ninnileri 1 Saat 🌙 Uyku Müziği"},
        {"tur": "short", "sure": 60,   "baslik": "Tatlı Rüyalar Ninnisi ⭐"},
    ],
    1: [  # Salı
        {"tur": "ninni", "sure": 7200, "baslik": "Bebek Ninnileri 2 Saat 🌙 Derin Uyku Müziği"},
        {"tur": "cocuk_sarki", "sure": 120, "baslik": "Renkli Toplar Şarkısı 🎵"},
    ],
    2: [  # Çarşamba
        {"tur": "ninni", "sure": 3600, "baslik": "Günaydın Ninnileri 🌅 1 Saat"},
        {"tur": "short", "sure": 60,   "baslik": "Ay ve Yıldızlar 🌙⭐"},
    ],
    3: [  # Perşembe
        {"tur": "ninni", "sure": 5400, "baslik": "Bebek Ninnileri 90 Dakika 🌙"},
        {"tur": "cocuk_sarki", "sure": 120, "baslik": "Zıplayan Toplar Şarkısı 🎈"},
    ],
    4: [  # Cuma
        {"tur": "ninni", "sure": 7200, "baslik": "Gece Ninnileri 2 Saat 🌙 Bebek Uyku Müziği"},
        {"tur": "short", "sure": 60,   "baslik": "Ninni Zamanı 🌙"},
    ],
    5: [  # Cumartesi
        {"tur": "cocuk_sarki", "sure": 3600, "baslik": "Çocuk Şarkıları 1 Saat 🎵 Renkli Animasyonlar"},
        {"tur": "short", "sure": 60,   "baslik": "Rengarenk Şarkı 🌈"},
    ],
    6: [  # Pazar
        {"tur": "ninni", "sure": 10800, "baslik": "Bebek Ninnileri 3 Saat 🌙 Tüm Gece Uyku Müziği"},
        {"tur": "cocuk_sarki", "sure": 120, "baslik": "Mutlu Pazartesi Şarkısı 🌞"},
    ],
}


def varsayilan_animasyon_bul(tur):
    """Türe göre animasyon dosyasını bul"""
    animasyon_dosyalari = {
        "ninni": os.path.join(ANIMASYON_DIR, "ninni_dongu.mp4"),
        "cocuk_sarki": os.path.join(ANIMASYON_DIR, "neseli_dongu.mp4"),
        "short": os.path.join(ANIMASYON_DIR, "short_dongu.mp4"),
    }
    dosya = animasyon_dosyalari.get(tur, animasyon_dosyalari["ninni"])

    # Dosya yoksa yer tutucu bildir
    if not os.path.exists(dosya):
        print(f"  UYARI: Animasyon bulunamadı: {dosya}")
        print(f"  Lütfen Blender ile animasyon render edin veya dosyayı kopyalayın.")
        return None
    return dosya

def varsayilan_muzik_bul(tur):
    """Türe göre müzik dosyasını bul"""
    muzik_dosyalari = {
        "ninni": os.path.join(MUZIK_DIR, "ninni_muzik.mp3"),
        "cocuk_sarki": os.path.join(MUZIK_DIR, "neseli_muzik.mp3"),
        "short": os.path.join(MUZIK_DIR, "short_muzik.mp3"),
    }
    dosya = muzik_dosyalari.get(tur, muzik_dosyalari["ninni"])

    if not os.path.exists(dosya):
        print(f"  UYARI: Müzik bulunamadı: {dosya}")
        print(f"  Lütfen Suno AI'den müzik indirin ve {dosya} yoluna kaydedin.")
        return None
    return dosya

def video_uret(plan_maddesi):
    """Tek bir video üret"""
    baslik = plan_maddesi["baslik"]
    tur = plan_maddesi["tur"]
    sure = plan_maddesi["sure"]

    print(f"\n{'='*50}")
    print(f"Video üretiliyor: {baslik}")
    print(f"Tür: {tur} | Süre: {sure//60} dakika")
    print(f"{'='*50}")

    animasyon = varsayilan_animasyon_bul(tur)
    muzik = varsayilan_muzik_bul(tur)

    if not animasyon or not muzik:
        print("  Eksik dosyalar var, bu video atlanıyor.")
        return None

    tarih = datetime.now().strftime("%Y%m%d")
    cikti_adi = f"{tarih}_{tur}_{sure//60}dk"

    if tur == "short":
        video_yolu = short_video_olustur(animasyon, muzik, sure, baslik, cikti_adi)
    else:
        video_yolu = uzun_video_olustur(animasyon, muzik, sure, baslik, cikti_adi)

    # Thumbnail oluştur
    sure_metni = f"{sure//3600} Saat" if sure >= 3600 else f"{sure//60} Dakika"
    thumbnail_yolu = thumbnail_olustur(
        baslik.split(" 🌙")[0].split(" 🎵")[0],
        sure_metni,
        tur=tur if tur != "short" else "ninni",
        dosya_adi=f"{cikti_adi}_thumb.jpg"
    )

    return {"video": video_yolu, "thumbnail": thumbnail_yolu, "meta": plan_maddesi}

def video_yukle_youtube(video_bilgisi):
    """Videoyu YouTube'a yükle"""
    if not video_bilgisi:
        return None

    if not os.path.exists(CREDENTIALS_FILE):
        print("\nHATA: credentials.json bulunamadı!")
        print("Google Cloud Console'dan credentials.json indirin ve proje kök dizinine koyun.")
        return None

    youtube = youtube_baglan()
    meta = video_bilgisi["meta"]

    aciklama = aciklama_olustur(meta["baslik"], meta["tur"])
    tags = KATEGORILER.get(meta["tur"], KATEGORILER["ninni"])["tags"]

    video_id = video_yukle(
        youtube,
        video_bilgisi["video"],
        meta["baslik"],
        aciklama,
        tags,
        thumbnail_dosyasi=video_bilgisi.get("thumbnail"),
        shorts=(meta["tur"] == "short")
    )
    return video_id

def gunluk_calistir(sadece_uret=False, sadece_yukle=False):
    """Ana pipeline"""
    bugun = datetime.now().weekday()
    bugunun_plani = HAFTALIK_PLAN.get(bugun, HAFTALIK_PLAN[0])

    print(f"\n{'='*60}")
    print(f"GÜNLÜK PIPELINE - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Bugün {len(bugunun_plani)} video planlandı")
    print(f"{'='*60}")

    sonuclar = []
    for i, plan in enumerate(bugunun_plani):
        print(f"\n[{i+1}/{len(bugunun_plani)}] {plan['baslik']}")

        if not sadece_yukle:
            video_bilgisi = video_uret(plan)
        else:
            # Mevcut dosyaları bul
            tarih = datetime.now().strftime("%Y%m%d")
            cikti_adi = f"{tarih}_{plan['tur']}_{plan['sure']//60}dk"
            video_yolu = os.path.join(VIDEO_DIR, f"{cikti_adi}.mp4")
            thumb_yolu = os.path.join(THUMBNAIL_DIR, f"{cikti_adi}_thumb.jpg")
            video_bilgisi = {"video": video_yolu, "thumbnail": thumb_yolu, "meta": plan} if os.path.exists(video_yolu) else None

        if not sadece_uret and video_bilgisi:
            video_id = video_yukle_youtube(video_bilgisi)
            if video_id:
                print(f"Yüklendi: https://www.youtube.com/watch?v={video_id}")
                sonuclar.append({"baslik": plan["baslik"], "video_id": video_id})

    print(f"\n{'='*60}")
    print(f"Pipeline tamamlandı! {len(sonuclar)} video yüklendi.")
    for s in sonuclar:
        print(f"  ✓ {s['baslik']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Günlük YouTube video pipeline")
    parser.add_argument("--sadece-uret", action="store_true", help="Sadece video üret")
    parser.add_argument("--sadece-yukle", action="store_true", help="Sadece yükle")
    args = parser.parse_args()

    gunluk_calistir(
        sadece_uret=args.sadece_uret,
        sadece_yukle=args.sadece_yukle
    )
