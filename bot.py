import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData

# ----------------- SOZLAMALAR -----------------
BOT_TOKEN = "8897921742:AAHX0mQ6iNYjQAiJwmVdEEvgEovfrJtox0Q"
ADMIN_ID = 8086545587  # Sizning Admin ID raqamingiz

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------- HOLATLAR (States) -----------------
# Bot kim nima qadamda turganini eslab qolishi uchun
class UserState(StatesGroup):
    waiting_for_photo = State()

class AdminState(StatesGroup):
    waiting_for_description = State()

# ----------------- TUGMALAR -----------------
# 1. Foydalanuvchiga chiqadigan menu
user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 x bet")]
    ],
    resize_keyboard=True
)

# 2. Admin uchun Inline (xabar tagidagi) tugmalar yasovchi klass
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

# ----------------- FOYDALANUVCHI QISMI -----------------

# /start bosilganda
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Assalomu alaykum! Qaysi kantora tanlaysiz?", reply_markup=user_menu)

# "1 x bet" tugmasi bosilganda
@dp.message(F.text == "1 x bet")
async def choose_kantora(message: Message, state: FSMContext):
    text = (
        "Iltimos faqat id koʻringan qismingizni screnshot orqali yuboring va toʻgʻri id koʻringan rasm yuboring, "
        "boshqa rasm yuborsangiz bot qabul qilmaydi.\n\n"
        "Botni bloklamang boʻlmasam id tasdiqlangan boʻlsa ham signal ola olmaysiz."
    )
    await message.answer(text)
    # Bot endi bu foydalanuvchidan rasm kutadi
    await state.set_state(UserState.waiting_for_photo)

# Foydalanuvchi rasm yuborganda
@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id # Rasmni olamiz
    
    # Rasmni adminga jo'natish
    admin_text = f"👤 Yangi ID tasdiqlash so'rovi!\nFoydalanuvchi ID: {user_id}\nIsmi: {message.from_user.full_name}"
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    # Foydalanuvchiga javob
    await message.answer("Tasdiqlanishini kuting...")
    # Kutish holatini tozalaymiz
    await state.clear() 

# Agar foydalanuvchi rasm so'ralganda matn yozsa
@dp.message(StateFilter(UserState.waiting_for_photo))
async def handle_not_photo(message: Message):
    await message.answer("Iltimos, faqat rasm (screenshot) yuboring.")


# ----------------- ADMIN QISMI -----------------

# Admin "Rad etish" tugmasini bossa
@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject(callback: CallbackQuery, callback_data: AdminAction):
    target_user_id = callback_data.user_id
    
    try:
        # Foydalanuvchiga rad xabarini yozish
        await bot.send_message(chat_id=target_user_id, text="Iltimos toʻgʻri id koʻrsatilgan 1 x bet id si kprsatilgan rasmni yuboring iltimos")
        # Admindagi xabarni tahrirlash (tugmalarni yo'qotib, rad etildi deb yozish)
        await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} rad etildi. ❌")
    except Exception:
        await callback.answer("Xatolik: Foydalanuvchi botni bloklagan bo'lishi mumkin.", show_alert=True)
    
    await callback.answer()

# Admin "Qabul qilish" tugmasini bossa
@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    target_user_id = callback_data.user_id
    
    # Adminga "Tavsif bering" deb yozish
    await callback.message.answer("Tavsiflarini bering:")
    await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} qabul qilindi. Tavsif kutilmoqda... ✅")
    
    # Adminni "Tavsif yozish" holatiga o'tkazamiz va qaysi userga yozayotganini xotiraga saqlaymiz
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user_id=target_user_id)
    await callback.answer()

# Admin tavsif/malumotlarni yuborganda
@dp.message(StateFilter(AdminState.waiting_for_description))
async def handle_admin_description(message: Message, state: FSMContext):
    # Xotiradan qaysi userga yuborilishi kerakligini chaqiramiz
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    # Foydalanuvchiga boradigan xabar
    user_text = f"Id ingiz muvaffaqyatli ulandi signal olishingiz mumkin.\n\nMalumotlar:\n{message.text}"
    
    try:
        await bot.send_message(chat_id=target_user_id, text=user_text)
        await message.answer("Xabar foydalanuvchiga muvaffaqiyatli yuborildi! ✅")
    except Exception:
        await message.answer("Xatolik: Foydalanuvchiga xabar borishi bekor bo'ldi (U botni bloklagan bo'lishi mumkin).")
    
    # Adminning holatini tozalab qo'yamiz (keyingi safar yozsa oddiy matn bo'lib ketishi uchun)
    await state.clear()


# ----------------- FLASK SERVER (RENDER UCHUN) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot faol ishlamoqda!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ----------------- ISHGA TUSHIRISH -----------------
async def main():
    # Veb serverni ishga tushirish
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
