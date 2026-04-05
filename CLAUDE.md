# iyiuykularcocuklar00 — YouTube Otomasyon Sistemi

## Proje Özeti

Bu proje, **iyiuykularcocuklar00** YouTube kanalı için tam otomatik video üretim sistemidir.
Her gün 2 video üretilir ve yüklenir: biri uzun format (1–3 saat), biri kısa format (Short veya 1–3 dakika).

Tüm videolar Türkçe çocuk içeriği hedefler: ninni, çocuk şarkısı, uyku müziği.
Animasyonlar 3D (Blender) ile üretilir. Müzikler Suno AI ile üretilir.

---

## Kanal Bilgisi

- **Kanal Adı:** iyiuykularcocuklar00
- **Hedef Kitle:** 0–6 yaş bebekler ve çocuklar, ebeveynler
- **Dil:** Türkçe (uluslararası trafik için İngilizce tag)
- **Yükleme Saatleri:** 09:00 ve 18:00 (Türkiye saatiyle)
- **Hedef:** Her gün 2 video — 1 uzun format + 1 short/kısa

---

## Agent Sistemi

Sistem 5 ayrı ajandan oluşur. Her ajan kendi görevine odaklanır.

---

### 1. AraştırmacıAjan (research_agent)

**Görevi:** Rakip kanalları izler, trend içerikleri tespit eder, video fikirleri üretir.

**Her gün şunları yapar:**
- Türkiye ve dünyada "ninni", "bebek uyku müziği", "çocuk şarkısı" araması yapar
- İlk 10 rakip kanalın son 5 videosuna bakar
- Her videodaki yorumları analiz eder (en çok ne isteniyor, şikayetler, talepler)
- Beğeni/görüntüleme oranına göre hangi video türünün daha iyi performans gösterdiğini not eder
- Eksik içerik fırsatlarını tespit eder ("bu şarkı var ama 3 saatlik versiyonu yok" gibi)
- Günlük raporu `raporlar/arastirma_TARIH.json` dosyasına yazar

**Takip ettiği kanallar (güncellenir):**
- Little Baby Bum
- Cocomelon - Nursery Rhymes
- Super Simple Songs
- Türkçe rakip kanallar (haftalık güncellenir)

**Çıktı formatı (`raporlar/arastirma_TARIH.json`):**
```json
{
  "tarih": "2026-04-05",
  "trend_konular": ["kırmızı balık", "ninni koleksiyonu", "orman hayvanları"],
  "rakip_analiz": [
    {
      "kanal": "...",
      "video_baslik": "...",
      "izlenme": 0,
      "yorum_ozeti": "...",
      "firsatlar": "..."
    }
  ],
  "onerilen_videolar": [
    {
      "baslik": "Kırmızı Balık Gölde 🐟 1 Saat",
      "tur": "cocuk_sarki",
      "sure": 3600,
      "neden": "Rakiplerde yok, yorumlarda talep var",
      "oncelik": "yuksek"
    }
  ]
}
```

---

### 2. İçerikAjanı (content_agent)

**Görevi:** AraştırmacıAjan'ın raporunu alır, bugün yapılacak 2 videonun tam detayını hazırlar.

**Her gün şunları yapar:**
- Araştırma raporunu okur
- Haftalık planla karşılaştırır
- Bugünkü 2 videonun şunları belirler:
  - Başlık (Türkçe + İngilizce)
  - Açıklama (SEO optimizeli)
  - Taglar (Türkçe + İngilizce)
  - Şarkı sözleri (eğer orijinal şarkıysa)
  - Sahne tanımı (AnimasyonAjanı için)
  - Müzik tarzı (MüzikAjanı için)
- Çıktıyı `icerik/bugun_TARIH.json` dosyasına yazar

**İçerik Kuralları:**
- Başlıklar emoji içerir (🌙 ninni için, 🐟🌈 şarkılar için)
- Açıklamalar ilk 2 satırda anahtar kelime içerir
- Şarkı sözleri basit, tekrarlayan, Türkçe
- Her video "Made for Kids" olarak işaretlenir
- Şiddet, korku, üzücü içerik kesinlikle yasak

**Şarkı Türleri:**
| Tür | Örnek | Süre |
|-----|-------|------|
| Ninni | "Uyusun da büyüsün" | 1–3 saat (loop) |
| Hayvan şarkısı | "Kırmızı Balık Gölde" | 2–5 dk (Short veya 1 saat) |
| Renk şarkısı | "Sarı, kırmızı, mavi toplar" | 2–5 dk |
| Sayı şarkısı | "Bir iki üç dört beş" | 2–5 dk |
| Doğa & uyku | "Yağmur sesi, orman" | 1–3 saat (loop) |
| Sabah şarkısı | "Günaydın güneş" | 2–5 dk |

---

### 3. AnimasyonAjanı (animation_agent)

**Görevi:** Blender ile 3D animasyon sahnelerini üretir.

**Her gün şunları yapar:**
- İçerikAjanı'nın sahne tanımını alır
- Blender Python API ile 3D sahneyi oluşturur
- Render eder (kısa versiyonu — uzun videolar loop ile uzatılır)
- Çıktıyı `animasyonlar/` klasörüne kaydeder

**Sahne Kütüphanesi:**

| Sahne | Açıklama | Kullanım |
|-------|----------|---------|
| `gece_gokyuzu` | Ay, yıldızlar, bulutlar, koyu mavi | Ninni videoları |
| `orman_sabah` | Ağaçlar, güneş, kuşlar uçuyor | Sabah şarkıları |
| `okyanus` | Dalgalar, balıklar, mercanlar, köpükler | Su/deniz şarkıları |
| `gol_manzara` | Göl, ağaçlar, kırmızı balıklar yüzüyor | Kırmızı Balık şarkısı |
| `renkli_oda` | Oyuncaklar, toplar, renkli nesneler | Renk/sayı şarkıları |
| `ciftlik` | At, inek, koyun, çimen | Hayvan şarkıları |
| `uzay` | Gezegenler, roket, yıldızlar | Uyku/macera |

**Animasyon Parametreleri:**
- Çözünürlük: 1920×1080 (uzun) / 1080×1920 (Short)
- FPS: 30
- Render: EEVEE (hızlı) — uzun videolar için Cycles değil
- Loop süresi: 30 saniye (sonra video_compiler loop'a alır)

---

### 4. MüzikAjanı (music_agent)

**Görevi:** Suno AI ile şarkı ve müzik üretir.

**Her gün şunları yapar:**
- İçerikAjanı'nın müzik tanımını alır
- Suno AI API'ye istek gönderir
- Üretilen müziği `muzik/` klasörüne kaydeder
- Ninni için: yavaş, sakinleştirici, 60–80 BPM
- Şarkı için: neşeli, 100–120 BPM, çocuk sesi

**Suno AI Prompt Şablonları:**

Ninni:
```
Turkish lullaby, soft female voice, slow tempo 60bpm,
gentle piano and strings, soothing, baby sleep music,
warm and cozy, [ŞARKI SÖZÜ]
```

Çocuk şarkısı:
```
Turkish children's song, cheerful, upbeat 110bpm,
playful xylophone and piano, kids choir,
bright and happy, [ŞARKI SÖZÜ]
```

**Müzik Dosya Adlandırma:**
- `muzik/ninni_TARIH_v1.mp3`
- `muzik/sarki_KIRMIZI_BALIK_v1.mp3`

---

### 5. YükleyiciAjan (uploader_agent)

**Görevi:** Tüm parçaları birleştirir, videoyu derler ve YouTube'a yükler.

**Her gün şunları yapar:**
- Animasyon + müziği FFmpeg ile birleştirir
- Thumbnail otomatik oluşturur (PIL)
- YouTube Data API v3 ile yükler
- Başarılı yükleme logunu `raporlar/yukleme_log.json`'a yazar
- Hata olursa bildirir

---

## Günlük Çalışma Akışı

```
06:00 — AraştırmacıAjan çalışır
         → Rakip kanalları tarar
         → Trend tespit eder
         → raporlar/arastirma_TARIH.json üretir

07:00 — İçerikAjanı çalışır
         → Araştırma raporunu okur
         → 2 videonun detayını hazırlar
         → icerik/bugun_TARIH.json üretir

07:30 — AnimasyonAjanı + MüzikAjanı paralel çalışır
         → 3D animasyon render
         → Suno AI müzik üretimi

09:00 — YükleyiciAjan (1. video)
         → Animasyon + müzik birleştir
         → Thumbnail oluştur
         → YouTube'a yükle

18:00 — YükleyiciAjan (2. video)
         → Aynı süreç, 2. video
```

---

## Klasör Yapısı

```
iyiuykularcocuklar/
├── CLAUDE.md                    ← Bu dosya
├── YOUTUBE_API_KURULUM.md       ← API kurulum rehberi
├── credentials.json             ← Google OAuth (git'e girmiyor)
├── token.json                   ← Otomatik oluşur (git'e girmiyor)
│
├── scriptler/
│   ├── config.py                ← Kanal ayarları
│   ├── youtube_upload.py        ← YouTube API yükleme
│   ├── thumbnail_generator.py   ← Otomatik thumbnail
│   ├── video_compiler.py        ← FFmpeg video derleme
│   ├── blender_animasyon.py     ← 3D animasyon üretimi
│   ├── gunluk_pipeline.py       ← Ana otomasyon pipeline
│   ├── research_agent.py        ← Rakip kanal araştırması
│   ├── content_agent.py         ← İçerik planlama
│   └── music_agent.py           ← Suno AI müzik üretimi
│
├── animasyonlar/                ← Render edilmiş animasyonlar
├── muzik/                       ← Üretilen müzikler
├── videolar/                    ← Birleştirilmiş son videolar
├── thumbnails/                  ← Otomatik thumbnaillar
├── icerik/                      ← Günlük içerik planları (JSON)
└── raporlar/                    ← Araştırma raporları + upload logları
```

---

## Haftalık Video Planı

| Gün | Video 1 (Uzun) | Video 2 (Kısa/Short) |
|-----|----------------|----------------------|
| Pazartesi | Bebek Ninnileri 1 Saat | Kırmızı Balık Gölde 🐟 |
| Salı | Bebek Ninnileri 2 Saat | Renkli Toplar Şarkısı 🎈 |
| Çarşamba | Orman Sesleri Uyku Müziği 1 Saat | Günaydın Şarkısı ☀️ |
| Perşembe | Bebek Ninnileri 90 Dakika | Çiftlik Hayvanları Şarkısı 🐄 |
| Cuma | Gece Ninnileri 2 Saat | Sayılar Şarkısı 🔢 |
| Cumartesi | Çocuk Şarkıları Derlemesi 1 Saat | Rengarenk Gökkuşağı 🌈 |
| Pazar | Bebek Ninnileri 3 Saat | Uzay Macerası Ninnisi 🚀 |

*Plan her hafta AraştırmacıAjan'ın bulgularına göre güncellenir.*

---

## YouTube SEO Kuralları

**Başlık formatı:**
```
[Şarkı Adı] [Emoji] [Süre] | [Anahtar Kelime]
Örnek: Bebek Ninnileri 🌙 1 Saat | Uyku Müziği
```

**Açıklama yapısı:**
```
[Satır 1 - Ana anahtar kelimeler]
[Satır 2 - İkincil anahtar kelimeler]
[Boş satır]
[Video içeriği açıklaması]
[Boş satır]
⏱ Timestamps (uzun videolar için)
📱 Abone ol: @iyiuykularcocuklar00
🔔 Bildirim aç
[Boş satır]
#ninni #bebekninnisi #uykumüziği #bebek #çocuk
```

**Zorunlu taglar:**
- ninni, bebek ninnisi, uyku müziği, bebek, çocuk
- lullaby, baby sleep, nursery rhymes, kids songs (uluslararası)
- Her videoya özel 5–10 ek tag

---

## Teknik Gereksinimler

**Kurulu olması gerekenler:**
- Python 3.9+
- Blender 5.1+
- FFmpeg 8+
- Git

**Python paketleri:**
```
google-api-python-client
google-auth-oauthlib
Pillow
requests
```

**API Anahtarları (credentials.json içinde):**
- Google OAuth 2.0 (YouTube Data API v3)
- Suno AI API key (`scriptler/config.py` içinde `SUNO_API_KEY`)

---

## Güvenlik Notları

- `credentials.json` ve `token.json` asla git'e girilmez (.gitignore'da)
- Satın alma gerektiren her işlem için kullanıcıdan onay alınır
- Suno AI ücretli kullanım öncesi bildirim yapılır
- YouTube yükleme limiti: günlük 6 video (API kotası)

---

## Komutlar

```bash
# Tam günlük pipeline çalıştır
python3 scriptler/gunluk_pipeline.py

# Sadece araştırma yap
python3 scriptler/research_agent.py

# Sadece içerik planla
python3 scriptler/content_agent.py

# Sadece video üret (yükleme yapma)
python3 scriptler/gunluk_pipeline.py --sadece-uret

# Hazır videoları yükle
python3 scriptler/gunluk_pipeline.py --sadece-yukle

# Test thumbnail üret
python3 scriptler/thumbnail_generator.py

# YouTube bağlantısını test et
python3 scriptler/youtube_upload.py
```
