"""
Günlük Otomasyon Pipeline — Tüm agentları sırayla çalıştırır

Akış:
  AraştırmacıAjan → İçerikAjanı → MüzikAjanı + AnimasyonAjanı → YükleyiciAjan

Kullanım:
  python3 scriptler/gunluk_pipeline.py                  # Tam pipeline
  python3 scriptler/gunluk_pipeline.py --adim arastir   # Sadece araştırma
  python3 scriptler/gunluk_pipeline.py --adim icerik    # Sadece içerik planla
  python3 scriptler/gunluk_pipeline.py --adim muzik     # Sadece müzik üret
  python3 scriptler/gunluk_pipeline.py --adim video     # Sadece video derle
  python3 scriptler/gunluk_pipeline.py --adim yukle     # Sadece yükle
  python3 scriptler/gunluk_pipeline.py --sadece-uret    # Üret ama yükleme
"""
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BASE_DIR, CREDENTIALS_FILE, VIDEO_DIR, THUMBNAIL_DIR, ANIMASYON_DIR

ICERIK_DIR = os.path.join(BASE_DIR, "icerik")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

LOG_DOSYASI = os.path.join(RAPOR_DIR, "yukleme_log.json")

# ─── Yardımcılar ──────────────────────────────────────────────────────────────

def log_yaz(tarih, video_baslik, video_id, durum, hata=""):
    os.makedirs(RAPOR_DIR, exist_ok=True)
    kayitlar = []
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, encoding="utf-8") as f:
            try:
                kayitlar = json.load(f)
            except Exception:
                kayitlar = []

    kayitlar.append({
        "tarih": tarih,
        "zaman": datetime.now().isoformat(),
        "baslik": video_baslik,
        "video_id": video_id,
        "durum": durum,
        "hata": hata,
    })

    with open(LOG_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=2)

def plan_oku(tarih):
    plan_yolu = os.path.join(ICERIK_DIR, f"bugun_{tarih}.json")
    if not os.path.exists(plan_yolu):
        return None
    with open(plan_yolu, encoding="utf-8") as f:
        return json.load(f)

def plan_kaydet(plan, tarih):
    plan_yolu = os.path.join(ICERIK_DIR, f"bugun_{tarih}.json")
    with open(plan_yolu, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

def baslik(metin):
    print(f"\n{'='*60}")
    print(f"  {metin}")
    print(f"{'='*60}")

# ─── Adım 1: Araştırma ────────────────────────────────────────────────────────

def adim_arastir(tarih, hizli=False):
    baslik("ADIM 1 — ARAŞTIRMACIAjan")
    from research_agent import arastir, youtube_baglan

    youtube = youtube_baglan() if os.path.exists(CREDENTIALS_FILE) else None
    if not youtube:
        print("  credentials.json yok — offline araştırma yapılıyor")

    rapor = arastir(youtube=youtube, hizli_mod=hizli)
    return rapor

# ─── Adım 2: İçerik planı ─────────────────────────────────────────────────────

def adim_icerik(tarih, arastirma_raporu=None):
    baslik("ADIM 2 — İÇERİKAJANI")
    from content_agent import icerik_plani_olustur, son_arastirma_oku

    if arastirma_raporu is None:
        arastirma_raporu = son_arastirma_oku(tarih)

    plan = icerik_plani_olustur(araştirma_raporu=arastirma_raporu, tarih=tarih)
    return plan

# ─── Adım 3: Müzik üretimi ────────────────────────────────────────────────────

def adim_muzik(tarih, plan):
    baslik("ADIM 3 — MÜZİKAJANI")
    from music_agent import icerik_planından_muzik_uret

    plan = icerik_planından_muzik_uret(plan)
    plan_kaydet(plan, tarih)
    return plan

# ─── Adım 4: Animasyon üretimi ────────────────────────────────────────────────

def adim_animasyon(tarih, plan):
    baslik("ADIM 4 — ANİMASYONAJANI")
    from blender_animasyon import blender_render_et

    os.makedirs(ANIMASYON_DIR, exist_ok=True)

    for video in plan["videolar"]:
        sahne = video.get("sahne", "gece_gokyuzu")
        sira = video["sira"]

        # Ninni → gece sahnesi, şarkı → neşeli sahne
        blender_sahne = "ninni" if video["tur"] == "ninni" else "neseli"

        animasyon_yolu = os.path.join(ANIMASYON_DIR, f"animasyon_{tarih}_v{sira}.mp4")

        if os.path.exists(animasyon_yolu):
            print(f"  Mevcut animasyon: {animasyon_yolu}")
            video["animasyon_dosyasi"] = animasyon_yolu
            continue

        print(f"  Render: {sahne} (30 saniyelik loop)...")
        try:
            blender_render_et(blender_sahne, 30, animasyon_yolu)
            video["animasyon_dosyasi"] = animasyon_yolu
            print(f"  Tamamlandı: {animasyon_yolu}")
        except Exception as e:
            print(f"  Blender hatası: {e}")
            print(f"  Uyarı: Animasyon yok, video üretimi atlanacak.")
            video["animasyon_dosyasi"] = ""

    plan_kaydet(plan, tarih)
    return plan

# ─── Adım 5: Video derleme ────────────────────────────────────────────────────

def adim_video_derle(tarih, plan):
    baslik("ADIM 5 — VİDEO DERLEMESİ")
    from video_compiler import uzun_video_olustur, short_video_olustur
    from thumbnail_generator import thumbnail_olustur

    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)

    for video in plan["videolar"]:
        sira = video["sira"]
        baslik_str = video["baslik"]
        tur = video["tur"]
        sure = video["sure_saniye"]
        animasyon = video.get("animasyon_dosyasi", "")
        muzik = video.get("muzik_dosyasi", "")

        if not animasyon or not os.path.exists(animasyon):
            print(f"  [{sira}] Animasyon yok, atlanıyor: {baslik_str}")
            video["video_dosyasi"] = ""
            continue

        if not muzik or not os.path.exists(muzik):
            print(f"  [{sira}] Müzik yok, atlanıyor: {baslik_str}")
            video["video_dosyasi"] = ""
            continue

        cikti_adi = f"video_{tarih}_v{sira}"
        cikti_yolu = os.path.join(VIDEO_DIR, f"{cikti_adi}.mp4")

        if os.path.exists(cikti_yolu):
            print(f"  [{sira}] Mevcut: {cikti_yolu}")
            video["video_dosyasi"] = cikti_yolu
        else:
            print(f"  [{sira}] Derleniyor: {baslik_str[:50]}")
            try:
                if video.get("shorts"):
                    video["video_dosyasi"] = short_video_olustur(animasyon, muzik, sure, baslik_str, cikti_adi)
                else:
                    video["video_dosyasi"] = uzun_video_olustur(animasyon, muzik, sure, baslik_str, cikti_adi)
            except Exception as e:
                print(f"  Derleme hatası: {e}")
                video["video_dosyasi"] = ""
                continue

        # Thumbnail
        sure_metin = f"{sure//3600} Saat" if sure >= 3600 else f"{sure//60} Dakika"
        temiz_baslik = baslik_str.split("🌙")[0].split("🎵")[0].split("🐟")[0].strip()
        try:
            video["thumbnail_dosyasi"] = thumbnail_olustur(
                temiz_baslik, sure_metin,
                tur=tur if tur != "short" else "ninni",
                dosya_adi=f"thumb_{tarih}_v{sira}.jpg",
                renk_sema=video.get("thumbnail_renk", "ninni_mavi"),
            )
        except Exception as e:
            print(f"  Thumbnail hatası: {e}")
            video["thumbnail_dosyasi"] = ""

    plan_kaydet(plan, tarih)
    return plan

# ─── Adım 6: YouTube'a yükle ──────────────────────────────────────────────────

def adim_yukle(tarih, plan):
    baslik("ADIM 6 — YÜKLEYİCİAJAN")

    if not os.path.exists(CREDENTIALS_FILE):
        print("  HATA: credentials.json bulunamadı!")
        print("  YOUTUBE_API_KURULUM.md dosyasını takip edin.")
        return plan

    from youtube_upload import youtube_baglan, video_yukle

    youtube = youtube_baglan()

    for video in plan["videolar"]:
        sira = video["sira"]
        baslik_str = video["baslik"]
        video_dosyasi = video.get("video_dosyasi", "")

        if not video_dosyasi or not os.path.exists(video_dosyasi):
            print(f"  [{sira}] Video yok, atlanıyor: {baslik_str}")
            continue

        if video.get("youtube_id"):
            print(f"  [{sira}] Zaten yüklendi: {video['youtube_id']}")
            continue

        print(f"\n  [{sira}] Yükleniyor: {baslik_str[:50]}")
        try:
            video_id = video_yukle(
                youtube,
                video_dosyasi,
                baslik_str,
                video["aciklama"],
                video["tags"],
                thumbnail_dosyasi=video.get("thumbnail_dosyasi"),
                shorts=video.get("shorts", False),
            )
            video["youtube_id"] = video_id
            video["youtube_url"] = f"https://www.youtube.com/watch?v={video_id}"
            log_yaz(tarih, baslik_str, video_id, "basarili")
            print(f"  ✓ {video['youtube_url']}")
        except Exception as e:
            print(f"  HATA: {e}")
            log_yaz(tarih, baslik_str, "", "hata", str(e))

    plan_kaydet(plan, tarih)
    return plan

# ─── Ana pipeline ─────────────────────────────────────────────────────────────

def pipeline_calistir(tarih=None, adim=None, sadece_uret=False, hizli=False):
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")

    print(f"\n{'*'*60}")
    print(f"  GÜNLÜK PİPELİNE — {tarih}")
    print(f"  Başlangıç: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'*'*60}")

    arastirma = None
    plan = None

    # Tek adım modu
    if adim:
        plan = plan_oku(tarih)
        if adim == "arastir":
            adim_arastir(tarih, hizli)
        elif adim == "icerik":
            adim_icerik(tarih)
        elif adim == "muzik":
            if plan:
                adim_muzik(tarih, plan)
            else:
                print("Önce içerik planı oluşturun: --adim icerik")
        elif adim == "animasyon":
            if plan:
                adim_animasyon(tarih, plan)
            else:
                print("Önce içerik planı oluşturun: --adim icerik")
        elif adim == "video":
            if plan:
                adim_video_derle(tarih, plan)
            else:
                print("Önce içerik planı oluşturun: --adim icerik")
        elif adim == "yukle":
            if plan:
                adim_yukle(tarih, plan)
            else:
                print("Video planı bulunamadı.")
        return

    # Tam pipeline
    try:
        arastirma = adim_arastir(tarih, hizli)
    except Exception as e:
        print(f"Araştırma hatası: {e} — devam ediliyor")

    plan = adim_icerik(tarih, arastirma)
    plan = adim_muzik(tarih, plan)
    plan = adim_animasyon(tarih, plan)
    plan = adim_video_derle(tarih, plan)

    if not sadece_uret:
        plan = adim_yukle(tarih, plan)

    # Özet
    print(f"\n{'*'*60}")
    print(f"  PİPELİNE TAMAMLANDI — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'*'*60}")
    for v in plan.get("videolar", []):
        if v.get("youtube_id"):
            print(f"  ✓ {v['baslik'][:50]}")
            print(f"    {v['youtube_url']}")
        elif v.get("video_dosyasi"):
            print(f"  ⚠ Üretildi ama yüklenmedi: {v['baslik'][:50]}")
        else:
            print(f"  ✗ Üretilemedi: {v['baslik'][:50]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Günlük YouTube pipeline")
    parser.add_argument("--tarih", help="Tarih (YYYY-MM-DD)")
    parser.add_argument("--adim", choices=["arastir","icerik","muzik","animasyon","video","yukle"],
                        help="Sadece tek adım çalıştır")
    parser.add_argument("--sadece-uret", action="store_true", help="Üret ama YouTube'a yükleme")
    parser.add_argument("--hizli", action="store_true", help="Hızlı araştırma modu")
    args = parser.parse_args()

    pipeline_calistir(
        tarih=args.tarih,
        adim=args.adim,
        sadece_uret=args.sadece_uret,
        hizli=args.hizli,
    )
