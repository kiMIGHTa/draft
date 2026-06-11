import os
from flask import Flask, render_template, request, jsonify, send_from_directory

from extract_yt_audio import extract_yt_audio_segment
from extract_local_audio import extract_local_audio_segment
from audio_to_text import transcribe_audio

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SUPPORTED_EXTENSIONS = {"mp3", "wav", "m4a", "aac", "mp4", "mkv", "mov", "avi"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    has_file = "file" in request.files and request.files["file"].filename != ""
    has_url = bool(request.form.get("youtube_url", "").strip())

    # XOR: exactly one of file or youtube_url must be present
    if has_file == has_url:
        return jsonify({"success": False, "message": "No input provided."}), 400

    # Parse translate flag: strip + case-insensitive compare against "true"
    translate_raw = request.form.get("translate", "")
    translate = translate_raw.strip().lower() == "true"

    if has_file:
        uploaded = request.files["file"]
        ext = os.path.splitext(uploaded.filename)[1].lstrip(".").lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return jsonify({"success": False, "message": "Unsupported file."}), 400

        saved_path = os.path.join(OUTPUT_DIR, uploaded.filename)
        try:
            uploaded.save(saved_path)
            audio_path = extract_local_audio_segment(
                saved_path, output_dir=OUTPUT_DIR)
            if not audio_path:
                return jsonify({"success": False, "message": "ffmpeg failed."}), 500
            txt_path, srt_path, vtt_path, language = transcribe_audio(
                audio_path,
                output_dir=OUTPUT_DIR,
                translate=translate,
            )
        finally:
            if os.path.exists(saved_path):
                os.remove(saved_path)

    else:
        youtube_url = request.form.get("youtube_url", "").strip()
        if not (youtube_url.startswith("http://") or youtube_url.startswith("https://")):
            return jsonify({"success": False, "message": "Invalid URL."}), 400

        audio_path = extract_yt_audio_segment(youtube_url, OUTPUT_DIR)
        if not audio_path:
            return jsonify({"success": False, "message": "Download failed."}), 500
        txt_path, srt_path, vtt_path, language = transcribe_audio(
            audio_path,
            output_dir=OUTPUT_DIR,
            translate=translate,
        )

    if not txt_path or not srt_path or not vtt_path:
        return jsonify({"success": False, "message": "Whisper failed."}), 500

    return jsonify({
        "success": True,
        "language": language,
        "txt_file": os.path.basename(txt_path),
        "srt_file": os.path.basename(srt_path),
        "vtt_file": os.path.basename(vtt_path),
        "message": "Transcription completed",
    }), 200


@app.route("/download/<filename>")
def download_file(filename):
    if not filename or not filename.strip():
        return jsonify({"success": False, "message": "No filename provided."}), 400
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
