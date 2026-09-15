import yt_dlp
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("URL não fornecida.")
        sys.exit(1)

    url = sys.argv[1]
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "ogg",
            "preferredquality": "192",
        }],
        "outtmpl": "downloads/%(title)s-%(id)s.%(ext)s",
        "quiet": False,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("Download concluído!")
