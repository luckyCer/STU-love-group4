from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 数据库连接设置
db = MySQLdb.connect(host='localhost', user='root', passwd='@Zx2022611039', db='ChatApp')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
            flash('注册成功！请登录。')
            return redirect(url_for('index'))
        except MySQLdb.IntegrityError:
            flash('用户名已被使用，请选择其他用户名。')
        except Exception as e:
            flash('注册失败：' + str(e))
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT id, password FROM Users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            session['user_id'] = user[0]  # 将用户 ID 存储在会话中
            return redirect(url_for('main_page'))  # 登录成功后重定向到主页面
        else:
            flash('用户名或密码错误！')  # 登录失败，显示错误信息

    return render_template('login.html')  # 如果是 GET 请求或登录失败，重新渲染登录页

@app.route('/main_page', methods=['GET'])
def main_page():
    current_user_id = session.get('user_id')
    
    if current_user_id is None:
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute("SELECT id, username FROM Users WHERE id != %s", (current_user_id,))
    users = cursor.fetchall()  # 获取所有用户，排除当前用户

    if not users:
        flash('没有找到用户！')
    
    return render_template('main_page.html', users=users)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    current_user_id = session.get('user_id')

    if current_user_id is None:
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        # 获取好友列表
        cursor.execute("SELECT friend_id FROM Friends WHERE user_id=%s", (current_user_id,))
        friends = cursor.fetchall()
        friend_usernames = []
        for friend in friends:
            cursor.execute("SELECT id, username FROM Users WHERE id=%s", (friend[0],))
            friend_usernames.append(cursor.fetchone())

    return render_template('chat.html', friends=friend_usernames, friend_username=None, messages=[])

@app.route('/chat/<int:friend_id>', methods=['GET', 'POST'])
def chat_with_friend(friend_id):
    current_user_id = session.get('user_id')

    if current_user_id is None:
        return redirect(url_for('login'))

    with db.cursor() as cursor:
        if request.method == 'POST':
            message = request.form.get('message', '').strip()  # 去除前后空格
            if message:  # 确保消息不为空
                try:
                    cursor.execute("INSERT INTO Messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)", 
                                   (current_user_id, friend_id, message))
                    db.commit()
                    flash('消息发送成功！')
                except Exception as e:
                    flash('发送消息失败：' + str(e))

        # 获取好友的用户名
        cursor.execute("SELECT username FROM Users WHERE id=%s", (friend_id,))
        friend_username = cursor.fetchone()[0]

        # 获取当前用户与好友之间的消息
        cursor.execute(
            "SELECT content, sender_id, created_at FROM Messages "
            "WHERE (sender_id=%s AND receiver_id=%s) OR (sender_id=%s AND receiver_id=%s) "
            "ORDER BY created_at ASC", 
            (current_user_id, friend_id, friend_id, current_user_id)
        )
        messages = cursor.fetchall()

        # 再次获取好友列表
        cursor.execute("SELECT friend_id FROM Friends WHERE user_id=%s", (current_user_id,))
        friends = cursor.fetchall()
        friend_usernames = []
        for friend in friends:
            cursor.execute("SELECT id, username FROM Users WHERE id=%s", (friend[0],))
            friend_usernames.append(cursor.fetchone())

    return render_template('chat.html', friends=friend_usernames, friend_username=friend_username, messages=messages, friend_id=friend_id)

@app.route('/add_friend_direct', methods=['POST'])
def add_friend_direct():
    current_user_id = session.get('user_id')

    if current_user_id is None:
        return redirect(url_for('login'))

    friend_id = request.form.get('friend_id')

    if not friend_id:
        flash('未指定好友！')
        return redirect(url_for('main_page'))

    # 确保 friend_id 是整数
    try:
        friend_id = int(friend_id)
    except ValueError:
        flash('好友 ID 无效！')
        return redirect(url_for('main_page'))

    with db.cursor() as cursor:
        # 检查是否已经是好友
        cursor.execute("SELECT * FROM Friends WHERE user_id=%s AND friend_id=%s", (current_user_id, friend_id))
        existing_friendship = cursor.fetchone()

        if existing_friendship:
            flash('你们已经是好友了！')
            return redirect(url_for('main_page'))

        # 将双方添加到 Friends 表中
        cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (%s, %s)", (current_user_id, friend_id))
        cursor.execute("INSERT INTO Friends (user_id, friend_id) VALUES (%s, %s)", (friend_id, current_user_id))
        db.commit()
        flash('已成功添加好友！')

    return redirect(url_for('main_page'))



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)



