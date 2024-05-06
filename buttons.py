import telebot
from telebot import types

# Файл для хранения статичных кнопок.

# Обычные кнопки
book_list_button = types.KeyboardButton('📖 Список книг')
book_find_button = types.KeyboardButton('🔎 Поиск книг')
book_add_button = types.KeyboardButton('➕ Добавить книгу')


# Inline кнопки
genre_add_button = types.InlineKeyboardButton('➕ Добавить жанр', callback_data = 'add_genre')
filter_button = types.InlineKeyboardButton('⚙️ Выбрать жанр', callback_data = 'choose_filter')
