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
class UserState(StatesGroup):
    waiting_for_photo = State()

class AdminState(StatesGroup):
    waiting_for_description = State()

# ----------------- TUGMALAR -----------------
user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 x bet")]
    ],
    resize_keyboard=True
)

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

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Assalomu alaykum! Qaysi kantora tanlaysiz?", reply_markup=user_menu)

@dp.message(F.text == "1 x bet")
async def choose_kantora(message: Message, state: FSMContext):
    text = (
        "Iltimos faqat id koʻringan qismingizni screnshot orqali yuboring va toʻgʻri id koʻringan rasm yuboring, "
        "boshqa rasm yuborsangiz bot qabul qilmaydi.\n\n"
        "Botni bloklamang boʻlmasam id tasdiqlangan boʻlsa ham signal ola olmaysiz."
    )
    await message.answer(text)
    await state.set_state(UserState.waiting_for_photo)

@dp.message(StateFilter(UserState.waiting_for_photo), F.photo)
async def handle_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    
    admin_text = f"👤 Yangi ID tasdiqlash so'rovi!\nFoydalanuvchi ID: {user_id}\nIsmi: {message.from_user.full_name}"
    await bot.send_photo(chat_id=ADMIN_ID, photo=photo_id, caption=admin_text, reply_markup=admin_inline_kb(user_id))
    
    await message.answer("Tasdiqlanishini kuting...")
    await state.clear() 

@dp.message(StateFilter(UserState.waiting_for_photo))
async def handle_not_photo(message: Message):
    await message.answer("Iltimos, faqat rasm (screenshot) yuboring.")

# ----------------- ADMIN QISMI -----------------

@dp.callback_query(AdminAction.filter(F.action == "reject"))
async def admin_reject(callback: CallbackQuery, callback_data: AdminAction):
    target_user_id = callback_data.user_id
    try:
        await bot.send_message(chat_id=target_user_id, text="Iltimos toʻgʻri id koʻrsatilgan 1 x bet id si kprsatilgan rasmni yuboring iltimos")
        await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} rad etildi. ❌")
    except Exception:
        await callback.answer("Xatolik: Foydalanuvchi botni bloklagan.", show_alert=True)
    await callback.answer()

@dp.callback_query(AdminAction.filter(F.action == "accept"))
async def admin_accept(callback: CallbackQuery, callback_data: AdminAction, state: FSMContext):
    target_user_id = callback_data.user_id
    await callback.message.answer("Tavsiflarini bering:")
    await callback.message.edit_caption(caption=f"Foydalanuvchi {target_user_id} qabul qilindi. Tavsif kutilmoqda... ✅")
    
    await state.set_state(AdminState.waiting_for_description)
    await state.update_data(target_user_id=target_user_id)
    await callback.answer()

@dp.message(StateFilter(AdminState.waiting_for_description))
async def handle_admin_description(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    
    user_text = f"Id ingiz muvaffaqyatli ulandi signal olishingiz mumkin.\n\nMalumotlar:\n{message.text}"
    try:
        await bot.send_message(chat_id=target_user_id, text=user_text)
        await message.answer("Xabar foydalanuvchiga muvaffaqiyatli yuborildi! ✅")
    except Exception:
        await message.answer("Xatolik: Foydalanuvchi botni bloklagan bo'lishi mumkin.")
    await state.clear()

# ----------------- FLASK SERVER (RENDER UCHUN) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot faol!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
