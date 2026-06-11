# main.py
import os
import re
from extract_yt_audio import extract_yt_audio_segment
from audio_to_text import transcribe_audio
from extract_local_audio import extract_local_audio_segment
from pathlib import Path


def is_url(input_dir):
    return bool(re.match(r'http(s)?://', input_dir))


def process_video(input_dir, translate=False):
    try:
        output_dir = str(Path.home() / "Downloads" / "audio")


        # download audio
        if is_url(input_dir):
            print("Input is a URL, downloading audio...")
            audio = extract_yt_audio_segment(input_dir, output_dir)
            # if not audio:
            #     print("Failed to download and convert YouTube audio")
            #     pass
        else:
            print("Input is a local file, extracting audio...")
            audio = extract_local_audio_segment(input_dir, output_dir)

        if not audio:
            print("Failed to download and convert audio")

        transcript_file, language = transcribe_audio(
            audio, output_dir, translate=translate)
        
        if not transcript_file:
            print("Failed to transcribe audio.")
            return None

        print(f"Transcribed in {language}. File: {transcript_file}")

        return f"Transcribed in {language}. File: {transcript_file}"

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    input_dir = input("Enter a video or audio URL or local path: ").strip()
    translate = input("Do you want to translate to English? (y/n): ").lower().strip() == 'y'

    process_video(input_dir, translate=translate)
