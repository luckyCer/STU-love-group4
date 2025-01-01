from flask import Flask,jsonify,request, render_template, redirect, url_for,flash
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='my_templates',static_folder='.', static_url_path='')
app.secret_key = '123456'  # 用于flash消息的加密

# 配置MySQL连接
app.config['MYSQL_HOST'] = 'localhost'  # 数据库主机地址
app.config['MYSQL_USER'] = 'root'  # 数据库用户名
app.config['MYSQL_PASSWORD'] = 'xp642308'  # 数据库密码
app.config['MYSQL_DB'] = 'data'  # 数据库名称

mysql = MySQL(app)

# 首页
@app.route('/')
def home():
    return render_template('main.html')

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']
        confirm_password = request.form['confirm_psw']
        name = request.form['name']
        email = request.form['email']

         # 密码确认
        if password != confirm_password:
            flash('密码不匹配，请重试。', 'danger')
            return redirect(url_for('register'))

        # 在数据库中插入数据
        cur = mysql.connection.cursor()
        try:
             # 在插入之前检查用户名是否已存在（防止重复注册）
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                flash('用户名已被占用，请选择其他用户名。', 'danger')
                return redirect(url_for('register'))
            
            # 插入用户数据
            cur.execute("INSERT INTO users (username, password, name, email) VALUES (%s, %s, %s, %s)",
                        (username, password, name, email))
            mysql.connection.commit()
            flash('注册成功！', 'success')
            return redirect(url_for('returnlogin'))  # 注册成功后重定向到登录页面
        except Exception as e:
            mysql.connection.rollback()  # 如果出错，回滚
            print(e)  # 打印错误信息
            flash('注册失败，请重试。', 'danger')
        finally:
            cur.close()

    return render_template('register.html')

# 注册成功页面
@app.route('/success')
def success():
    return "注册成功！"

# 返回登录页面
@app.route('/returnlogin')
def returnlogin():
    return render_template('login.html') 

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']

         # 查询数据库以验证用户
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            if user:
                flash('登录成功！', 'success')
                return redirect(url_for('dashboard'))  # 登录成功后重定向到主页
            else:
                flash('用户名或密码错误！', 'danger')
        except Exception as e:
            print(e)  # 打印错误信息
            flash('登录失败，请重试。', 'danger')
        finally:
            cur.close()

    return render_template('login.html')

# 主页（登录成功后）
@app.route('/dashboard')
def dashboard():
    return "欢迎来到用户中心！"

# 忘记密码
@app.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    new_password = data.get('newPassword')

    if not username or not email or not new_password:
        return jsonify({'success': False, 'message': '缺少必要的参数'}), 400

    cur = mysql.connection.cursor()
    try:
        # 查询用户是否存在，验证用户名和邮箱是否匹配
        cur.execute("SELECT * FROM users WHERE username = %s AND email = %s", (username, email))
        user = cur.fetchone()# 取出查询结果
        
        if user:
            # 更新密码
            cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
            mysql.connection.commit()# 提交更改
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': '用户名和邮箱不匹配'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()


if __name__ == '__main__':
    app.run(debug=True)