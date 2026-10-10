"""Telegram Kalkulyator Botini ishga tushirish (Main) fayli."""

import asyncio
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

import config
from handlers import router


WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "webapp")


async def create_web_server(port: int) -> web.AppRunner:
    """Railway va Mini App uchun statik veb-server runner yaratish."""
    app = web.Application()

    async def index_handler(request):
        index_path = os.path.join(WEBAPP_DIR, "index.html")
        if os.path.exists(index_path):
            return web.FileResponse(index_path)
        return web.Response(text="Telegram Mini App Kalkulyator ishlamoqda.")

    async def health_handler(request):
        return web.Response(text="OK - Bot va Mini App faol!", status=200)

    app.router.add_get("/", index_handler)
    app.router.add_get("/health", health_handler)
    if os.path.exists(WEBAPP_DIR):
        app.router.add_static("/", WEBAPP_DIR, show_index=True)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    return runner


async def set_bot_commands(bot: Bot) -> None:
    """Telegram menyusida paydo bo'ladigan asosiy buyruqlar."""
    commands = [
        BotCommand(command="start", description="Botni qayta ishga tushirish"),
        BotCommand(command="calc", description="🧮 Yangi kalkulyator oynasi"),
        BotCommand(command="help", description="💡 Yordam va foydalanish misollari"),
        BotCommand(command="history", description="📜 Hisob-kitoblar tarixi"),
        BotCommand(command="clear", description="🗑 Tarixni tozalash"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    """Botning asosiy asinxron ishga tushish funksiyasi."""
    token = config.BOT_TOKEN

    if not token or token == "YOUR_BOT_TOKEN_HERE":
        config.logger.error(
            "\n" + "=" * 60 + "\n"
            "XATOLIK: Bot tokeni topilmadi!\n\n"
            "Botni ishga tushirishdan oldin:\n"
            "1. .env fayliga kiring (yoki .env.example dan nusxa oling)\n"
            "2. @BotFather dan olgan bot tokeningizni quyidagicha yozing:\n"
            "   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ\n"
            "3. So'ngra qaytadan ishga tushiring: python3 main.py\n"
            + "=" * 60
        )
        sys.exit(1)

    web_runner = None
    port_env = os.getenv("PORT")
    if port_env:
        try:
            port = int(port_env)
            web_runner = await create_web_server(port)
            config.logger.info(f"Veb-server (Mini App) ishga tushdi: http://0.0.0.0:{port}")
        except Exception as ex:
            config.logger.warning(f"Veb-serverni ishga tushirishda xatolik: {ex}")

    # Bot obyekti (HTML formatlash yoqilgan)
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # Dispatcher obyekti
    dp = Dispatcher()
    dp.include_router(router)

    config.logger.info("Bot ishga tushmoqda...")

    try:
        # Eski keshdagi yangilanishlarni tozalash
        await bot.delete_webhook(drop_pending_updates=True)

        # Telegram menyu buyruqlarini sozlash
        await set_bot_commands(bot)

        bot_info = await bot.get_me()
        config.logger.info(
            f"Bot muvaffaqiyatli ishga tushdi! @{bot_info.username} (ID: {bot_info.id})"
        )

        # Polling rejimida xabarlarni tinglash
        await dp.start_polling(bot)

    except Exception as e:
        config.logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")
    finally:
        if web_runner:
            await web_runner.cleanup()
        await bot.session.close()
        config.logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        config.logger.info("Bot yakunlandi.")
