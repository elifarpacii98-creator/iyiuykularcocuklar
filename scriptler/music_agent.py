"""
MüzikAjanı — Suno AI ile şarkı ve müzik üretir

Kullanım:
  python3 scriptler/music_agent.py
  python3 scriptler/music_agent.py --tarih 2026-04-05
  python3 scriptler/music_agent.py --tur ninni --ad "Ay Işığı Ninnisi"
  python3 scriptler/music_agent.py --test   # API bağlantısını test et
"""
import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BASE_DIR, MUZIK_DIR

ICERIK_DIR = os.path.join(BASE_DIR, "icerik")
SUNO_API_KEY = os.environ.get("SUNO_API_KEY", "")  # export SUNO_API_KEY=xxx ile ayarla
SUNO_API_URL = "https://studio-api.suno.ai/api/external/"

# ─── Suno AI prompt şablonları ────────────────────────────────────────────────

MUZIK_SABLONLARI = {
    "ninni": {
        "style": "Turkish lullaby, soft female vocal, slow gentle tempo 60-65 BPM, "
                 "piano and strings, soothing, warm, peaceful, baby sleep music",
        "aciklama": "Yavaş ninni, piyano ve keman",
    },
    "ninni_ambient": {
        "style": "ambient lullaby, no lyrics, slow 55 BPM, soft piano, "
                 "gentle strings, sleep music, calm, peaceful, instrumental",
        "aciklama": "Enstrümantal uyku müziği",
    },
    "cocuk_sarki": {
        "style": "Turkish children's song, cheerful upbeat 108-112 BPM, "
                 "xylophone and piano, children's choir, playful, bright, happy",
        "aciklama": "Neşeli çocuk şarkısı",
    },
    "cocuk_sabah": {
        "style": "Turkish children's morning song, cheerful 105 BPM, "
                 "acoustic guitar and piano, warm, happy, bright",
        "aciklama": "Sabah şarkısı",
    },
    "short_ninni": {
        "style": "Turkish lullaby short version 60 seconds, soft female vocal, "
                 "60 BPM, piano, gentle, dreamy",
        "aciklama": "Kısa ninni (60sn)",
    },
}

# ─── Suno API fonksiyonları ───────────────────────────────────────────────────

def suno_sarki_uret(baslik, sozler, muzik_tarzi, cikti_yolu, max_bekleme=300):
    """
    Suno AI API ile şarkı üret.
    API anahtarı yoksa simüle modda çalışır.
    """
    os.makedirs(MUZIK_DIR, exist_ok=True)

    if not SUNO_API_KEY:
        print(f"  UYARI: SUNO_API_KEY ayarlanmamış.")
        print(f"  Simüle mod: {cikti_yolu} için yer tutucu oluşturuluyor...")
        _yer_tutucu_olustur(cikti_yolu, baslik)
        return cikti_yolu

    print(f"  Suno AI'ye istek gönderiliyor: {baslik}")

    # Prompt hazırla
    tam_prompt = _suno_prompt_olustur(baslik, sozler, muzik_tarzi)

    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json",
    }

    # Üretim isteği
    try:
        yanit = requests.post(
            f"{SUNO_API_URL}generate/",
            headers=headers,
            json={
                "prompt": tam_prompt,
                "mv": "chirp-v3-5",
                "title": baslik,
                "tags": muzik_tarzi,
                "make_instrumental": not bool(sozler.strip()),
                "wait_audio": False,
            },
            timeout=30,
        )
        yanit.raise_for_status()
        uretim_id = yanit.json()["id"]
        print(f"  Üretim başladı. ID: {uretim_id}")
    except requests.RequestException as e:
        print(f"  Suno API hatası: {e}")
        _yer_tutucu_olustur(cikti_yolu, baslik)
        return cikti_yolu

    # Üretim tamamlanana kadar bekle
    bekleme = 0
    kontrol_araligi = 10
    while bekleme < max_bekleme:
        time.sleep(kontrol_araligi)
        bekleme += kontrol_araligi

        try:
            durum = requests.get(
                f"{SUNO_API_URL}feed/",
                headers=headers,
                params={"ids": uretim_id},
                timeout=15,
            ).json()

            if durum and durum[0].get("status") == "complete":
                audio_url = durum[0].get("audio_url")
                if audio_url:
                    print(f"  Üretim tamamlandı! İndiriliyor...")
                    _indir(audio_url, cikti_yolu)
                    print(f"  Kaydedildi: {cikti_yolu}")
                    return cikti_yolu

            print(f"  Bekleniyor... ({bekleme}s)")
        except Exception as e:
            print(f"  Durum kontrolü hatası: {e}")

    print(f"  Zaman aşımı. Yer tutucu oluşturuluyor.")
    _yer_tutucu_olustur(cikti_yolu, baslik)
    return cikti_yolu

def _suno_prompt_olustur(baslik, sozler, muzik_tarzi):
    if sozler and sozler.strip():
        return f"[{muzik_tarzi}]\n\n{sozler}"
    return f"[{muzik_tarzi}]\n[instrumental, no lyrics]"

def _indir(url, yol):
    yanit = requests.get(url, stream=True, timeout=60)
    yanit.raise_for_status()
    with open(yol, "wb") as f:
        for parca in yanit.iter_content(chunk_size=8192):
            f.write(parca)

def _yer_tutucu_olustur(yol, baslik):
    """
    Suno API yokken sessiz bir ses dosyası oluşturur.
    Gerçek müzik eklendiğinde bu dosya değiştirilir.
    """
    try:
        # FFmpeg ile 3 saniyelik sessiz ses
        import subprocess
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "3", "-q:a", "9", "-acodec", "libmp3lame",
            yol
        ], capture_output=True)
        print(f"  Sessiz yer tutucu oluşturuldu: {yol}")
    except Exception:
        # FFmpeg yoksa boş dosya
        open(yol, "wb").close()

# ─── İçerik planından müzik üret ─────────────────────────────────────────────

def icerik_planından_muzik_uret(icerik_plani):
    """Günün içerik planındaki tüm videolar için müzik üret"""
    tarih = icerik_plani["tarih"]
    uretilen = []

    print(f"\n{'='*60}")
    print(f"MÜZİKAJANI — {tarih}")
    print(f"{'='*60}")

    for video in icerik_plani["videolar"]:
        sira = video["sira"]
        baslik = video["baslik"]
        tur = video["tur"]
        sarki_adi = video.get("sarki_adi", baslik)
        sozler = video.get("sarki_sozleri", "")
        muzik_tarzi = video.get("muzik_tarzi", "")

        print(f"\n[{sira}/2] {sarki_adi}")

        # Müzik tipi belirle
        if tur == "ninni" and not sozler.strip():
            sablon_key = "ninni_ambient"
        elif tur == "ninni":
            sablon_key = "ninni"
        elif tur == "short":
            sablon_key = "short_ninni"
        else:
            sablon_key = "cocuk_sarki"

        sablon = MUZIK_SABLONLARI.get(sablon_key, MUZIK_SABLONLARI["ninni"])

        # Müzik tarzı: içerik planındaki değer öncelikli
        tam_muzik_tarzi = muzik_tarzi if muzik_tarzi else sablon["style"]

        # Dosya adı
        temiz_ad = sarki_adi.lower().replace(" ", "_").replace("ç","c").replace("ş","s")
        temiz_ad = temiz_ad.replace("ğ","g").replace("ü","u").replace("ö","o").replace("ı","i")
        temiz_ad = "".join(c for c in temiz_ad if c.isalnum() or c == "_")[:30]
        cikti_yolu = os.path.join(MUZIK_DIR, f"{temiz_ad}_{tarih}.mp3")

        # Zaten varsa atla
        if os.path.exists(cikti_yolu) and os.path.getsize(cikti_yolu) > 1000:
            print(f"  Mevcut: {cikti_yolu}")
            uretilen.append({"video_sira": sira, "dosya": cikti_yolu, "baslik": sarki_adi})
            continue

        # Üret
        dosya = suno_sarki_uret(sarki_adi, sozler, tam_muzik_tarzi, cikti_yolu)
        uretilen.append({"video_sira": sira, "dosya": dosya, "baslik": sarki_adi})

    # Sonuçları plana ekle
    muzik_haritasi = {m["video_sira"]: m["dosya"] for m in uretilen}
    for video in icerik_plani["videolar"]:
        video["muzik_dosyasi"] = muzik_haritasi.get(video["sira"], "")

    print(f"\n{'='*60}")
    print(f"Müzik üretimi tamamlandı: {len(uretilen)} dosya")
    for u in uretilen:
        durum = "✓" if os.path.getsize(u["dosya"]) > 1000 else "⚠ yer tutucu"
        print(f"  {durum} {u['baslik']}")

    return icerik_plani

def suno_api_test():
    """API bağlantısını test et"""
    if not SUNO_API_KEY:
        print("SUNO_API_KEY ayarlanmamış.")
        print("Ayarlamak için: export SUNO_API_KEY=your_key_here")
        print("\nSuno AI hesabı için: https://suno.ai")
        return False

    print("Suno API test ediliyor...")
    try:
        yanit = requests.get(
            f"{SUNO_API_URL}get_credits/",
            headers={"Authorization": f"Bearer {SUNO_API_KEY}"},
            timeout=10,
        )
        if yanit.status_code == 200:
            kredi = yanit.json().get("credits_left", 0)
            print(f"Bağlantı başarılı! Kalan kredi: {kredi}")
            return True
        else:
            print(f"API hatası: {yanit.status_code}")
            return False
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MüzikAjanı")
    parser.add_argument("--tarih", help="Tarih (YYYY-MM-DD)")
    parser.add_argument("--tur", choices=["ninni", "cocuk_sarki", "short"], help="Müzik türü")
    parser.add_argument("--ad", help="Şarkı adı")
    parser.add_argument("--test", action="store_true", help="API bağlantısını test et")
    args = parser.parse_args()

    if args.test:
        suno_api_test()
        sys.exit(0)

    # Tek şarkı modu
    if args.tur and args.ad:
        sablon = MUZIK_SABLONLARI.get(args.tur, MUZIK_SABLONLARI["ninni"])
        tarih = (args.tarih or datetime.now().strftime("%Y-%m-%d"))
        temiz = args.ad.lower().replace(" ", "_")[:20]
        cikti = os.path.join(MUZIK_DIR, f"{temiz}_{tarih}.mp3")
        suno_sarki_uret(args.ad, "", sablon["style"], cikti)
        sys.exit(0)

    # İçerik planından üret
    tarih = args.tarih or datetime.now().strftime("%Y-%m-%d")
    plan_yolu = os.path.join(ICERIK_DIR, f"bugun_{tarih}.json")

    if not os.path.exists(plan_yolu):
        print(f"İçerik planı bulunamadı: {plan_yolu}")
        print("Önce content_agent.py çalıştırın.")
        sys.exit(1)

    with open(plan_yolu, encoding="utf-8") as f:
        plan = json.load(f)

    guncellenmis_plan = icerik_planından_muzik_uret(plan)

    with open(plan_yolu, "w", encoding="utf-8") as f:
        json.dump(guncellenmis_plan, f, ensure_ascii=False, indent=2)

    print(f"\nPlan güncellendi: {plan_yolu}")
