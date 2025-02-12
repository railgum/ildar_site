from flask import Flask, render_template, redirect, url_for, request
# Flask - библиотека для запуска нашего приложения Flask - app
# render_template - нужен для того, чтобы ваша страница html отобразилась корректно
# redirect - понадобится для обработки запросов формы, где мы перенаправим пользователя на страницу админ панели
# url_for - вспомогательная библиотека для того, чтобы сделать правильный переход по ссылке - в нашем случае, мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и других
#

app = Flask(__name__)

#  наша корневая страиницу лендинга


@app.route('/')
def home():
    # Загрузка и отображение главной страницы (landing page)
    return render_template('landing.html')


# страница формы логина в админ панель
@app.route('/adm_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        # Если аутентификация прошла успешно, перенаправляем на /admin_panel
        return redirect(url_for('admin_panel'))
    # Если GET запрос, показываем форму входа
    return render_template('login_adm.html')

# Страница админ панели


@app.route('/admin_panel')
def admin_panel():
    # Загрузка и отображение админ панели
    return render_template('admin_panel.html')


if __name__ == '__main__':
    app.run(debug=True)
