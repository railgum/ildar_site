import sqlite3  # подключаем Sqlite в проект
import hashlib  # библиотека для хеширования !!! заменить на что-нибудь понадежнее !!!

from flask import Flask, render_template, redirect, url_for, request, session
# Flask - библиотека для запуска нашего приложения Flask - app
# render_template - нужен для того, чтобы ваша страница html отобразилась корректно
# redirect - понадобится для обработки запросов формы, где мы перенаправим пользователя на страницу админ панели
# url_for - вспомогательная библиотека для того, чтобы сделать правильный переход по ссылке - в нашем случае, мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и других
#

app = Flask(__name__)
app.secret_key = '5jfjkvdfsKLkds09KFM4M&4'
# КЛЮЧ ДЛЯ ХЭШИРОВАНИЯ !!! конфиг-файл !!!

# Соединение с БД


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


#  корневая страница лендинга


@app.route('/')
def home():
    # Загрузка и отображение главной страницы (landing page)
    return render_template('landing.html')


# страница формы логина в админ панель
@app.route('/adm_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        # обработка запроса к нашей форме, который имеет атрибут name="username"
        username = request.form['username']
        # обработка запроса к нашей форме, который имеет атрибут name="password"
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode(
            'utf-8')).hexdigest()  # шифруем в sha-256

        # соединение с БД
        conn = get_db_connection()

        # создаем запрос для поиска пользователя по username,
        # если такой пользователь существует, то получаем все данные id, password
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        # проверяем сходятся ли данные формы с данными БД
        if user and user['password'] == hashed_password:
            # если успешно, создаем сессию, в которую записываем id пользователя
            session['user_id'] = user['id']
            # и перенаправляем на /admin_panel
            return redirect(url_for('admin_panel'))
        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login_adm.html', error=error)


@app.route('/logout')
def logout():
    # Удаление данных пользователя из сессии
    session.clear()
    # перенаправление на главную страницу или страницу входа
    return redirect(url_for('admin_login'))


# Страница админ панели
@app.route('/admin_panel')
def admin_panel():
    # дополнительная проверка на сессию
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_panel.html')


if __name__ == '__main__':
    app.run(debug=True)
