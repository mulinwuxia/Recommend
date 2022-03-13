from flask_login import login_required, login_user, logout_user
from flask_paginate import Pagination, get_page_parameter

from recommend.model.user import User
from recommend.model.role import Role
import os

from recommend import app, db
from flask import request,render_template,flash,abort,url_for,redirect,session,Flask,g

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/?<registerMessage>')
def register_index(registerMessage):
    return render_template('index.html', registerMessage=registerMessage)

@app.route('/admin/?<userid>/rolelist')
def admin_rolelist(userid):
    #每页数量
    PER_PAGE = 1
    #总共的数量
    total = db.session.query(Role).count()
    #获取页面，默认为第一页
    page = request.args.get(get_page_parameter(), type=int, default=1)
    #每页开始位置
    start = (page-1)*PER_PAGE
    #每页结束位置
    end = start + PER_PAGE

    pagination = Pagination(bs_version=5, page=page, total=total, per_page=PER_PAGE)
    roles = db.session.query(Role).slice(start, end)

    datas = {
        'userid': userid,
        'pagination': pagination,
        'roles': roles
    }

    print(datas)
    print(pagination.links)


    return render_template('admin.html', **datas)

@app.route('/admin/?<userid>/userlist')
def admin_userlist(userid):
    # 每页数量
    PER_PAGE = 5
    # 总共的数量
    total = db.session.query(User).count()
    # 获取页面，默认为第一页
    page = request.args.get(get_page_parameter(), type=int, default=1)
    # 每页开始位置
    start = (page - 1) * PER_PAGE
    # 每页结束位置
    end = start + PER_PAGE

    pagination = Pagination(bs_version=5, page=page, total=total)
    users = db.session.query(User).slice(start, end)

    datas = {
        'userid': userid,
        'pagination': pagination,
        'users': users
    }

    print(pagination.links)

    return render_template('admin.html',datas=datas)

@app.route('/user/?<userid>')
def user(userid):
    return render_template('user.html', userid=userid)

@app.route('/login',methods=['GET','POST'])
def login():
    loginError = None
    if request.method == 'POST':
        # 根据账号userid找用户
        user = User.query.filter_by(id=request.form['id']).first()
        print(user)

        # 根据rolename找role
        role = Role.query.filter_by(rolename=request.form['role']).first()
        print(role)

        #判断账号userid是否存在，否则将error赋值
        if user is not None:
            #判断用户user的密码是否输入正确
            print("用户存在")
            if request.form['password'] == user.password:
                print("密码正确")
                if role in user.roles:
                    login_user(user)
                    flash('Logged in successfully.')
                    print('%d %s登录成功' %(role.roleid, role.rolename))
                    if role.rolename == 'admin':
                        return redirect(url_for('admin_rolelist', userid=user.id))
                    else:
                        return redirect(url_for('user', userid=user.id))
                else:
                    loginError='账户类型错误'

            else:
                loginError='密码错误'
        else:
            loginError='账号不存在'

    print(loginError)
    print(dict(request.form))
    return render_template('index.html', loginError=loginError)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register',methods=['GET','POST'])
def register():
    registerMessage = None
    registerError = None
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        role=Role.query.filter_by(rolename='user').first()

        user=User(username=username,password=password, roles=[role])

        db.session.add(user)
        db.session.commit()

        registerMessage='注册成功'

        return redirect(url_for('register_index', registerMessage=registerMessage))

    registerError='注册失败'
    return render_template('index.html',  registerError=registerError)


