from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from flask import Flask, request, session
from dotenv import load_dotenv
from models import db, Users, Content
from views import *
from app import app
from config import *

import hashlib  # библиотека для хеширования !!! заменить на что-нибудь понадежнее !!!
import os
import datetime
import git
import click

# Обеспечивает безопасность имён файлов, загруженных пользователями, предотвращая атаки через манипуляции с файловой системой.


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

HOST = os.getenv('MYSQL_HOST')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')
DBNAME = os.getenv('MYSQL_DBNAME')


# app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DBNAME}'

app.secret_key = os.getenv('SECRET_KEY')
path_to_save_images = os.path.join(app.root_path, 'static', 'imgs')

db.init_app(app)


# проверка расширения файла изображения
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in os.getenv('ALLOWED_EXTENSIONS')


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


# Добавление пользователя
@app.cli.command('add_user')
@click.argument('name')
@click.argument('password')
def add_user(name, password):
    new_user = Users(username=name, password=password, is_admin=True)
    db.session.add(new_user)
    db.session.commit()


@app.cli.command('add_content')
@click.argument('idblock')
@click.argument('short_title')
@click.argument('img')
@click.argument('altimg')
@click.argument('title')
@click.argument('contenttext')
@click.argument('author')
@click.argument('timestampdata')
def add_content(idblock, short_title, img, altimg, title, contenttext, author, timestampdata):
    new_content = Content(idblock=idblock, short_title=short_title, img=img, altimg=altimg,
                          title=title, contenttext=contenttext, author=author, timestampdata=timestampdata, is_active=1)
    db.session.add(new_content)
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
