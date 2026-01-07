import os
import discord
from discord.ext import commands
import psycopg2

# ---------------- CONFIG ----------------
GALLERY_BASE_URL = "https://discord-gallery.up.railway.app"
# ⬆️ change this if Railway gives you a different URL

# ---------------- DISCORD ----------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- DATABASE (POSTGRES) ----------------
conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.autocommit = True
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS galleries (
    id SERIAL PRIMARY KEY,
    gallery_id INTEGER,
    user_id BIGINT,
    image_url TEXT
)
""")

# ---------------- TEMP STORAGE ----------------
active_galleries = {}

# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ---------------- COLLECT IMAGES ----------------
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

# ---------------- GALLERY COMMAND ----------------
@bot.command()
async def gallery(ctx, action=None):
    uid = ctx.author.id

    # START
    if action == "start":
        active_galleries[uid] = []
        await ctx.send(
            "🟢 **Gallery started**\n"
            "Upload images (multiple messages allowed).\n"
            "Finish with `!gallery done`."
        )
        return

    # DONE
    if action == "done":
        images = active_galleries.get(uid)

        if not images:
            await ctx.send("❌ No images uploaded.")
            return

        cursor.execute("SELECT COALESCE(MAX(gallery_id), 0) + 1 FROM galleries")
        gallery_id = cursor.fetchone()[0]

        for url in images:
            cursor.execute(
                "INSERT INTO galleries (gallery_id, user_id, image_url) VALUES (%s, %s, %s)",
                (gallery_id, uid, url)
            )

        del active_galleries[uid]

        await ctx.send(
            f"🖼 **Gallery created ({len(images)} images)**\n"
            f"{GALLERY_BASE_URL}/gallery/{gallery_id}"
        )
        return

    # HELP
    await ctx.send(
        "**Gallery Commands**\n"
        "`!gallery start` → upload images → `!gallery done`"
    )

# ---------------- RUN ----------------
bot.run(os.environ["DISCORD_TOKEN"])
