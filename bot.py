import asyncio
import base64
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from openai import OpenAI

BOT_TOKEN = "TELEGRAM_TOKEN"
OPENAI_KEY = "OPENAI_KEY"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_KEY)

# --- клавиатуры ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📒 Подготовка к НМТ")],
        [KeyboardButton(text="📝 Решить тест текстом")],
        [KeyboardButton(text="📸 Решить тест по фото")]
    ],
    resize_keyboard=True
)

subjects_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Украинский язык")],
        [KeyboardButton(text="Математика")],
        [KeyboardButton(text="История Украины")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

user_mode = {}

# --- старт ---
@dp.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Я бот для подготовки к тестам 🙂", reply_markup=main_kb)

# --- меню ---
@dp.message(F.text == "📒 Подготовка к НМТ")
async def nmt_menu(msg: Message):
    user_mode[msg.from_user.id] = "nmt"
    await msg.answer("Выбери предмет:", reply_markup=subjects_kb)

@dp.message(F.text == "📝 Решить тест текстом")
async def text_mode(msg: Message):
    user_mode[msg.from_user.id] = "text"
    await msg.answer("Отправь вопрос и варианты.")

@dp.message(F.text == "📸 Решить тест по фото")
async def photo_mode(msg: Message):
    user_mode[msg.from_user.id] = "photo"
    await msg.answer("Отправь фото теста.")

@dp.message(F.text == "Назад")
async def back(msg: Message):
    await msg.answer("Главное меню", reply_markup=main_kb)

# --- предмет выбран ---
@dp.message(lambda m: m.text in ["Украинский язык","Математика","История Украины"])
async def subject_selected(msg: Message):
    user_mode[msg.from_user.id] = f"nmt_{msg.text}"
    await msg.answer(
        f"Режим НМТ: {msg.text}\n"
        "Отправь вопрос с вариантами."
    )

# --- текстовый вопрос ---
@dp.message(lambda m: user_mode.get(m.from_user.id,"").startswith("text") 
            or user_mode.get(m.from_user.id,"").startswith("nmt"))
async def solve_text(msg: Message):
    await msg.answer("🧠 Анализирую...")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты помощник для подготовки к экзаменам. "
                           "Определи правильный ответ и объясни кратко."
            },
            {"role": "user", "content": msg.text}
        ],
        temperature=0.3
    )

    await msg.answer(response.choices[0].message.content)

# --- фото ---
@dp.message(F.photo)
async def solve_photo(msg: Message):
    if user_mode.get(msg.from_user.id) != "photo":
        return

    await msg.answer("📸 Считываю текст с фото...")

    photo = msg.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_data = await bot.download_file(file.file_path)

    image_bytes = file_data.read()
    b64 = base64.b64encode(image_bytes).decode()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Прочитай текст с изображения, реши тест и объясни ответ."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Реши тест:"},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{b64}"
                    }
                ]
            }
        ],
        temperature=0.3
    )

    await msg.answer(response.choices[0].message.content)

# --- запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())