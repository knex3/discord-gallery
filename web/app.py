from flask import Flask, render_template, abort
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.environ["DATABASE_URL"]

def get_db():
    return psycopg2.connect(DATABASE_URL)

def get_images(gallery_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT image_url FROM galleries WHERE gallery_id = %s",
        (gallery_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

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

if __name__ == "__main__":
    # IMPORTANT: Railway public networking uses port 5000
    app.run(host="0.0.0.0", port=5000)
