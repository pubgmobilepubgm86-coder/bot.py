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
    """Ma'lumotlar bazasini yaratish va foydalanuvchilarni eslab qolish tizimi"""
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

# Baza jadvalini darhol ishga tushiramiz
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
# Tasdiqlanmagan odam ko'radigan menu
register_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎰 1 x bet")]],
    resize_keyboard=True,
    input_field_placeholder="Kantorani tanlang..."
)

# Tasdiqlangan (VIP) foydalanuvchi ko'radigan doimiy menu
main_vip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡️ Signal olish")],
        [KeyboardButton(text="🍀 Omad darajasi")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Kerakli bo'limni tanlang..."
)

# O'yin menyusi
apple_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍎 APPLE OF FORTUNE 🍏 UCHUN")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True,
    input_field_placeholder="O'yinni tanlang!"
)

# Admin inline tugmalari
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
# 👤 4. FOYDALANUVCHI BO'LIMI (MIJOZ LOGIKASI)
# ==========================================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Bazadan tekshiramiz
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        # Agar oldin tasdiqlangan bo'lsa, to'g'ridan-to'g'ri VIP menuga
        text = "👋 <b>Siz tizimdan muvaffaqiyatli o'tgansiz!</b>\n\n⚡️ Quyidagi menyudan foydalanib signallar olishingiz mumkin:"
        await message.answer(text, reply_markup=main_vip_menu)
    else:
        # Ro'yxatdan o'tmagan bo'lsa
        text = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "🎯 <i>Ultimate Premium signallar</i> botiga xush kelibsiz.\n"
            "Davom etish uchun pastdagi menyudan o'zingizga kerakli kantorani tanlang 👇"
        )
        await message.answer(text, reply_markup=register_menu)

@dp.message(F.text == "🎰 1 x bet")
async def choose_kantora(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz!", reply_markup=main_vip_menu)
        return

    text = (
        "⚠️ <b>DIQQAT - TASDIQLASH JARAYONI!</b>\n\n"
        "📸 Iltimos, faqat <b>ID raqamingiz koʻringan</b> qismni screenshot (rasm) qilib yuboring.\n"
        "<i>Boshqa turdagi yoki noto'g'ri rasmlar tizim tomonidan avtomatik rad etiladi.</i>\n\n"
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
        "🛡 <b>YANGI TASDIQLASH SO'ROVI</b>\n\n"
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        "<i>Qabul qilasizmi yoki rad etasizmi? 👇</i>"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    await message.answer("⏳ <i>Ma'lumotlar adminga yuborildi. Iltimos, tasdiqlanishini kuting...</i>", reply_markup=ReplyKeyboardRemove())
    await state.clear() 

# 🍀 OMAD DARAJASI TUGMASI
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
        await message.answer("❌ Siz hali tasdiqdan o'tmagansiz. Iltimos, avval ro'yxatdan o'ting.")

# ⚡️ SIGNAL OLISH BOSILGANDA
@dp.message(F.text == "⚡️ Signal olish")
async def process_signal_olish(message: Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == "approved":
        await message.answer("🚀 O'yinlar paneli faollashdi. Tanlang 👇", reply_markup=apple_menu)
    else:
        await message.answer("❌ Bu bo'lim faqat tasdiqlangan VIP a'zolar uchun!")

@dp.message(F.text == "⬅️ Orqaga")
async def process_back(message: Message):
    await message.answer("Bosh menyu 👇", reply_markup=main_vip_menu)

# 🍎 APPLE OF FORTUNE SIGNAL GENERATOR (HAQIQIY PRO LOGIKA)
@dp.message(F.text == "🍎 APPLE OF FORTUNE 🍏 UCHUN")
async def process_apple_fortune(message: Message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status, luck_level, signal_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row or row[0] != "approved":
        conn.close()
        await message.answer("❌ Ruxsat berilmagan!")
        return
        
    current_luck = row[1]
    current_signals = row[2]
    
    # 🚨 65% CHEKLOVI
    if current_luck <= 65.0:
        conn.close()
        await message.answer("⚠️ Kechrasiz sizga signala bera olmayman iltimos kesh holatini tozalang")
        return

    # ⏳ JONLI ANIMATSIYA (LOADING EFFECT)
    loading_msg = await message.answer("🔄 <code>Signala olinmoqda kuting</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("🔄 <code>Signala olinmoqda kuting.</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("🔄 <code>Signala olinmoqda kuting..</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("🔄 <code>Signala olinmoqda kuting...</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("🛰 <code>Xavfsiz algoritm yuklanmoqda...</code>")
    await asyncio.sleep(0.4)

    # 🎲 RANDOM RAQAM (2, 4, 5 ko'p chiqadigan og'irlik tizimi)
    # 1 va 3 ga 10% dan imkoniyat, 2 ga 30%, 4 va 5 ga 25% dan imkoniyat beramiz
    numbers = [1, 2, 3, 4, 5]
    weights = [10, 30, 10, 25, 25]
    chosen_num = random.choices(numbers, weights=weights)[0]
    
    # Omad darajasini 1% yoki 2% random tarzda kamaytirish (Masalan: 1.2% yoki 1.7%)
    minus_luck = random.uniform(1.0, 2.0)
    new_luck = max(64.0, current_luck - minus_luck) # 64 dan pastga tushib ketmasligi uchun
    new_signal_count = current_signals + 1
    
    # Bazani yangilaymiz
    cursor.execute("UPDATE users SET luck_level = ?, signal_count = ? WHERE user_id = ?", (new_luck, new_signal_count, user_id))
    conn.commit()
    conn.close()
    
    # Natija xabari
    result_text = f"🍏 <b>APPLE OF FORTUNE</b> 🍎\n\n🎯 <b>Tavsiya etilgan yo'lak:</b> <code>{chosen_num}</code>\n📊 Yangi omad darajangiz: <code>{round(new_luck, 1)}%</code>"
    
    # ⚠️ 3 TA RAQAMDAN SO'NG OGOHLANTIRISH
    if new_signal_count % 3 == 0:
        result_text += "\n\n⚠️ <b>Bu yoʻliga omad foizingiz juda kam iltimoss yutuqni oling yoki davom eting!</b>"
        
    await loading_msg.edit_text(result_text)

@dp.message(StateFilter(UserState.waiting_for_photo))
async def handle_not_photo(message: Message):
    await message.answer("❌ <b>Xatolik!</b>\nIltimos, faqat rasm (screenshot) formatida fayl yuboring.")

# ==========================================
# 👑 5. ADMIN BO'LIMI (BOSHQARUV)
# ==========================================

@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject(callback: CallbackQuery, callback_data: AdminAction):
    target_user_id = callback_data.user_id
    try:
        reject_text = (
            "❌ <b>Tasdiqlanmadi!</b>\n\n"
            "Iltimos, toʻgʻri ko'rsatilgan <b>1 x bet ID</b> rasmini qoidalarga muvofiq qayta yuboring."
        )
        await bot.send_message(chat_id=target_user_id, text=reject_text)
        await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} rad etildi. ❌")
    except Exception:
        await callback.answer("⚠️ Mijoz botni bloklagan!", show_alert=True)
    await callback.answer()

@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    target_user_id = callback_data.user_id
    
    await callback.message.answer(f"✅ <b>Qabul qilindi!</b>\nFoydalanuvchi: <code>{target_user_id}</code>\n\n📝 <i>Endi unga yuboriladigan maxsus tavsifni yozib yuboring:</i>")
    await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} qabul qilindi. Tavsif kutilmoqda... ✅")
    
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user_id=target_user_id)
    await callback.answer()

@dp.message(StateFilter(AdminState.waiting_for_description))
async def handle_admin_description(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    # Foydalanuvchini bazaga 'approved' (tasdiqlangan) deb yozamiz
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
        "Sizning ID raqamingiz muvaffaqiyatli ulandi va tasdiqdan o'tdi.\n\n"
        "💡 <b>Admin xabari:</b>\n"
        f"<i>{message.text}</i>\n\n"
        "👇 <b>Signal olish uchun pastdagi tugmani bosing!</b>"
    )
    try:
        # Tasdiqlangan odamga yangi VIP menu yuboriladi
        await bot.send_message(chat_id=target_user_id, text=user_text, reply_markup=main_vip_menu)
        await message.answer("✅ Mijoz bazaga qo'shildi va unga VIP menyu yuborildi!")
    except Exception:
        await message.answer("❌ Xatolik: Foydalanuvchi botni bloklagan.")
    await state.clear()

# ==========================================
# 🌐 6. FLASK SERVER (24/7 ISHLASHI UCHUN)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Ultimate Premium Bot faol holatda ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 🏁 7. BOTNI ISHGA TUSHIRISH (MAIN)
# ==========================================
async def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("🚀 Premium bot barcha yangi funksiyalari bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

