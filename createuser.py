import sqlite3
import hashlib


def create_user(username, password):
    # Хеширование пароля
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # Подключение к нашей базе данных
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Добавление нового пользователя
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
              (username, hashed_password))

    # Сохранение изменений и закрытие соединения с базой данных
    conn.commit()
    conn.close()


# Замените 'admin' и 'your_password' на желаемые имя пользователя и пароль
create_user('rail', '56sI7IJTn4EWrn5I3GTg')
create_user('ildar', 'fk09Kfj94nvfd8')
