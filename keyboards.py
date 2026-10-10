"""Telegram bot klaviaturalari (Keyboards).

Foydalanuvchi interfeysi uchun estetik, qulay va interaktiv tugmalar:
- Inline kalkulyator klaviaturasi (Standart va Ilmiy rejim)
- Asosiy doimiy Reply klaviatura (Menyu)
- Natija va tarix uchun qo'shimcha boshqaruv tugmalari
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

import config


def get_calc_inline_keyboard(mode: str = "std") -> InlineKeyboardMarkup:
    """Kalkulyatorning interaktiv inline klaviaturasini yaratadi."""
    if mode == "sci":
        # Ilmiy (muhandislik) rejimi tugmalari
        buttons = [
            [
                InlineKeyboardButton(text="√x", callback_data="calc:fn_sqrt"),
                InlineKeyboardButton(text="x²", callback_data="calc:fn_sqr"),
                InlineKeyboardButton(text="xʸ", callback_data="calc:fn_pow"),
                InlineKeyboardButton(text="n!", callback_data="calc:fn_fact"),
            ],
            [
                InlineKeyboardButton(text="sin", callback_data="calc:fn_sin"),
                InlineKeyboardButton(text="cos", callback_data="calc:fn_cos"),
                InlineKeyboardButton(text="tan", callback_data="calc:fn_tan"),
                InlineKeyboardButton(text="log", callback_data="calc:fn_log"),
            ],
            [
                InlineKeyboardButton(text="π", callback_data="calc:fn_pi"),
                InlineKeyboardButton(text="e", callback_data="calc:fn_e"),
                InlineKeyboardButton(text="|x|", callback_data="calc:fn_abs"),
                InlineKeyboardButton(text="⌫", callback_data="calc:backspace"),
            ],
            [
                InlineKeyboardButton(text="(", callback_data="calc:("),
                InlineKeyboardButton(text=")", callback_data="calc:)"),
                InlineKeyboardButton(text="C", callback_data="calc:clear"),
                InlineKeyboardButton(text="=", callback_data="calc:equal"),
            ],
            [
                InlineKeyboardButton(text="🔙 Standart rejim", callback_data="calc:mode_std"),
                InlineKeyboardButton(text="📱 Mini App", web_app=WebAppInfo(url=config.WEBAPP_URL)),
            ],
        ]
    else:
        # Standart rejim tugmalari
        buttons = [
            [
                InlineKeyboardButton(text="C", callback_data="calc:clear"),
                InlineKeyboardButton(text="(", callback_data="calc:("),
                InlineKeyboardButton(text=")", callback_data="calc:)"),
                InlineKeyboardButton(text="⌫", callback_data="calc:backspace"),
            ],
            [
                InlineKeyboardButton(text="7", callback_data="calc:7"),
                InlineKeyboardButton(text="8", callback_data="calc:8"),
                InlineKeyboardButton(text="9", callback_data="calc:9"),
                InlineKeyboardButton(text="÷", callback_data="calc:/"),
            ],
            [
                InlineKeyboardButton(text="4", callback_data="calc:4"),
                InlineKeyboardButton(text="5", callback_data="calc:5"),
                InlineKeyboardButton(text="6", callback_data="calc:6"),
                InlineKeyboardButton(text="×", callback_data="calc:*"),
            ],
            [
                InlineKeyboardButton(text="1", callback_data="calc:1"),
                InlineKeyboardButton(text="2", callback_data="calc:2"),
                InlineKeyboardButton(text="3", callback_data="calc:3"),
                InlineKeyboardButton(text="−", callback_data="calc:-"),
            ],
            [
                InlineKeyboardButton(text="0", callback_data="calc:0"),
                InlineKeyboardButton(text=".", callback_data="calc:."),
                InlineKeyboardButton(text="%", callback_data="calc:%"),
                InlineKeyboardButton(text="+", callback_data="calc:+"),
            ],
            [
                InlineKeyboardButton(text="🔬 Ilmiy rejim", callback_data="calc:mode_sci"),
                InlineKeyboardButton(text="=", callback_data="calc:equal"),
            ],
            [
                InlineKeyboardButton(
                    text="📱 Mini Appda ochish",
                    web_app=WebAppInfo(url=config.WEBAPP_URL),
                ),
            ],
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu uchun pastki qulay Reply klaviatura."""
    keyboard = [
        [
            KeyboardButton(
                text="📱 Mini App Kalkulyator",
                web_app=WebAppInfo(url=config.WEBAPP_URL),
            ),
        ],
        [
            KeyboardButton(text="🧮 Kalkulyator"),
            KeyboardButton(text="📜 Tarix"),
        ],
        [
            KeyboardButton(text="💡 Yordam & Misollar"),
            KeyboardButton(text="🗑 Tarixni tozalash"),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Misolni yozing yoki menyudan tanlang...",
    )


def get_result_inline_keyboard(result_val: str) -> InlineKeyboardMarkup:
    """Matn orqali hisoblangan natija ostidagi tezkor tugmalar."""
    # Natija qiymatidagi probellarni olib tashlaymiz
    clean_val = result_val.split("(")[0].strip()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧮 Ushbu natija bilan davom etish",
                    callback_data=f"use_res:{clean_val}",
                ),
            ],
            [
                InlineKeyboardButton(text="📜 Tarix", callback_data="view_history"),
                InlineKeyboardButton(text="🔄 Yangi kalkulyator", callback_data="new_calc"),
            ],
        ]
    )


def get_history_inline_keyboard() -> InlineKeyboardMarkup:
    """Tarix xabari ostidagi tugmalar."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧮 Kalkulyatorni ochish", callback_data="new_calc"),
                InlineKeyboardButton(text="🗑 Tarixni tozalash", callback_data="clear_history_cb"),
            ]
        ]
    )
