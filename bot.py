import os
import asyncio
import threading
from aiohttp import web
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]
DEFAULT_COUNT = int(os.environ.get("SPAM_COUNT", "50"))
DELAY = float(os.environ.get("DELAY", "0.7"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Бот поднят как {bot.user}", flush=True)

@bot.command(name="target")
async def target(ctx, user_id: int, count: int = None, *, text: str = None):
    # порядок: !target <id> [сколько] <текст>
    # если count не задан — текст идёт сразу после id
    if text is None:
        # значит второй аргумент — это текст, а не число
        text = str(count) if count is not None else ""
        count = DEFAULT_COUNT
    if not text:
        await ctx.send("Формат: `!target <id> [сколько] <текст>`")
        return

    try:
        target_user = await bot.fetch_user(user_id)
    except discord.NotFound:
        await ctx.send("Юзер не найден.")
        return

    try:
        dm = await target_user.create_dm()
    except discord.Forbidden:
        await ctx.send("Не могу открыть личку.")
        return

    await ctx.send(f"Старт: {count} сообщений → {target_user}")

    for i in range(count):
        try:
            await dm.send(text)
        except discord.HTTPException as e:
            print(f"[{i}] {e}", flush=True)
            await asyncio.sleep(2)
            continue
        await asyncio.sleep(DELAY)

    await ctx.send(f"Готово: {count} сообщений → {target_user}")

async def health(request):
    return web.Response(text="ok")

def run_web():
    app = web.Application()
    app.router.add_get("/", health)
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    bot.run(TOKEN)
