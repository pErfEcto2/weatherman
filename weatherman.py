import time
import telebot
import requests
import logging as log
import os
import lib

#define pathes to necessary files
bot_id_path = "/home/projects/weatherman/bot_id"
gismeteo_token_path = "/home/projects/weatherman/gismeteo_token"
db_info_path = "/home/projects/weatherman/dbInfo"
creator_path = "/home/projects/weatherman/creator"

#define log format
log.basicConfig(filename="/var/log/weatherman/log.txt", level=log.INFO, format="%(asctime)s:%(message)s")
log.debug("App started!")

#define some vars
keyboard = ["покажи погоду", "шутка"]
show_geo_but = "поделиться геоположением"
cancel_but = "отмена"
help_but = "помощь"
offer_but = "/offer"
text = """Привет,
я обновился, и теперь ты можешь предложить любую функцию с помощью команды /offer и, возможно, в следующей версии она будет добавлена в этого бота.
Кроме функций можно предлагать всё, что душе угодно, например, какие-либо косметические улучшения и тп.
Так же если ты найдешь в этом боте ошибку, смело сообщай о ней с помощью той же команды.
Спасибо за использование!
P. S.
Сейчас была небольшая ошибочка, но все уже исправлено"""

#open some files
with open(bot_id_path, "r") as f:
    bot_id = f.readline().strip()

with open(gismeteo_token_path, "r") as f:
    gismeteo_token = f.readline().strip()

with open(db_info_path, "r") as f:
    db_info = f.readline().split()

with open(creator_path, "r") as f:
    creator = f.readline()

#use bot chat id
bot = telebot.TeleBot(bot_id)

#make individual keyboard with our commands
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row(*keyboard, help_but)
keyboard2 = telebot.types.ReplyKeyboardMarkup()
button_geo = telebot.types.KeyboardButton(text=show_geo_but, request_location=True)
keyboard2.row(button_geo, cancel_but)
# help button's text
helpAns = "Привет, я великий бот, показывающий погоду.\n\
Все довольно просто, у меня есть 3 кнопки:\n\
*покажи погоду*, *помощь*, *отмена*.\n\
*Первая* покажет тебе погоду в твоем районе.\n\
*Вторая* покажет это сообщение.\n\
*Третья* вернет тебя к стартовым кнопкам.\n\
В честности этого бота можешь не сомневаться, вот ссылочка на исходники [ТЫК](https://github.com/pErfEcto2/weatherman)"

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Начало работы"),
    telebot.types.BotCommand("/offer", "Предложить программисту добавить какую-либо функцию в этого бота")
])

#for chatID in lib.getChatIDs(db_info):
#    print(chatID)
#    if chatID:
#        try:
#            bot.send_message(chatID, text)
#        except Exception as e:
#            log.error(f"Error: {e}")

#bot starts with command 'start'
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я могу показывать погоду', reply_markup=keyboard1)

#main functions
@bot.message_handler(content_types=['text'])
def start(message):
    global helpAns
    #ask user about his geolocation
    if message.text == keyboard[0]:
        bot.send_message(message.chat.id, "Поделись со мной своим геоположением и я тебе скажу погоду", reply_markup=keyboard2)
    #what to do when cancel button pressed
    elif message.text == cancel_but:
        bot.send_message(message.chat.id, "Готово", reply_markup=keyboard1)
    #help message
    elif message.text == help_but:
        bot.send_message(message.chat.id, helpAns, parse_mode="Markdown", disable_web_page_preview=True)
        if message.from_user.username == creator:
            res = f"{lib.getNumUsers(db_info)} - столько людей используют этого бота."
            bot.send_message(message.chat.id, res)
    
    elif message.text == keyboard[1]:
        #joke = lib.getJoke()
        bot.send_message(message.chat.id, "Пока не работает, потому как я еще не нашел ресурс с хорошими шутками")
    
    elif message.text == offer_but:
        bot.send_message(message.chat.id, "Теперь можешь написать, что хотелось бы увидеть в этом боте или что можно исправить")
        bot.register_next_step_handler(message, lib.saveOffer, bot)

#when user sends his geolocation
@bot.message_handler(content_types=['location'])
#this function showes user's weather
def current_geo(message):
    lib.hashToDB(message, db_info)
    
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
Скорость ветра: {wind_speed_m_s} м/с или {wind_speed_km_h} км/ч. \n\
Облачность: {cloudiness}%. \n"
    if storm == False:
        res += "Грозы не будет. \n"
    else:
        res += "Возможна гроза. \n"
    res += f"Температура воздуха: {temperature_air}°С, ощущается как {temperature_comfort}°С. \n\
Вся информация предоставлена сервисом [Gismeteo](https://www.gismeteo.ru/)."
    bot.send_message(message.chat.id, res, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=keyboard1)

try:
    bot.polling()
except Exception as e:
    log.error(f"Error: {e}")
    time.sleep(15)
    log.info("Trying to restart app")
    os.system("systemctl restart weatherman.service")
