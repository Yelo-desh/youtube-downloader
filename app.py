from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# تغيير مسار التحميل إلى خارج OneDrive لتجنب المشاكل
download_path = "C:/AI-Downloads"

# تأكد أن المجلد موجود
os.makedirs(download_path, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_formats', methods=['GET'])
def get_formats():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "يرجى إدخال رابط الفيديو"}), 400

    try:
        options = {'quiet': True}
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = [
                {"format_id": f["format_id"], "resolution": f.get("format_note", "Unknown"), "ext": f["ext"]}
                for f in info.get('formats', []) if f.get('vcodec') != 'none'
            ]
        
        return jsonify({"formats": formats})

    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء جلب الجودات: {str(e)}"}), 500

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    format_id = request.args.get('format')

    if not url or not format_id:
        return jsonify({"error": "يرجى إدخال رابط الفيديو واختيار الجودة"}), 400

    try:
        options = {
            'format': format_id,
            'outtmpl': os.path.join(download_path, 'video.%(ext)s'),
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        for file in os.listdir(download_path):
            if file.startswith("video") and file.endswith((".mp4", ".webm", ".mkv")):
                return send_file(os.path.join(download_path, file), as_attachment=True)

        return jsonify({"error": "لم يتم العثور على الملف بعد التحميل"}), 500

    except Exception as e:
        return jsonify({"error": f"حدث خطأ أثناء التحميل: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



