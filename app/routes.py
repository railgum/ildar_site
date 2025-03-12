from flask import render_template, flash, redirect, url_for, request
from models import db, Content, User
from app import app
from app.forms import LoginForm
from config import *


# render_template - нужен для того, чтобы ваша страница html отобразилась корректно
# redirect - понадобится для обработки запросов формы, где мы перенаправим пользователя на страницу админ панели
# url_for - вспомогательная библиотека для того, чтобы сделать правильный переход по ссылке - в нашем случае, мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и других


#  корневая страница лендинга
@app.route('/')
def home():
    # получить все записи из БД
    blocks = Content.query.all()

    # Группировка данных в словарь JSON (jsonify?)
    json_data = {}
    for raw in blocks:
        # Создание новой записи, если ключ еще не существует
        if 'idblock' not in json_data:
            json_data['idblock'] = []
        # Добавление данных в существующий ключ
        if 'is_active' == 0:
            continue
        else:
            json_data['idblock'].append({
                'id': raw.id,
                'short_title': raw.short_title,
                'img': raw.img,
                'altimg': raw.altimg,
                'title': raw.title,
                'contenttext': raw.contenttext,
                'author': raw.author,
                'timestampdata': raw.timestampdata,
                'is_active': raw.is_active
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
        # conn = get_db_connection()
        user = User.query.filter(User.username == username).first()

        # проверяем сходятся ли данные формы с данными БД
        if user:
            # проверяем активен ли пользователь
            if not user.is_admin:
                error = 'Пользователь заблокирован'
                return render_template('login_adm.html', error=error)
            else:
                # если успешно, создаем сессию

                db.session.add(user)
                db.session.commit()
                # и перенаправляем на /admin_panel
                return redirect(url_for('admin_panel'))
        else:
            error = 'Неправильное имя пользователя или пароль'

    return render_template('login_adm.html', error=error)


# Выход из админки
@app.route('/logout')
def logout():
    # Удаление данных пользователя из сессии
    db.session.clear()
    # перенаправление на главную страницу или страницу входа
    return redirect(url_for('home'))


# Страница админ панели
@app.route('/admin_panel')
def admin_panel():
    # дополнительная проверка на сессию
    if 'user_id' not in db.session:
        return redirect(url_for('admin_login'))
    # conn = get_db_connection()
    # Получаем все записи из таблицы content
    # blocks = conn.execute('SELECT * FROM content').fetchall()
    blocks = Content.query.all()
    # name_admin = getName(conn, session['user_id'])
    name_admin = db.session.query(User).filter
    # name_admin = getOneValueFromBase(
    #     conn, 'username', 'users', session['user_id'])
    # conn.close()

    # Преобразование данных из БД в список словарей
    # blocks_list = [dict(ix) for ix in blocks]
    # print(blocks_list) [{строка 1 из бд},{строка 2 из бд},{строка 3 из бд}, {строка 4 из бд}]
    # Теперь нужно сделать группировку списка в один словарь json
    # Группировка данных в словарь JSON
    json_data = {}
    for raw in blocks:
        # Создание новой записи, если ключ еще не существует
        if raw.idblock not in json_data:
            json_data[raw.idblock] = []

        json_data[raw.idblock].append({
            'id': raw.id,
            'short_title': raw.short_title,
            'img': raw.img,
            'altimg': raw.altimg,
            'title': raw.title,
            'contenttext': raw.contenttext,
            'author': raw.author,
            'timestampdata': raw.timestampdata,
            'is_active': raw.is_active
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

    # conn = get_db_connection()
    # cursor = conn.cursor()
    # author = getOneValueFromBase(conn, 'username', 'users', author_id)
    author = Users.query.filter_by(user_id=author_id).first()

    if 'new_item' in request.form:
        new_title = request.form['new_title']
        new_contenttext = request.form['new_contenttext']
        new_img_file = request.files['new_img']
        imgpath = process_img_file(new_img_file, short_title)
        # cursor.execute('INSERT INTO content (idblock, short_title, img, altimg, title, contenttext, author, timestampdata, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        #                (idblock, short_title, imgpath, altimg, new_title, new_contenttext, author, date_time, True))
        new_item = Content(idblock=idblock, short_title=short_title, img=imgpath, altimg=altimg, title=new_title,
                           contenttext=new_contenttext, author=author.username, timestampdata=date_time, is_active=True)
        db.session.add(new_item)
        db.session.commit()
    elif 'deactivate' in request.form:
        content_id = request.form['id']
        # cursor.execute(
        #     'UPDATE content SET is_active=FALSE WHERE id=?', (content_id,))
        deact_cont = Content.query.filter_by(id=content_id).first()
        deact_cont.is_active = False
        db.session.commit()
    elif 'activate' in request.form:
        content_id = request.form['id']
        act_cont = Content.query.filter_by(id=content_id).first()
        act_cont.is_active = True
        db.session.commit()
    else:
        content_id = request.form['id']
        file = request.files['img']
        imgpath = process_img_file(file, short_title)
        new_cont = Content.query.filter_by(id=content_id).first()
        new_cont.title = title
        new_cont.contenttext = contenttext
        new_cont.timestampdata = date_time
        if file:
            # cursor.execute('UPDATE content SET short_title=?, img=?, altimg=?, title=?, contenttext=?, author=?, timestampdata=?, is_active=? WHERE id=?',
            #                (short_title, imgpath, altimg, title, contenttext, author, date_time, True, content_id))

            new_cont.img = imgpath
        # else:
            # cursor.execute('UPDATE content SET short_title=?, altimg=?, title=?, contenttext=?, author=?, timestampdata=?, is_active=? WHERE id=?',
            #    (short_title, altimg, title, contenttext, author, date_time, True, content_id))

        db.session.commit()

    return redirect(url_for('admin_panel'))


@app.route('/update_server', methods=['POST'])
def webhook():
    if request.method == 'POST':
        repo = git.Repo('https://github.com/railgum/ildar_site.git')
        origin = repo.remotes.origin

        origin.pull()

        return 'Updated PythonAnyWhere successfully!', 200
    else:
        return 'Wrong event type', 400
