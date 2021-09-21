#import libs
#from time import clock_gettime
import time
import telebot
import requests
import logging
import os

#define pathes to necessary files
bot_id_path = "/home/projects/weatherman/bot_id"
gismeteo_token_path = "/home/projects/weatherman/gismeteo_token"

#define some vars
keyboard = ["покажи погоду"]
show_geo_button = "поделиться геоположением"
cancel_button = "/cancel"
help_but = "/help"
user_latitude = 0
user_longitude = 0

#define logging format
logging.basicConfig(filename="/var/log/weatherman/log.txt", level=logging.DEBUG, format="%(asctime)s:%(message)s")
logging.debug("App started!")

#open some files
with open(bot_id_path, "r") as f:
    bot_id = f.readline().strip()

with open(gismeteo_token_path, "r") as f:
    gismeteo_token = f.readline().strip()

#use bot chat id
bot = telebot.TeleBot(bot_id)

#make individual keyboard with our commands
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row(*keyboard, help_but, cancel_button)
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
    if message.text == keyboard[0]:
        bot.send_message(message.chat.id, "Поделись со мной своим геоположением и я тебе скажу погоду", reply_markup=keyboard2)
    #what to do when cancel button pressed
    elif message.text == cancel_button:
        bot.send_message(message.chat.id, "Готово", reply_markup=keyboard1)
        user_latitude = 0
        user_longitude = 0
    #in another options
    elif message.text == help_but:
        res = "Привет, я великий бот, показывающий погоду.\n\
Все довольно просто, у меня есть 3 кнопки:\n\
\"покажи погоду\", \"/help\", \"/cancel\".\n\
Первая покажет тебе погоду в твоем районе.\n\
Вторая покажет это окно.\n\
Третьей ты можешь вернуться к стартовым кнопкам."
        bot.send_message(message.chat.id, res)
    else:
        bot.send_message(message.chat.id, "Я не понель(")

#when user sends his geolocation
@bot.message_handler(content_types=['location'])
#this function showes user's weather
def current_geo(message):
    get_req = f"https://api.gismeteo.net/v2/weather/current/?latitude={str(message.location.latitude)}&longitude={str(message.location.longitude)}"
    get_headers = {"X-Gismeteo-Token": gismeteo_token}
    response = requests.get(get_req, headers=get_headers)
    json_response = response.json()
    pressure = json_response["response"]["pressure"]["mm_hg_atm"]
    humidity = json_response["response"]["humidity"]["percent"]
    wind_speed_km_h = json_response["response"]["wind"]["speed"]["km_h"]
    wind_speed_m_s = json_response["response"]["wind"]["speed"]["m_s"]
    cloudiness = json_response["response"]["cloudiness"]["percent"]
    storm = json_response["response"]["storm"]
    temperature_air = json_response["response"]["temperature"]["air"]["C"]
    temperature_comfort = json_response["response"]["temperature"]["comfort"]["C"]
    description = json_response["response"]["description"]["full"].lower()
    res = f"На улице у вас {description}. \n\
Давление: {pressure} мм ртутного столба. \n\
Влажность: {humidity}%. \n\
Скорость ветра: {wind_speed_km_h} км/ч или {wind_speed_m_s} м/с. \n\
Облачность: {cloudiness}%. \n\
"
    if storm == False:
        res += "Грозы не будет. \n\
"
    else:
        res += "Возможна гроза. \n\
"
    res += f"Температура воздуха: {temperature_air}°С, ощущается как {temperature_comfort}°С. \n\
Вся информация предоставлена сервисом [Gismeteo](https://www.gismeteo.ru/)."
    bot.send_message(message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=keyboard1)

try:
    bot.polling()
except Exception as e:
    logging.debug(f"Error: {e}")
    time.sleep(15)
    os.system("systemctl restart weatherman.service")
