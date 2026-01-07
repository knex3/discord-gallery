from flask import Flask, render_template, abort
import sqlite3
import os

app = Flask(__name__)

# ---------- DATABASE ----------
# SQLite must live in the project root on Railway
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "galleries.db")


def get_images(gallery_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT image_url FROM galleries WHERE gallery_id = ?",
        (gallery_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


# ---------- ROUTES ----------

@app.route("/")
def index():
    return "Discord Gallery is running."


@app.route("/gallery/<int:gallery_id>")
def gallery(gallery_id):
    images = get_images(gallery_id)
    if not images:
        abort(404)
    return render_template(
        "gallery.html",
        images=images,
        gallery_id=gallery_id
    )


# ---------- START SERVER ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port)
