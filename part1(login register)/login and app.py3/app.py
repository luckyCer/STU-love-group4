from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_cors import CORS
import numpy as np
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime
import uuid
#加多
import os
from sqlalchemy import or_, text,func
from sqlalchemy.orm import joinedload
from functools import wraps
from flask import request, redirect, url_for
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus

app = Flask(__name__, template_folder='my_templates',static_folder='.', static_url_path='')
app.secret_key = '123456'  # 用于flash消息的加密

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/mydate' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#登录注册使用的user表格
class User(db.Model):
    __tablename__ = 'users'
    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = db.Column(db.String(15), unique=True, nullable=False) 
    #username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    
    user_info = db.relationship('UserInfo', back_populates='user', uselist=False,lazy=True, foreign_keys='UserInfo.id')


#main页面指的是登录、注册一开始出现的页面
@app.route('/')
def home():
    return render_template('main.html')
#注册界面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #username = request.form['username']
        phone_number = request.form['phone_number']
        password = request.form['psw']
        confirm_password = request.form['confirm_psw']
        name = request.form['name']
        email = request.form['email']

        # 密码确认
        if password != confirm_password:
            flash('密码不匹配，请重试。', 'danger')
            return redirect(url_for('register'))

        # 检查用户名是否已存在（防止重复注册）
        existing_user = User.query.filter_by(phone_number = phone_number).first()
        if existing_user:
            flash('该号码已被注册', 'danger')
            return redirect(url_for('register'))

        # 插入用户数据
        try:
            id = generate_random_id()
            hashed_password = generate_password_hash(password)  # 哈希密码
            new_user = User(id = id , phone_number = phone_number, password=hashed_password, name=name, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功！', 'success')
            return redirect(url_for('login'))  # 注册成功后重定向到登录页面
        except Exception as e:
            db.session.rollback()  # 如果出错，回滚
            print(e)  # 打印错误信息
            flash('注册失败，请重试。', 'danger')

    return render_template('register.html')

# 注册成功页面
@app.route('/success')
def success():
    return "注册成功！"

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        password = request.form['psw']

        # 查询数据库以验证用户
        user = User.query.filter_by(phone_number = phone_number).first()  # 查找用户

        if user and check_password_hash(user.password, password):  # 验证密码
            session['user_id'] = user.id  # 将用户 ID 存储在会话中
            flash('登录成功！', 'success')
            return redirect(url_for('main_page'))  # 登录成功后重定向到主页
        else:
            flash('手机号或密码错误！', 'danger')

    return render_template('login.html')

#忘记密码
@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    phone_number = data.get('phone_number')
    new_password = data.get('new_password')

    if not phone_number or not new_password:
        return jsonify({'success': False, 'message': '缺少必要的参数'}), 400

    # 查询用户是否存在
    user = User.query.filter_by(phone_number=phone_number).first()

    if not user:
        return jsonify({'success': False, 'message': '手机号不存在'}), 404

    try:
        # 更新密码
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': '密码重置成功！'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)