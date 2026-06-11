# audio_to_text.py
import whisper
from whisper.utils import get_writer
import os

# Load once at startup (Docker/build time or app startup)
print("Preloading Whisper model...")
MODEL = whisper.load_model("small")
print("Whisper model ready.")


def transcribe_audio(audio_path, output_dir=None, translate=False):
    """
    Converts audio file to text transcript
    Returns path to transcript file or None if failed
    """
    try:
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), "data", "audio")

        os.makedirs(output_dir, exist_ok=True)

        

        # print(f"Loading Whisper model ({model_size})...")
        # model = MODEL

        print("Transcribing audio...")
        result = MODEL.transcribe(
            audio_path, verbose=True,task='translate' if translate else 'transcribe')

        # Detect the language
        language = result['language']

        print(f"Language Detected: {language}")

        # Generate output filenames
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        srt_path = os.path.join(output_dir, f"{base_name}.srt")
        vtt_path = os.path.join(output_dir, f"{base_name}.vtt")

        # Save outputs
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        srt_writer = get_writer("srt", output_dir)
        srt_writer(result, audio_path)


        vtt_writer = get_writer("vtt", output_dir)
        vtt_writer(result, audio_path)
        
        print(f"Transcript saved to: {txt_path}")
        print(f"SRT Subtitles saved to: {srt_path}")
        print(f"VTT Subtitles saved to: {vtt_path}")

        return txt_path, srt_path, vtt_path, language

    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return None, None, None, None
    
    # clean up audio files
    finally:
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Deleted temporary audio: {audio_path}")
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")