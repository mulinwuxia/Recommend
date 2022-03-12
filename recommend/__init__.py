from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


#加载配置文件内容
print("加载配置文件内容")
app = Flask(__name__)
app.config.from_object('recommend.setting')

#创建数据库对象
print("创建数据库对象")
db = SQLAlchemy(app)
user_role = db.Table(
    'user_role',

    db.Column('userid', db.Integer, db.ForeignKey('user.id'), primary_key=True),

    db.Column('roleid', db.Integer, db.ForeignKey('role.roleid'), primary_key=True)
)

#只有在app对象之后声明，用于导入model否则无法创建表
print("只有在app对象之后声明，用于导入model否则无法创建表")
from recommend.model.user import User
from recommend.model.role import Role

#只有在app对象之后声明，用于导入view模块
print("只有在app对象之后声明，用于导入view模块")
from recommend.controller import recommend_manage

#登陆管理
print("登陆管理")
login_manager = LoginManager()
login_manager.init_app(app)

print(login_manager)
login_manager.login_view = "index"



@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))