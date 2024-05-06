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
        bot.send_message(message.chat.id, '🏠 Привет!\n\nБот представляет собой базу управления книгами в библиотеке. Пользователь может добавить и удалять книгу. У книг должны имеются жанры. Вы имеете возможность поиска книги по названию и/или автору.', reply_markup = keyboard)
    except Exception as e:
        # Обрабатываем ошибку, в случае ее возникновения.
        print(e)
        bot.send_message(message.chat.id, '⚠️ Возникла ошибка при запуске бота!\n\nПожалуйста, обратитесь в тех. поддержку: @re_dream')  

    # Обнуляем состояние.
    db.set_status(message.chat.id, '0')

@bot.message_handler(content_types = ['text'])
def law(message):
    status = db.get_status(message.chat.id)

    if status == '0':
        if message.text == '➕ Добавить книгу':
            # Предлагаем выбрать жанр для книги, которую необходимо добавить.
            keyboard = types.InlineKeyboardMarkup()
            genres = db.get_all_genres()
            
            # Формируем клавиатуру из строк жанров, полученных из БД.
            for genre in genres:
                button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
                keyboard.add(button)

            # Добавляем кнопку "Добавить жанр" и отправляем сообщение.
            keyboard.add(buttons.genre_add_button)
            bot.send_message(message.chat.id, '🔹 Выберите жанр книги или добавьте новый: ', reply_markup = keyboard)

        elif message.text == '📖 Список книг':
            # Выводим список всех книг.
            books = db.get_all_books()
            keyboard = types.InlineKeyboardMarkup()

            # Формируем клавиатуру из книг, полученных из БД.
            for book in books:
                button = types.InlineKeyboardButton('📕 "' + book[1] + '", ' + str(book[2]), callback_data = 'book_chosen:' + str(book[0]))
                keyboard.add(button)

            # Добавляем кнопку "Выбрать жанр" и отправляем сообщение.
            keyboard.add(buttons.filter_button)
            bot.send_message(message.chat.id, '🔹 Книг найдено: ' + str(len(books)) +'\n\n🔹 Выберите книгу из списка: ', reply_markup = keyboard)

        elif message.text == '🔎 Поиск книг':
            # Задаем статус, предлагаем ввести ключевые слова для поиска.
            db.set_status(message.chat.id, 'book_search')
            cancel_button = types.InlineKeyboardButton('❌ Отмена', callback_data = 'cancel_search')
            keyboard = types.InlineKeyboardMarkup().add(cancel_button)
            bot.send_message(message.chat.id, '🔹 Введите ключевое слово для поиска по автору/названию книги: ', reply_markup = keyboard)

    elif status == 'book_search' and message.text:
        books = db.search_books(message.text)
        
        # Проверяем наличие результатов поиска.
        if len(books) >= 1:
            keyboard = types.InlineKeyboardMarkup()

            # Формируем клавиатуру из книг, полученных из БД.
            for book in books:
                button = types.InlineKeyboardButton('📕 "' + book[1] + '", ' + str(book[2]), callback_data = 'book_chosen:' + str(book[0]))
                keyboard.add(button)

            # Добавляем кнопку "Выбрать жанр" и отправляем сообщение.
            bot.send_message(message.chat.id, '🔹 Книг найдено: ' + str(len(books)) +'\n\n🔹 Результаты поиска: ', reply_markup = keyboard)
        else:
            bot.send_message(message.chat.id, '⚠️ По вашему запросу не было найдено книг!')

        db.set_status(message.chat.id, '0')

    # Добавляем жанр.
    elif status == 'add_genre' and message.text:
        # Проверяем существование такого жанра в БД.
        if(not db.check_genre(message.text)):
            # Вносим жанр в БД.
            db.add_genre(message.text)
            keyboard = types.InlineKeyboardMarkup()
            genres = db.get_all_genres()
            
            # Формируем клавиатуру из строк жанров, полученных из БД.
            for genre in genres:
                button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
                keyboard.add(button)

            # Добавляем кнопку "Добавить жанр" и отправляем сообщение, обнуляем статус.
            keyboard.add(buttons.genre_add_button)
            bot.send_message(message.chat.id, '☑️ Жанр успешно добавлен, теперь выберите жанр для книги:', reply_markup = keyboard)
            db.set_status(message.chat.id, '0')
        else:
            bot.send_message(message.chat.id, '⚠️ Данный жанр уже существует!')

    # Добавляем книгу.
    elif 'add_book:' in status and message.text:
        # Получаем свойства книги из состояния и сообщения.
        payload = status.split(':')[1]
        book = message.text.split('\n\n', 2)

        # Проверка соответствия формата
        if len(book) == 3:
            # Добавляем книгу в базу данных, отправляем сообщение.
            db.add_book(book[0], book[1], book[2], payload)
            bot.send_message(message.chat.id, '☑️ Книга успешно добавлена!')
            db.set_status(message.chat.id, '0') 
        else: 
            bot.send_message(message.chat.id, '⚠️ Ваше сообщение не соответствует указанному формату!')

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    # Добавить жанр
    if call.data == 'add_genre':
        # Присваиваем состояние ожидания названия жанра.
        db.set_status(call.message.chat.id, 'add_genre')
        back_button = types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back:genre_list')
        keyboard = types.InlineKeyboardMarkup().add(back_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 Введите название нового жанра:', reply_markup = keyboard)
        
    # Отменить поиск
    if call.data == 'cancel_search':
        db.set_status(call.message.chat.id, '0')
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '⚠️ Поиск отменен!')

    # Выбран жанр для добавления книги.
    elif 'genre_chosen:' in call.data:
        # Получаем id жанра.
        payload = call.data.split(':')[1]

        # Задаем статус ожидания книги, передаем в него выбранный жанр и редактируем сообщение.
        db.set_status(call.message.chat.id, 'add_book:' + str(payload))
        back_button = types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back:genre_list')
        keyboard = types.InlineKeyboardMarkup().add(back_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 *Введите информацию о книге в следующем формате:*\n\n`Название книги\n\nАвтор книги\n\nОписание книги`', reply_markup = keyboard, parse_mode = 'markdown')

    # Выбрана книга.
    elif 'book_chosen:' in call.data:
        # Получаем информацию о книге
        payload = call.data.split(':')[1]
        book = db.get_book(payload)
        genre = db.get_genre_name(book[4])

        # Формируем клавиатуру и сообщение с информацией, отправляем
        delete_button = types.InlineKeyboardButton('🗑 Удалить', callback_data = 'delete_book:' + str(book[0]))
        back_button = types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back:book_list')
        keyboard = types.InlineKeyboardMarkup(row_width = 1).add(delete_button, back_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '📖 *Информация о книге.\n\nНазвание:* ' + book[1] + '\n\n*Автор:* ' + book[2] + '\n\n*Жанр:* ' + genre + '\n\n*Описание:* ' + book[3], parse_mode = 'markdown', reply_markup = keyboard)

    # Удаление книги
    elif 'delete_book:' in call.data:
        payload = call.data.split(':')[1]
        db.delete_book(payload)
        back_button = types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back:book_list')
        keyboard = types.InlineKeyboardMarkup().add(back_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = 'Книга успешно удалена!', reply_markup = keyboard)

    # Меню выбора фильтра по жанру
    elif call.data == 'choose_filter':
        keyboard = types.InlineKeyboardMarkup()
        genres = db.get_all_genres()
            
        # Формируем клавиатуру из строк жанров, полученных из БД.
        for genre in genres:
            button = types.InlineKeyboardButton(genre[1], callback_data = 'filter_chosen:' + str(genre[0]))
            keyboard.add(button)

        # Добавляем кнопку "Очистить фильтр" и отправляем сообщение.
        clear_filter_button = types.InlineKeyboardButton('🗑 Очистить фильтр', callback_data = 'back:book_list')
        keyboard.add(clear_filter_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 Выберите жанр из списка:', reply_markup = keyboard)

    # Выбран фильтр
    elif 'filter_chosen:' in call.data:
        payload = call.data.split(':')[1]
        books = db.get_genre_books(payload)
        genre_name = db.get_genre_name(payload)

        keyboard = types.InlineKeyboardMarkup()

        # Формируем клавиатуру из книг, полученных из БД.
        for book in books:
            button = types.InlineKeyboardButton('📕 "' + book[1] + '", ' + str(book[2]), callback_data = 'book_chosen:' + str(book[0]))
            keyboard.add(button)

        # Добавляем кнопку "Выбрать жанр" и отправляем сообщение.
        keyboard.add(buttons.filter_button)
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 Книг найдено: ' + str(len(books)) + '\n\n🔹 Применен фильтр по жанру "' + genre_name + '"\n\n🔹 Выберите книгу из списка:', reply_markup = keyboard)

    # Обработка кнопок возврата.
    elif 'back:' in call.data:
        payload = call.data.split(':')[1]
        
        # Выбор жанра < Добавление жанра | Выбор жанра < Добавление книги
        if payload == 'genre_list':
            # Предлагаем выбрать жанр книги.
            keyboard = types.InlineKeyboardMarkup()
            genres = db.get_all_genres()
            
            for genre in genres:
                button = types.InlineKeyboardButton(genre[1], callback_data = 'genre_chosen:' + str(genre[0]))
                keyboard.add(button)

            keyboard.add(buttons.genre_add_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 Выберите жанр книги или добавьте новый: ', reply_markup = keyboard)
            db.set_status(call.message.chat.id, '0')

        # Выбор книги < Информация о книге | Выбор книги < Выбор фильтра
        elif payload == 'book_list':
            # Выводим список всех книг.
            books = db.get_all_books()
            keyboard = types.InlineKeyboardMarkup()

            # Формируем клавиатуру из книг, полученных из БД.
            for book in books:
                button = types.InlineKeyboardButton('📕 "' + book[1] + '", ' + str(book[2]), callback_data = 'book_chosen:' + str(book[0]))
                keyboard.add(button)

            # Добавляем кнопку "Выбрать жанр" и отправляем сообщение.
            keyboard.add(buttons.filter_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '🔹 Книг найдено: ' + str(len(books)) + '\n\n🔹 Выберите книгу из списка: ', reply_markup = keyboard)


# Украсить все эмодзями !!!!!!!!!!!!!!!!!!!!!!!!
# Составить инструкцию на гитхабе !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

bot.polling(non_stop = True, interval = 0)

# while True:
#     try:
#         bot.polling(non_stop = True, interval = 0)
#     except Exception as e:
#         print(e)
#         # Дописать логирование ошибок в txt                         
#         time.sleep(3)
#         continue
