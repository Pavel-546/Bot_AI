from dotenv import load_dotenv
import os
import telebot
from telebot import types
load_dotenv()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Hi, i`m bot, can i help you?') # Возвращает просто сообщение
    bot.reply_to(message, 'Hi, i`m bot, can i help you?') #-- Возвращает ответ на сообщеение!!!

bot.polling()