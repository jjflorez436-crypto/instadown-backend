from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import re

app = Flask(**name**)
CORS(app)

def is_valid_instagram_url(url):
return bool(re.search(r”instagram.com”, url, re.I))

@app.route(”/”)
def index():
return jsonify({“status”: “InstaDown API corriendo”})

@app.route(”/api/info”, methods=[“POST”])
def get_info():
data = request.get_json()
url = data.get(“url”, “”).strip()
if not url or not is_valid_instagram_url(url):
return jsonify({“error”: “URL invalida”}), 400
ydl_opts = {“quiet”: True, “skip_download”: True}
try:
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
info = ydl.extract_info(url, download=False)
return jsonify({
“title”: info.get(“title”, “Video de Instagram”),
“author”: info.get(“uploader”, “usuario”),
“thumbnail”: info.get(“thumbnail”, “”),
“duration”: info.get(“duration”, 0),
})
except Exception as e:
return jsonify({“error”: str(e)}), 500

@app.route(”/api/download”, methods=[“POST”])
def download_video():
data = request.get_json()
url = data.get(“url”, “”).strip()
fmt = data.get(“format”, “mp4”)
if not url or not is_valid_instagram_url(url):
return jsonify({“error”: “URL invalida”}), 400
tmp_dir = tempfile.mkdtemp()
output_path = os.path.join(tmp_dir, “instadown_video.%(ext)s”)
if fmt == “mp3”:
ydl_opts = {
“format”: “bestaudio/best”,
“outtmpl”: output_path,
“quiet”: True,
“postprocessors”: [{“key”: “FFmpegExtractAudio”, “preferredcodec”: “mp3”, “preferredquality”: “192”}],
}
final_ext = “mp3”
mime = “audio/mpeg”
else:
ydl_opts = {
“format”: “bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best”,
“outtmpl”: output_path,
“quiet”: True,
}
final_ext = “mp4”
mime = “video/mp4”
try:
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
ydl.download([url])
final_file = os.path.join(tmp_dir, “instadown_video.” + final_ext)
if not os.path.exists(final_file):
for f in os.listdir(tmp_dir):
if f.endswith(final_ext):
final_file = os.path.join(tmp_dir, f)
break
return send_file(final_file, mimetype=mime, as_attachment=True, download_name=“instadown.” + final_ext)
except Exception as e:
return jsonify({“error”: str(e)}), 500

if **name** == “**main**”:
port = int(os.environ.get(“PORT”, 5000))
app.run(host=“0.0.0.0”, port=port)
