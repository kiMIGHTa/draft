import yt_dlp
import ffmpeg
import os
import uuid


def extract_yt_audio_segment(url, output_dir):
    temp_audio_path = None
    output_file = None

    # COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")

    try:
        os.makedirs(output_dir, exist_ok=True)

        # -------------------------
        # Metadata
        # -------------------------
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)

        video_title = (info.get("title") or "audio").replace("/", "-")[:50]
        upload_date = info.get("upload_date") or ""

        upload_date = (
            f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}_"
            if upload_date else ""
        )

        output_file = os.path.join(output_dir, f"{upload_date}{video_title}.wav")

        # -------------------------
        # Temp file
        # -------------------------
        temp_dir = os.path.join(os.path.expanduser("~"), "tmp_audio_downloads")
        os.makedirs(temp_dir, exist_ok=True)

        temp_audio_path = os.path.join(
            temp_dir,
            f"temp_audio_{uuid.uuid4().hex}"
        )

        # -------------------------
        # 🔥 FIXED yt-dlp CONFIG
        # -------------------------
        ydl_opts = {
            # IMPORTANT: force real audio formats first
            "format": (
                "bestaudio[ext=m4a]/"
                "bestaudio[ext=webm]/"
                "bestaudio/best"
            ),

            "outtmpl": temp_audio_path,

            "noplaylist": True,
            "quiet": False,
            "no_warnings": False,

            # -------------------------
            # AUTH (cookies fix)
            # -------------------------
            "cookiesfrombrowser": ("chrome",),

            # -------------------------
            # 🔥 CLIENT FALLBACK STRATEGY
            # -------------------------
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web", "ios", "tv"]
                }
            },

            # -------------------------
            # STABILITY FIXES
            # -------------------------
            "retries": 10,
            "fragment_retries": 10,
            "concurrent_fragment_downloads": 1,

            "skip_unavailable_fragments": True,
            "ignoreerrors": False,

            # helps with modern YouTube throttling
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        }

        # -------------------------
        # Download
        # -------------------------
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_file = temp_audio_path

        # fallback if yt-dlp changes extension
        if not os.path.exists(downloaded_file):
            matches = [
                f for f in os.listdir(temp_dir)
                if f.startswith(os.path.basename(temp_audio_path))
            ]

            if matches:
                downloaded_file = os.path.join(temp_dir, matches[0])
            else:
                raise FileNotFoundError("yt-dlp did not produce audio file")

        # -------------------------
        # Convert to WAV
        # -------------------------
        (
            ffmpeg
            .input(downloaded_file)
            .output(
                output_file,
                acodec="pcm_s16le",
                ar="48000",
                ac=2
            )
            .run(overwrite_output=True, quiet=True)
        )

        return output_file

    except Exception as e:
        print(f"[YT-DLP ERROR]: {e}")
        return False

    finally:
        try:
            if temp_audio_path and os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    if f.startswith(os.path.basename(temp_audio_path)):
                        os.remove(os.path.join(temp_dir, f))
        except Exception:
            pass