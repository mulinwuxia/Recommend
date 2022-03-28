from flask_login import login_required, login_user, logout_user
from sqlalchemy import or_

from recommend.model.user import User
from recommend.model.role import Role

from recommend import app, db
from flask import request,render_template,flash,abort,url_for,redirect,session,Flask,g

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/?<registerMessage>')
def register_index(registerMessage):
    return render_template('index.html', registerMessage=registerMessage)

# 管理员界面-展示权限管理rolelist
@app.route('/admin/?<userid>/rolelist')
def admin_rolelist(userid):

    page = int(request.args.get('page', 1))  # 当前页数
    per_page = int(request.args.get('per_page', 5))  # 设置每页数量
    pagination = Role.query.paginate(page, per_page, error_out=False)
    roles = pagination.items  # 获取当前页数据

    datas = {
        'userid': userid,
        'pagination': pagination,
        'roles': roles,
    }

    print(datas)

    return render_template('admin_rolelist.html', **datas)

@app.route('/admin/?<userid>/rolelist/addrole', methods=['GET','POST'])
def admin_addrole(userid):

    #添加新角色role



    return redirect(url_for('admin_rolelist', userid=userid))

@app.route('/admin/?<userid>/rolelist/updaterole', methods=['GET','POST'])
def admin_updaterole(userid):

    print('修改权限')

    # 更新角色信息
    if request.method == 'POST':
        roleid = request.form['roleid']
        rolename = request.form['rolename']
        roledescription = request.form['roledescription']

        # print(roleid)
        print(rolename)
        print(roledescription)

        update_role = Role.query.filter_by(roleid=roleid).first()
        update_role.rolename = rolename
        update_role.roledescription = roledescription

        db.session.commit()

        return redirect(url_for('admin_rolelist', userid=userid))

    return redirect(url_for('admin_rolelist', userid=userid))

@app.route('/admin/?<userid>/rolelist/deleterole/?<roleid>', methods=['GET', 'POST'])
def admin_deleterole(userid, roleid):
    # 删除角色role

    print('删除角色role')

    delete_role = Role.query.filter_by(roleid=roleid).first()

    # 删除多对多关系表user_role中关于delete_role的信息
    if delete_role.users:
        for u in delete_role.users:
            delete_role.users.remove(u)
        db.session.commit()

    db.session.delete(delete_role)
    db.session.commit()

    return redirect(url_for('admin_rolelist', userid=userid))


# 获取userlist的paginate
def getUserListPagination():
    page = int(request.args.get('page', 1))  # 当前页数
    per_page = int(request.args.get('per_page', 5))  # 设置每页数量
    pagination = User.query.paginate(page, per_page, error_out=False)
    return pagination

def getSearchUserListPagination(idCondition, id, roleCondition, username):
    page = int(request.args.get('page', 1))  # 当前页数
    per_page = int(request.args.get('per_page', 5))  # 设置每页数量

    print('idCondition, id, roleCondition, username')
    print(idCondition, id, roleCondition, username)
    filterConditions = []

    if id:
        print('id is not None')
        if idCondition == '-1':
            print('idCondition == -1')
            if roleCondition != '-1':
                print(roleCondition)
                print('roleConditon != -1')
                role = Role.query.filter_by(rolename=roleCondition).first()

                print(role)
                filterConditions.append(User.roles.contains(role))
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))
            else:
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))

        elif idCondition == '0':
            print('idCondition == 0')
            filterConditions.append(User.id > id)
            if roleCondition != '-1':
                print(roleCondition)
                print('roleConditon != -1')
                role = Role.query.filter_by(rolename=roleCondition).first()
                filterConditions.append(User.roles.contains(role))
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))
            else:
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))
        elif idCondition == '1':
            print('idCondition == 1')
            filterConditions.append(User.id == id)
        else:
            filterConditions.append(User.id < id)
            if roleCondition != '-1':
                print(roleCondition)
                print('roleConditon != -1')
                role = Role.query.filter_by(rolename=roleCondition).first()
                filterConditions.append(User.roles.contains(role))
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))
            else:
                if username:
                    print('username is not None')
                    filterConditions.append(User.username.like('%' + username + '%'))
    else:
        print('id is None')
        if roleCondition != '-1':
            print(roleCondition)
            print('roleConditon != -1')
            role = Role.query.filter_by(rolename=roleCondition).first()
            filterConditions.append(User.roles.contains(role))
            if username:
                print('username is not None')
                filterConditions.append(User.username.like('%'+username+'%'))
        else:
            if username:
                print('username is not None')
                filterConditions.append(User.username.like('%'+username+'%'))
    print(filterConditions)
    pagination = User.query.filter(*filterConditions).paginate(page, per_page, error_out=False)
    return pagination


# 管理员界面-展示用户管理userlist
@app.route('/admin/?<userid>/userlist', methods=['GET', 'POST'])
def admin_userlist(userid):

    print('用户显示')

    pagination = getUserListPagination()
    users = pagination.items  # 获取当前页数据

    print(pagination)
    print(users)



    adminRole = Role.query.filter_by(rolename='admin').first()

    userRole = Role.query.filter_by(rolename='user').first()

    datas = {
        'userid': userid,
        'pagination': pagination,
        'users': users,
        'adminRole':adminRole,
        'userRole':userRole

    }

    return render_template('admin_userlist.html', **datas)


@app.route('/admin/?<userid>/userlist/searchuser', methods=['GET', 'POST'])
def admin_searchuser(userid):

    print('搜索用户')
    if request.method == 'POST':
        idCondition = request.form['idCondition']
        id = request.form['id']
        roleCondition = request.form['roleCondition']
        username = request.form['username']

        print(roleCondition)

        pagination = getSearchUserListPagination(idCondition, id, roleCondition, username)
        users = pagination.items  # 获取当前页数据

        print(pagination)
        print('users:')
        print(users)


        datas = {
            'userid': userid,
            'pagination': pagination,
            'users': users,

            'idCondition': idCondition,
            'id': id,
            'roleCondition': roleCondition,
            'username': username


        }

        return render_template('admin_userlist.html', **datas)
    return redirect(url_for('admin_userlist', userid=userid))

@app.route('/admin/?<userid>/userlist/adduser', methods=['GET', 'POST'])
def admin_adduser(userid):
    # 添加用户

    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        role=Role.query.filter_by(rolename=request.form['rolename']).first()

        user=User(username=username,password=password, roles=[role])

        db.session.add(user)
        db.session.commit()

    return redirect(url_for('admin_userlist', userid=userid))

@app.route('/admin/?<userid>/userlist/updateuser', methods=['GET', 'POST'])
def admin_updateuser(userid):
    # 更新用户user
    print('修改用户')

    # 更新角色信息
    if request.method == 'POST':
        userid = request.form['userid']
        username = request.form['username']
        password = request.form['password']
        roles = request.form.getlist('role')

        update_user = User.query.filter_by(id=userid).first()
        update_user.username = username
        update_user.password = password

        rolelist = []
        for r in update_user.roles:
            rolelist.append(r.rolename)

        print('roles, rolelist')
        print(roles, rolelist)

        # 如果复选框中的role是user.roles中所不存在的，新增user权限
        for r in roles:
            if r not in rolelist:
                role = Role.query.filter_by(rolename=r).first()
                update_user.roles.append(role)
                db.session.commit()

        # 如果user.roles中的role是复选框的role中所不存在的，删除user权限
        for r in rolelist:
            if r not in roles:
                role = Role.query.filter_by(rolename=r).first()
                update_user.roles.remove(role)
                db.session.commit()

        print(update_user)

        db.session.commit()

        return redirect(url_for('admin_userlist', userid=userid))


    return redirect(url_for('admin_userlist', userid=userid))

@app.route('/admin/?<userid>/userlist/deleteuser/?<id>', methods=['GET', 'POST'])
def admin_deleteuser(userid, id):
    # 删除角色role

    print('删除用户user')

    delete_user = User.query.filter_by(id=id).first()
    print(delete_user.roles)

    # 删除多对多表user_role中关于delete_user的信息
    if delete_user.roles:
        for r in delete_user.roles:
            delete_user.roles.remove(r)
        db.session.commit()

    db.session.delete(delete_user)
    db.session.commit()

    return redirect(url_for('admin_userlist', userid=userid))


@app.route('/admin/?<userid>/licenselist')
def admin_licenselist(userid):
    return render_template('admin_licenselist.html', userid=userid)


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


