#import libs
import telebot
import os

#define pathes to necessary files
absolute_path = os.path.dirname(__file__)
bot_id_path = absolute_path + "/bot_id"

#define some vars
keyboard = ["/start", "покажи погоду"]
show_geo_button = "поделиться геоположением"
cancel_button = "/cancel"
user_latitude = 0
user_longitude = 0

#open some files
with open(bot_id_path, "r") as f:
    bot_id = f.readline().strip()

#use bot chat id
bot = telebot.TeleBot(bot_id)

#make individual keyboard with our commands
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row(*keyboard, cancel_button)
keyboard2 = telebot.types.ReplyKeyboardMarkup()
button_geo = telebot.types.KeyboardButton(text=show_geo_button, request_location=True)
keyboard2.row(button_geo, cancel_button)

#bot starts with command 'start'
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я могу показывать погоду', reply_markup=keyboard1)

#main functions
@bot.message_handler(content_types=['text'])
def start(message):
    #ask user about his geolocation
    if message.text == keyboard[1]:
        bot.send_message(message.chat.id, "Поделись со мной своим геоположением и я тебе скажу погоду", reply_markup=keyboard2)
    #what to do when cancel button pressed
    elif message.text == cancel_button:
        bot.send_message(message.chat.id, "Готово", reply_markup=keyboard1)
        user_latitude = 0
        user_longitude = 0
    #in another options
    else:
        bot.send_message(message.chat.id, "Я не понель(")

#when user sends his geolocation
@bot.message_handler(content_types=['location'])
#this function showes user's weather
def current_geo(message):
    res = str(message.location.latitude) + ' ' + str(message.location.longitude)
    bot.send_message(message.chat.id, res)

bot.polling()
