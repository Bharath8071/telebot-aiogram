import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
import aiohttp

# 🔹 Bot token from Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# 🔹 Public Render URL (Render automatically sets this)
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

# 🔹 Webhook configuration
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{RENDER_URL}{WEBHOOK_PATH}"

bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# =========================
# 🔸 Inline Keyboard
# =========================
def join_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join Our Group", url="https://t.me/ardonaterbot")],
    ])


# =========================
# 🔸 Fetch JSON Data
# =========================
async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                return await r.json()
    return None


# =========================
# 🔸 /like command handler
# =========================
@dp.message(Command("like"))
async def like_handler(msg: Message):
    parts = msg.text.split()
    if len(parts) != 3:
        await msg.reply("❗ Correct format: /like bd uid", reply_markup=join_keyboard())
        return

    region, uid = parts[1].upper(), parts[2]
    if region not in ["BD", "IND"]:
        await msg.reply("❗ Only BD or IND regions are supported!", reply_markup=join_keyboard())
        return

    wait = await msg.reply("⏳ Sending Likes, Please Wait.....")
    url = f"https://anish-likes.vercel.app/like?server_name={region.lower()}&uid={uid}&key=jex4rrr"
    data = await fetch_json(url)

    if not data:
        await wait.edit_text("❌ Failed to send request. Check UID or try later.", reply_markup=join_keyboard())
        return

    if data.get("status") == 2:
        await wait.edit_text(
            f"🚫 Max Likes Reached by API\n\n"
            f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
            f"🆔 UID: {uid}\n"
            f"🌍 Region: {region}\n"
            f"❤️ Current Likes: {data.get('LikesNow', 'N/A')}",
            reply_markup=join_keyboard()
        )
        return

    await wait.edit_text(
        f"✅ Likes Sent Successfully!\n\n"
        f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
        f"🆔 UID: {uid}\n"
        f"❤️ Before Likes: {data.get('LikesbeforeCommand', 'N/A')}\n"
        f"👍 Current Likes: {data.get('LikesafterCommand', 'N/A')}\n"
        f"🎯 Likes Sent By ARDONATER BOT: {data.get('LikesGivenByAPI', 'N/A')}",
        reply_markup=join_keyboard()
    )


# =========================
# 🔸 Startup & Shutdown
# =========================
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()
    print("❌ Webhook removed")


# =========================
# 🔸 AIOHTTP Web Server
# =========================
app = web.Application()
app.router.add_post(WEBHOOK_PATH, dp.start_webhook(bot))
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
