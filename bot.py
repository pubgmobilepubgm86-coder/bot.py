import os
import asyncio
import threading
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
# ⚙️ 1. ASOSIY SOZLAMALAR (PRO VERSION)
# ==========================================
BOT_TOKEN = "8897921742:AAHX0mQ6iNYjQAiJwmVdEEvgEovfrJtox0Q"
ADMIN_ID = 8086545587  # Xo'jayin ID si

# Botga HTML formatda chiroyli yozish imkoniyatini qo'shamiz
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

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
# Mijoz uchun birinchi qadam
user_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎰 1 x bet")]],
    resize_keyboard=True,
    input_field_placeholder="Kantorani tanlang..."
)

# Ruxsat olingandan keyingi qadam
signal_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⚡️ Signal olish")]],
    resize_keyboard=True,
    input_field_placeholder="Signallarni boshlaymizmi?"
)

# O'yin menyusi
apple_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🍎 APPLE OF FORTUNE 🍏 UCHUN")]],
    resize_keyboard=True,
    input_field_placeholder="O'yinni tanlang!"
)

# Admin panel tugmalari (Inline)
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
    text = (
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "🎯 <i>Ultimate Premium signallar</i> botiga xush kelibsiz.\n"
        "Davom etish uchun pastdagi menyudan o'zingizga kerakli kantorani tanlang 👇"
    )
    await message.answer(text, reply_markup=user_menu)

@dp.message(F.text == "🎰 1 x bet")
async def choose_kantora(message: Message, state: FSMContext):
    text = (
        "⚠️ <b>DIQQAT - TASDIQLASH JARAYONI!</b>\n\n"
        "📸 Iltimos, faqat <b>ID raqamingiz koʻringan</b> qismni screenshot (rasm) qilib yuboring.\n"
        "<i>Boshqa turdagi yoki noto'g'ri rasmlar tizim tomonidan avtomatik rad etiladi.</i>\n\n"
        "🚨 <b>MUHIM:</b> Botni aslo bloklamang! Aks holda ID tasdiqlangan taqdirda ham "
        "maxsus signallarni qabul qila olmaysiz."
    )
    # Tugmani yo'qotib, xabarni chiroyli qilib yuboramiz
    await message.answer(text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserState.waiting_for_photo)

@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    
    # Adminga chiroyli ko'rinishda boradigan xabar
    admin_text = (
        "🛡 <b>YANGI TASDIQLASH SO'ROVI</b>\n\n"
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={user_id}'>{message.from_user.full_name}</a>\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        "<i>Qabul qilasizmi yoki rad etasizmi? 👇</i>"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    await message.answer("⏳ <i>Ma'lumotlar adminga yuborildi. Iltimos, tasdiqlanishini kuting...</i>", reply_markup=ReplyKeyboardRemove())
    await state.clear() 

@dp.message(F.text == "⚡️ Signal olish")
async def process_signal_olish(message: Message):
    text = "🚀 <b>Ajoyib!</b>\n\nO'yinlar paneli faollashdi. Pastdan kerakli o'yinni tanlang 👇"
    await message.answer(text, reply_markup=apple_menu)

@dp.message(F.text == "🍎 APPLE OF FORTUNE 🍏 UCHUN")
async def process_apple_fortune(message: Message):
    # Bu yerga keyinchalik o'yin logikasini qo'shishingiz mumkin
    text = (
        "🍎 <b>APPLE OF FORTUNE</b> 🍏\n\n"
        "📡 <i>Serverga ulanmoqda... Signallar tayyorlanmoqda!</i>\n"
        "Tez orada ushbu panel orqali aniq ko'rsatmalar olasiz. Omad!"
    )
    await message.answer(text)

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
    await callback.answer("Rad etildi!")

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
    
    user_text = (
        "🎉 <b>TABRIKLAYMIZ!</b>\n"
        "Sizning ID raqamingiz muvaffaqiyatli ulandi va tasdiqdan o'tdi.\n\n"
        "💡 <b>Admin xabari:</b>\n"
        f"<i>{message.text}</i>\n\n"
        "👇 <b>Signal olish uchun pastdagi tugmani bosing!</b>"
    )
    try:
        await bot.send_message(chat_id=target_user_id, text=user_text, reply_markup=signal_menu)
        await message.answer("✅ Xabar va ⚡️ Signal olish tugmasi mijozga yetkazildi!")
    except Exception:
        await message.answer("❌ Xatolik: Foydalanuvchi botni bloklagan ko'rinadi.")
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
    
    print("🚀 Premium bot mukammal dizaynda ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
