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

COMMON_OPTS = {
“quiet”: True,
“no_warnings”: True,
“http_headers”: {
“User-Agent”: “Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1”,
“Accept”: “text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8”,
“Accept-Language”: “en-US,en;q=0.5”,
“Accept-Encoding”: “gzip, deflate, br”,
“DNT”: “1”,
“Connection”: “keep-alive”,
},
“extractor_args”: {
“instagram”: {
“include_feed_videos”: True,
}
},
}

@app.route(”/”)
def index():
return jsonify({“status”: “InstaDown API corriendo”})

@app.route(”/api/info”, methods=[“POST”])
def get_info():
data = request.get_json()
url = data.get(“url”, “”).strip()
if not url or not is_valid_instagram_url(url):
return jsonify({“error”: “URL invalida”}), 400
ydl_opts = {**COMMON_OPTS, “skip_download”: True}
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
**COMMON_OPTS,
“format”: “bestaudio/best”,
“outtmpl”: output_path,
“postprocessors”: [{“key”: “FFmpegExtractAudio”, “preferredcodec”: “mp3”, “preferredquality”: “192”}],
}
final_ext = “mp3”
mime = “audio/mpeg”
else:
ydl_opts = {
**COMMON_OPTS,
“format”: “bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best”,
“outtmpl”: output_path,
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
