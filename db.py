import sqlite3
import threading

lock = threading.Lock()



class DB:
	def __init__(self, database):

		self.connection = sqlite3.connect(database, check_same_thread = False)
		self.cursor = self.connection.cursor()

	def check_user(self, uid):
		# Проверка на наличие пользователя в БД.
		with self.connection:
			with lock:
				result = self.cursor.execute('SELECT * FROM `user` WHERE `uid` = ?', (uid,)).fetchall()
				return bool(len(result))

	def add_user(self, uid, un, name):
		# Добавление пользователя в БД.
		with self.connection:
			with lock:
				return self.cursor.execute("INSERT INTO `user` (`uid`, `un`, `name`) VALUES(?,?,?)", (uid, un, name,))

	def get_user(self, uid):
		# Получение строки пользователя по ID.
		with self.connection:
			with lock:
				result = self.cursor.execute('SELECT * FROM `user` WHERE `uid` = ?', (uid,)).fetchone()
				return result

	def get_limit_users(self, limit):
		# Получение всех строк пользователей с указанным лимитом.
		with self.connection:
			with lock:
				result = self.cursor.execute('SELECT * FROM `user` LIMIT ' + str(limit)).fetchall()
				return result

	def set_status(self, uid, status):
		# Присвоение состояния пользователю.
		with self.connection:
			with lock:
				return self.cursor.execute("UPDATE `user` SET `status` = ? WHERE `uid` = ?", (status, uid,))

	def get_status(self, uid):
		# Получения статуса пользователя.
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT `status` FROM `user` WHERE `uid` = ?", (uid,)).fetchone()[0]
			
	def add_genre(self, name):
		# Добавление пользователя в БД.
		with self.connection:
			with lock:
				return self.cursor.execute("INSERT INTO `genres` (`name`) VALUES(?)", (name,))
		
	def check_genre(self, name):
		# Проверка на наличие пользователя в БД.
		with self.connection:
			with lock:
				result = self.cursor.execute('SELECT * FROM `genres` WHERE `name` = ?', (name,)).fetchall()
				return bool(len(result))
	
	def get_all_genres(self):
		# Получение всех строк жанров.
		with self.connection:
			with lock:
				request = 'SELECT * FROM `genres`'
				result = self.cursor.execute(request).fetchall()
				return result
			
	def get_genre_name(self, id):
		# Получения статуса пользователя.
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT `name` FROM `genres` WHERE `id` = ?", (id,)).fetchone()[0]
			
	def add_book(self, title, author, description, genre_id):
		# Добавление пользователя в БД.
		with self.connection:
			with lock:
				return self.cursor.execute("INSERT INTO `books` (`title`, `author`, `description`, `genre_id`) VALUES(?,?,?,?)", (title, author, description, genre_id,))
			
	def get_all_books(self):
		# Получения списка всех книг.
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT * FROM `books`").fetchall()
			
	def get_book(self, id):
		# Получения статуса пользователя.
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT * FROM `books` WHERE `id` = ?", (id,)).fetchone()
			
	def delete_book(self, id):
		with self.connection:
			with lock:
				return self.cursor.execute("DELETE FROM books WHERE `id` = ?", (id,)).fetchone()
			
	def get_genre_books(self, genre_id):
		# Получения списка всех книг.
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT * FROM `books` WHERE `genre_id` = ?", (genre_id,)).fetchall()
			
	def search_books(self, keyword):
		# Получения списка книг, найденных по ключевому слову.
		keyword = '%' + keyword + '%'
		with self.connection:
			with lock:
				return self.cursor.execute("SELECT * FROM `books` WHERE `author` LIKE ? OR `title` LIKE ?", (keyword, keyword,)).fetchall()