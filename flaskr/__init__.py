import os

from flask import (
    Flask,Blueprint, flash, g, redirect, render_template, request, session, url_for,jsonify,json,Response
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#venv\Scripts\activate
#$env:FLASK_APP = "flaskr"
#$env:FLASK_ENV = "development"
#flask run


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return render_template('hello.html')

    @app.route('/analyze')
    def analyze():
        return render_template('analyze.html')


    @app.route('/sheet')
    def sheet():
        return render_template('SheetJS.html')

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()

    @app.route('/login',methods=('GET', 'POST'))
    def login():
        if request.method == 'POST':
            error = None
            text=json.loads(request.get_data())
            if(text['type']=="login"):
                username = text['username']
                password = text['password']
                db = get_db()
                user = db.execute(
                    'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

                if user is None:
                    error = '用户名不存在！'
                elif not check_password_hash(user['password'], password):
                    error = '密码错误！'

                elif error is None:
                    session.clear()
                    session['user_id'] = user['id']
                    return redirect(url_for('hello'))
            
            elif(text['type']=="register"):
                email=text['email']
                username=text['username']
                password=text['password']
                passwordrepeat=text['passwordrepeat']
                
                
                if(email.isspace() or len(email)==0):
                    error = '邮箱输入不能为空！'
                elif(username.isspace() or len(username)==0):
                    error = '用户名输入不能为空！'
                elif(password.isspace() or len(password)<4):
                    error = '密码格式错误！'
                elif(password!=passwordrepeat):
                    error = '两次密码输入不一致！'
                else:
                    db = get_db()
                    user = db.execute(
                        'SELECT * FROM user WHERE username = ?', (username,)
                    ).fetchone()
                    user_email = db.execute(
                        'SELECT * FROM user WHERE email = ?', (email,)
                    ).fetchone()
                    if user is not None:
                        error = '用户名已经存在！'
                    elif email is not None:
                        error = '邮箱已被注册！'
                    elif error is None:
                        db.execute(
                            'INSERT INTO user (email,username, password) VALUES (?, ? , ?)',
                            (email, username, generate_password_hash(password))
                        )
                        db.commit()
                        error='注册成功！'
            return(Response(response=error,content_type='text/plain;charset=utf-8'))
        if request.method == 'GET':
            return render_template('login0.html')

    return app

    