import asyncio
import logging
import sys
from mimetypes import init

from _curses import echo
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from pip._internal.vcs import git

TOKEN = "7237003539:AAGvYBe0wxaybLY9PcD_qKcO-wg62FIuzzs"

dp = Dispatcher()


# === FSM (Bosqichma-bosqich holatlar) ===
class DeveloperForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_occupation = State()


class CustomerForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
# === Inline Tugma ===
def inline_button():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Developer", callback_data="Developer"),
        InlineKeyboardButton(text="Customer", callback_data="Customer"),
    )
    return builder.as_markup()
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Siz kimsiz?",
        reply_markup=inline_button()  # Inline buttonlar qaytadi
    )

    # ReplyKeyboardRemove yuborish orqali eski pastki menyuni yo‘q qilamiz
    await message.answer(reply_markup=ReplyKeyboardRemove())
# === /start komandasi ===
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Siz kimsiz?", reply_markup=inline_button())

# === Developer tugmasi bosilganda ===
@dp.callback_query(F.data == "Developer")
async def developer_selected(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ismingizni kiriting:")
    await state.set_state(DeveloperForm.waiting_for_name)

# === Ism kiritilganda ===
@dp.message(DeveloperForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Contact ma'lumotingizni kiriting:")
    await state.set_state(DeveloperForm.waiting_for_contact)

# === Contact kiritilganda ===
@dp.message(DeveloperForm.waiting_for_contact)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("Occupation (kasbingiz) ni kiriting:")
    await state.set_state(DeveloperForm.waiting_for_occupation)

@dp.callback_query(F.data == "Customer")
async def handle_customer(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ismingizni kiriting:")
    await state.set_state(CustomerForm.waiting_for_name)

@dp.message(CustomerForm.waiting_for_name)
async def get_cust_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Contactingizni kiriting:")
    await state.set_state(CustomerForm.waiting_for_contact)


def admin_panel():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧾 Oxirgi Buyurtma")],
            [KeyboardButton(text="📂 Mening Buyurtmalarim"), KeyboardButton(text="👤 O'zim haqida")],
            [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="📞 Biz bilan bog'lanish")],
        ],
        resize_keyboard=True
    )

# === Developer yakuniy step (update qilish) ===
@dp.message(DeveloperForm.waiting_for_occupation)
async def get_dev_occupation(message: Message, state: FSMContext):
    await state.update_data(occupation=message.text)
    data = await state.get_data()

    await message.answer(
        f"✅ Ma'lumotlar saqlandi!\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Contact: {data['contact']}\n"
        f"💼 Kasb: {data['occupation']}"
    )

    # ADMIN PANELNI CHIQARISH
    await message.answer(
        "📋 <b>Assosiy Panelga Hush kelibsiz!</b>",
        reply_markup=admin_panel(),
        parse_mode="HTML"
    )

    await state.clear()

# === CUSTOMER PANEL KNOPKALARI ===
def customer_panel():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish")],
            [KeyboardButton(text="📂 Mening Buyurtmalarim"), KeyboardButton(text="👤 O'zim haqida")],
            [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="📞 Biz bilan bog'lanish")],
        ],
        resize_keyboard=True
    )
@dp.message(CustomerForm.waiting_for_contact)
async def get_customer_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    await message.answer(
        f"✅ Ma'lumotlar saqlandi!\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Contact: {data['contact']}"
    )

    # CUSTOMER PANELNI CHIQARISH
    await message.answer(
        "📋 <b>Assosiy Panelga Hush kelibsiz!</b>",
        reply_markup=customer_panel(),
        parse_mode="HTML"
    )

    await state.clear()

# === Main ===
async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

"""
echo "# lesson_2" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Bilol-ui/lesson_2.git
git push -u origin main
"""