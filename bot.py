import os
import asyncio
import threading
from aiohttp import web
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]        # задаётся в Render → Environment
TARGET_USER_ID = int(os.environ.get("TARGET_USER_ID", "0"))
SPAM_TEXT = os.environ.get("SPAM_TEXT", "текст спама")
SPAM_COUNT = int(os.environ.get("SPAM_COUNT", "50"))
DELAY = float(os.environ.get("DELAY", "0.7"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот поднят как {bot.user}", flush=True)

@bot.command(name="spam")
async def spam(ctx, user_id: int, *, text: str):
    target = await bot.fetch_user(user_id)
    try:
        dm = await target.create_dm()
    except discord.Forbidden:
        await ctx.send("Не могу открыть личку.")
        return
    for i in range(SPAM_COUNT):
        try:
            await dm.send(text)
        except discord.HTTPException as e:
            print(f"[{i}] {e}", flush=True)
            await asyncio.sleep(2)
            continue
        await asyncio.sleep(DELAY)
    await ctx.send(f"Готово: {SPAM_COUNT} сообщений → {target}")

# --- health-сервер для Render ---
async def health(request):
    return web.Response(text="ok")

def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))

# --- запуск ---
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.run(TOKEN)
