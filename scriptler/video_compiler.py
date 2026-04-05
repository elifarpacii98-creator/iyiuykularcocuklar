import subprocess
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import VIDEO_DIR, MUZIK_DIR, ANIMASYON_DIR, VIDEO_GENISLIK, VIDEO_YUKSEKLIK, VIDEO_FPS

FFMPEG = "ffmpeg"

def ffmpeg_calistir(komut, aciklama=""):
    if aciklama:
        print(f"  {aciklama}...")
    result = subprocess.run(komut, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"HATA: {result.stderr[-500:]}")
        raise RuntimeError(f"FFmpeg hatası: {aciklama}")
    return result

def muzik_loop_olustur(muzik_dosyasi, sure_saniye, cikti_dosyasi):
    """Müziği belirtilen süre kadar döngüye al"""
    ffmpeg_calistir([
        FFMPEG, "-y",
        "-stream_loop", "-1",
        "-i", muzik_dosyasi,
        "-t", str(sure_saniye),
        "-c:a", "aac",
        "-b:a", "192k",
        cikti_dosyasi
    ], f"Müzik loop oluşturuluyor ({sure_saniye}s)")
    return cikti_dosyasi

def animasyon_loop_olustur(animasyon_dosyasi, sure_saniye, cikti_dosyasi):
    """Video/animasyonu belirtilen süre kadar döngüye al"""
    ffmpeg_calistir([
        FFMPEG, "-y",
        "-stream_loop", "-1",
        "-i", animasyon_dosyasi,
        "-t", str(sure_saniye),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-vf", f"scale={VIDEO_GENISLIK}:{VIDEO_YUKSEKLIK},fps={VIDEO_FPS}",
        "-an",
        cikti_dosyasi
    ], f"Animasyon loop oluşturuluyor ({sure_saniye}s)")
    return cikti_dosyasi

def video_muzik_birlestir(video_dosyasi, muzik_dosyasi, cikti_dosyasi):
    """Video ve müziği birleştir"""
    ffmpeg_calistir([
        FFMPEG, "-y",
        "-i", video_dosyasi,
        "-i", muzik_dosyasi,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        cikti_dosyasi
    ], "Video ve müzik birleştiriliyor")
    return cikti_dosyasi

def uzun_video_olustur(animasyon_dosyasi, muzik_dosyasi, sure_saniye, baslik, cikti_adi=None):
    """Ana fonksiyon: animasyon + müzik loop ile uzun video oluştur"""
    os.makedirs(VIDEO_DIR, exist_ok=True)
    gecici_dir = os.path.join(VIDEO_DIR, "gecici")
    os.makedirs(gecici_dir, exist_ok=True)

    if cikti_adi is None:
        cikti_adi = baslik.replace(" ", "_").lower()[:30]

    sure_dk = sure_saniye // 60
    print(f"\n{baslik} ({sure_dk} dakika) oluşturuluyor...")

    # 1. Animasyonu loop'a al
    gecici_video = os.path.join(gecici_dir, f"{cikti_adi}_video.mp4")
    animasyon_loop_olustur(animasyon_dosyasi, sure_saniye, gecici_video)

    # 2. Müziği loop'a al
    gecici_muzik = os.path.join(gecici_dir, f"{cikti_adi}_muzik.aac")
    muzik_loop_olustur(muzik_dosyasi, sure_saniye, gecici_muzik)

    # 3. Birleştir
    cikti_dosyasi = os.path.join(VIDEO_DIR, f"{cikti_adi}.mp4")
    video_muzik_birlestir(gecici_video, gecici_muzik, cikti_dosyasi)

    # 4. Geçici dosyaları sil
    for f in [gecici_video, gecici_muzik]:
        if os.path.exists(f):
            os.remove(f)

    print(f"Video hazır: {cikti_dosyasi}")
    return cikti_dosyasi

def short_video_olustur(animasyon_dosyasi, muzik_dosyasi, sure_saniye, baslik, cikti_adi=None):
    """Shorts için dikey video (1080x1920) oluştur"""
    os.makedirs(VIDEO_DIR, exist_ok=True)

    if cikti_adi is None:
        cikti_adi = "short_" + baslik.replace(" ", "_").lower()[:25]

    cikti_dosyasi = os.path.join(VIDEO_DIR, f"{cikti_adi}.mp4")

    print(f"\nShort video oluşturuluyor: {baslik}")

    ffmpeg_calistir([
        FFMPEG, "-y",
        "-stream_loop", "-1", "-i", animasyon_dosyasi,
        "-stream_loop", "-1", "-i", muzik_dosyasi,
        "-t", str(sure_saniye),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        cikti_dosyasi
    ], "Short video oluşturuluyor")

    print(f"Short video hazır: {cikti_dosyasi}")
    return cikti_dosyasi

def resimden_video_olustur(resim_dosyasi, muzik_dosyasi, sure_saniye, cikti_dosyasi):
    """Tek bir resimden + müzikten video oluştur (basit ninni videoları için)"""
    ffmpeg_calistir([
        FFMPEG, "-y",
        "-loop", "1", "-i", resim_dosyasi,
        "-stream_loop", "-1", "-i", muzik_dosyasi,
        "-t", str(sure_saniye),
        "-vf", f"scale={VIDEO_GENISLIK}:{VIDEO_YUKSEKLIK},fps={VIDEO_FPS}",
        "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        cikti_dosyasi
    ], "Resimden video oluşturuluyor")
    return cikti_dosyasi


if __name__ == "__main__":
    print("Video compiler hazır.")
    print(f"FFmpeg kontrol: ", end="")
    result = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True)
    print("OK" if result.returncode == 0 else "HATA")
