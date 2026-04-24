import os
from pathlib import Path
import yt_dlp

def download_youtube_video(url: str, output_path: Path | None = None, cookies_file: str | None = None) -> Path | None:
    if output_path is None:
        output_path = Path(__file__).resolve().parents[2] / "data" / "downloads"

    output_path.mkdir(parents=True, exist_ok=True)

    ytdlp_options: dict = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": str(output_path / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "merge_output_format": "mp4",
        "js_runtimes": {"node": {}},
        "extractor_retries": 3,
        "sleep_interval": 2,
        "max_sleep_interval": 5,
        "quiet": False,
    }

    if cookies_file:
        ytdlp_options["cookiefile"] = cookies_file

    downloaded_file: Path | None = None

    def on_progress(d: dict) -> None:
        nonlocal downloaded_file
        if d.get("status") == "finished":
            downloaded_file = Path(d["filename"])

    ytdlp_options["progress_hooks"] = [on_progress]

    print(f"Attempting to download: {url}")
    try:
        with yt_dlp.YoutubeDL(ytdlp_options) as ydl:
            ydl.download([url])
        print(f"Download completed. Saved in: {output_path}")
        return downloaded_file

    except yt_dlp.utils.DownloadError as de:
        print(f"Download error: {de}")
        print("\nAvailable formats:")
        try:
            with yt_dlp.YoutubeDL({"listformats": True, "quiet": True}) as ydl:
                ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"Could not list formats: {e}")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    return None

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    result = download_youtube_video(video_url, cookies_file=r'D:\Coding\Python Projects\YTtoMIDI\data\cookies\www.youtube.com_cookies.txt')
    if result:
        print(f"File saved at: {result}")