import os
from extract_yt_audio import extract_yt_audio_segment
from audio_to_text import transcribe_audio

def process_video(youtube_url):
    try: 
        output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "audio")

        #download audio
        audio = extract_yt_audio_segment(youtube_url, output_dir)
        if not audio:
            print("Failed to download and convert audio")
        to_text = transcribe_audio(audio,output_dir)
        if not to_text:
            print("Failed to transcribe audio")
        return f"{audio} /n - {to_text}"  
    except Exception as e:
        print(f"Error: {str(e)}")
        return None




if __name__ == "__main__":
    youtube_url = 'https://www.youtube.com/watch?v=LdY5VIXZ0YA&pp=ygUcZWFybCBzd2VhdHNoaXJ0IGhlYXZlbiBrbm93cw%3D%3D'
    process_video(youtube_url)


