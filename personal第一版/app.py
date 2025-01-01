from flask import Flask, request, render_template, jsonify
import pymysql

app = Flask(__name__)

# 数据库配置
db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',  # 数据库用户名
    'password': 'Lxt909964',  # 数据库密码
    'database': 'personal'  # 数据库的名字
}

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/update_info', methods=['POST'])
def update_info():
    if request.method == 'POST':
        try:
            # 获取JSON数据
            data = request.get_json()
            name = data.get('name')
            gender = data.get('gender')
            age = data.get('age')
            signature = data.get('signature')
            hometown = data.get('hometown')
            hobby = data.get('hobby')
            campus = data.get('campus')
            major = data.get('major')
            constellation = data.get('constellation')
            mbti = data.get('mbti')
            declaration = data.get('declaration')
            personality = data.get('personality')
            user_id = data.get('user_id')  # 用户ID
            avatar = data.get('avatar')  # 头像URL
            birthday = data.get('birthday')


            if not all([name, gender, age, signature, hometown, hobby, campus, major, constellation, mbti, declaration, personality, user_id, avatar, birthday]):
                return jsonify({'message': '缺少必要参数'}), 400

            # 连接数据库
            connection = pymysql.connect(**db_config)
            try:
                with connection.cursor() as cursor:
                    # 检查是否有该用户的记录
                    cursor.execute("SELECT * FROM user_info WHERE id=%s", (user_id,))
                    result = cursor.fetchone()

                    if result:
                        # 如果有记录，则更新
                        sql = """
                        UPDATE user_info SET
                            name=%s, gender=%s, age=%s, signature=%s, hometown=%s, hobby=%s,
                            campus=%s, major=%s, constellation=%s, mbti=%s, declaration=%s, personality=%s, avatar=%s, birthday=%s
                        WHERE id=%s
                        """
                        cursor.execute(sql, (name, gender, age, signature, hometown, hobby, campus, major, constellation, mbti, declaration, personality, avatar, user_id, birthday))
                    else:
                        # 如果没有记录，则插入新记录
                        sql = """
                        INSERT INTO user_info (id, name, gender, age, signature, hometown, hobby, campus, major, constellation, mbti, declaration, personality, avatar, birthday)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (user_id, name, gender, age, signature, hometown, hobby, campus, major, constellation, mbti, declaration, personality, avatar, birthday))

                connection.commit()
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({'message': '信息更新失败，请重试。'}), 500
            finally:
                connection.close()

            return jsonify({'message': '信息更新成功！'}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'message': '请求解析失败，请检查请求格式。'}), 400
    return jsonify({'message': '无效请求'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)