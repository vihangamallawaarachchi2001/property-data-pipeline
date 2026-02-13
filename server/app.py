from flask import Flask, render_template, send_from_directory
import sys
import os

# Add parent directory to path to import scraper modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import storage, config

app = Flask(__name__)

@app.route("/")
def index():
    listings = storage.get_all_listings()
    return render_template("index.html", listings=listings)

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory(config.IMAGES_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
