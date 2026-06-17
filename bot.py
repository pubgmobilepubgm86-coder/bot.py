import os
import asyncio
import threading
import sqlite3
import random
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# ==========================================
# ⚙️ 1. ASOSIY SOZLAMALAR VA BAZA
# ==========================================
BOT_TOKEN = "8897921742:AAHX0mQ6iNYjQAiJwmVdEEvgEovfrJtox0Q"
ADMIN_ID = 8086545587  # Xo'jayin ID si

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def init_db():
    """Ma'lumotlar bazasini yangilash va foydalanuvchilarni saqlash tizimi"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            status TEXT,
            luck_level REAL DEFAULT 91.2,
            signal_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 🧠 2. HOLATLAR XOTIRASI (FSM)
# ==========================================
class UserState(StatesGroup):
    waiting_for_photo = State()

class AdminState(StatesGroup):
    waiting_for_description = State()

# ==========================================
# 🎛 3. PREMIUM MENULAR VA TUGMALAR
# ==========================================
# Oddiy foydalanuvchi menyusi
register_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎰 1xBet")]],
    resize_keyboard=True,
    input_field_placeholder="Bukmekerlik idorasini tanlang..."
)

# Tasdiqlangan VIP foydalanuvchi menyusi
main_vip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡️ Signal olish")],
        [KeyboardButton(text="🍀 Omad darajasi")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Kerakli bo'limni tanlang..."
)

# O'yinlar menyusi
apple_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍎 APPLE OF FORTUNE 🍏 UCHUN")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True,
    input_field_placeholder="O'yin panelini tanlang!"
)

# Maxfiy "Dark World" menyusi
dark_world_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌌 Dark World")],
        [KeyboardButton(text="🔙 Asosiy menyuga qaytish")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Maxfiy tizim faollashtirildi..."
)

# Admin inline boshqaruv tugmalari
class AdminAction(CallbackData, prefix="admin"):
    action: str
    user_id: int

def admin_inline_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=AdminAction(action="accept", user_id=user_id).pack()),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=AdminAction(action="reject", user_id=user_id).pack())
            ]
        ]
    )

# ==========================================
# 👤 4. FOYDALANUVCHI REJIMLARI VA MANTIQ
# ==========================================

# MAXFIY PAROL TIZIMI (262626121212 kiritilganda mutloq boshqa menu ochiladi)
@dp.message(F.text == "262626121212")
async def secret_dark_world(message: Message):
    try:
        await message.delete()  # Maxfiy parol ekranda qolib ketmasligi uchun o'chiriladi
    except:
        pass
    text = (
        "🚨 <b>TIZIM BUZIB KIRILDI (ACCESS GRANTED)</b> 🚨\n\n"
        "🔒 <i>Siz avvalgi menyularga aloqador bo'lmagan mutloq boshqa maxfiy dunyoga kirdingiz.</i>\n"
        "Quyidagi paneldan foydalanishingiz mumkin 👇"
    )
    await message.answer(text, reply_markup=dark_world_menu)

@dp.message(F.text == "🌌 Dark World")
async def dark_world_action(message: Message):
    await message.answer("💀 <b>Welcome to the Dark World.</b>\n<i>Bu yerda maxfiy skriptlar va yopiq algoritm panellari joylashgan.</i>")

@dp.message(F.text == "🔙 Asosiy menyuga qaytish")
async def back_from_dark(message: Message):
    await message.answer("Tizim tiklanmoqda...", reply_markup=ReplyKeyboardRemove())
    await cmd_start(message)

# Standart /start buyrug'i
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        text = "👋 <b>Siz tizimdan muvaffaqiyatli roʻyxatdan oʻtgansiz!</b>\n\n⚡️ Quyidagi menyudan foydalanib premium signallarni olishingiz mumkin:"
        await message.answer(text, reply_markup=main_vip_menu)
    else:
        text = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "🎯 <i>Ultimate Premium signallar</i> rasmiy botiga xush kelibsiz.\n"
            "Davom etish uchun pastdagi menyudan oʻzingizga kerakli platformani tanlang 👇"
        )
        await message.answer(text, reply_markup=register_menu)

@dp.message(F.text == "🎰 1xBet")
async def choose_kantora(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        await message.answer("Siz allaqachon roʻyxatdan oʻtgansiz!", reply_markup=main_vip_menu)
        return

    text = (
        "⚠️ <b>DIQQAT – TASDIQLASH JARAYONI!</b>\n\n"
        "📸 Iltimos, faqat <b>ID raqamingiz aniq koʻringan</b> skrinshotni (rasm formatida) yuboring.\n"
        "<i>Boshqa turdagi yoki notoʻgʻri rasmlar tizim tomonidan avtomatik ravishda rad etiladi.</i>\n\n"
        "🚨 <b>MUHIM:</b> Botni aslo bloklamang! Aks holda ID tasdiqlangan taqdirda ham "
        "maxsus signallarni qabul qila olmaysiz."
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.waiting_for_photo)

@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    
    admin_text = (
        "🛡 <b>YANGI TASDIQLASH SOʻROVI</b>\n\n"
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        "<i>Foydalanuvchining soʻrovini tasdiqlaysizmi? 👇</i>"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    await message.answer("⏳ <i>Maʼlumotlar adminga yuborildi. Iltimos, tasdiqlanishini kuting...</i>", reply_markup=ReplyKeyboardRemove())
    await state.clear() 

@dp.message(F.text == "🍀 Omad darajasi")
async def check_luck(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT luck_level FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        luck = round(row[0], 1)
        await message.answer(f"📊 <b>Sizning ayni vaqtdagi omad darajangiz:</b> <code>{luck}%</code>")
    else:
        await message.answer("❌ Siz hali tasdiqdan oʻtmagansiz. Iltimos, avval roʻyxatdan oʻting.")

@dp.message(F.text == "⚡️ Signal olish")
async def process_signal_olish(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        await message.answer("🚀 Oʻyinlar paneli muvaffaqiyatli faollashdi. Tanlang 👇", reply_markup=apple_menu)
    else:
        await message.answer("❌ Bu boʻlim faqat tasdiqlangan VIP aʼzolar uchun moʻljallangan!")

@dp.message(F.text == "⬅️ Orqaga")
async def process_back(message: Message):
    await message.answer("Bosh menyu 👇", reply_markup=main_vip_menu)

# 🍎 APPLE OF FORTUNE SIGNAL GENERATOR (JONLI KOSMIK ANIMATSIYA)
@dp.message(F.text == "🍎 APPLE OF FORTUNE 🍏 UCHUN")
async def process_apple_fortune(message: Message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status, luck_level, signal_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row or row[0] != "approved":
        conn.close()
        await message.answer("❌ Kirish taqiqlangan!")
        return
        
    current_luck = row[1]
    current_signals = row[2]
    
    # 🚨 65% CHEKLOVI
    if current_luck <= 65.0:
        conn.close()
        await message.answer("⚠️ <b>Kechirasiz, sizga signal bera olmayman. Iltimos, kesh (cache) holatini tozalang!</b>")
        return

    # ⏳ SIFATLI VA JONLI LOADING EFFEKTI
    loading_msg = await message.answer("📡 <code>[◽️◽️◽️◽️◽️◽️◽️◽️◽️◽️] 0% Serverga ulanish...</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("⚡️ <code>[==◽️◽️◽️◽️◽️◽️◽️◽️] 25% Algoritm kesh xotirasi tekshirilmoqda...</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("🌀 <code>[====◽️◽️◽️◽️◽️◽️] 50% Yoʻlaklar matritsasi skanerlanmoqda...</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("🔮 <code>[======◽️◽️◽️◽️] 75% Omad koeffitsiyenti sinxronizatsiya qilinmoqda...</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("🚀 <code>[========] 100% Signal muvaffaqiyatli generatsiya qilindi!</code>")
    await asyncio.sleep(0.2)

    # 🎲 RANDOM RAQAM BALANSI (1-5 oralig'ida: 2, 4, 5 ustunroq, lekin muvozanatli)
    # Og'irliklarni muvozanatga keltirdik: 1(14%), 2(25%), 3(14%), 4(23%), 5(24%)
    numbers = [1, 2, 3, 4, 5]
    weights = [14, 25, 14, 23, 24]
    chosen_num = random.choices(numbers, weights=weights)[0]
    
    # Omadni 1% yoki 2% oralig'ida kamaytirish
    minus_luck = random.uniform(1.0, 2.0)
    new_luck = max(64.0, current_luck - minus_luck)
    new_signal_count = current_signals + 1
    
    cursor.execute("UPDATE users SET luck_level = ?, signal_count = ? WHERE user_id = ?", (new_luck, new_signal_count, user_id))
    conn.commit()
    conn.close()
    
    result_text = (
        "🍏 <b>APPLE OF FORTUNE DASTURI</b> 🍎\n\n"
        f"🎯 <b>Tavsiya etilgan yoʻlak:</b> <code>{chosen_num}</code>\n"
        f"📊 Yangi omad darajangiz: <code>{round(new_luck, 1)}%</code>"
    )
    
    # ⚠️ 3 TA RAQAMDAN SO'NG OGOHLANTIRISH
    if new_signal_count % 3 == 0:
        result_text += "\n\n⚠️ <b>Bu yoʻlakda omad foizingiz juda past! Iltimos, yutuqni oling yoki ehtiyotkorlik bilan davom eting.</b>"
        
    await loading_msg.edit_text(result_text)

@dp.message(StateFilter(UserState.waiting_for_photo))
async def handle_not_photo(message: Message):
    await message.answer("❌ <b>Xatolik!</b>\nIltimos, faqat rasm (skrinshot) formatida fayl yuboring.")

# ==========================================
# 👑 5. ADMIN PANELI (BOSHQARUV)
# ==========================================

@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject(callback: CallbackQuery, callback_data: AdminAction):
    target_user_id = callback_data.user_id
    try:
        reject_text = (
            "❌ <b>Sizning soʻrovingiz tasdiqlanmadi!</b>\n\n"
            "Iltimos, toʻgʻri koʻrsatilgan <b>1xBet ID</b> rasmini qoidalarga muvofiq qaytadan yuboring."
        )
        await bot.send_message(chat_id=target_user_id, text=reject_text)
        await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} rad etildi. ❌")
    except Exception:
        await callback.answer("⚠️ Mijoz botni bloklagan!", show_alert=True)
    await callback.answer()

@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    target_user_id = callback_data.user_id
    
    await callback.message.answer(f"✅ <b>Qabul qilindi!</b>\nFoydalanuvchi: <code>{target_user_id}</code>\n\n📝 <i>Mijozga yuboriladigan maxsus tavsifni kiriting:</i>")
    await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} qabul qilindi. Tavsif kutilmoqda... ✅")
    
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user_id=target_user_id)
    await callback.answer()

@dp.message(StateFilter(AdminState.waiting_for_description))
async def handle_admin_description(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, status, luck_level, signal_count)
        VALUES (?, 'approved', 91.2, 0)
    """, (target_user_id,))
    conn.commit()
    conn.close()
    
    user_text = (
        "🎉 <b>TABRIKLAYMIZ!</b>\n"
        "Sizning ID raqamingiz muvaffaqiyatli ulandi va tizimda tasdiqlandi.\n\n"
        "💡 <b>Admin eslatmasi:</b>\n"
        f"<i>{message.text}</i>\n\n"
        "👇 <b>Signal olish uchun pastdagi tugmani bosing!</b>"
    )
    try:
        await bot.send_message(chat_id=target_user_id, text=user_text, reply_markup=main_vip_menu)
        await message.answer("✅ Mijoz bazaga qoʻshildi va unga VIP menyu yuborildi!")
    except Exception:
        await message.answer("❌ Xatolik: Foydalanuvchi botni bloklagan.")
    await state.clear()

# ==========================================
# 🌐 6. FLASK SERVER (24/7 RENDER HOSTING)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Tizim barqaror holatda ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 🏁 7. LOYIHANI ISHGA TUSHIRISH
# ==========================================
async def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("🚀 Barcha oʻzgarishlar va maxfiy funksiyalar yuklandi. Bot faol!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
