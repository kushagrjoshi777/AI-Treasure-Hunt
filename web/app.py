"""
Minimal Flask server for the AI Treasure Hunt web app.
Serves the single-page index.html (and any static assets).
Run:  python app.py
Then open http://localhost:5000 in your browser.
"""

import os
from flask import Flask, send_from_directory

# Resolve the directory that contains this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


@app.route("/")
def index():
    """Serve the main SPA."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve any other static file next to index.html."""
    return send_from_directory(BASE_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"AI Treasure Hunt  ->  http://localhost:{port}")
    # debug=True gives auto-reload during development; set to False for production
    app.run(host="0.0.0.0", port=port, debug=True)
