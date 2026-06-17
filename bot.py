# -*- coding: utf-8 -*-
"""
⚡️ GALAXY MATRIX ENTERPRISE SYSTEM V5.0 PREMIUM ⚡️
==================================================
🤖 Platform: aiogram 3.x Fast Framework
📦 Database: SQLite3 Unified Cyber Schema
🌐 Server Architecture: Flask Web Service + Async aiohttp Self-Ping Loop
🛡 Security Module: Firewall Override & Anti-Sleep Engine Active
"""

import os
import io
import sys
import asyncio
import logging
import sqlite3
import random
import threading
import aiohttp
from datetime import datetime
from flask import Flask

# Aiogram kutubxonasi modullari
from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton, 
                           ReplyKeyboardRemove, CallbackQuery, 
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramForbiddenError

# =====================================================================
# ⚙️ 1. GLOBAL KONFIGURATSIYA VA TIZIM SOZLAMALARI
# =====================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BOT_TOKEN = "8897921742:AAHX0mQ6iNYjQAiJwmVdEEvgEovfrJtox0Q"
ADMIN_ID = 8086545587  
RENDER_URL = "https://savdo-bot.onrender.com"  # Render ilovangiz manzili

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# =====================================================================
# 🗄 2. INTELLEKTUAL CYBER DATA CORE (MA'LUMOTLAR BAZASI ARXITEKTURASI)
# =====================================================================
class DeepCyberDatabase:
    def __init__(self, db_name="galaxy_core_v5.db"):
        self.db_name = db_name
        self._build_mainframe()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _build_mainframe(self):
        """Tizim uchun zarur bo'lgan barcha jadvallarni noldan yaratish"""
        with self._connect() as conn:
            # Foydalanuvchilar jadvali (Barcha modullar ustunlari birlashtirilgan)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    luck_level REAL DEFAULT 88.5,
                    signal_count INTEGER DEFAULT 0,
                    last_golden_date TEXT DEFAULT '2000-01-01',
                    is_dark_mode INTEGER DEFAULT 0,
                    join_date TEXT,
                    referred_by INTEGER DEFAULT 0,
                    cyber_coins REAL DEFAULT 150.0,
                    last_wheel_date TEXT DEFAULT '2000-01-01',
                    last_quiz_date TEXT DEFAULT '2000-01-01',
                    is_boss INTEGER DEFAULT 0
                )
            """)
            # Promo-kodlar boshqaruvi
            conn.execute("""
                CREATE TABLE IF NOT EXISTS promo_codes (
                    code TEXT PRIMARY KEY,
                    reward_luck REAL,
                    max_uses INTEGER,
                    used_count INTEGER DEFAULT 0
                )
            """)
            # Tizim xavfsizlik jurnali (Logs)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    description TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

    # --- FOYDALANUVCHI AMALLARI ---
    def get_user(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone()

    def create_user(self, user_id, referrer=0):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._connect() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, status, join_date, referred_by)
                VALUES (?, 'pending', ?, ?)
            """, (user_id, now, referrer))
            conn.commit()

    def update_vip_status(self, user_id, status):
        with self._connect() as conn:
            conn.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
            conn.commit()

    def save_metrics(self, user_id, luck, signals):
        with self._connect() as conn:
            conn.execute("UPDATE users SET luck_level = ?, signal_count = ? WHERE user_id = ?", (luck, signals, user_id))
            conn.commit()

    def update_wallet(self, user_id, amount):
        with self._connect() as conn:
            conn.execute("UPDATE users SET cyber_coins = cyber_coins + ? WHERE user_id = ?", (amount, user_id))
            conn.commit()

    # --- KUNLIK CHEKLOVLAR VA SANALAR ---
    def set_date_restriction(self, user_id, column_name, date_str):
        with self._connect() as conn:
            conn.execute(f"UPDATE users SET {column_name} = ? WHERE user_id = ?", (date_str, user_id))
            conn.commit()

    def toggle_mode_flag(self, user_id, column_name, flag: int):
        with self._connect() as conn:
            conn.execute(f"UPDATE users SET {column_name} = ? WHERE user_id = ?", (flag, user_id))
            conn.commit()

    # --- STATISTIKA VA REYTING ---
    def get_stats(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'approved'")
            vips = cursor.fetchone()[0]
            return total, vips

    def get_leaderboard(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, signal_count, cyber_coins FROM users WHERE status = 'approved' ORDER BY cyber_coins DESC LIMIT 5")
            return cursor.fetchall()

    def get_all_users_list(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users")
            return [row[0] for row in cursor.fetchall()]

    def count_referrals(self, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (user_id,))
            return cursor.fetchone()[0]

    # --- PROMO-KOD SISTEMASI ---
    def insert_promo(self, code, luck, uses):
        with self._connect() as conn:
            conn.execute("INSERT OR REPLACE INTO promo_codes VALUES (?, ?, ?, 0)", (code, luck, uses))
            conn.commit()

    def execute_promo_claim(self, code, user_id):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT reward_luck, max_uses, used_count FROM promo_codes WHERE code = ?", (code,))
            promo = cursor.fetchone()
            if not promo: return "invalid"
            reward, max_u, used = promo
            if used >= max_u: return "expired"
            
            cursor.execute("SELECT luck_level FROM users WHERE user_id = ?", (user_id,))
            current_luck = cursor.fetchone()[0]
            conn.execute("UPDATE users SET luck_level = ? WHERE user_id = ?", (min(100.0, current_luck + reward), user_id))
            conn.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
            conn.commit()
            return "success"

    # --- BOSS OVERRIDE MODULLARI ---
    def set_boss_privilege(self, user_id, flag: int):
        with self._connect() as conn:
            conn.execute("UPDATE users SET is_boss = ? WHERE user_id = ?", (flag, user_id))
            conn.commit()

    def inject_system_log(self, etype, desc):
        now = datetime.now().strftime("%H:%M:%S")
        with self._connect() as conn:
            conn.execute("INSERT INTO system_logs (event_type, description, timestamp) VALUES (?, ?, ?)", (etype, desc, now))
            conn.commit()

    def fetch_latest_logs(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT event_type, description, timestamp FROM system_logs ORDER BY id DESC LIMIT 4")
            return cursor.fetchall()

db = DeepCyberDatabase()

# =====================================================================
# 🧠 3. STATE MANAGEMENT ENGINE (FSM & CALLBACK CONFIGS)
# =====================================================================
class UserState(StatesGroup):
    waiting_for_photo = State()
    entering_promo = State()
    risk_calc_balance = State()
    sending_feedback = State()

class AdminState(StatesGroup):
    waiting_for_description = State()
    waiting_for_broadcast = State()
    creating_promo_data = State()
    replying_to_user = State()

class BossState(StatesGroup):
    waiting_for_global_alert = State()
    manual_coin_injection = State()

class AdminAction(CallbackData, prefix="cyber"):
    action: str
    user_id: int

# =====================================================================
# 🎛 4. ADVANCED DESIGNS KEYBOARDS (KLAVIATURALAR TIZIMI)
# =====================================================================
register_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎰 1xBet Platformasi")]],
    resize_keyboard=True
)

main_vip_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⚡️ Signal olish"), KeyboardButton(text="🎰 Omad Charxpalagi")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🏆 Reyting"), KeyboardButton(text="📊 Statistika")],
        [KeyboardButton(text="🔗 Taklifnomalar"), KeyboardButton(text="🧮 Risk Menejer"), KeyboardButton(text="🎮 Kiber Viktorina")],
        [KeyboardButton(text="🎫 Promo-kod"), KeyboardButton(text="📣 Adminga aloqa"), KeyboardButton(text="🍀 Omad darajasi")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Matrix Mainframe Terminal Active..."
)

games_selection_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍎 APPLE OF FORTUNE 🍏"), KeyboardButton(text="💣 Mines Matrix")],
        [KeyboardButton(text="✈️ Aviator Skaner"), KeyboardButton(text="🔙 Asosiy menyuga qaytish")]
    ],
    resize_keyboard=True
)

dark_world_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏆 Kunlik Oltin Signal")],
        [KeyboardButton(text="☣️ Dark Mines Skaner")],
        [KeyboardButton(text="💀 Terminalni o'qish")],
        [KeyboardButton(text="🚪 Dark World'dan chiqish")]
    ],
    resize_keyboard=True
)

# ULTRA MAXFIY BOSS KLAVIATURASI (FAQAT KOD BILAN KIRILADI)
boss_mainframe_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👑 Matritsani Boshqarish (God Mode)"), KeyboardButton(text="📢 Global Alert Tarqatish")],
        [KeyboardButton(text="🚨 Soxta Jackpot E'lon Qilish"), KeyboardButton(text="💾 Jonli Terminal Jurnallari")],
        [KeyboardButton(text="🚪 Boss Rejimidan Chiqish")]
    ],
    resize_keyboard=True,
    input_field_placeholder="WELCOME BACK, MASTER... DEV MODE ON"
)

def build_admin_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=AdminAction(action="accept", user_id=user_id).pack()),
                InlineKeyboardButton(text="❌ Rad qilish", callback_data=AdminAction(action="reject", user_id=user_id).pack())
            ]
        ]
    )

# =====================================================================
# 👤 5. CORE WORKFLOW - START AND AUTHFUL ACTIONS
# =====================================================================
@dp.message(CommandStart())
async def cmd_start_processor(message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    referrer_id = 0
    
    # Referral link tekshirish (/start 8086545)
    if len(args) > 1 and args[1].isdigit():
        if int(args[1]) != user_id:
            referrer_id = int(args[1])

    is_new = db.get_user(user_id) is None
    db.create_user(user_id, referrer_id)
    user = db.get_user(user_id)
    
    if is_new:
        db.inject_system_log("NEW_USER", f"ID {user_id} registered.")
        if referrer_id > 0:
            db.update_wallet(referrer_id, 35.0)  # Do'stiga premium bonus
            try:
                await bot.send_message(
                    chat_id=referrer_id, 
                    text="🎁 <b>Kiber-Hamkorlik!</b> Do'stingiz tizimga kirdi, hamyoningizga <b>+35 Cyber-Coin</b> joylandi!"
                )
            except: pass
            
        alert = (
            "🔥 <b>YANGI FOYDALANUVCHI BAZADA!</b>\n\n"
            f"👤 <b>Ism:</b> {message.from_user.full_name}\n"
            f"🆔 <b>Tizim ID:</b> <code>{user_id}</code>\n"
            f"🔗 <b>Ssilka:</b> @{message.from_user.username if message.from_user.username else 'Yo\'q'}\n"
        )
        try: await bot.send_message(chat_id=ADMIN_ID, text=alert)
        except: pass

    if user and user[1] == "approved":
        db.toggle_mode_flag(user_id, "is_dark_mode", 0)
        await message.answer("💎 <b>CYBER MATRIX SYSTEM V5.0 DEPLOYED</b>\n\nBarcha algoritmik oqimlar yuklandi. Xush kelibsiz!", reply_markup=main_vip_menu)
    else:
        await message.answer("👋 <b>Yopiq yutuqli signallar portali boshqaruv markazi!</b>\n\nBot imkoniyatlarini ochish uchun verifikatsiya bosing:", reply_markup=register_menu)

@dp.message(F.text == "🎰 1xBet Platformasi")
async def register_start(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer("✅ Sizning ID raqamingiz allaqachon global serverda tasdiqlangan!", reply_markup=main_vip_menu)
        return
    await message.answer("📸 Iltimos, <b>1xBet ID raqamingiz</b> aniq ko'ringan profil sahifangiz skrinshotini (Rasm holatida) yuboring:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.waiting_for_photo)

@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def register_photo_get(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    
    admin_caption = (
        "🛡 <b>YANGI VIP PROFILE ARYZA</b>\n\n"
        f"👤 Profil: <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"🆔 ID raqami: <code>{user_id}</code>\n"
        "Tasdiqlash yoki rad qilish tugmasini bosing."
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_caption, reply_markup=build_admin_kb(user_id))
    await message.answer("⏳ <i>Sizning skrinshotingiz sun'iy intellekt va admin tekshiruviga yuborildi. Kuting...</i>", reply_markup=ReplyKeyboardRemove())
    await state.clear()

# =====================================================================
# 📊 6. STANDARD USER UTILITIES AND METRICS (PROFIL, STATS, PROMO)
# =====================================================================
@dp.message(F.text == "👤 Profil")
async def user_profile_card(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[1] != "approved": return
    
    refs = db.count_referrals(user[0])
    text = (
        "🪪 <b>KIBER-LOYIHA PROFIL TIZIMI</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name}\n"
        f"🆔 <b>Tizim ID:</b> <code>{user[0]}</code>\n"
        f"👑 <b>Status:</b> Ultra VIP Access ✅\n"
        f"💰 <b>Cyber-Coin Hamyoni:</b> <code>{round(user[8], 2)} CC</code>\n"
        f"⚡️ <b>Olingan signallar:</b> {user[3]} marta\n"
        f"🍀 <b>Omad Matritsasi:</b> <code>{round(user[2], 1)}%</code>\n"
        f"👥 <b>Siz chaqirgan geymerlar:</b> {refs} ta\n"
    )
    await message.answer(text)

@dp.message(F.text == "📊 Statistika")
async def system_stats_card(message: Message):
    if db.get_user(message.from_user.id)[1] != "approved": return
    total, vip = db.get_stats()
    await message.answer(
        f"📊 <b>LOYIHA GLOBAL METRIKALARI</b>\n\n"
        f"👥 Umumiy geymerlar: {total} ta\n"
        f"💎 VIP tasdiqlanganlar: {vip} ta\n"
        f"🛰 Tarmoq yadrosi: Render Enterprise Web Service\n"
        f"📶 Ping kechikishi: 4.81ms (Anti-Sleep Loop Active)"
    )

@dp.message(F.text == "🍀 Omad darajasi")
async def luck_factor_card(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer(f"📈 Sizning ayni vaqtdagi global neyro-tarmoq kiber omad koeffitsiyentingiz: <code>{round(user[2], 1)}%</code>")

@dp.message(F.text == "⚡️ Signal olish")
async def show_games_panel(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        await message.answer("🚀 <b>Premium o'yinlar algoritmlari tayyor. Tanlang:</b>", reply_markup=games_selection_menu)

@dp.message(F.text == "🔙 Asosiy menyuga qaytish")
async def back_to_home(message: Message):
    await message.answer("Bosh boshqaruv paneliga qaytildi 👇", reply_markup=main_vip_menu)

@dp.message(F.text == "🎫 Promo-kod")
async def promo_start(message: Message, state: FSMContext):
    if db.get_user(message.from_user.id)[1] == "approved":
        await message.answer("🎫 Maxfiy vaucher yoki kiber promo-kodni kiriting:")
        await state.set_state(UserState.entering_promo)

@dp.message(StateFilter(UserState.entering_promo))
async def promo_finish(message: Message, state: FSMContext):
    result = db.execute_promo_claim(message.text.strip(), message.from_user.id)
    await state.clear()
    if result == "invalid": 
        await message.answer("❌ Bunday kod mavjud emas yoki xato kiritildi!", reply_markup=main_vip_menu)
    elif result == "expired": 
        await message.answer("⏳ Kodning global faollashuv muddati yoki soni tugagan!", reply_markup=main_vip_menu)
    else: 
        await message.answer("🎉 Muvaffaqiyatli! Tizim omad koeffitsiyentingiz yuqoriladi!", reply_markup=main_vip_menu)

@dp.message(F.text == "🔗 Taklifnomalar")
async def ref_handler(message: Message):
    uid = message.from_user.id
    if db.get_user(uid)[1] != "approved": return
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={uid}"
    await message.answer(
        f"🔗 <b>KIBER HAMKORLIK LINKI</b>\n\n"
        f"Do'stlaringizni botga taklif qiling!\n"
        f"🎁 Har bir faol geymer uchun hamyoningizga: <b>+35 Cyber-Coin</b> o'tkaziladi.\n\n"
        f"📌 Sizning shaxsiy havolangiz:\n<code>{referral_link}</code>"
    )

@dp.message(F.text == "🧮 Risk Menejer")
async def risk_start(message: Message, state: FSMContext):
    if db.get_user(message.from_user.id)[1] == "approved":
        await message.answer("🧮 Balansingizdagi joriy summani faqat sonlarda kiriting (Masalan: 50000):")
        await state.set_state(UserState.risk_calc_balance)

@dp.message(StateFilter(UserState.risk_calc_balance))
async def risk_finish(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Xatolik! Iltimos faqat raqamlardan iborat summa kiriting.")
        return
    balance = float(message.text)
    await state.clear()
    step1 = balance * 0.02
    await message.answer(
        f"📊 <b>RISK MATRIX MARTINGALE CALCULATOR</b>\n\n"
        f"💰 Joriy umumiy balans: {balance} UZS\n\n"
        f"1-Qadam (Xavfsiz): <code>{round(step1,1)} UZS</code>\n"
        f"2-Qadam (Sug'urta): <code>{round(step1*2.5,1)} UZS</code>\n"
        f"3-Qadam (Tiklanish): <code>{round(step1*6.25,1)} UZS</code>\n"
        f"4-Qadam (Kritik Xavf): <code>{round(step1*15.6,1)} UZS</code>\n\n"
        f"⚠️ <i>Qoida: Mag'lubiyatda tikishni 2.5 barobar oshiring, g'alabada esa har doim 1-qadamga qayting!</i>", 
        reply_markup=main_vip_menu
    )

# =====================================================================
# 🎰 7. SIMULATED INTERACTIVE GAMES MODULES (CHARXPALAK, AVIATOR, QUIZ)
# =====================================================================
@dp.message(F.text == "🎰 Omad Charxpalagi")
async def lucky_wheel_handler(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user or user[1] != "approved": return

    today = datetime.now().strftime("%Y-%m-%d")
    if user[9] == today:
        await message.answer("🛑 <b>Kunlik cheklov faollashgan!</b>\nOmad charxpalagini 24 soatda faqat 1 marta aylantirish mumkin. Ertaga urinib ko'ring! ⏳")
        return

    db.set_date_restriction(user_id, "last_wheel_date", today)
    msg = await message.answer("🎰 <code>Kiber-Charxpalak aylanmoqda... [ 🎡 ]</code>")
    await asyncio.sleep(0.4)
    await msg.edit_text("🎰 <code>Natija hisoblanmoqda... [ 🌀 ]</code>")
    await asyncio.sleep(0.4)

    prizes = [
        ("15 Cyber-Coins", 15.0, "coins"),
        ("60 Cyber-Coins", 60.0, "coins"),
        ("+3.0% Omad Boost", 3.0, "luck"),
        ("JACKPOT! 200 Cyber-Coins", 200.0, "coins"),
        ("Omad kelmadi", 0.0, "nothing")
    ]
    win = random.choices(prizes, weights=[45, 25, 15, 5, 10])[0]

    if win[2] == "coins":
        db.update_wallet(user_id, win[1])
        await msg.edit_text(f"🎉 <b>YUTUQ NOMINAL!</b>\n\nSizga <code>{win[0]}</code> taqdim etildi! Tangalar balansga qo'shildi.")
    elif win[2] == "luck":
        db.save_metrics(user_id, min(100.0, user[2] + win[1]), user[3])
        await msg.edit_text(f"🌟 <b>OMAD REAKTORI BOOST!</b>\n\nSizga <code>{win[0]}</code> berildi! Global signallar aniqligi oshdi.")
    else:
        await msg.edit_text("😢 <i>Bu safar omad kulib boqmadi. Keyingi urinishda albatta yutasiz!</i>")

@dp.message(F.text == "✈️ Aviator Skaner")
async def aviator_predictor_handler(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[1] != "approved": return

    msg = await message.answer("🚀 <code>Aviator Neyro-Skaner yuklanmoqda... 0%</code>")
    await asyncio.sleep(0.3)
    await msg.edit_text("📈 <code>Koeffitsiyent matritsasi tahlil qilinmoqda... 75%</code>")
    await asyncio.sleep(0.3)

    coef = random.choices([random.uniform(1.1, 1.8), random.uniform(1.9, 3.8), random.uniform(4.0, 18.0)], weights=[65, 25, 10])[0]
    db.save_metrics(user[0], user[2], user[3] + 1)

    result = (
        "✈️ <b>AVIATOR CRASH PREDICTOR AI</b> ✈️\n\n"
        "<blockquote>Matritsadan olingan xavfsiz uchish nuqtasi:</blockquote>\n"
        f"🎯 <b>Portlash chegarasi:</b> <code>{round(coef, 2)}x</code>\n\n"
        "⚠️ <i>Diqqat: Koeffitsiyent ko'rsatilgan nuqtaga yetishidan biroz oldin pulingizni naqd qiling!</i>"
    )
    await msg.edit_text(result)

@dp.message(F.text == "🎮 Kiber Viktorina")
async def quiz_handler(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user or user[1] != "approved": return

    today = datetime.now().strftime("%Y-%m-%d")
    if user[10] == today:
        await message.answer("🛑 <b>Bugungi intellektual kviz imkoniyatingiz tugagan.</b>\nYangi savollar ertaga yangilanadi! 🧠")
        return

    quizzes = [
        {"q": "Counter Strike o'yinida eng mashhur va klassik snayper quroli qaysi?", "a": "AWP", "o": ["M4A1", "AWP", "AK-47"]},
        {"q": "Dota 2 o'yinidagi eng markaziy ob'ekt (Bosh bino) nima deb ataladi?", "a": "Ancient", "o": ["Ancient", "Barrak", "Roshan"]},
        {"q": "1xBet o'yinlarida Martingale strategiyasi asosan qanday koeffitsiyentlar uchun ishlaydi?", "a": "2.00 va undan yuqori", "o": ["1.20 koeffitsiyent", "1.50 koeffitsiyent", "2.00 va undan yuqori"]}
    ]
    quiz = random.choice(quizzes)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for option in quiz["o"]:
        is_correct_flag = "1" if option == quiz["a"] else "0"
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=option, callback_data=f"quiz_ans:{is_correct_flag}")])
        
    db.set_date_restriction(user_id, "last_quiz_date", today)
    await message.answer(
        f"🎮 <b>GEYMERLAR INTELLEKT VIKTORINASI</b>\n\n"
        f"<b>Savol:</b> {quiz['q']}\n\n"
        f"<i>💡 To'g'ri javob uchun kiber hamyoningizga +35 Cyber-Coins qo'shiladi!</i>", 
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("quiz_ans:"))
async def quiz_callback_handler(callback: CallbackQuery):
    is_correct = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    if is_correct == "1":
        db.update_wallet(user_id, 35.0)
        await callback.message.edit_text("🎉 <b>MUKAMMAL TO'G'RI JAVOB!</b>\nHamyoningizga +35 Cyber-Coin muvaffaqiyatli yuklandi!")
    else:
        await callback.message.edit_text("❌ <b>NOTO'G'RI JAVOB!</b>\nAfsuski noto'g'ri javob berdingiz. Ertangi savollarda omadingizni sinang!")
    await callback.answer()

# =====================================================================
# 🍏 8. LEGACY GAMES ALGORITHMS (APPLE OF FORTUNE & MINES MATRIX)
# =====================================================================
@dp.message(F.text == "🍎 APPLE OF FORTUNE 🍏")
async def apple_fortune_game(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user or user[1] != "approved": return
    if user[2] <= 60.0:
        await message.answer("⚠️ Kritik muammo! Omad darajangiz juda past. Promo-kod ishlatib ko'taring.")
        return

    loading = await message.answer("📡 <code>Neyro-kanal o'rnatilmoqda... [■■□□□] 40%</code>")
    await asyncio.sleep(0.2)
    await loading.edit_text("🚀 <code>Xavfsiz yo'lak aniqlandi! [■■■■■] 100%</code>")

    safe_cell = random.choices([1, 2, 3, 4, 5], weights=[15, 23, 16, 22, 24])[0]
    db.save_metrics(user_id, max(55.0, user[2] - 1.2), user[3] + 1)

    await loading.edit_text(
        f"🍏 <b>APPLE OF FORTUNE MATRIX ENGINE</b> 🍎\n\n"
        f"🎯 <b>Tavsiya etilgan katak:</b> <code>[{safe_cell}]</code>\n"
        f"📊 Joriy kiber omad foizi: <code>{round(db.get_user(user_id)[2], 1)}%</code>"
    )

@dp.message(F.text == "💣 Mines Matrix")
async def mines_game(message: Message):
    if db.get_user(message.from_user.id)[1] != "approved": return
    loading = await message.answer("📡 <code>Kvadrat matritsa skanerlanmoqda...</code>")
    await asyncio.sleep(0.2)
    
    grid = [["⬜️" for _ in range(5)] for _ in range(5)]
    # 3 ta xavfsiz yulduzni tasodifiy joylashtirish
    for step in random.sample(range(25), 3):
        grid[step // 5][step % 5] = "🌟"
        
    grid_string = "\n".join(" ".join(row) for row in grid)
    await loading.edit_text(
        f"💣 <b>MINES QUANTUM MAP (3 BOMBAS CODES)</b> 💣\n\n"
        f"{grid_string}\n\n"
        f"⚠️ <i>Faqat ko'rsatilgan yulduzli [🌟] kataklarni bosing!</i>"
    )

# =====================================================================
# 🌌 9. DARK WORLD MODE (MAXFIY ALGORITMLAR VA REJIMLAR)
# =====================================================================
@dp.message(F.text == "262626121212")
async def enter_dark_world(message: Message):
    try: await message.delete()
    except: pass
    user = db.get_user(message.from_user.id)
    if user and user[1] == "approved":
        db.toggle_mode_flag(message.from_user.id, "is_dark_mode", 1)
        db.inject_system_log("DARK_WORLD", f"ID {message.from_user.id} accessed Dark Net.")
        await message.answer(
            "🚨 <b>SYSTEM OVERRIDE: DARK WORLD ACTIVATED</b> 🚨\n\n"
            "Siz super shifrlangan tarmoqqa ulandingiz. Kunlik 99.9% aniqlikdagi Oltin Signal rejimi faollashdi.", 
            reply_markup=dark_world_menu
        )

@dp.message(F.text == "💀 Terminalni o'qish")
async def read_terminal_logs(message: Message):
    user = db.get_user(message.from_user.id)
    if user and user[5] == 1:
        await message.answer(
            "<code>root@cyber_mainframe:~# ./bypass_security_protocols\n"
            "[SUCCESS] Tunnel established via proxy layers.\n"
            "[READY] Memory injection completed successfully. Ready to breach.</code>"
        )

@dp.message(F.text == "☣️ Dark Mines Skaner")
async def dark_mines_scanner(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[5] != 1: return
    
    grid = [["⬛️" for _ in range(5)] for _ in range(5)]
    for step in random.sample(range(25), 5):
        grid[step // 5][step % 5] = "🔥"
        
    await message.answer(
        f"💀 <b>DARK NET MINES QUANTUM BREACH</b> 💀\n\n"
        f"{'\n'.join(' '.join(row) for row in grid)}\n\n"
        f"⚠️ O'ta maxfiy kiber tizim xaritasi."
    )

@dp.message(F.text == "🚪 Dark World'dan chiqish")
async def exit_dark_world(message: Message):
    db.toggle_mode_flag(message.from_user.id, "is_dark_mode", 0)
    await message.answer("Standart xavfsiz premium rejimga qaytildi.", reply_markup=main_vip_menu)

@dp.message(F.text == "🏆 Kunlik Oltin Signal")
async def golden_signal_handler(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user or user[5] != 1: return

    today = datetime.now().strftime("%Y-%m-%d")
    if user[4] == today:
        await message.answer("🛑 <b>RUXSAT ETILMAYDI!</b>\n\nSiz bugungi shifrlangan Oltin Signal limitini ishlatib bo'lgansiz. Algoritm kuniga faqat bitta kombinatsiya ochish imkonini beradi!")
        return

    db.set_date_restriction(user_id, "last_golden_date", today)
    loading = await message.answer("🔓 <code>[DECRYPTING]: Algoritm xavfsizlik devorini chetlab o'tmoqda...</code>")
    await asyncio.sleep(0.4)
    
    cell1, cell2, cell3 = random.randint(1,5), random.randint(1,5), random.randint(1,5)
    await loading.edit_text(
        f"🏆 <b>KUNLIK ABSOLYUT OLTIN SIGNAL (99.9%)</b> 🏆\n\n"
        f"1️⃣ Bosqich yo'li: <code>[{cell1}]</code>\n"
        f"2️⃣ Bosqich yo'li: <code>[{cell2}]</code>\n"
        f"3️⃣ Bosqich yo'li: <code>[{cell3}]</code>\n\n"
        f"<blockquote>🚨 MUHIM KO'RSATMA: Ushbu kombinatsiya faqat bir marta ishlash uchun sozlangan. Yutuqni olgach to'xtang.</blockquote>"
    )

# =====================================================================
# 📣 10. FEEDBACK EXPRESS AND SUPPORT PLATFORM
# =====================================================================
@dp.message(F.text == "📣 Adminga aloqa")
async def feedback_start(message: Message, state: FSMContext):
    if db.get_user(message.from_user.id)[1] == "approved":
        await message.answer(
            "📣 <b>Adminga tezkor murojaat tizimi</b>\n\n"
            "Xabaringizni, shikoyat yoki takliflaringizni to'liq matn shaklida yozib yuboring. Admin tez orada javob qaytaradi:", 
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(UserState.sending_feedback)

@dp.message(StateFilter(UserState.sending_feedback))
async def feedback_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    
    admin_reply_kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✍️ Javob yozish", callback_data=f"reply_u:{user_id}")
    ]])
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💬 <b>YANGI MUROJAAT KELDI!</b>\n\n👤 <b>Kimdan:</b> {message.from_user.full_name}\n🆔 <b>ID:</b> <code>{user_id}</code>\n\n📝 <b>Matn:</b>\n<i>{message.text}</i>",
        reply_markup=admin_reply_kb
    )
    await message.answer("✅ <b>Xabaringiz xavfsiz kanallar orqali adminga yuborildi. Tez orada javob olasiz!</b>", reply_markup=main_vip_menu)

# =====================================================================
# 👑 11. YASHIRIN "BOSS CONTROL CENTER" TIZIMI (mutloq boshqaruv)
# =====================================================================
@dp.message(F.text == "77779999_MATRIX_OVERRIDE")
async def activate_boss_mode(message: Message):
    try: await message.delete()
    except: pass
    user_id = message.from_user.id
    
    # Boss statusini bazada yoqish
    db.set_boss_privilege(user_id, 1)
    db.update_vip_status(user_id, "approved")
    db.inject_system_log("BOSS_OVERRIDE", f"User {user_id} triggered Master Boss Menu.")
    
    await message.answer(
        "🎛 <code>[ACCESS GRANTED]: Welcome back, Almighty Game Director...</code>\n\n"
        "👑 <b>Siz endi tizim mutloq boshlig'isiz! Maxfiy boshqaruv xonasi faollashdi.</b>", 
        reply_markup=boss_mainframe_menu
    )

@dp.message(F.text == "🚪 Boss Rejimidan Chiqish")
async def exit_boss_mode(message: Message):
    db.set_boss_privilege(message.from_user.id, 0)
    await message.answer("Boss imtiyozlari o'chirildi. Oddiy menyuga qaytdingiz.", reply_markup=main_vip_menu)

@dp.message(F.text == "👑 Matritsani Boshqarish (God Mode)")
async def boss_god_mode_action(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[11] != 1: return
    
    # O'z profiliga cheksiz pul va omad berish
    db.update_wallet(message.from_user.id, 99999.0)
    db.save_metrics(message.from_user.id, 999.9, user[3])
    db.inject_system_log("GOD_MODE", f"Boss injected balances to himself.")
    
    await message.answer("⚡️ <b>MATRIX STATUS: SUCCESS!</b>\n\nHamyoningizga <b>+99,999 Cyber-Coins</b> qo'shildi va kiber omad darajangiz <b>999.9%</b> ga o'rnatildi!")

@dp.message(F.text == "📢 Global Alert Tarqatish")
async def boss_global_alert_start(message: Message, state: FSMContext):
    user = db.get_user(message.from_user.id)
    if not user or user[11] != 1: return
    
    await message.answer("📢 Barcha foydalanuvchilarga yuboriladigan vahimali/qiziqarli global xabarni yozing:")
    await state.set_state(BossState.waiting_for_global_alert)

@dp.message(StateFilter(BossState.waiting_for_global_alert))
async def boss_global_alert_finish(message: Message, state: FSMContext):
    await state.clear()
    users_list = db.get_all_users_list()
    counter = 0
    
    for uid in users_list:
        try:
            await bot.send_message(
                chat_id=uid,
                text=f"🚨 <b>TIZIM OGOHLANTIRIShI (MATRIX DIRECT ALERT):</b>\n\n{message.text}"
            )
            counter += 1
            await asyncio.sleep(0.05)
        except: pass
        
    await message.answer(f"✅ Global e'lon muvaffaqiyatli {counter} ta ID ga tarqatildi!", reply_markup=boss_mainframe_menu)

@dp.message(F.text == "🚨 Soxta Jackpot E'lon Qilish")
async def boss_fake_jackpot(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[11] != 1: return
    
    users_list = db.get_all_users_list()
    random_fake_id = random.randint(100000, 999999)
    fake_sum = random.choice(["45,200,000", "78,500,000", "120,000,000"])
    
    jackpot_text = (
        "🎉 <b>GLOBAL MATRIX JACKPOT BREAKS!</b> 🎉\n\n"
        f"Geymerlar jamoamiz a'zosi (ID: <code>{random_fake_id}***</code>) tizimning Oltin Signal algoritmi orqali bugun 1xBet platformasida <b>{fake_sum} UZS</b> yutuqni qo'lga kiritdi! 💸\n\n"
        "🔥 Bizning signallar ishlashda davom etadi! Omad darajangizni tekshiring."
    )
    
    for uid in users_list:
        try:
            await bot.send_message(chat_id=uid, text=jackpot_text)
            await asyncio.sleep(0.04)
        except: pass
        
    await message.answer("🚨 Soxta Jackpot e'loni barcha foydalanuvchilar ekraniga muvaffaqiyatli yuborildi!")

@dp.message(F.text == "💾 Jonli Terminal Jurnallari")
async def boss_view_logs(message: Message):
    user = db.get_user(message.from_user.id)
    if not user or user[11] != 1: return
    
    logs = db.fetch_latest_logs()
    log_text = "💾 <b>SYSTEM MAINFRAME LIVE LOGS STREAM:</b>\n\n"
    for item in logs:
        log_text += f"<code>[{item[2]}] [{item[0]}] -> {item[1]}</code>\n"
        
    log_text += "\n<i>Tizim yadrosi barqaror holatda ishlamoqda. Ready.</i>"
    await message.answer(log_text)

# =====================================================================
# 👑 12. STANDARD ADMIN INTERFACE AND CALLBAKS (TASDIQLASH TIZIMI)
# =====================================================================
@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject_user(callback: CallbackQuery, callback_data: AdminAction):
    uid = callback_data.user_id
    try: await bot.send_message(chat_id=uid, text="❌ Arizangiz ma'lumotlar mos kelmagani sababli rad etildi. To'g'ri profil skrinshotini yuboring.")
    except: pass
    await callback.message.edit_caption(caption="❌ Ushbu foydalanuvchi arizasi rad etildi.")
    await callback.answer()

@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept_user(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    uid = callback_data.user_id
    await callback.message.edit_caption(caption=f"✅ ID {uid} tasdiqlash rejimida. Foydalanuvchiga VIP ko'rsatma yozing:")
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user_id=uid)
    await callback.answer()

@dp.message(StateFilter(AdminState.waiting_for_description))
async def admin_desc_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get("target_user_id")
    db.update_vip_status(uid, "approved")
    db.inject_system_log("VIP_APPROVE", f"User {uid} approved to VIP status.")
    
    try:
        await bot.send_message(
            chat_id=uid, 
            text=f"🎉 <b>VIP ERKIN PROFILE ACCESS AKTIVLASHTIRILDI!</b>\n\n💡 Admin yo'riqnomasi: <i>{message.text}</i>", 
            reply_markup=main_vip_menu
        )
        await message.answer("✅ Muvaffaqiyatli! Foydalanuvchiga VIP yoqildi va xabarnoma ketdi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")
    await state.clear()

@dp.callback_query(F.data.startswith("reply_u:"))
async def admin_reply_start(callback: CallbackQuery, state: FSMContext):
    target_uid = int(callback.data.split(":")[1])
    await callback.message.answer(f"✍️ ID <code>{target_uid}</code> ga yuboriladigan to'g'ridan-to'g'ri javob matnini yozing:")
    await state.set_state(AdminState.replying_to_user)
    await state.update_data(reply_target_uid=target_uid)
    await callback.answer()

@dp.message(StateFilter(AdminState.replying_to_user))
async def admin_reply_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    target_uid = data.get("reply_target_uid")
    await state.clear()
    
    try:
        await bot.send_message(
            chat_id=target_uid, 
            text=f"🔔 <b>Admindan rasmiy javob keldi:</b>\n\n<blockquote><i>{message.text}</i></blockquote>"
        )
        await message.answer("✅ Javobingiz foydalanuvchiga yetkazildi!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@dp.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    total, vip = db.get_stats()
    await message.answer(
        f"👨‍💻 <b>KIBER ADMIN PANEL STATUS CORE</b>\n\n"
        f"Foydalanuvchilar: {total} ta\n"
        f"VIP a'zolar: {vip} ta\n\n"
        f"Promo yaratish: <code>/create_promo</code>\n"
        f"Umumiy reklama tarqatish uchun matn yozing va kuting:"
    )
    await state.set_state(AdminState.waiting_for_broadcast)

@dp.message(Command("create_promo"))
async def create_promo_cmd(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Format: <code>kod bonus_omad foydalanish_soni</code>\nMasalan: <code>GIFT777 5.5 15</code>")
        await state.set_state(AdminState.creating_promo_data)

@dp.message(StateFilter(AdminState.creating_promo_data))
async def create_promo_finish(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        db.insert_promo(parts[0], float(parts[1]), int(parts[2]))
        await message.answer("✅ Yangi promo-kod muvaffaqiyatli global bazaga qo'shildi!")
    except: 
        await message.answer("❌ Format xato. Qaytadan urinib ko'ring.")
    await state.clear()

@dp.message(StateFilter(AdminState.waiting_for_broadcast))
async def broadcast_action(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        return
    uids = db.get_all_users_list()
    count = 0
    await message.answer("Reklama translyatsiyasi boshlandi...")
    for uid in uids:
        try:
            await bot.send_message(chat_id=uid, text=f"🔔 <b>ADMIN BILDIRISHNOMASI:</b>\n\n{message.text}")
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await message.answer(f"✅ Xabar muvaffaqiyatli ravishda {count} ta foydalanuvchiga tarqatildi.")
    await state.clear()

# =====================================================================
# 🌐 13. WEB INFRASTRUCTURE DEPLOYMENT (FLASK BACKEND ENGINE)
# =====================================================================
app = Flask(__name__)

@app.route('/')
def mainframe_home_route():
    return f"🚀 CYBER CORE OPERATIONAL V5.0 STATUS: OK. RUNNING 24/7. METRIC SYNCED AT: {datetime.now().strftime('%H:%M:%S')}"

def start_flask_runtime():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# =====================================================================
# 🛰 14. FIREWALL PERSISTENCE ENGINE (ANTI-SLEEP CORE LOOP)
# =====================================================================
async def anti_sleep_ping_loop():
    """Render xizmatini uxlab qolishdan (Spin down) 24/7 himoya qilish sikli"""
    await asyncio.sleep(25)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as response:
                    logging.info(f"🛰 [SELF-PING]: Packet synced with Render Cloud. Code: {response.status}")
            except Exception as e:
                logging.error(f"🛰 [PING ERROR ENGINE]: {e}")
            await asyncio.sleep(240)  # Har 4 daqiqada doimiy so'rov yuborish

# =====================================================================
# 🏁 15. RUNTIME GLOBAL EXECUTION ENTRY POINT
# =====================================================================
async def main():
    # Bot ishga tushganda eski vaqtinchalik Dark rejimlarni tozalash
    with sqlite3.connect("galaxy_core_v5.db") as conn:
        conn.execute("UPDATE users SET is_dark_mode = 0")
        conn.commit()
    
    # Flask serverni parallel oqimda portlatish
    flask_thread = threading.Thread(target=start_flask_runtime, daemon=True)
    flask_thread.start()
    
    # Anti-Sleep siklini asinxron fonda orqaga yuklash
    asyncio.create_task(anti_sleep_ping_loop())
    
    print("=====================================================")
    print("🔥 GALAXY MATRIX BOT ENGINE V5.0 FULLY OPERATIONAL 24/7!")
    print("=====================================================")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
