from mysql.connector import connect, Error
from flask_mysqldb import MySQL
from PIL import Image, ImageOps, ImageGrab
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, session
# import sqlite3  # подключаем Sqlite в проект
import hashlib  # библиотека для хеширования !!! заменить на что-нибудь понадежнее !!!
import os
import datetime
import git

# Обеспечивает безопасность имён файлов, загруженных пользователями, предотвращая атаки через манипуляции с файловой системой.

# Flask - библиотека для запуска нашего приложения Flask - app
# render_template - нужен для того, чтобы ваша страница html отобразилась корректно
# redirect - понадобится для обработки запросов формы, где мы перенаправим пользователя на страницу админ панели
# url_for - вспомогательная библиотека для того, чтобы сделать правильный переход по ссылке - в нашем случае, мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и других
#

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
path_to_save_images = os.path.join(app.root_path, 'static', 'imgs')
HOST = os.getenv('MYSQL_HOST')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')
DBNAME = os.getenv('MYSQL_DBNAME')


mysql = MySQL(app)

# Соединение с БД


def get_db_connection():
    try:
        with connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DBNAME
        ) as conn:
            return conn.cursor()
    except Error as e:
        return e
    # conn.row_factory = conn.Row
    # return conn


# проверка расширения файла изображения
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Функция обработки изображения
def process_img_file(file, short_title):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(
            path_to_save_images, f'{short_title}/{filename}')
        imgpath = f'/static/imgs/{short_title}/' + filename
        file = Image.open(file)

        # Обработка загруженного файла
        if short_title == SLIDER:
            file = ImageOps.fit(file, MAX_SIZE_SLIDER, centering=(0.5, 0.5))
        elif short_title == MINICARDS:
            file = ImageOps.fit(file, MAX_SIZE_MINICARDS, centering=(0.5, 0.5))
        elif short_title == FEATURETTE:
            file = ImageOps.fit(file, MAX_SIZE_FEATURETTE,
                                centering=(0.5, 0.5))
        file.save(save_path)
        return imgpath
    else:
        return None


# получение одного значения из БД по ID
def getOneValueFromBase(connection, data, database, dataId: int):
    c = connection.cursor()
    c.execute(f'SELECT {data} FROM {database} WHERE id = ?', (dataId, ))
    result = c.fetchone()
    if result:
        return result[0]


#  корневая страница лендинга
@app.route('/')
def home():
    conn = get_db_connection()
    # Получаем все записи из таблицы content
    blocks = conn.execute('SELECT * FROM content').fetchall()
    conn.close()
    # Преобразование данных из БД в список словарей
    blocks_list = [dict(ix) for ix in blocks]

    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks_list:
        # Создание новой записи, если ключ еще не существует
        if raw['idblock'] not in json_data:
            json_data[raw['idblock']] = []

        # Добавление данных в существующий ключ
        if raw['is_active'] == 0:
            continue
        else:
            json_data[raw['idblock']].append({
                'id': raw['id'],
                'short_title': raw['short_title'],
                'img': raw['img'],
                'altimg': raw['altimg'],
                'title': raw['title'],
                'contenttext': raw['contenttext'],
                'author': raw['author'],
                'timestampdata': raw['timestampdata'],
                'is_active': raw['is_active']
            })
    context = {'json_data': json_data,
               'SLIDER_ID': SLIDER_ID,
               'MINICARDS_ID': MINICARDS_ID,
               'FEATURETTE_ID': FEATURETTE_ID,
               'FOOTER_ID': FOOTER_ID}

    # Загрузка и отображение главной страницы (landing page)
    return render_template('landing.html', **context)


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
            # проверяем активен ли пользователь
            if not user['is_admin']:
                error = 'Пользователь заблокирован'
                return render_template('login_adm.html', error=error)
            else:
                # если успешно, создаем сессию, в которую записываем id пользователя
                session['user_id'] = user['id']
                # и перенаправляем на /admin_panel
                return redirect(url_for('admin_panel'))
        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login_adm.html', error=error)


# Выход из админки
@app.route('/logout')
def logout():
    # Удаление данных пользователя из сессии
    session.clear()
    # перенаправление на главную страницу или страницу входа
    return redirect(url_for('home'))


# Страница админ панели
@app.route('/admin_panel')
def admin_panel():
    # дополнительная проверка на сессию
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    # Получаем все записи из таблицы content
    blocks = conn.execute('SELECT * FROM content').fetchall()
    # name_admin = getName(conn, session['user_id'])
    name_admin = getOneValueFromBase(
        conn, 'username', 'users', session['user_id'])
    conn.close()

    # Преобразование данных из БД в список словарей
    blocks_list = [dict(ix) for ix in blocks]
    # print(blocks_list) [{строка 1 из бд},{строка 2 из бд},{строка 3 из бд}, {строка 4 из бд}]
    # Теперь нужно сделать группировку списка в один словарь json
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks_list:
        # Создание новой записи, если ключ еще не существует
        if raw['idblock'] not in json_data:
            json_data[raw['idblock']] = []

        json_data[raw['idblock']].append({
            'id': raw['id'],
            'short_title': raw['short_title'],
            'img': raw['img'],
            'altimg': raw['altimg'],
            'title': raw['title'],
            'contenttext': raw['contenttext'],
            'author': raw['author'],
            'timestampdata': raw['timestampdata'],
            'is_active': raw['is_active']
        })
    context = {
        'json_data': json_data,
        'name_admin': name_admin,
    }
    # print(json_data)
    # передаем json на фронт - далее нужно смотреть admin_panel.html и обрабатывать там
    return render_template('admin_panel.html', **context)


# Обновление информации
@app.route('/update_content', methods=['POST'])
def update_content():
    short_title = request.form['short_title']
    altimg = 'Photo'
    author_id = request.form['user_id']
    date_time = datetime.datetime.now().strftime('%d/%m/%y %H:%M')
    idblock = request.form['id_block']
    title = request.form['title']
    contenttext = request.form['contenttext']

    conn = get_db_connection()
    cursor = conn.cursor()
    author = getOneValueFromBase(conn, 'username', 'users', author_id)

    if 'new_item' in request.form:
        new_title = request.form['new_title']
        new_contenttext = request.form['new_contenttext']
        new_img_file = request.files['new_img']
        imgpath = process_img_file(new_img_file, short_title)
        cursor.execute('INSERT INTO content (idblock, short_title, img, altimg, title, contenttext, author, timestampdata, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (idblock, short_title, imgpath, altimg, new_title, new_contenttext, author, date_time, True))
    elif 'deactivate' in request.form:
        content_id = request.form['id']
        cursor.execute(
            'UPDATE content SET is_active=FALSE WHERE id=?', (content_id,))
    elif 'activate' in request.form:
        content_id = request.form['id']
        cursor.execute(
            'UPDATE content SET is_active=True WHERE id=?', (content_id,))
    else:
        content_id = request.form['id']
        file = request.files['img']
        imgpath = process_img_file(file, short_title)
        if file:
            cursor.execute('UPDATE content SET short_title=?, img=?, altimg=?, title=?, contenttext=?, author=?, timestampdata=?, is_active=? WHERE id=?',
                           (short_title, imgpath, altimg, title, contenttext, author, date_time, True, content_id))
        else:
            cursor.execute('UPDATE content SET short_title=?, altimg=?, title=?, contenttext=?, author=?, timestampdata=?, is_active=? WHERE id=?',
                           (short_title, altimg, title, contenttext, author, date_time, True, content_id))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_panel'))


@app.route('update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/railgum/ildar_site.git')
        origin = repo.remotes.origin

        origin.pull()

        return 'Updated PythonAnyWhere successfully!', 200
    else:
        return 'Wrong event type', 400


if __name__ == '__main__':
    app.run(debug=False)
