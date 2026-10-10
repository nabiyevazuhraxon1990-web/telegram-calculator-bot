"""Telegram bot xabar va hodisalarini boshqaruvchi (Handlers) moduli."""

from datetime import datetime
import json
import re
from typing import Dict, List, Optional

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from calculator import SafeCalculator
import keyboards

router = Router()

# ==========================================
# SEANSI VA TARIXNI XOTIRADA SAQLASH
# ==========================================

# Key: (chat_id, message_id) -> Session data
calc_sessions: Dict[tuple, dict] = {}

# Key: user_id -> List[{"expr": str, "result": str, "time": str}]
user_histories: Dict[int, List[dict]] = {}


def get_or_create_session(chat_id: int, message_id: int, initial_expr: str = "") -> dict:
    """Xabar uchun kalkulyator seansini olish yoki yangisini yaratish."""
    key = (chat_id, message_id)
    if key not in calc_sessions:
        calc_sessions[key] = {
            "expr": initial_expr,
            "mode": "std",
            "last_result": initial_expr if initial_expr else None,
            "just_evaluated": bool(initial_expr),
            "error_msg": None,
        }
    return calc_sessions[key]


def add_to_history(user_id: int, expr: str, result: str) -> None:
    """Foydalanuvchi hisoblash tarixiga yangi yozuv qo'shish."""
    if user_id not in user_histories:
        user_histories[user_id] = []

    now_str = datetime.now().strftime("%H:%M")
    user_histories[user_id].insert(
        0, {"expr": expr, "result": result, "time": now_str}
    )

    # Oxirgi 10 ta yozuvni saqlaymiz
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][:10]


def render_display(session: dict) -> str:
    """Kalkulyator ekrani matnini chiroyli grafik ko'rinishda yaratadi."""
    expr = session.get("expr", "").strip()
    last_res = session.get("last_result")
    just_eval = session.get("just_evaluated", False)
    err = session.get("error_msg")
    mode = session.get("mode", "std")

    mode_title = "🔬 ILMIY REJIM" if mode == "sci" else "🔢 STANDART REJIM"

    # Agar ifoda bo'sh bo'lsa
    top_line = expr if expr else "0"

    # Matnni qisqartirish (agar haddan tashqari uzun bo'lsa)
    if len(top_line) > 30:
        top_line = "..." + top_line[-27:]

    # Ekranning pastki qatori
    if err:
        bottom_line = f"⚠️ {err}"
    elif just_eval and last_res is not None:
        clean_res = last_res.split("(")[0].strip()
        bottom_line = f"= {clean_res}"
    else:
        bottom_line = " "

    # Vizual ramka
    display = (
        f"╔══════════════════════════════╗\n"
        f"║    🧮 <b>AQLLI KALKULYATOR</b>     ║\n"
        f"║         <i>{mode_title}</i>         ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"<code>┌────────────────────────────┐\n"
        f"│ {top_line:<26} │\n"
        f"│                            │\n"
        f"│ {bottom_line:<26} │\n"
        f"└────────────────────────────┘</code>\n\n"
        f"💡 <i>Tugmalarni bosing yoki istalgan misolni matn sifatida yuboring!</i>"
    )
    return display


# ==========================================
# ASOSIY BUYRUQLAR (COMMANDS)
# ==========================================

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Botni ishga tushirish (/start buyrug'i)."""
    user_name = message.from_user.first_name if message.from_user else "Foydalanuvchi"

    greeting = (
        f"Assalomu alaykum, <b>{user_name}</b>! 👋\n\n"
        f"Men — <b>Aqlli Kalkulyator Botiman</b> 🧮\n"
        f"Sizga oddiy va murakkab matematik amallarni bir zumda "
        f"hisoblab berishda yordam beraman.\n\n"
        f"✨ <b>Imkoniyatlarim:</b>\n"
        f"• 📱 <b>Telegram Mini App:</b> to'liq grafikli zamonaviy kalkulyator (pastdagi tugma)\n"
        f"• 🔘 <b>Interaktiv tugmali kalkulyator</b> (quyidagi xabar ekranida)\n"
        f"• ✍️ <b>Matnli ifodalar:</b> misolni shunchaki yozib yuboring\n"
        f"• 🔬 <b>Ilmiy amallar:</b> ildiz, daraja, sin, cos, faktorial\n"
        f"• 📊 <b>Foizlar:</b> <code>200 + 15%</code> yoki <code>500 * 20%</code>\n"
        f"• 📜 <b>Hisob-kitoblar tarixi</b>\n"
        f"• 🌐 <b>Inline rejim:</b> istalgan chatda @bot_nomi orqali hisoblash"
    )

    # Doimiy menyuni yuborish
    await message.answer(greeting, reply_markup=keyboards.get_main_reply_keyboard())

    # Interaktiv inline kalkulyatorni chiqarish
    session = {"expr": "", "mode": "std", "last_result": None, "just_evaluated": False}
    display_text = render_display(session)
    calc_msg = await message.answer(
        display_text,
        reply_markup=keyboards.get_calc_inline_keyboard(mode="std"),
    )
    calc_sessions[(calc_msg.chat.id, calc_msg.message_id)] = session


@router.message(Command("calc"))
@router.message(F.text == "🧮 Kalkulyator")
async def cmd_calculator(message: Message) -> None:
    """Yangi kalkulyator oynasini ochish."""
    session = {"expr": "", "mode": "std", "last_result": None, "just_evaluated": False}
    display_text = render_display(session)
    calc_msg = await message.answer(
        display_text,
        reply_markup=keyboards.get_calc_inline_keyboard(mode="std"),
    )
    calc_sessions[(calc_msg.chat.id, calc_msg.message_id)] = session


@router.message(Command("help"))
@router.message(F.text == "💡 Yordam & Misollar")
async def cmd_help(message: Message) -> None:
    """Yordam va qo'llanma bo'limi."""
    help_text = (
        f"📖 <b>BOTDAN FOYDALANISH QO'LLANMASI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>1️⃣ Standart amallar:</b>\n"
        f"• <code>25 + 75</code> ➔ 100\n"
        f"• <code>125 * 8</code> ➔ 1000\n"
        f"• <code>(40 + 60) * 5 / 2</code> ➔ 250\n"
        f"• <code>1 000 000 + 500 000</code> ➔ 1 500 000\n\n"
        f"<b>2️⃣ Foiz hisoblash:</b>\n"
        f"• <code>200 + 15%</code> ➔ 230\n"
        f"• <code>500 - 20%</code> ➔ 400\n"
        f"• <code>1000 * 12%</code> ➔ 120\n\n"
        f"<b>3️⃣ Ilmiy va trigonometrik amallar:</b>\n"
        f"• <code>sqrt(144)</code> yoki <code>√144</code> ➔ 12 (ildiz)\n"
        f"• <code>2^10</code> ➔ 1024 (daraja)\n"
        f"• <code>5!</code> yoki <code>factorial(5)</code> ➔ 120\n"
        f"• <code>sin(30)</code> ➔ 0.5 (burchak gradusda)\n"
        f"• <code>cos(60)</code> ➔ 0.5\n"
        f"• <code>log10(1000)</code> ➔ 3\n"
        f"• <code>2pi</code> ➔ 6.28318...\n\n"
        f"<b>4️⃣ Inline qidiruv rejimi:</b>\n"
        f"Istalgan guruh yoki do'stingiz bilan yozishayotganda bot nomini "
        f"va misolni yozing (masalan: <code>@bot_username 25*4</code>), natija darhol chiqadi!\n\n"
        f"💬 <i>Savol yoki takliflar bo'lsa, bemalol murojaat qiling!</i>"
    )
    await message.answer(help_text, reply_markup=keyboards.get_main_reply_keyboard())


@router.message(Command("history"))
@router.message(F.text == "📜 Tarix")
async def cmd_history(message: Message) -> None:
    """Hisoblashlar tarixini ko'rish."""
    user_id = message.from_user.id if message.from_user else 0
    history = user_histories.get(user_id, [])

    if not history:
        await message.answer(
            "📜 <b>Hisob-kitoblar tarixi hozircha bo'sh!</b>\n\n"
            "Biror misol yuboring yoki kalkulyator tugmalaridan foydalaning.",
            reply_markup=keyboards.get_history_inline_keyboard(),
        )
        return

    lines = ["📜 <b>Sizning oxirgi hisob-kitoblaringiz:</b>\n"]
    for i, item in enumerate(history, 1):
        lines.append(
            f"{i}️⃣ [<code>{item['time']}</code>] <code>{item['expr']}</code> = <b>{item['result']}</b>"
        )

    lines.append("\n💡 <i>Tarixni tozalash uchun quyidagi tugmani bosing.</i>")
    text = "\n".join(lines)

    await message.answer(text, reply_markup=keyboards.get_history_inline_keyboard())


@router.message(Command("clear_history"))
@router.message(Command("clear"))
@router.message(F.text == "🗑 Tarixni tozalash")
async def cmd_clear_history(message: Message) -> None:
    """Tarixni tozalash."""
    user_id = message.from_user.id if message.from_user else 0
    if user_id in user_histories:
        user_histories[user_id] = []

    await message.answer(
        "🗑 <b>Hisoblashlar tarixi muvaffaqiyatli tozalandi!</b>",
        reply_markup=keyboards.get_main_reply_keyboard(),
    )


# ==========================================
# INTERAKTIV INLINE TUGMALARNI BOSHQARISH
# ==========================================

@router.callback_query(F.data.startswith("calc:"))
async def handle_calc_callback(callback: CallbackQuery) -> None:
    """Kalkulyator tugmalari bosilganda ishlovchi handler."""
    action = callback.data.split(":", 1)[1]
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    user_id = callback.from_user.id

    session = get_or_create_session(chat_id, message_id)
    session["error_msg"] = None  # Xatolikni tozalaymiz

    expr = session["expr"]
    just_eval = session.get("just_evaluated", False)
    last_res = session.get("last_result")
    mode = session.get("mode", "std")

    # 1. Rejimni almashtirish
    if action == "mode_sci":
        session["mode"] = "sci"
        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode="sci"),
        )
        await callback.answer()
        return

    elif action == "mode_std":
        session["mode"] = "std"
        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode="std"),
        )
        await callback.answer()
        return

    # 2. Tozalash (C)
    elif action == "clear":
        session["expr"] = ""
        session["last_result"] = None
        session["just_evaluated"] = False
        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
        )
        await callback.answer("Tozalandi")
        return

    # 3. Oxirgi belgini o'chirish (Backspace)
    elif action == "backspace":
        if just_eval:
            session["expr"] = ""
            session["just_evaluated"] = False
        else:
            session["expr"] = expr.rstrip()
            if session["expr"]:
                # Agar oxirgi belgi probel bilan bo'lsa (masalan " + ")
                if session["expr"].endswith((" +", " -", " *", " /")):
                    session["expr"] = session["expr"][:-2].rstrip()
                else:
                    session["expr"] = session["expr"][:-1].rstrip()

        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
        )
        await callback.answer()
        return

    # 4. Tenglik (=)
    elif action == "equal":
        if not expr.strip():
            await callback.answer("Ifoda kiritilmagan!", show_alert=False)
            return

        result, error = SafeCalculator.calculate(expr)
        if error:
            session["error_msg"] = error
            session["just_evaluated"] = False
            await callback.answer(f"⚠️ {error}", show_alert=True)
        else:
            session["last_result"] = result
            session["just_evaluated"] = True
            add_to_history(user_id, expr, result)
            await callback.answer(f"Natija: {result}")

        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
        )
        return

    # 5. Matematik funksiyalar (Ilmiy rejim)
    fn_map = {
        "fn_sqrt": "sqrt(",
        "fn_sqr": "^2",
        "fn_pow": "^",
        "fn_fact": "!",
        "fn_sin": "sin(",
        "fn_cos": "cos(",
        "fn_tan": "tan(",
        "fn_log": "log10(",
        "fn_pi": "pi",
        "fn_e": "e",
        "fn_abs": "abs(",
    }

    if action in fn_map:
        token = fn_map[action]
        if just_eval:
            if token in ("^2", "^", "!"):
                clean_res = (last_res or "0").split("(")[0].strip()
                session["expr"] = clean_res + token
            else:
                session["expr"] = token
            session["just_evaluated"] = False
        else:
            session["expr"] = expr + token

        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
        )
        await callback.answer()
        return

    # 6. Standart amallar (+, -, *, /, %)
    operators = {"+": " + ", "-": " − ", "*": " × ", "/": " ÷ ", "%": "%"}
    if action in operators:
        op_symbol = operators[action]
        if just_eval:
            clean_res = (last_res or "0").split("(")[0].strip()
            session["expr"] = clean_res + op_symbol
            session["just_evaluated"] = False
        else:
            session["expr"] = expr.rstrip() + op_symbol

        await callback.message.edit_text(
            render_display(session),
            reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
        )
        await callback.answer()
        return

    # 7. Raqamlar va boshqa belgilar (0-9, ., (, ))
    if just_eval:
        if action in ("(", ")"):
            session["expr"] = action
        else:
            session["expr"] = action
        session["just_evaluated"] = False
    else:
        session["expr"] = expr + action

    await callback.message.edit_text(
        render_display(session),
        reply_markup=keyboards.get_calc_inline_keyboard(mode=mode),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("use_res:"))
async def handle_use_result(callback: CallbackQuery) -> None:
    """Natijani yangi kalkulyator seansiga o'tkazish."""
    res_val = callback.data.split(":", 1)[1]
    session = {
        "expr": res_val,
        "mode": "std",
        "last_result": res_val,
        "just_evaluated": True,
        "error_msg": None,
    }
    calc_msg = await callback.message.answer(
        render_display(session),
        reply_markup=keyboards.get_calc_inline_keyboard(mode="std"),
    )
    calc_sessions[(calc_msg.chat.id, calc_msg.message_id)] = session
    await callback.answer("Kalkulyator ochildi!")


@router.callback_query(F.data == "new_calc")
async def handle_new_calc(callback: CallbackQuery) -> None:
    """Tugma orqali yangi kalkulyator yaratish."""
    session = {"expr": "", "mode": "std", "last_result": None, "just_evaluated": False}
    calc_msg = await callback.message.answer(
        render_display(session),
        reply_markup=keyboards.get_calc_inline_keyboard(mode="std"),
    )
    calc_sessions[(calc_msg.chat.id, calc_msg.message_id)] = session
    await callback.answer()


@router.callback_query(F.data == "view_history")
async def handle_view_history_cb(callback: CallbackQuery) -> None:
    """Inline tugma orqali tarixni ochish."""
    user_id = callback.from_user.id
    history = user_histories.get(user_id, [])
    if not history:
        await callback.answer("Tarix bo'sh!", show_alert=True)
        return

    lines = ["📜 <b>Sizning oxirgi hisob-kitoblaringiz:</b>\n"]
    for i, item in enumerate(history, 1):
        lines.append(
            f"{i}️⃣ [<code>{item['time']}</code>] <code>{item['expr']}</code> = <b>{item['result']}</b>"
        )
    text = "\n".join(lines)
    await callback.message.answer(text, reply_markup=keyboards.get_history_inline_keyboard())
    await callback.answer()


@router.callback_query(F.data == "clear_history_cb")
async def handle_clear_history_cb(callback: CallbackQuery) -> None:
    """Inline tugma orqali tarixni tozalash."""
    user_id = callback.from_user.id
    user_histories[user_id] = []
    await callback.answer("Tarix tozalandi!", show_alert=True)
    await callback.message.edit_text(
        "🗑 <b>Hisoblashlar tarixi muvaffaqiyatli tozalandi!</b>",
        reply_markup=keyboards.get_history_inline_keyboard(),
    )


# ==========================================
# TELEGRAM MINI APP (WEB APP) HANDLERI
# ==========================================

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message) -> None:
    """Telegram Mini App dan yuborilgan natijani qabul qilish."""
    user_id = message.from_user.id if message.from_user else 0
    raw_data = message.web_app_data.data

    try:
        data = json.loads(raw_data)
        expr = data.get("expression", "")
        res = data.get("result", "")
    except Exception:
        expr = "Mini App ifodasi"
        res = raw_data

    # Tarixga qo'shish
    if expr and res:
        add_to_history(user_id, expr, str(res))

    result_box = (
        f"╔══════════════════════════════╗\n"
        f"║   📱 <b>MINI APP HISOBLASH NATIJASI</b>   ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"📝 <b>Ifoda:</b>  <code>{expr}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Natija:</b> <b>{res}</b>\n\n"
        f"✨ <i>Natija to'g'ridan-to'g'ri Telegram Mini App ekranidan uzatildi va tarixga saqlandi!</i>"
    )

    await message.reply(
        result_box,
        reply_markup=keyboards.get_result_inline_keyboard(str(res)),
    )


# ==========================================
# FOYDALANUVCHIDAN KELGAN MATNLARNI HISOBLASH
# ==========================================

@router.message(F.text)
async def handle_text_expression(message: Message) -> None:
    """
    Foydalanuvchi to'g'ridan-to'g'ri yozgan matnli ifodani hisoblash.
    """
    text = message.text.strip()
    user_id = message.from_user.id if message.from_user else 0

    # Matematik belgilar yoki raqamlar borligini tekshirish
    has_math = any(ch in text for ch in "+-*/×÷^%=!√") or re.search(
        r"\b(sqrt|cbrt|sin|cos|tan|log|pi|e|factorial)\b", text, re.IGNORECASE
    )
    has_digit = any(ch.isdigit() for ch in text)

    if not (has_math and has_digit):
        # Agar oddiy matn bo'lsa
        await message.answer(
            "👋 <b>Matematik ifodani yozing</b> yoki pastdagi <b>«🧮 Kalkulyator»</b> tugmasidan foydalaning!\n\n"
            "Misollar:\n"
            "• <code>25 * 4 + 150</code>\n"
            "• <code>200 + 15%</code>\n"
            "• <code>sqrt(64) + 2^8</code>",
            reply_markup=keyboards.get_main_reply_keyboard(),
        )
        return

    result, error = SafeCalculator.calculate(text)

    if error:
        error_box = (
            f"╔══════════════════════════════╗\n"
            f"║      ⚠️ <b>HISOBLASHDA XATOLIK</b>     ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"📝 <b>Kiritilgan ifoda:</b> <code>{text}</code>\n"
            f"❌ <b>Sabab:</b> {error}\n\n"
            f"💡 <i>Iltimos, ifodani to'g'ri yozilganligini tekshirib qaytadan yuboring.</i>"
        )
        await message.reply(error_box, reply_markup=keyboards.get_main_reply_keyboard())
        return

    # Muvaffaqiyatli hisoblandi
    add_to_history(user_id, text, result)

    result_box = (
        f"╔══════════════════════════════╗\n"
        f"║     📊 <b>HISOBLASH NATIJASI</b>     ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"📝 <b>Ifoda:</b>  <code>{text}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>Natija:</b> <b>{result}</b>\n\n"
        f"💡 <i>Natija ustida davom etish uchun quyidagi tugmani bosing:</i>"
    )

    await message.reply(
        result_box,
        reply_markup=keyboards.get_result_inline_keyboard(result),
    )


# ==========================================
# INLINE REJIM (Boshqa chatlarda hisoblash)
# ==========================================

@router.inline_query()
async def inline_calc_handler(inline_query: InlineQuery) -> None:
    """Istalgan chatda @bot_username misol shaklida hisoblash."""
    query = inline_query.query.strip()
    if not query:
        return

    result, error = SafeCalculator.calculate(query)

    if error:
        item = InlineQueryResultArticle(
            id="error",
            title=f"Xatolik: {error}",
            description=f"Ifoda: {query}",
            input_message_content=InputTextMessageContent(
                message_text=f"⚠️ Ifodada xato: <code>{query}</code>\nSabab: {error}"
            ),
        )
    else:
        item = InlineQueryResultArticle(
            id="result",
            title=f"= {result}",
            description=f"Ifoda: {query}",
            input_message_content=InputTextMessageContent(
                message_text=(
                    f"🧮 <b>Hisoblash:</b> <code>{query}</code>\n"
                    f"🎯 <b>Natija:</b> <b>{result}</b>"
                )
            ),
        )

    await inline_query.answer([item], cache_time=1)
