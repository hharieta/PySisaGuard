import os
import telebot
import requests
from telebot import types
from dotenv import load_dotenv


if os.getenv('ENV') == 'DEV':
    load_dotenv()


TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "How can I help u?")


@bot.message_handler(commands=['sisa'])
def send_options(message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    bnt_yes = types.InlineKeyboardButton('Yes', callback_data='sisa_yes')
    bnt_no = types.InlineKeyboardButton('No', callback_data='sisa_no')

    markup.add(bnt_yes, bnt_no)

    bot.send_message(message.chat.id, "Do you want to know about SiSaGuard?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'sisa_yes':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "SiSaGuard is a security system that helps you to detect and prevent attacks in your network")
    elif call.data == 'sisa_no':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ok, let me know if you need something else")

@bot.message_handler(commands=['photo'])
def send_photo(message):
    url_image = "https://cdn.glitch.global/d2f60e58-9efe-4a05-bb88-fd4999848107/sisaguard.webp?v=1712221972086"
    bot.send_photo(message.chat.id, url_image, caption="SiSGuard Logo")

@bot.message_handler(func=lambda message: True)
def send_message_attacker(message):
    bot.reply_to(message, "You have been attacked by a suspicious agent")

# Generic message handler. It will reply to any message at final
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

def main():
    bot.polling(non_stop=True)

if __name__ == '__main__':
    main()
