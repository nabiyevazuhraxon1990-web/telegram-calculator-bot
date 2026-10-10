"""Telegram Mini App (Web App) uchun statik veb-server.

Ushbu server 'webapp/' papkasidagi fayllarni lokal tarmoqda taqdim etadi.
Telegram Web App ishlashi uchun HTTPS kerak bo'lgani sababli, lokal testda
ngrok yoki Cloudflare Tunnel dan foydalanishingiz mumkin:
  ngrok http 8080
"""

import os
from aiohttp import web

WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "webapp")
PORT = int(os.getenv("PORT", 8080))


async def init_app():
    app = web.Application()
    # Asosiy index sahifasini uzatish
    async def index(request):
        return web.FileResponse(os.path.join(WEBAPP_DIR, "index.html"))

    app.router.add_get("/", index)
    # Statik fayllarni (css, js, rasmlar) uzatish
    app.router.add_static("/", WEBAPP_DIR, show_index=True)
    return app


def main():
    print("=" * 60)
    print(f"🚀 Telegram Mini App veb-serveri ishga tushmoqda!")
    print(f"📍 Manzil: http://localhost:{PORT}")
    print(f"📁 Papka:  {WEBAPP_DIR}")
    print("\n💡 Telegramda ochish uchun:")
    print("1. Terminalda yangi oynada: ngrok http 8080")
    print("2. Chiqqan HTTPS havolani .env dagi WEBAPP_URL ga qo'ying.")
    print("3. Yoki Vercel/GitHub Pages orqali bepul joylang.")
    print("=" * 60 + "\n")

    app = init_app()
    web.run_app(app, port=PORT)


if __name__ == "__main__":
    main()
