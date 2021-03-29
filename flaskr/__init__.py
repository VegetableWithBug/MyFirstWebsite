import os

from flask import (
    Flask,Blueprint, flash, g, redirect, render_template, request, session, url_for,jsonify,json,Response
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from functools import wraps

from . import db

from . import auth

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

    
    db.init_app(app)
    app.jinja_env.variable_start_string = '{['
    app.jinja_env.variable_end_string = ']}'

    
    #app.register_blueprint(auth.bp)


    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('login'))
        return wrap

    
    @app.route('/')
    @login_required
    def home():
        return redirect(url_for('hello'))

    
    @app.route('/hello',methods=('GET', 'POST'))
    @login_required
    def hello():
        return render_template('hello.html')

    @app.route('/analyze',methods=('GET', 'POST'))
    @login_required
    def analyze():
        if request.method == 'POST':
            code=-1
            data=json.loads(request.get_data())
            print(data)
            json_data={
                'code':code,
            }
            answer=json.dumps(json_data)
            return(Response(response=answer))
        elif request.method == 'GET':
            return render_template('analyze.html')


    @app.route('/settings')
    def settings():
        return render_template('settings.html')

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
            code=-1
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
                    session['logged_in'] = True
                    session['user_id'] = user['id']
                    code=1
            
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
                    elif user_email is not None:
                        error = '邮箱已被注册！'
                    elif error is None:
                        db.execute(
                            'INSERT INTO user (email,username, password) VALUES (?, ? , ?)',
                            (email, username, generate_password_hash(password))
                        )
                        db.commit()
                        """
                        x=db.execute(
                            'SELECT id FROM user WHERE username = ?', (username,)
                        )
                        db.commit()
                        db.execute(
                            'INSERT INTO settings (author_id,setting_name,is_choose,header_L,header_a,header_b,header_magenta ,header_yellow ,cyan_standard,magenta_standard ,yellow_standard ,black_standard ,cyan_expend ,magenta_expend,yellow_expend ,black_expend ,cyan_L ,cyan_a ,cyan_b ,magenta_L ,magenta_a ,magenta_b ,yellow_L ,yellow_a ,yellow_b ,black_L ,black_a ,black_b ,header_density_difference ,header_difference ,middle_expend ,four_expend ,field_density ,field_density_consistency ,four_defference ,gray_banlance ,de_standard ,ink_number) VALUES (?,'默认参数',1,50.6,38.5,20.8,0.8,0.8,0.87,0.87,0.85,1.05,17,17,17,17,57,-23,-27,53,48,0,79,-5,60,40,1,4,20,20,20,40,20,0,20,20,0.39,32)',(x,)
                        )
                        db.commit()
                        """
                        error='注册成功！'
            data={
                'code':code,
                'msg':error
            }
            answer=json.dumps(data)
            return(Response(response=answer))
        elif request.method == 'GET':
            return render_template('login0.html')

    return app

    