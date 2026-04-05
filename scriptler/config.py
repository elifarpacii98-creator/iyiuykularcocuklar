# Kanal Konfigürasyonu
KANAL_ADI = "iyiuykularcocuklar00"
KANAL_ID = ""  # YouTube'dan alınacak

# Video Ayarları
VIDEO_GENISLIK = 1920
VIDEO_YUKSEKLIK = 1080
VIDEO_FPS = 30
SHORT_GENISLIK = 1080
SHORT_YUKSEKLIK = 1920

# Uzun Video Süreleri (saniye)
UZUN_VIDEO_SURELERI = {
    "30_dakika": 30 * 60,
    "1_saat": 60 * 60,
    "2_saat": 2 * 60 * 60,
    "3_saat": 3 * 60 * 60,
}

# Klasörler
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANIMASYON_DIR = os.path.join(BASE_DIR, "animasyonlar")
MUZIK_DIR = os.path.join(BASE_DIR, "muzik")
VIDEO_DIR = os.path.join(BASE_DIR, "videolar")
THUMBNAIL_DIR = os.path.join(BASE_DIR, "thumbnails")
SCRIPTLER_DIR = os.path.join(BASE_DIR, "scriptler")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

# Video Kategorileri
KATEGORILER = {
    "ninni": {
        "tags": ["ninni", "bebek ninnisi", "uyku müziği", "lullaby", "baby sleep"],
        "kategori_id": "10",  # Music
    },
    "cocuk_sarki": {
        "tags": ["çocuk şarkısı", "bebek şarkısı", "nursery rhymes", "kids songs"],
        "kategori_id": "10",
    },
    "short": {
        "tags": ["çocuk", "bebek", "ninni", "shorts"],
        "kategori_id": "10",
    }
}

# Günlük plan: sabah ve akşam upload
GUNLUK_UPLOAD_SAATLERI = ["09:00", "18:00"]
