from flask import Flask, render_template, abort
import sqlite3

app = Flask(__name__)

DB_PATH = "../galleries.db"

def get_images(gallery_id):
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    rows = cur.execute(
        "SELECT image_url FROM galleries WHERE gallery_id = ?",
        (gallery_id,)
    ).fetchall()
    db.close()
    return [r[0] for r in rows]

@app.route("/gallery/<int:gallery_id>")
def gallery(gallery_id):
    images = get_images(gallery_id)
    if not images:
        abort(404)
    return render_template("gallery.html", images=images, gallery_id=gallery_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
