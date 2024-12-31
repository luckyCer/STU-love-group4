#整合后更改：增加传入用户ID，实现添加好友

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
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import Column, String, Text, TIMESTAMP
import logging

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16)
password = quote_plus('@Zx2022611039')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Li4444555635!@localhost/carddatabase'
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

    
class UserInfo(db.Model):
    _tablename_ = 'user_info'
    
    id = db.Column(db.String(36),db.ForeignKey('users.id'),primary_key = True)
    username = db.Column(db.String(50),nullable = False)
    gender = db.Column(db.String(10), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    college = db.Column(db.String(20),nullable=False)
    signature = db.Column(db.Text , nullable = True)
    hometown = db.Column(db.String(255) ,nullable = True)
    hobby = db.Column(db.String(255) ,nullable = True)
    campus = db.Column(db.String(255) ,nullable = False)
    major = db.Column(db.String(255) ,nullable = True)
    constellation = db.Column(db.String(50) , nullable = True)
    mbti = db.Column(db.String(50) , nullable = True)
    declaration = db.Column(db.Text ,nullable = True)
    personality = db.Column(db.String(255) ,nullable = True)
    avatar = db.Column(db.String(255) , nullable = True)
    birthday = db.Column(db.String(255) , nullable = True)
    user = db.relationship('User', back_populates='user_info',lazy=True, foreign_keys=[id])
    def to_dict(self):
        return {
            'username': self.username,
            'gender': self.gender,
            'campus': self.campus,
            'college': self.college,
            'grade': self.grade,
            'id': self.id
        } 

# 汕恋路由
@app.route('/shanlian')
def shanlian():
    return render_template('shanlian.html')


@app.route('/api/shanlian')
def api_shanlian():
    users = UserInfo.query.all()
    user_data = [user.to_dict() for user in users]  # 转换为字典格式
    return jsonify(user_data)


@app.route('/filter_users')
def filter_users():
    filters = request.args.to_dict()

    query = UserInfo.query

    # 处理多个筛选条件
    for key, value in filters.items():
        if value != 'all':
            query = query.filter(getattr(UserInfo, key) == value)

    users = query.all()
    return [user.to_dict() for user in users]

@app.route('/add_to_chat', methods=['POST'])
def add_to_chat():
    try:
        data = request.get_json()
        print("Received data:", data)  # 输出接收到的请求数据
        
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')

        # 检查 ID 是否有效
        if not sender_id or not receiver_id:
            return jsonify({"status": "error", "message": "缺少 sender_id 或 receiver_id"}), 400

        # 添加聊天关系
        new_chat_relationship = Friend(user_id=sender_id, friend_id=receiver_id)
        db.session.add(new_chat_relationship)
        db.session.commit()

        return jsonify({"status": "success", "message": "成功添加到对话列表"})

    except Exception as e:
        print("Error:", str(e))  # 输出错误信息用于调试
        return jsonify({"status": "error", "message": "服务器错误"}), 500