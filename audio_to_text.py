import whisper
from whisper.utils import get_writer
import os

def transcribe_audio(audio_path, output_dir=None, model_size="small"):
    """
    Converts audio file to text transcript
    Returns path to transcript file or None if failed
    """
    try:
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)

        print(f"Loading Whisper model ({model_size})...")
        model = whisper.load_model(model_size)

        print("Transcribing audio...")
        result = model.transcribe(audio_path)

        # Generate output filenames
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        txt_path = os.path.join(output_dir, f"{base_name}.txt")
        srt_path = os.path.join(output_dir, f"{base_name}.srt")

        # Save outputs
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        writer = get_writer("srt", output_dir)
        writer(result, audio_path)

        print(f"Transcript saved to: {txt_path}")
        print(f"Subtitles saved to: {srt_path}")
        return txt_path

    except Exception as e:
        print(f"Transcription error: {str(e)}")
        return None