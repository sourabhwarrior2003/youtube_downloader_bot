from flask import Flask, request, render_template, send_file, url_for
import os, sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from downloader import download_audio, download_video

app = Flask(__name__, static_folder="assets", static_url_path="/assets")  # 👈 custom folder name with static_url_path set

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        format_type = request.form["format"]
        cancel_flag = threading.Event()

        try:
            if format_type == "audio":
                filename, title, _ = download_audio(url, cancel_flag)
            else:
                filename, title, _ = download_video(url, cancel_flag)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            return f"<h3>Error:</h3><p>{str(e)}</p>"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
