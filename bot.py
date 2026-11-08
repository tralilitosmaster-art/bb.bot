import os
import asyncio
from aiohttp import web
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]
DEFAULT_COUNT = int(os.environ.get("SPAM_COUNT", "50"))
DELAY = float(os.environ.get("DELAY", "0.7"))
PORT = int(os.environ.get("PORT", "8080"))

intents = discord.Intents.default()
intents.message_content = True
# intents.members = True  # не нужен для ЛС, не включай без нужды

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Бот поднят как {bot.user}", flush=True)


@bot.command(name="target")
async def target(ctx, user_id: int, *, args: str = ""):
    if not args:
        await ctx.send("Формат: `!target <id> [сколько] <текст>`")
        return

    parts = args.split(maxsplit=1)
    if parts[0].isdigit() and len(parts) == 2:
        count = int(parts[0])
        text = parts[1]
    else:
        count = DEFAULT_COUNT
        text = args

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


async def main():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Health-сервер на порту {PORT}", flush=True)

    try:
        await bot.start(TOKEN)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
