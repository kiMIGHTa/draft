import yt_dlp
import ffmpeg
import os

def extract_audio_segment(url, output_dir):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)

        # Get video info for naming
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'audio').replace("/", "-")[:50]
            upload_date = info.get('upload_date', '')
            if upload_date:
                upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}_"

        # Generate dynamic filename
        output_filename = f"{upload_date}_{video_title}.wav"

        output_file = os.path.join(output_dir, output_filename)



        # Temporary file path (in system temp directory)
        temp_dir = os.path.join(os.path.expanduser("~"), "tmp_audio_downloads")
        os.makedirs(temp_dir, exist_ok=True)
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")

        # Download best audio stream
        ydl_opts = {
            'format': 'bestaudio[ext=webm]/bestaudio/best',
            'outtmpl': temp_audio_path.replace('.wav', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '0',  

            }],
            'extract_audio': True,
            'audio_quality': '0', 
            'quiet': True,
        }

        print("Downloading audio from YouTube...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Converting audio to desired format...")
        # Convert to desired format
        (
            ffmpeg
            .input(temp_audio_path)
            .output(output_file, acodec='pcm_s16le', ar='48000', 
                    ac=2,        
                    af='loudnorm=I=-16:TP=-1.5:LRA=11',)
            .run(overwrite_output=True)
        )

        print(f"Successfully saved audio to: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


