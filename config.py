"""Bot konfiguratsiya va sozlamalar moduli."""

import logging
import os
import sys
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Telegram Mini App (Web App) havolasi
# Eslatma: Telegram Web App faqat HTTPS havolalarni qo'llab-quvvatlaydi
# (masalan: Vercel, GitHub Pages, Render yoki ngrok havolasi)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://calculator-miniapp.vercel.app").strip()

# Log formatlash sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s : %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("CalculatorBot")

if not BOT_TOKEN:
    logger.warning(
        "DIQQAT: BOT_TOKEN topilmadi! Iltimos, .env faylida BOT_TOKEN ni belgilang."
    )
