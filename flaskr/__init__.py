import os
from flask import (
    Flask,Blueprint, flash, g, redirect, render_template, request, session, url_for,jsonify,json,Response
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from functools import wraps
from . import db
from . import auth
#from . import score
from math import sqrt,pow
#from score import (score_one,score_two,get_density_score,get_difference_score,get_expend_score,get_gray_score,get_header_density_score,get_header_difference_score,get_middle_score)
import traceback

#venv\Scripts\activate
#$env:FLASK_APP = "flaskr"
#$env:FLASK_ENV = "development"
#flask run

#计算网扩值
def expend(x,wx,y):
    return 100*((1-pow(10,wx-x))/(1-pow(10,wx-y))-0.4)
#通用分数计算函数1
def score_one(weightScore, currentValue, up):
    score=weightScore
    if(currentValue>0):
        score=weightScore-pow(2,int(currentValue/up))
        if(score<0):
            return 0
    return score
#通用分数计算函数2
def score_two(weightScore, currentValue, up, down, level_up, level_down):
    score=weightScore
    if(currentValue>up):
        score=weightScore-pow(2,int((currentValue-up)/level_up))
    elif(currentValue<down):
        score=weightScore-pow(2,int((down-currentValue)/level_down))
    if(score<0):
        return 0
    return score
#计算密度得分
def get_density_score(kk,cc,mm,yy,field_density):
    weight=field_density/4
    S_Dc_c = score_two(weight, cc, 0.9, 0.85, 0.02, 0.015)
    S_Dm_m = score_two(weight, mm, 0.9, 0.85, 0.02, 0.015)
    S_Dy_y = score_two(weight, yy, 0.9, 0.8, 0.02, 0.015)
    S_Dk_k = score_two(weight, kk, 1.1, 1.0, 0.03, 0.02)
    return (S_Dc_c + S_Dm_m + S_Dy_y + S_Dk_k)
#计算扩展值得分
def get_expend_score(cyan_expend,magenta_expend,yellow_expend,black_expend,four_expend):
    weight=four_expend/4
    S_F40=score_two(weight, cyan_expend, 22, 14, 2, 2)+score_two(weight, magenta_expend, 22, 14, 2, 2)+score_two(weight, yellow_expend, 22, 14, 2, 2)+score_two(weight, black_expend, 22, 14, 2, 2)
    return S_F40
#计算中间值得分
def get_middle_score(middle_expend,middle_expend_s):
    return score_one(middle_expend_s, middle_expend - 3, 1)
#计算报头密度得分
def get_header_density_score(tm,ty,header_magenta,header_yellow,header_density_difference):
    dtD = sqrt(pow(tm-header_magenta,2)+pow(ty-header_yellow),2)
    return score_one(header_density_difference, dtD - 0.1, 0.01)
#计算色差得分
def get_difference_score(cyan_difference,magenta_difference,yellow_difference,black_difference,gray_banlance_s):
    weight=gray_banlance_s/4
    return score_one(weight,abs(cyan_difference)-3,1)+score_one(weight,abs(magenta_difference)-5,1)+score_one(weight,abs(yellow_difference)-4,1)+score_one(weight,abs(black_difference)-3,1)
#计算灰平衡彩度差得分
def get_gray_score(gray_banlance,gray_banlance_s):
    return score_one(gray_banlance_s,gray_banlance-3,1)
#计算报头色度得分
def get_header_difference_score(header_difference,header_difference_s):
    return score_one(header_difference_s,header_difference-2,1.5)


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
            #print(data)
            #把前端返回的表格值加载到字典
            name=[
                ['wk','wc','wm','wy','wl','wa','wb','machine'],
                ['gk','gc','gm','gy','gl','ga','gb'],
                ['hk','hc','hm','hy','hl','ha','hb'],
                ['c4k','c4c','c4m','c4y','c4l','c4a','c4b'],
                ['m4k','m4c','m4m','m4y','m4l','m4a','m4b'],
                ['y4k','y4c','y4m','y4y','y4l','y4a','y4b'],
                ['k4k','k4c','k4m','k4y','k4l','k4a','k4b'],
                ['ck','cc','cm','cy','cl','ca','cb'],
                ['mk','mc','mm','my','ml','ma','mb'],
                ['yk','yc','ym','yy','yl','ya','yb'],
                ['kk','kc','km','ky','kl','ka','kb'],
                ['tk','tc','tm','ty','tl','ta','tb'],
            ]
            data_dict={}
            for i in range(1,len(data)):
                for j in range(1,len(data[i])):
                    data_dict[name[i-1][j-1]]=data[i][j]
            #print(data_dict)
            try:
                #先获取直接取得的值
                cyan_density=data_dict['cc']
                magenta_density=data_dict['mm']
                yellow_density=data_dict['yy']
                black_density=data_dict['kk']
                header_M=data_dict['tm']
                header_Y=data_dict['ty']

                #计算没有lab的部分
                cyan_expend=expend(data_dict['c4c'],data_dict['wc'],cyan_density)
                magenta_expend=expend(data_dict['m4m'],data_dict['wm'],magenta_density)
                yellow_expend=expend(data_dict['y4y'],data_dict['wy'],yellow_density)
                black_expend=expend(data_dict['k4k'],data_dict['wk'],black_density)
                expend_list=[cyan_expend,magenta_expend,yellow_expend]
                middle_expend=max(expend_list)-min(expend_list)
                gray_banlance=abs(sqrt(pow(data_dict['ga'],2)+pow(data_dict['gb'],2))-sqrt(pow(data_dict['ha'],2)+pow(data_dict['hb'],2)))
            except Exception as e:
                traceback.print_exc()
            
            #数据库查询，得到用户的参数设置
            user_id = session.get('user_id')
            db=get_db()
            setting=db.execute(
                'SELECT * FROM settings WHERE author_id=? AND is_choose=1',(user_id,)
            ).fetchone()
            try:
                density_score=get_density_score(data_dict['kk'],data_dict['cc'],data_dict['mm'],data_dict['yy'],setting['field_density'])
                expend_score=get_expend_score(cyan_expend,magenta_expend,yellow_expend,black_expend,setting['four_expend'])
                middle_score=get_middle_score(middle_expend,setting['middle_expend'])
            except Exception as e:
                traceback.print_exc() 

            if data_dict['cl'] is None:
                try:#计算无lab时的得分
                    header_density_score=get_header_density_score(data_dict['tm'],data_dict['ty'],setting['header_magenta'],setting['header_yellow'],setting['header_density_difference'])
                    score=density_score+expend_score+middle_score+header_density_score
                    print(score)
                except Exception as e:
                    traceback.print_exc()
            else:                   
                try:#计算有lab值的项目及得分
                    cyan_difference=sqrt(pow(data_dict['cl']-setting['cyan_L'],2)+pow(data_dict['ca']-setting['cyan_a'],2)+pow(data_dict['cb']-setting['cyan_b'],2))
                    magenta_difference=sqrt(pow(data_dict['ml']-setting['magenta_L'],2)+pow(data_dict['ma']-setting['magenta_a'],2)+pow(data_dict['mb']-setting['magenta_b'],2))
                    yellow_difference=sqrt(pow(data_dict['yl']-setting['yellow_L'],2)+pow(data_dict['ya']-setting['yellow_a'],2)+pow(data_dict['yb']-setting['yellow_b'],2))
                    black_difference=sqrt(pow(data_dict['kl']-setting['black_L'],2)+pow(data_dict['ka']-setting['black_a'],2)+pow(data_dict['kb']-setting['black_b'],2))
                    header_difference=sqrt(pow(data_dict['tl']-setting['header_L'],2)+pow(data_dict['ta']-setting['header_a'],2)+pow(data_dict['tb']-setting['header_b'],2))
                    #print(expend_list)
                    difference_score=get_difference_score(cyan_difference,magenta_difference,yellow_difference,black_difference,setting['gray_banlance'])
                    gray_score=get_gray_score(gray_banlance,setting['gray_banlance'])
                    header_difference_score=get_header_difference_score(header_difference,setting['header_difference'])
                    score=100*(density_score+expend_score+middle_score+difference_score+gray_score+header_difference_score*2)/(setting['header_density_difference']+setting['header_difference']+setting['middle_expend']+setting['four_expend']+setting['field_density']+setting['four_defference']+setting['gray_banlance'])
                    #print(gray_banlance,cyan_expend,cyan_density,cyan_difference,magenta_expend,magenta_density,magenta_difference,yellow_expend,yellow_density,yellow_difference,black_expend,black_density,black_difference,header_M,header_Y,header_difference,middle_expend)
                    print(score)
                except Exception as e:
                    print(e)
                    #print ("repr(e):\t", repr(e)) #输出 repr(e):	ZeroDivisionError('integer division or modulo by zero',)
                    traceback.print_exc()
                    #print(data_dict)

            
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
                        x=db.execute(
                            'SELECT id FROM user WHERE username = ?', (username,)
                        ).fetchone()
                        print(x['id'])
                        db.execute(
                            'INSERT INTO settings (author_id,setting_name,is_choose,header_L,header_a,header_b,header_magenta ,header_yellow,cyan_standard,magenta_standard,yellow_standard,black_standard,cyan_expend,magenta_expend,yellow_expend,black_expend,cyan_L,cyan_a,cyan_b,magenta_L,magenta_a,magenta_b,yellow_L,yellow_a,yellow_b,black_L,black_a,black_b,header_density_difference,header_difference,middle_expend,four_expend,field_density,field_density_consistency,four_defference,gray_banlance,de_standard,ink_number) VALUES (?,"默认参数",1,50.6,38.5,20.8,0.8,0.8,0.87,0.87,0.85,1.05,17,17,17,17,57,-23,-27,53,48,0,79,-5,60,40,1,4,20,20,20,40,20,0,20,20,0.39,32)',(x['id'],)
                        )
                        db.commit()
                        
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

    