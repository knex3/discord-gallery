import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- DATABASE ----------
db = sqlite3.connect("galleries.db")
cursor = db.cursor()

# CORRECT schema: multiple rows per gallery_id
cursor.execute("""
CREATE TABLE IF NOT EXISTS galleries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gallery_id INTEGER,
    user_id INTEGER,
    image_url TEXT
)
""")
db.commit()

# Temporary upload sessions
active_galleries = {}

# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ---------- COLLECT IMAGES ----------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    if uid in active_galleries:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image"):
                active_galleries[uid].append(attachment.url)

    await bot.process_commands(message)

# ---------- GALLERY COMMAND ----------
@bot.command()
async def gallery(ctx, action=None):
    uid = ctx.author.id

    # START SESSION
    if action == "start":
        active_galleries[uid] = []
        await ctx.send(
            "Gallery started.\n"
            "Upload images (multiple messages allowed).\n"
            "Finish with `!gallery done`."
        )
        return

    # FINISH SESSION
    if action == "done":
        images = active_galleries.get(uid)

        if not images:
            await ctx.send("No images uploaded.")
            return

        # Generate new gallery_id safely
        gallery_id = cursor.execute(
            "SELECT COALESCE(MAX(gallery_id), 0) + 1 FROM galleries"
        ).fetchone()[0]

        # Insert ALL images under SAME gallery_id
        for url in images:
            cursor.execute(
                "INSERT INTO galleries (gallery_id, user_id, image_url) VALUES (?, ?, ?)",
                (gallery_id, uid, url)
            )

        db.commit()
        del active_galleries[uid]

        # SEND PERMANENT LINK
        await ctx.send(
            f"🖼 **Gallery ({len(images)} images)**\n"
            f"http://localhost:5000/gallery/{gallery_id}"
        )
        return

    # HELP
    await ctx.send(
        "**Usage**\n"
        "`!gallery start` → upload images → `!gallery done`"
    )

# ---------- RUN ----------

import os

bot.run(os.environ.get("DISCORD_TOKEN"))


