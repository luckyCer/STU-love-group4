from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理，确保每个用户会话是独立的
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@Zx2022611039@localhost/chat_db'  # 你的数据库 URI

# 定义允许的文件扩展名和上传文件夹
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'

# 如果上传文件夹不存在，则创建它
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

bcrypt = Bcrypt(app)

# 获取数据库连接
def get_db_connection():
    return pymysql.connect(
        host='localhost',  # 替换为你的主机
        user='root',       # 你的 MySQL 用户名
        password='@Zx2022611039',  # 你的 MySQL 密码
        db='chat_db',      # 你的数据库名称
        cursorclass=pymysql.cursors.DictCursor  # 使用字典游标，以便查询结果为字典格式
    )

@app.route('/')
def index():
    return render_template('register.html')  # 这里你可以替换为你的主页模板

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册功能"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 校验用户名和密码长度
        if len(username) < 0 or len(password) < 6:
            flash("用户名或密码长度不符合要求", 'error')
            return render_template('register.html')

        # 密码加密
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 插入新用户
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('login'))
        except pymysql.MySQLError:
            flash('用户名已被使用，请选择其他用户名。', 'error')
        except Exception as e:
            flash(f'注册失败：{str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录功能"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 连接到数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询用户名对应的用户信息
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            # 使用 bcrypt 验证密码
            if bcrypt.check_password_hash(user['password'], password):
                # 登录成功，记录用户ID到 session
                session['user_id'] = user['id']
                session.permanent = True  # 会话保持，避免会话过期
                flash('登录成功！', 'success')
                return redirect(url_for('chat'))  # 登录后跳转到聊天界面
            else:
                flash('用户名或密码错误！', 'error')
        else:
            flash('用户名不存在！', 'error')

        cursor.close()
        conn.close()

    return render_template('login.html')

@app.route('/chat')
def chat():
    """聊天功能"""
    if 'user_id' not in session:
        flash("请先登录", 'error')
        return redirect(url_for('login'))

    # 获取当前用户的好友列表
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id IN (SELECT friend_id FROM friends WHERE user_id = %s)", (session['user_id'],))
    friends = cursor.fetchall()

    # 获取当前用户与某个好友的聊天记录
    receiver_id = request.args.get('receiver_id')
    if receiver_id:
        cursor.execute(""" 
            SELECT sender_id, receiver_id, content 
            FROM messages 
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp
        """, (session['user_id'], receiver_id, receiver_id, session['user_id']))
        messages = cursor.fetchall()
    else:
        messages = []

    cursor.close()
    conn.close()

    return render_template('chat_combined.html', friends=friends, messages=messages)

@app.route('/add_friend', methods=['POST'])
def add_friend():
    """添加好友"""
    if 'user_id' not in session:
        return jsonify({'error': '用户未登录'}), 401

    friend_id = request.form['friend_id']
    if not friend_id:
        return jsonify({'error': '好友ID不能为空'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询好友是否存在
    cursor.execute("SELECT id FROM users WHERE id = %s", (friend_id,))
    friend = cursor.fetchone()

    if not friend:
        return jsonify({'error': '好友不存在'}), 404

    # 检查是否已经是好友
    cursor.execute("SELECT * FROM friends WHERE user_id = %s AND friend_id = %s", (session['user_id'], friend_id))
    existing_friendship = cursor.fetchone()

    if existing_friendship:
        return jsonify({'status': 'error', 'message': '已经是好友'}), 400

    # 插入新的好友关系
    cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)", (session['user_id'], friend_id))
    conn.commit()

    cursor.close()
    conn.close()

    # 好友添加成功后，重定向到聊天页面，刷新好友列表
    flash('好友添加成功！', 'success')
    return redirect(url_for('chat'))

@app.route('/send_message', methods=['POST'])
def send_message():
    """发送消息"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '请先登录'}), 401

    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message = data.get('message')

    print(f"Received message: {message}, Receiver ID: {receiver_id}")  # Debugging print

    if not receiver_id or not message:
        return jsonify({'status': 'error', 'message': '缺少必要的参数'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 插入消息到数据库
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)", 
                       (session['user_id'], receiver_id, message))
        conn.commit()

        # 获取最新发送的消息
        cursor.execute(""" 
            SELECT m.sender_id, m.receiver_id, m.message, m.timestamp, u.username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.sender_id = %s AND m.receiver_id = %s
            ORDER BY m.timestamp DESC
            LIMIT 1
        """, (session['user_id'], receiver_id))
        message = cursor.fetchone()

        print(f"Message sent: {message}")  # Debugging print

        # 返回最新发送的消息
        return jsonify({
            'status': 'success',
            'message': '消息发送成功',
            'message_data': message  # 只返回新消息
        }), 200
    except pymysql.MySQLError as e:
        print(f"Error: {e}")  # Debugging print
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 新增的路由，处理获取当前用户信息
@app.route('/get_current_user', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    return jsonify({'user_id': session['user_id']})

# 新增的路由，获取与某个用户的聊天记录
@app.route('/get_messages', methods=['GET'])
def get_messages():
    """获取历史消息"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': '请先登录'}), 401

    # 获取查询参数
    receiver_id = request.args.get('receiver_id')

    if not receiver_id:
        return jsonify({'status': 'error', 'message': '缺少接收者ID'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 查询与当前聊天相关的所有消息
        cursor.execute("""
            SELECT m.sender_id, m.receiver_id, m.message, m.timestamp, u.username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s) OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.timestamp DESC
        """, (session['user_id'], receiver_id, receiver_id, session['user_id']))
        messages = cursor.fetchall()

        # 返回所有历史消息
        return jsonify({
            'status': 'success',
            'messages': messages
        }), 200
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
