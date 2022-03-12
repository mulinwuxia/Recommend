from flask_login import login_required, login_user, logout_user

from recommend.model.user import User
from recommend.model.role import Role
import os

from recommend import app, db
from flask import request,render_template,flash,abort,url_for,redirect,session,Flask,g

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/?<userid>')
def admin(userid):
    return render_template('admin.html', userid=userid)

@app.route('/user/?<userid>')
def user(userid):
    return render_template('user.html', userid=userid)

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
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
                        return redirect(url_for('admin', userid=user.id))
                    else:
                        return redirect(url_for('user', userid=user.id))
                else:
                    error='账户类型错误'

            else:
                error='密码错误'
        else:
            error='账号不存在'

    print(error)
    return render_template('index.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))