"""
İçerikAjanı — Araştırma raporunu okur, bugünkü 2 videonun tam içeriğini hazırlar.

Kullanım:
  python3 scriptler/content_agent.py
  python3 scriptler/content_agent.py --tarih 2026-04-05
  python3 scriptler/content_agent.py --manuel "Kırmızı Balık Gölde"
"""
import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BASE_DIR, KATEGORILER

RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
ICERIK_DIR = os.path.join(BASE_DIR, "icerik")

# ─── Şarkı sözü kütüphanesi ───────────────────────────────────────────────────

SARKI_KITAPLIGI = {
    "ninni_temel": {
        "baslik": "Ninni Ninni",
        "sozler": """Ninni ninni ninniii
Uyu bebek uyu
Gözlerini yum da
Tatlı rüyalar gör

Ninni ninni ninniii
Annecim bekliyor
Kollarında sımsıcak
Sarılıyor sana

Ninni ninni ninniii
Ay ışığı düşmüş
Yıldızlar selamlıyor
Seni sevgili bebeğim""",
        "sahne": "gece_gokyuzu",
        "muzik": "Yavaş ninni, piyano ve keman, kadın sesi, 65 BPM",
    },
    "kirmizi_balik": {
        "baslik": "Kırmızı Balık Gölde",
        "sozler": """Kırmızı balık gölde yüzüyor
Kırmızı balık gölde yüzüyor
Sağa sola dans ediyor
Neşeyle yüzüyor

Mavi sular içinde
Yeşil otlar arasında
Kırmızı balık mutlu
Her gün oynuyor

Yüz balık yüz balık
Göl senin evin
Yüz balık yüz balık
Mutlu ol her zaman""",
        "sahne": "gol_manzara",
        "muzik": "Neşeli çocuk şarkısı, ksilofon ve akordeon, 108 BPM, çocuk korosu",
    },
    "renkli_toplar": {
        "baslik": "Renkli Toplar Şarkısı",
        "sozler": """Kırmızı top zıplıyor zıplıyor
Mavi top uçuyor uçuyor
Sarı top dönüyor dönüyor
Hepsi oynuyor birlikte

Kırmızı mavi sarı
Yeşil turuncu pembe
Rengarenk dünyamız
Ne kadar güzel

Top top top
Zıpla zıpla zıpla
Top top top
Hepimiz oynayalım""",
        "sahne": "renkli_oda",
        "muzik": "Neşeli, 112 BPM, ksilofon, çocuk sesi",
    },
    "gunayin_sarki": {
        "baslik": "Günaydın Şarkısı",
        "sozler": """Günaydın günaydın
Güneş doğdu artık
Günaydın günaydın
Uyan uyan artık

Kuşlar ötüyor
Çiçekler açıyor
Yeni bir gün başladı
Haydi gülümse

Günaydın anneciğim
Günaydın babacığım
Günaydın dünya
Mutlu sabahlar""",
        "sahne": "orman_sabah",
        "muzik": "Neşeli sabah şarkısı, 105 BPM, akustik gitar",
    },
    "hayvanlar_ciftlikte": {
        "baslik": "Çiftlik Hayvanları Şarkısı",
        "sozler": """İnek böyle bağırır möö möö möö
Koyun böyle bağırır meee meee meee
Horoz böyle bağırır üü üü rüü
Hepsi çiftlikte yaşar

At böyle kişner hıhhı hıhhı
Kedi böyle miyavlar miyav miyav
Köpek böyle havlar hav hav hav
Hepsi arkadaş

Çiftlikte sabah oldu
Hayvanlar uyandı
Hepsi günaydın der
Neşeli bir gün başlar""",
        "sahne": "ciftlik",
        "muzik": "Neşeli çocuk şarkısı, 100 BPM, akordeon",
    },
    "sayilar": {
        "baslik": "Sayılar Şarkısı",
        "sozler": """Bir iki üç dört beş
Parmak sayalım hep
Bir iki üç dört beş
Beraber sayalım

Bir tane elma var
İki tane armut
Üç tane çilek var
Dört tane kiraz

Beş altı yedi sekiz
Dokuz ve on
Sayıları öğrendik
Aferin bize""",
        "sahne": "renkli_oda",
        "muzik": "Öğretici çocuk şarkısı, 100 BPM, piyano",
    },
    "uyku_muzigi": {
        "baslik": "Bebek Uyku Müziği",
        "sozler": "",  # Enstrümantal
        "sahne": "gece_gokyuzu",
        "muzik": "Enstrümantal uyku müziği, ambient piyano, 55 BPM, yumuşak",
    },
    "uzay_ninnisi": {
        "baslik": "Uzay Ninnisi",
        "sozler": """Yıldızlar parlar gecede
Ay ışığı düşer yüzüne
Uyu bebeğim uyu
Uzayda rüya gör

Gezegenler dans eder
Kuyrukluyıldızlar uçar
Uyu bebeğim uyu
Tatlı rüyalar gör

Roket seni taşır
Yıldızlara kadar
Uyu bebeğim uyu
Sabaha kadar""",
        "sahne": "uzay",
        "muzik": "Uzay temalı ninni, synthesizer ve piyano, 60 BPM",
    },
}

# ─── SEO ve açıklama şablonları ───────────────────────────────────────────────

def aciklama_olustur(baslik, tur, sure_saniye, sarki_adi=""):
    sure_metin = f"{sure_saniye//3600} saat" if sure_saniye >= 3600 else f"{sure_saniye//60} dakika"

    if tur == "ninni":
        return f"""{baslik} | Bebek Uyku Müziği | Ninni Türkçe

Bebeğiniz için özel hazırlanmış {sure_metin} boyunca kesintisiz ninni müziği 🌙
Rahatlatıcı 3D animasyonlar ve yumuşak sesler ile bebeğinizin uyumasına yardımcı olun.

⭐ {sure_metin} kesintisiz ninni
⭐ Rahatlatıcı 3D animasyonlar
⭐ Çocuklar için güvenli içerik
⭐ Reklamsız dinleme deneyimi

📱 Abone olun: @iyiuykularcocuklar00
🔔 Yeni videoları kaçırmamak için bildirimleri açın!

─────────────────────────────
Bu video bebekler ve küçük çocuklar için hazırlanmıştır.
Uyku zamanında sessizce oynayabilirsiniz.
─────────────────────────────

#ninni #bebekninnisi #uykumüziği #bebek #çocuk #ninniler
#lullaby #babysleep #sleepmusic #nurseryrhymes #baby
#iyiuykularcocuklar #türkçeninni #bebekvideoları"""

    elif tur == "cocuk_sarki":
        return f"""{baslik} | Çocuk Şarkısı | Bebek Şarkıları Türkçe

{sarki_adi if sarki_adi else baslik} — Çocuklar için eğlenceli ve öğretici şarkı! 🎵
Renkli 3D animasyonlar ve neşeli müzik ile küçükler için harika bir izleme deneyimi.

🎵 Eğlenceli çocuk şarkısı
🎨 Renkli 3D animasyonlar
📚 Öğretici ve eğlenceli içerik
✅ Çocuklar için güvenli

📱 Abone olun: @iyiuykularcocuklar00
🔔 Bildirimleri açın!

#çocukşarkısı #bebekşarkısı #çocuk #bebek #türkçeşarkı
#kidssongs #nurseryrhymes #childrensongs #toddler
#iyiuykularcocuklar #animasyon #çocukvideoları"""

    else:  # short
        return f"""{baslik} | #Shorts

{sarki_adi if sarki_adi else baslik} 🌙

#shorts #ninni #bebek #çocuk #baby #lullaby #iyiuykularcocuklar"""

def tag_listesi_olustur(tur, sarki_adi=""):
    temel_tags = {
        "ninni": [
            "ninni", "bebek ninnisi", "uyku müziği", "bebek uyku müziği",
            "ninniler", "türkçe ninni", "bebek", "çocuk", "uyku",
            "lullaby", "baby sleep", "sleep music", "baby lullaby",
            "nursery rhymes", "baby music", "toddler sleep",
        ],
        "cocuk_sarki": [
            "çocuk şarkısı", "bebek şarkısı", "türkçe çocuk şarkısı",
            "çocuk müziği", "bebek müziği", "anaokulu şarkıları",
            "kids songs", "children's songs", "nursery rhymes",
            "baby songs", "toddler songs", "preschool songs",
        ],
        "short": [
            "shorts", "ninni", "bebek", "çocuk", "baby", "lullaby",
        ],
    }

    tags = temel_tags.get(tur, temel_tags["ninni"])[:]
    if sarki_adi:
        tags.insert(0, sarki_adi.lower())
        tags.insert(1, sarki_adi.lower() + " şarkısı")

    return tags[:20]

# ─── İçerik planı oluştur ─────────────────────────────────────────────────────

def icerik_plani_olustur(araştirma_raporu=None, tarih=None):
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")

    gun_no = datetime.strptime(tarih, "%Y-%m-%d").weekday()

    # Araştırma raporundan öneri al
    oneriler = []
    if araştirma_raporu and araştirma_raporu.get("onerilen_videolar"):
        oneriler = araştirma_raporu["onerilen_videolar"]

    # Haftalık varsayılan plan
    haftalik_sarki_plani = [
        # Pazartesi
        [("ninni_temel", 3600, False), ("kirmizi_balik", 120, True)],
        # Salı
        [("uyku_muzigi", 7200, False), ("renkli_toplar", 120, True)],
        # Çarşamba
        [("ninni_temel", 3600, False), ("gunayin_sarki", 60, True)],
        # Perşembe
        [("uzay_ninnisi", 5400, False), ("hayvanlar_ciftlikte", 120, True)],
        # Cuma
        [("uyku_muzigi", 7200, False), ("sayilar", 60, True)],
        # Cumartesi
        [("kirmizi_balik", 3600, False), ("renkli_toplar", 60, True)],
        # Pazar
        [("ninni_temel", 10800, False), ("uzay_ninnisi", 120, True)],
    ]

    bugunun_plani = haftalik_sarki_plani[gun_no]

    videolar = []
    for i, (sarki_key, sure, shorts_mi) in enumerate(bugunun_plani):
        sarki = SARKI_KITAPLIGI[sarki_key]

        # Araştırma önerisi varsa öncelikli kullan
        if oneriler and i < len(oneriler):
            oneri = oneriler[i]
            sure = oneri.get("sure", sure)
            sahne = oneri.get("sahne", sarki["sahne"])
            muzik_tarzi = oneri.get("muzik_tarzi", sarki["muzik"])

            # Önerilen başlığa uygun şarkı bul
            baslik = oneri["baslik"]
            tur = oneri["tur"]
        else:
            sahne = sarki["sahne"]
            muzik_tarzi = sarki["muzik"]
            tur = "short" if shorts_mi else ("cocuk_sarki" if sarki_key not in ["ninni_temel", "uyku_muzigi", "uzay_ninnisi"] else "ninni")

            sure_metin = f"{sure//3600} Saat" if sure >= 3600 else f"{sure//60} Dakika"
            if tur == "short":
                baslik = f"{sarki['baslik']} ⭐ #shorts"
            elif tur == "ninni":
                baslik = f"{sarki['baslik']} 🌙 {sure_metin} | Uyku Müziği"
            else:
                baslik = f"{sarki['baslik']} 🎵 {sure_metin}"

        video = {
            "sira": i + 1,
            "baslik": baslik,
            "tur": tur,
            "sure_saniye": sure,
            "shorts": shorts_mi or tur == "short",
            "sarki_adi": sarki["baslik"],
            "sarki_sozleri": sarki.get("sozler", ""),
            "sahne": sahne,
            "muzik_tarzi": muzik_tarzi,
            "aciklama": aciklama_olustur(baslik, tur, sure, sarki["baslik"]),
            "tags": tag_listesi_olustur(tur, sarki["baslik"]),
            "upload_saati": "09:00" if i == 0 else "18:00",
            "thumbnail_renk": "ninni_mavi" if tur == "ninni" else "neseli_sari",
        }
        videolar.append(video)

    plan = {
        "tarih": tarih,
        "gun": ["Pazartesi","Salı","Çarşamba","Perşembe","Cuma","Cumartesi","Pazar"][gun_no],
        "olusturulma": datetime.now().isoformat(),
        "arastirma_kullanildi": araştirma_raporu is not None,
        "videolar": videolar,
    }

    os.makedirs(ICERIK_DIR, exist_ok=True)
    plan_yolu = os.path.join(ICERIK_DIR, f"bugun_{tarih}.json")
    with open(plan_yolu, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"İÇERİKAJANI — {tarih} ({plan['gun']})")
    print(f"{'='*60}")
    for v in videolar:
        print(f"\n[Video {v['sira']}] {v['baslik']}")
        print(f"  Tür: {v['tur']} | Süre: {v['sure_saniye']//60} dk | Upload: {v['upload_saati']}")
        print(f"  Sahne: {v['sahne']} | Müzik: {v['muzik_tarzi'][:50]}")

    print(f"\nPlan kaydedildi: {plan_yolu}")
    return plan

def son_arastirma_oku(tarih=None):
    """En güncel araştırma raporunu bul ve oku"""
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")

    rapor_yolu = os.path.join(RAPOR_DIR, f"arastirma_{tarih}.json")
    if os.path.exists(rapor_yolu):
        with open(rapor_yolu, encoding="utf-8") as f:
            return json.load(f)

    # Dün's raporu dene
    dun = (datetime.strptime(tarih, "%Y-%m-%d") - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    rapor_yolu = os.path.join(RAPOR_DIR, f"arastirma_{dun}.json")
    if os.path.exists(rapor_yolu):
        with open(rapor_yolu, encoding="utf-8") as f:
            return json.load(f)

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="İçerikAjanı")
    parser.add_argument("--tarih", help="Tarih (YYYY-MM-DD)")
    parser.add_argument("--manuel", help="Manuel şarkı adı ile plan oluştur")
    args = parser.parse_args()

    arastirma = son_arastirma_oku(args.tarih)
    if arastirma:
        print(f"Araştırma raporu bulundu: {arastirma['tarih']}")
    else:
        print("Araştırma raporu yok, varsayılan plan kullanılıyor.")

    icerik_plani_olustur(araştirma_raporu=arastirma, tarih=args.tarih)
