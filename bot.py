import os
import telebot
from telebot import types
import openai

# Подключаем ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_KEY

# Главное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Подготовка к НМТ📒", "Google Form Test")
    return markup

# Меню предметов для НМТ
def nmt_subject_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Українська мова", "Математика")
    markup.row("Фізика", "Біологія")
    markup.row("Назад")
    return markup

# Обработчик /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Оберіть дію:", reply_markup=main_menu())

# Обработчик текстовых кнопок
@bot.message_handler(func=lambda m: True)
def menu(message):
    text = message.text

    if text == "Подготовка к НМТ📒":
        bot.send_message(message.chat.id, "Оберіть предмет:", reply_markup=nmt_subject_menu())
    elif text in ["Українська мова", "Математика", "Фізика", "Біологія"]:
        bot.send_message(message.chat.id, f"Ви обрали предмет: {text}. Тут можна додати матеріали чи фото.")
    elif text == "Назад":
        bot.send_message(message.chat.id, "Повертаємось у головне меню:", reply_markup=main_menu())
    elif text == "Google Form Test":
        bot.send_message(message.chat.id, "Вставте посилання на Google Form, і я дам підказки.")
    else:
        bot.send_message(message.chat.id, "Невідома команда, спробуйте ще раз.")

# Команда для OpenAI
@bot.message_handler(commands=['ask'])
def ask_ai(message):
    question = message.text.replace("/ask", "").strip()
    if not question:
        bot.send_message(message.chat.id, "Напишіть питання після /ask")
        return
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=question,
            max_tokens=200
        )
        bot.send_message(message.chat.id, response.choices[0].text.strip())
    except Exception as e:
        bot.send_message(message.chat.id, f"Помилка OpenAI: {e}")

# Запуск бота
bot.polling(none_stop=True)