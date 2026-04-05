import os
import json
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import CREDENTIALS_FILE, TOKEN_FILE

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

def youtube_baglan():
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

def video_yukle(youtube, video_dosyasi, baslik, aciklama, tags, thumbnail_dosyasi=None, shorts=False):
    print(f"Yükleniyor: {baslik}")

    body = {
        "snippet": {
            "title": baslik,
            "description": aciklama,
            "tags": tags,
            "categoryId": "10",
            "defaultLanguage": "tr",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": True,
        },
    }

    media = MediaFileUpload(
        video_dosyasi,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 10,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            yuzde = int(status.progress() * 100)
            print(f"  %{yuzde} yüklendi...")

    video_id = response["id"]
    print(f"Video yüklendi! ID: {video_id}")
    print(f"Link: https://www.youtube.com/watch?v={video_id}")

    if thumbnail_dosyasi and os.path.exists(thumbnail_dosyasi):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_dosyasi)
        ).execute()
        print("Thumbnail ayarlandı.")

    return video_id

def aciklama_olustur(baslik, tur="ninni"):
    if tur == "ninni":
        return f"""{baslik}

Bebeğiniz için özel olarak hazırlanmış sakinleştirici ninni müziği 🌙

✨ Bebeğinizin uyumasına yardımcı olur
✨ Rahatlatıcı animasyonlar
✨ Çocuklar için güvenli içerik

📱 Abone ol: @iyiuykularcocuklar00
🔔 Bildirimleri aç, yeni videolar kaçırma!

#ninni #bebekninnisi #uykumüziği #bebek #çocuk #lullaby #babysleep
"""
    elif tur == "cocuk_sarki":
        return f"""{baslik}

Çocuklar için eğlenceli ve öğretici şarkı! 🎵

✨ Renkli animasyonlar
✨ Neşeli müzik
✨ Çocuklar için güvenli içerik

📱 Abone ol: @iyiuykularcocuklar00
🔔 Bildirimleri aç!

#çocukşarkısı #bebekşarkısı #çocuk #bebek #kidssongs #nurseryrhymes
"""
    return baslik


if __name__ == "__main__":
    print("YouTube bağlantısı test ediliyor...")
    youtube = youtube_baglan()
    kanal = youtube.channels().list(part="snippet", mine=True).execute()
    print(f"Bağlı kanal: {kanal['items'][0]['snippet']['title']}")
