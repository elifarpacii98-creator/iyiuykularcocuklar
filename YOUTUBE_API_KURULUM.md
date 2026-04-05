# YouTube API Kurulum Rehberi

## Adım 1 — Google Cloud Console

1. https://console.cloud.google.com adresine git
2. YouTube kanalının bağlı olduğu Google hesabıyla giriş yap
3. Üstteki proje açılır menüsüne tıkla → **New Project**
4. Proje adı: `iyiuykularcocuklar`
5. **Create** butonuna tıkla

## Adım 2 — YouTube Data API v3'ü Etkinleştir

1. Sol menüden **APIs & Services > Library** seç
2. Arama kutusuna `YouTube Data API v3` yaz
3. Üstüne tıkla → **Enable** butonuna bas

## Adım 3 — OAuth Credentials Oluştur

1. Sol menüden **APIs & Services > Credentials** seç
2. **+ Create Credentials** → **OAuth client ID**
3. Eğer consent screen uyarısı çıkarsa:
   - **Configure Consent Screen** tıkla
   - **External** seç → **Create**
   - App name: `iyiuykularcocuklar`
   - User support email: kendi emailin
   - **Save and Continue** (diğer adımları atlayabilirsin)
   - **Back to Dashboard**
4. Tekrar **Create Credentials > OAuth client ID**
5. Application type: **Desktop app**
6. Name: `iyiuykularcocuklar-desktop`
7. **Create** → **Download JSON** butonuna bas
8. İndirilen dosyayı `credentials.json` olarak yeniden adlandır
9. Bu dosyayı `/Users/elifarpaci/iyiuykularcocuklar/` klasörüne taşı

## Adım 4 — Test Bağlantısı

Terminalde şunu çalıştır:
```bash
cd /Users/elifarpaci/iyiuykularcocuklar
python3 scriptler/youtube_upload.py
```

Tarayıcı açılacak, Google hesabına izin ver. Başarılı olursa kanal adın görünecek.
