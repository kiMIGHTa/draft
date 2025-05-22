import ffmpeg
import os

def extract_local_audio_segment(input_path, output_dir):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{base_name}.wav"
        output_file = os.path.join(output_dir, output_filename)

        print("Extracting audio from local file...")
        # Convert to desired format directly
        (
            ffmpeg
            .input(input_path)
            .output(output_file, 
                    acodec='pcm_s16le',  # 16-bit PCM
                    ar='48000',           # 48kHz sample rate
                    ac=2,                 # Stereo
                    af='loudnorm=I=-16:TP=-1.5:LRA=11')  # Loudness normalization
            .run(overwrite_output=True)
        )

        print(f"Successfully saved audio to: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error: {str(e)}")
        return False