import time
import telebot
from telebot import types
import config
from db import DB
import buttons

# INIT
db = DB('db.db')
bot = telebot.TeleBot(config.token)

# Обработка команды /start
@bot.message_handler(commands = ['start'])
def law(message):
    try:
        # Добавляем пользователя в базу данных, если его там нет.
        if (not db.check_user(message.chat.id)):
            db.add_user(message.chat.id, message.chat.username, message.chat.first_name)

        # Формируем клавиатуру и отправляем приветственное сообщение.
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1).add(buttons.book_list_button, buttons.book_find_button, buttons.book_add_button)
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup = keyboard)

    except Exception as e:
        # Обрабатываем ошибку, в случае ее возникновения.
        print(e)
        bot.send_message(message.chat.id, '❗️ Возникла ошибка при запуске бота!\n\nПожалуйста, обратитесь в тех. поддержку: @re_dream')  

    # Обнуляем состояние.
    db.set_status(message.chat.id, '0')


@bot.message_handler(content_types = ['text'])
def law(message):
    status = db.get_status(message.chat.id)

    if message.text == '➕ Добавить книгу':
        # Предлагаем выбрать жанр книги.
        keyboard = types.InlineKeyboardMarkup()
        genres = db.get_genres()
        
        for genre in genres:
            button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
            keyboard.add(button)

        keyboard.add(buttons.genre_add_button)
        bot.send_message(message.chat.id, 'Выберите жанр книги или добавьте новый: ', reply_markup = keyboard)

    if status == 'add_genre' and message.text:
        # Добавляем жанр.
        if(not db.check_genre(message.text)):
            db.add_genre(message.text)
            keyboard = types.InlineKeyboardMarkup()
            genres = db.get_genres()
            
            for genre in genres:
                button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
                keyboard.add(button)

            keyboard.add(buttons.genre_add_button)
            bot.send_message(message.chat.id, 'Жанр успешно добавлен, теперь выберите жанр для книги:', reply_markup = keyboard)
            db.set_status(message.chat.id, '0')
        else:
            bot.send_message(message.chat.id, '❗️ Данный жанр уже существует!')
        

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    if call.data == 'add_genre':
        # Присваиваем состояние ожидания названия жанра.
        db.set_status(call.message.chat.id, 'add_genre')
        back_button = types.InlineKeyboardButton('Назад', callback_data = 'back:add_genre')
        keyboard = types.InlineKeyboardMarkup().add(back_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'Введите название нового жанра:', reply_markup = keyboard)

    # Обработка кнопок назад
    if 'back:' in call.data:
        payload = call.data.split(':')
        
        # Выбор жанра < Добавление жанра
        if payload[1] == 'add_genre':
            # Предлагаем выбрать жанр книги.
            keyboard = types.InlineKeyboardMarkup()
            genres = db.get_genres()
            
            for genre in genres:
                button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
                keyboard.add(button)

            keyboard.add(buttons.genre_add_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'Выберите жанр книги или добавьте новый: ', reply_markup = keyboard)
            db.set_status(call.message.chat.id, '0')
            
            

    


bot.polling(non_stop = True, interval = 0)

# while True:
#     try:
#         bot.polling(non_stop=True, interval=0)
#     except Exception as e:
#         print(e)
#         # Дописать логирование ошибок в txt
#         time.sleep(3)
#         continue
