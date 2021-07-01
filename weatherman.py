#import libs
import telebot

#define pathes to necessary files
bot_id_path = "/home/projects/weatherman/bot_id"
#define some vars
keyboard = ["/start", "/покажи погоду", "/cancel"]

#open some files
with open(bot_id_path, "r") as f:
    bot_id = f.readline().strip()

# Use bot chat id
bot = telebot.TeleBot(bot_id)

# Make individual keyboard with our commands
keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row(*keyboard)

# Bot starts with command 'start'
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я могу показывать погоду', reply_markup=keyboard1)


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == keyboard[1]:
        send = bot.send_message(message.chat.id, 'Введи место, в котором хочешь узнать погоду')
        bot.register_next_step_handler(send, fun)
    elif message.text == keyboard[2]:
        bot.send_message(message.chat.id, "Нечего пока отменять")
    else:
        bot.send_message(message.chat.id, "Я не понель(")

def fun(message):
    if message.text == "/cancel":
        bot.send_message(message.from_user.id, 'На нет и суда нет')
        return
    else:
        place = message.text
        bot.send_message(message.chat.id, place)
bot.polling()