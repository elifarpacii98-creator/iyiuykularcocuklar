"""
AraştırmacıAjan — Rakip kanal analizi ve trend tespiti

Kullanım:
  python3 scriptler/research_agent.py
  python3 scriptler/research_agent.py --kanal UCxxxxxx
  python3 scriptler/research_agent.py --konu "ninni"
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BASE_DIR

RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

# ─── Takip edilen rakip kanallar ──────────────────────────────────────────────

RAKIP_KANALLAR = [
    {"isim": "Little Baby Bum",        "id": "UCZd89j56im3TqHBMzpqm3_Q"},
    {"isim": "Cocomelon",              "id": "UCbCmjCuTUZos6Inko4u57UQ"},
    {"isim": "Super Simple Songs",     "id": "UCLsooMJoIpl_7ux2jvdPB-Q"},
    {"isim": "Bebek Ninnileri TR",     "id": ""},  # Türkçe rakip — ID eklenecek
    {"isim": "Ninni Dünyası",          "id": ""},  # Türkçe rakip — ID eklenecek
]

ARAMA_TERIMLERI = [
    "bebek ninnisi",
    "ninni türkçe",
    "çocuk şarkısı",
    "uyku müziği bebek",
    "lullaby turkish",
    "baby sleep music",
    "nursery rhymes turkish",
    "kırmızı balık şarkısı",
]

# ─── YouTube API bağlantısı ───────────────────────────────────────────────────

def youtube_baglan():
    try:
        import pickle
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
        TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"YouTube bağlantı hatası: {e}")
        return None

# ─── Arama ve veri çekme ──────────────────────────────────────────────────────

def trend_videolari_ara(youtube, sorgu, max_sonuc=10):
    """YouTube'da arama yap, en popüler sonuçları getir"""
    try:
        yanit = youtube.search().list(
            q=sorgu,
            part="snippet",
            type="video",
            order="viewCount",
            relevanceLanguage="tr",
            maxResults=max_sonuc,
            publishedAfter=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ).execute()

        videolar = []
        for item in yanit.get("items", []):
            videolar.append({
                "video_id": item["id"]["videoId"],
                "baslik": item["snippet"]["title"],
                "kanal": item["snippet"]["channelTitle"],
                "tarih": item["snippet"]["publishedAt"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            })
        return videolar
    except Exception as e:
        print(f"  Arama hatası ({sorgu}): {e}")
        return []

def video_detay_getir(youtube, video_ids):
    """Video istatistiklerini getir"""
    if not video_ids:
        return {}
    try:
        yanit = youtube.videos().list(
            part="statistics,contentDetails",
            id=",".join(video_ids[:50]),
        ).execute()

        detaylar = {}
        for item in yanit.get("items", []):
            istatistik = item.get("statistics", {})
            detaylar[item["id"]] = {
                "izlenme": int(istatistik.get("viewCount", 0)),
                "begeni": int(istatistik.get("likeCount", 0)),
                "yorum_sayisi": int(istatistik.get("commentCount", 0)),
            }
        return detaylar
    except Exception as e:
        print(f"  Video detay hatası: {e}")
        return {}

def yorumlari_getir(youtube, video_id, max_yorum=20):
    """Video yorumlarını getir ve analiz et"""
    try:
        yanit = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=max_yorum,
            textFormat="plainText",
        ).execute()

        yorumlar = []
        for item in yanit.get("items", []):
            yorum = item["snippet"]["topLevelComment"]["snippet"]
            yorumlar.append({
                "metin": yorum["textDisplay"][:200],
                "begeni": yorum["likeCount"],
            })
        return yorumlar
    except Exception:
        return []  # Yorumlar kapalı olabilir

def kanal_son_videolari(youtube, kanal_id, max_video=5):
    """Bir kanalın son videolarını getir"""
    if not kanal_id:
        return []
    try:
        yanit = youtube.search().list(
            channelId=kanal_id,
            part="snippet",
            order="date",
            type="video",
            maxResults=max_video,
        ).execute()

        videolar = []
        for item in yanit.get("items", []):
            videolar.append({
                "video_id": item["id"]["videoId"],
                "baslik": item["snippet"]["title"],
                "tarih": item["snippet"]["publishedAt"],
            })
        return videolar
    except Exception as e:
        print(f"  Kanal video hatası: {e}")
        return []

# ─── Yorum analizi ────────────────────────────────────────────────────────────

def yorum_analiz_et(yorumlar):
    """Yorumlardan öne çıkan talep ve şikayetleri çıkar"""
    talep_anahtar = [
        "daha uzun", "daha fazla", "tekrar", "bunu istiyorum",
        "bir daha", "saat", "gece", "uyuttu", "bayıldım",
        "more", "longer", "again", "please", "love",
    ]
    sikayet_anahtar = [
        "çok kısa", "bitti", "devam", "kesildi", "reklam",
        "too short", "ended", "cut", "ads",
    ]

    talepler = []
    sikayetler = []

    for yorum in yorumlar:
        metin = yorum["metin"].lower()
        for k in talep_anahtar:
            if k in metin:
                talepler.append(yorum["metin"][:100])
                break
        for k in sikayet_anahtar:
            if k in metin:
                sikayetler.append(yorum["metin"][:100])
                break

    return {
        "talep_sayisi": len(talepler),
        "sikayet_sayisi": len(sikayetler),
        "ornekler": talepler[:3] + sikayetler[:3],
    }

# ─── Fırsat tespiti ───────────────────────────────────────────────────────────

def firsat_tespit_et(arama_sonuclari, detaylar):
    """
    Hangi içeriklerin eksik veya az olduğunu tespit et.
    Yüksek izlenme + az rakip = fırsat
    """
    firsatlar = []

    # Ortalama izlenmeyi bul
    izlenmeler = [d["izlenme"] for d in detaylar.values() if d["izlenme"] > 0]
    if not izlenmeler:
        return firsatlar

    ortalama = sum(izlenmeler) / len(izlenmeler)

    for video in arama_sonuclari:
        vid_id = video["video_id"]
        if vid_id not in detaylar:
            continue

        izlenme = detaylar[vid_id]["izlenme"]
        yorum = detaylar[vid_id]["yorum_sayisi"]

        # Yüksek performanslı video → benzer içerik fırsatı
        if izlenme > ortalama * 2:
            firsatlar.append({
                "baslik": video["baslik"],
                "kanal": video["kanal"],
                "izlenme": izlenme,
                "neden": f"Çok yüksek izlenme ({izlenme:,}), benzer içerik üretilebilir",
                "oncelik": "yuksek",
            })

    return firsatlar[:5]

# ─── Video önerisi üret ───────────────────────────────────────────────────────

def video_onerileri_uret(firsatlar, trend_basliklar):
    """Araştırmaya göre video önerileri oluştur"""
    oneriler = []

    # Trend başlıklardan çıkar
    ninni_sayac = sum(1 for b in trend_basliklar if "ninni" in b.lower() or "lullaby" in b.lower())
    sarki_sayac = sum(1 for b in trend_basliklar if "şarkı" in b.lower() or "song" in b.lower())

    if ninni_sayac > sarki_sayac:
        oneriler.append({
            "baslik": "Bebek Ninnileri 🌙 2 Saat | Uyku Müziği",
            "tur": "ninni", "sure": 7200,
            "neden": f"Ninni içeriği trendde ({ninni_sayac} hit)",
            "oncelik": "yuksek",
            "sahne": "gece_gokyuzu",
            "muzik_tarzi": "Yavaş ninni, piyano ve keman, 65 BPM",
        })
    else:
        oneriler.append({
            "baslik": "Çocuk Şarkıları 🎵 1 Saat | Renkli Animasyonlar",
            "tur": "cocuk_sarki", "sure": 3600,
            "neden": f"Şarkı içeriği trendde ({sarki_sayac} hit)",
            "oncelik": "yuksek",
            "sahne": "renkli_oda",
            "muzik_tarzi": "Neşeli çocuk şarkısı, ksilofon, 110 BPM",
        })

    # Fırsatlardan video öner
    for f in firsatlar[:2]:
        baslik_lower = f["baslik"].lower()
        if "fish" in baslik_lower or "balık" in baslik_lower:
            oneriler.append({
                "baslik": "Kırmızı Balık Gölde 🐟 | Çocuk Şarkısı",
                "tur": "cocuk_sarki", "sure": 180,
                "neden": "Rakipte yüksek izlenme, Türkçe versiyonu eksik",
                "oncelik": "yuksek",
                "sahne": "gol_manzara",
                "muzik_tarzi": "Neşeli, 105 BPM, çocuk korosu",
            })
        elif "sleep" in baslik_lower or "uyku" in baslik_lower:
            oneriler.append({
                "baslik": "Bebek Uyku Müziği 🌙 3 Saat | Derin Uyku",
                "tur": "ninni", "sure": 10800,
                "neden": "Uzun uyku müziği talep görüyor",
                "oncelik": "orta",
                "sahne": "gece_gokyuzu",
                "muzik_tarzi": "Çok yavaş, ambient, 55 BPM",
            })

    # Her zaman bir Short öner
    oneriler.append({
        "baslik": "Tatlı Rüyalar ⭐ #shorts",
        "tur": "short", "sure": 60,
        "neden": "Shorts algoritma desteği alıyor",
        "oncelik": "orta",
        "sahne": "gece_gokyuzu",
        "muzik_tarzi": "Kısa ninni, 60 saniye",
    })

    return oneriler[:4]

# ─── Ana araştırma fonksiyonu ─────────────────────────────────────────────────

def arastir(youtube=None, hizli_mod=False):
    """Tam araştırma yap, rapor döndür"""
    os.makedirs(RAPOR_DIR, exist_ok=True)
    tarih = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"ARAŞTIRMACIAjan — {tarih}")
    print(f"{'='*60}")

    tum_videolar = []
    tum_detaylar = {}
    tum_yorum_analizleri = []
    rakip_analizleri = []

    if youtube:
        # 1. Trend aramaları
        print("\n[1/3] Trend videolar aranıyor...")
        aramalar = ARAMA_TERIMLERI[:3] if hizli_mod else ARAMA_TERIMLERI
        for terim in aramalar:
            print(f"  Aranıyor: {terim}")
            videolar = trend_videolari_ara(youtube, terim, max_sonuc=5)
            tum_videolar.extend(videolar)
            time.sleep(0.5)

        # 2. İstatistikler
        print("\n[2/3] Video istatistikleri çekiliyor...")
        video_ids = list({v["video_id"] for v in tum_videolar})
        tum_detaylar = video_detay_getir(youtube, video_ids)

        # 3. Yorumlar (ilk 3 video)
        print("\n[3/3] Yorumlar analiz ediliyor...")
        for video in tum_videolar[:3]:
            vid_id = video["video_id"]
            yorumlar = yorumlari_getir(youtube, vid_id, max_yorum=15)
            if yorumlar:
                analiz = yorum_analiz_et(yorumlar)
                analiz["video_baslik"] = video["baslik"]
                analiz["kanal"] = video["kanal"]
                tum_yorum_analizleri.append(analiz)

        # 4. Rakip kanal analizi
        if not hizli_mod:
            for kanal in RAKIP_KANALLAR[:3]:
                if not kanal["id"]:
                    continue
                print(f"  Kanal taranıyor: {kanal['isim']}")
                son_videolar = kanal_son_videolari(youtube, kanal["id"])
                vid_ids = [v["video_id"] for v in son_videolar]
                detaylar = video_detay_getir(youtube, vid_ids)
                rakip_analizleri.append({
                    "kanal": kanal["isim"],
                    "son_videolar": [
                        {**v, **detaylar.get(v["video_id"], {})}
                        for v in son_videolar
                    ],
                })
                time.sleep(0.5)
    else:
        print("  YouTube bağlantısı yok — varsayılan öneriler kullanılıyor")

    # 5. Fırsat ve öneri üret
    firsatlar = firsat_tespit_et(tum_videolar, tum_detaylar)
    trend_basliklar = [v["baslik"] for v in tum_videolar]
    onerilen_videolar = video_onerileri_uret(firsatlar, trend_basliklar)

    # 6. Raporu oluştur
    rapor = {
        "tarih": tarih,
        "olusturulma": datetime.now().isoformat(),
        "taranan_video_sayisi": len(tum_videolar),
        "trend_konular": list({v["baslik"].split("|")[0].strip() for v in tum_videolar[:10]}),
        "firsatlar": firsatlar,
        "yorum_analizleri": tum_yorum_analizleri,
        "rakip_analizleri": rakip_analizleri,
        "onerilen_videolar": onerilen_videolar,
    }

    # 7. Kaydet
    rapor_yolu = os.path.join(RAPOR_DIR, f"arastirma_{tarih}.json")
    with open(rapor_yolu, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print(f"\nRapor kaydedildi: {rapor_yolu}")
    print(f"Önerilen videolar:")
    for i, v in enumerate(onerilen_videolar, 1):
        print(f"  {i}. [{v['oncelik'].upper()}] {v['baslik']} ({v['sure']//60} dk)")

    return rapor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AraştırmacıAjan")
    parser.add_argument("--hizli", action="store_true", help="Hızlı mod (az API çağrısı)")
    parser.add_argument("--offline", action="store_true", help="API olmadan varsayılan öneriler")
    args = parser.parse_args()

    youtube = None if args.offline else youtube_baglan()
    arastir(youtube=youtube, hizli_mod=args.hizli)
