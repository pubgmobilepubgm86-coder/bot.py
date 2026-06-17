import os
import asyncio
import threading
import sqlite3
import random
import logging
from datetime import datetime
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramForbiddenError

# ==========================================
# ⚙️ 1. SOZLAMALAR VA KONFIGURATSIYA
# ==========================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BOT_TOKEN = "8897921742:AAESAkH-sCZB_TairPZDK3B_3_KiGKavDYU"
ADMIN_ID = 8086545587 

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ==========================================
# 🗄 2. MA'LUMOTLAR BAZASI (OOP ARCHITECTURE)
# ==========================================
class Database:
    def __init__(self, db_name="premium_bot.db"):
        self.db_name = db_name
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    luck_level REAL DEFAULT 91.2,
                    signal_count INTEGER DEFAULT 0,
                    last_golden_date TEXT DEFAULT '2000-01-01',
                    is_dark_mode INTEGER DEFAULT 0,
                    join_date TEXT
                )
            """)
            conn.commit()

    def get_user(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def add_user(self, user_id, status='pending'):
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, status, join_date)
                VALUES (?, ?, ?)
            """, (user_id, status, join_date))
            conn.commit()

    def update_status(self, user_id, status):
        with self._connect() as conn:
            conn.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
            conn.commit()

    def update_luck_and_signals(self, user_id, new_luck, new_signals):
        with self._connect() as conn:
            conn.execute("UPDATE users SET luck_level = ?, signal_count = ? WHERE user_id = ?", (new_luck, new_signals, user_id))
            conn.commit()

    def update_golden_date(self, user_id, date_str):
        with self._connect() as conn:
            conn.execute("UPDATE users SET last_golden_date = ? WHERE user_id = ?", (date_str, user_id))
            conn.commit()

    def set_dark_mode(self, user_id, mode: int):
        with self._connect() as conn:
            conn.execute("UPDATE users SET is_dark_mode = ? WHERE user_id = ?", (mode, user_id))
            conn.commit()

    def get_stats(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'approved'")
            vips = cursor.fetchone()[0]
            return total, vips

    def get_all_users(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]

db = Database()

# ==========================================
# 🧠 3. HOLATLAR VA CALLBACK'LAR (FSM)
# ==========================================
class UserState(StatesGroup):
    waiting_for_photo = State()

class AdminState(StatesGroup):
    waiting_for_description = State()
    waiting_for_broadcast = State()

class AdminAction(CallbackData, prefix="admin"):
    action: str
    user_id: int

# ==========================================
# 🎛 4. PREMIUM KLAVIATURALAR (UI/UX)
# ==========================================
register_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎰 1xBet Platformasi")]],
    resize_keyboard=True,
    input_field_placeholder="Bukmekerni tanlang..."
)

main_vip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡️ Signal olish")],
        [KeyboardButton(text="👤 Mening Profilim"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🍀 Omad darajasi")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Premium panel faol..."
)

apple_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍎 APPLE OF FORTUNE 🍏")],
        [KeyboardButton(text="🔙 Asosiy menyuga qaytish")]
    ],
    resize_keyboard=True
)

dark_world_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏆 Kunlik Oltin Signal")],
        [KeyboardButton(text="💀 Terminalni o'qish")],
        [KeyboardButton(text="🚪 Dark World'dan chiqish")]
    ],
    resize_keyboard=True,
    input_field_placeholder="root@dark_world:~#"
)

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
# 👤 5. ASOSIY FOYDALANUVCHI MANTIQ (CORE LOGIC)
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    db.add_user(user_id)
    user = db.get_user(user_id)
    
    if user[1] == "approved":
        if user[5] == 1: # Agar Dark Mode qolib ketgan bo'lsa
            db.set_dark_mode(user_id, 0)
        text = (
            "💎 <b>ULTIMATE PREMIUM BOT</b> 💎\n\n"
            "👋 Xush kelibsiz, VIP a'zo!\n"
            "<blockquote>Tizim barqaror ishlamoqda. Signallar olish uchun kerakli bo'limni tanlang.</blockquote>"
        )
        await message.answer(text, reply_markup=main_vip_menu)
    else:
        text = (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "🛡 <i>Ushbu bot yopiq turdagi premium signallar markazi hisoblanadi.</i>\n"
            "Davom etish uchun pastdagi tugma orqali platformani tanlang 👇"
        )
        await message.answer(text, reply_markup=register_menu)

@dp.message(F.text == "🎰 1xBet Platformasi")
async def register_step(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer("✅ Siz allaqachon VIP a'zosiz!", reply_markup=main_vip_menu)
        return

    text = (
        "⚠️ <b>VERIFIKATSIYA JARAYONI</b>\n\n"
        "📸 Iltimos, <b>1xBet ID raqamingiz</b> aniq ko'ringan profil skrinshotini yuboring.\n\n"
        "<i>Qat'iy qoida: Rasm sifatsiz yoki boshqa narsa bo'lsa, avtomatik rad etiladi.</i>"
    )
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.waiting_for_photo)

@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    
    admin_text = (
        "🛡 <b>YANGI VERIFIKATSIYA SO'ROVI</b>\n\n"
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    await message.answer("⏳ <i>Ma'lumotlar shifrlangan holda adminga yuborildi. Tasdiqni kuting...</i>", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message(StateFilter(UserState.waiting_for_photo))
async def handle_not_photo(message: Message):
    await message.answer("❌ <b>Tizim xatoligi!</b>\nFaqat rasm formatidagi fayl yuklang.")

# ==========================================
# 📱 6. PREMIUM MENU FUNKSIYALARI
# ==========================================
@dp.message(F.text == "👤 Mening Profilim")
async def profile_menu(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[1] != "approved":
        return
    
    text = (
        "🪪 <b>VIP FOYDALANUVCHI PROFILI</b>\n\n"
        f"👤 <b>Ism:</b> {message.from_user.full_name}\n"
        f"🆔 <b>Tizim ID:</b> <code>{user[0]}</code>\n"
        f"👑 <b>Status:</b> Premium A'zo ✅\n"
        f"🎯 <b>Olingan signallar:</b> {user[3]} ta\n"
        f"🍀 <b>Omad darajasi:</b> {round(user[2], 1)}%\n"
        f"📅 <b>Ulanish sanasi:</b> {user[6]}\n"
    )
    await message.answer(text)

@dp.message(F.text == "📊 Statistika")
async def stats_menu(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[1] != "approved": return
    
    total, vips = db.get_stats()
    text = (
        "📊 <b>LOYIHA STATISTIKASI</b>\n\n"
        f"👥 <b>Umumiy a'zolar:</b> {total} ta\n"
        f"💎 <b>VIP foydalanuvchilar:</b> {vips} ta\n"
        f"⚙️ <b>Server holati:</b> Barqaror (Ping: 12ms)\n\n"
        "<i>Tizim xakerlik hujumlaridan 100% himoyalangan.</i>"
    )
    await message.answer(text)

@dp.message(F.text == "🍀 Omad darajasi")
async def luck_menu(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer(f"📈 <b>Sizning ayni vaqtdagi omad darajangiz:</b> <code>{round(user[2], 1)}%</code>")

@dp.message(F.text == "⚡️ Signal olish")
async def process_signal(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer("🚀 <b>O'yinlar serveri faollashdi.</b>", reply_markup=apple_menu)

@dp.message(F.text == "🔙 Asosiy menyuga qaytish")
async def process_back(message: Message):
    await message.answer("Bosh menyuga qaytildi 👇", reply_markup=main_vip_menu)

# ==========================================
# 🍏 7. APPLE OF FORTUNE ALGORITMI
# ==========================================
@dp.message(F.text == "🍎 APPLE OF FORTUNE 🍏")
async def apple_fortune_game(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user[1] != "approved": return
    
    current_luck, current_signals = user[2], user[3]
    
    if current_luck <= 65.0:
        await message.answer("⚠️ <b>Kritik xatolik!</b>\nOmad ko'rsatkichi 65% dan past. Iltimos, o'yinni to'xtating va keshni tozalang.")
        return

    # Ultra animatsiya
    loading_msg = await message.answer("📡 <code>Serverga to'g'ridan-to'g'ri ulanish... [■□□□□□□□□□] 10%</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("⚡️ <code>Kesh ma'lumotlari tahlili... [■■■■□□□□□□] 40%</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("🌀 <code>Yo'laklar matritsasi yechilmoqda... [■■■■■■■□□□] 75%</code>")
    await asyncio.sleep(0.3)
    await loading_msg.edit_text("🚀 <code>Algoritm tayyor! [■■■■■■■■■■] 100%</code>")
    await asyncio.sleep(0.2)

    # Matematik og'irlik: 2, 4, 5 ko'p chiqadi
    chosen_num = random.choices([1, 2, 3, 4, 5], weights=[14, 25, 14, 23, 24])[0]
    minus_luck = random.uniform(1.0, 2.0)
    new_luck = max(64.0, current_luck - minus_luck)
    new_signals = current_signals + 1
    
    db.update_luck_and_signals(user_id, new_luck, new_signals)
    
    result = (
        "🍏 <b>APPLE OF FORTUNE GENERATORI</b> 🍎\n\n"
        f"🎯 <b>Xavfsiz yo'lak:</b> <code>[{chosen_num}]</code>\n"
        f"📊 <b>Yangi omad darajasi:</b> <code>{round(new_luck, 1)}%</code>"
    )
    
    if new_signals % 3 == 0:
        result += "\n\n<blockquote>⚠️ <b>Diqqat!</b> Bu yo'lakda omad foizi keskin tushdi. Yutuqni olishingiz qat'iy tavsiya etiladi!</blockquote>"
        
    await loading_msg.edit_text(result)

# ==========================================
# 🌌 8. DARK WORLD (XAKERLIK REJIMI)
# ==========================================
@dp.message(F.text == "262626121212")
async def enter_dark_world(message: Message):
    try: await message.delete() 
    except: pass
    
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user and user[1] == "approved":
        db.set_dark_mode(user_id, 1) # Dark modeni yoqish
        text = (
            "🚨 <b>SYSTEM OVERRIDE: ACCESS GRANTED</b> 🚨\n\n"
            "🔒 <i>Siz yashirin xakerlik qatlamiga kirdingiz.</i>\n"
            "Bu yerdagi signallar kuniga faqat 1 marta ishlaydi va aniqligi 99.9%."
        )
        await message.answer(text, reply_markup=dark_world_menu)

@dp.message(F.text == "💀 Terminalni o'qish")
async def fake_terminal(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[5] == 1:
        await message.answer("<code>root@server:~# ping 1xbet.com...\n64 bytes from 104.18.23.11: icmp_seq=1 ttl=56 time=1.2ms\n[OK] Port 80 is OPEN. Injection ready.</code>")

@dp.message(F.text == "🚪 Dark World'dan chiqish")
async def exit_dark_world(message: Message):
    db.set_dark_mode(message.from_user.id, 0)
    await message.answer("Standart rejimga qaytish...", reply_markup=main_vip_menu)

# QAT'IY KUNLIK CHEKLOV (1 KUNDA 1 MARTA)
@dp.message(F.text == "🏆 Kunlik Oltin Signal")
async def golden_signal(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if not user or user[5] != 1: return # Faqat Dark World ichida ishlaydi
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_date = user[4]
    
    if last_date == today_str:
        await message.answer(
            "🛑 <b>RUXSAT ETILMAYDI!</b>\n"
            "Siz bugungi shifrlangan Oltin Signalni allaqachon qabul qilgansiz.\n"
            "<i>Ushbu algoritm faqat ertaga qayta tiklanadi. Qayta urinish xavfsizlik tizimini bloklaydi.</i>"
        )
        return

    # Yuklanish effekti
    loading_msg = await message.answer("🔓 <code>[MAIN_FRAME]: Shifrlangan kanal ochilmoqda...</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("☣️ <code>[BYPASSING]: Anti-cheat himoya chetlab o'tilmoqda...</code>")
    await asyncio.sleep(0.4)
    await loading_msg.edit_text("🎯 <code>[SUCCESS]: Bugungi oltin matritsa yuklandi!</code>")
    await asyncio.sleep(0.3)

    db.update_golden_date(user_id, today_str) # BAZAGA BUGUNGI SANANI YOZISH

    step1 = random.choices([1,2,3,4,5], [14,25,14,23,24])[0]
    step2 = random.choices([1,2,3,4,5], [14,25,14,23,24])[0]
    step3 = random.choices([1,2,3,4,5], [14,25,14,23,24])[0]

    golden_text = (
        "🏆 <b>KUNLIK PREMIUM OLTIN SIGNAL</b> 🏆\n"
        "🎯 <i>Maksimal aniqlik darajasi: 99.9%</i>\n\n"
        f"1️⃣ <b>1-bosqich:</b> <code>[{step1}]</code>\n"
        f"2️⃣ <b>2-bosqich:</b> <code>[{step2}]</code>\n"
        f"3️⃣ <b>3-bosqich:</b> <code>[{step3}]</code>\n\n"
        "<blockquote>🚨 ESLATMA: Bu kombinatsiya bugun boshqa ochilmaydi!</blockquote>"
    )
    await loading_msg.edit_text(golden_text)

# ==========================================
# 👑 9. ADMIN PANEL VA BOSHQARUV
# ==========================================
@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject(callback: CallbackQuery, callback_data: AdminAction):
    target_user = callback_data.user_id
    try:
        await bot.send_message(chat_id=target_user, text="❌ <b>Verifikatsiya bekor qilindi!</b>\n\nFaqat 1xBet ID skrinshotini yuboring.")
        await callback.message.edit_caption(caption=f"❌ ID {target_user} rad etildi.")
    except TelegramForbiddenError:
        await callback.answer("Mijoz botni bloklagan!", show_alert=True)

@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    target_user = callback_data.user_id
    await callback.message.edit_caption(caption=f"✅ ID {target_user} qabul qilindi. Tavsif yozing...")
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user=target_user)

@dp.message(StateFilter(AdminState.waiting_for_description))
async def handle_description(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user = data.get("target_user")
    
    db.update_status(target_user, "approved")
    
    user_text = (
        "🎉 <b>TABRIKLAYMIZ, SIZ TASDIQLANDINGIZ!</b>\n\n"
        f"💡 <b>Admin eslatmasi:</b> <i>{message.text}</i>\n\n"
        "👇 Signal olishni boshlashingiz mumkin."
    )
    try:
        await bot.send_message(chat_id=target_user, text=user_text, reply_markup=main_vip_menu)
        await message.answer("✅ Mijozga Premium ruxsat berildi!")
    except TelegramForbiddenError:
        await message.answer("❌ Mijoz botni bloklagan.")
    await state.clear()

# Admin boshqaruv paneli (Faqat admin uchun)
@dp.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    total, vips = db.get_stats()
    text = f"👨‍💻 <b>ADMIN PANEL</b>\n\n👥 Umumiy botdagi odamlar: {total}\n💎 Tasdiqlangan VIP'lar: {vips}\n\n<i>Hammaga xabar yuborish uchun matnni yozing yoki /cancel deng:</i>"
    await message.answer(text)
    await state.set_state(AdminState.waiting_for_broadcast)

@dp.message(StateFilter(AdminState.waiting_for_broadcast))
async def broadcast_message(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await message.answer("Bekor qilindi.")
        await state.clear()
        return
        
    users = db.get_all_users()
    count = 0
    await message.answer("Tarqatish boshlandi...")
    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=f"🔔 <b>Admin xabari:</b>\n\n{message.text}")
            count += 1
            await asyncio.sleep(0.05) # Flood wait oldini olish
        except: pass
    await message.answer(f"✅ Xabar {count} kishiga yuborildi.")
    await state.clear()

# ==========================================
# 🌐 10. FLASK SERVER (RENDER HOSTING UCHUN 24/7)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Bot 100% aktiv. Baza tizimi barqaror!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 🏁 11. LOYIHANI ISHGA TUSHIRISH
# ==========================================
async def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("🚀 ULTIMATE PREMIUM BOT YUKLANDI - TIZIM ISHLAMOQDA!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
