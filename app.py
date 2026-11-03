from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
from datetime import datetime
import traceback
import re

app = Flask(__name__)
app.secret_key = "campus_secondhand_auth_2026"
DATABASE = "auth.db"


# 数据库初始化
def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS user
    (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    phone TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    create_time DATETIME,
    last_login_time DATETIME,
    fail_count INTEGER DEFAULT 0,
    locked INTEGER DEFAULT 0)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS login_log
    (log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    login_time DATETIME,
    status TEXT)''')
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(raw_pwd):
    return bcrypt.hashpw(raw_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# 学号校验工具函数，无全局正则变量
def validate_student_id(sid: str) -> bool:
    pattern = re.compile(r'^(10\d{8}|\d{13})$')
    return bool(pattern.fullmatch(sid.strip()))


# 修复后的add_login_log（3个参数）
def add_login_log(sid, status, conn):
    cur = conn.cursor()
    cur.execute("INSERT INTO login_log (student_id, login_time, status) VALUES (?, ?, ?)",
                (sid, datetime.now(), status))
    conn.commit()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=["GET", "POST"])
def login():
    error_msg = ""
    conn = None
    student_id = ""
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        password = request.form.get("password", "").strip()
        if not student_id or not password:
            error_msg = "学号和密码不能为空"
            return render_template("login.html", error=error_msg, student_id=student_id)

        try:
            conn = sqlite3.connect("auth.db")
            cur = conn.cursor()
            cur.execute("SELECT password_hash, role, username, fail_count, locked FROM user WHERE student_id=?",
                        (student_id,))
            row = cur.fetchone()

            if not row:
                error_msg = "该学号不存在"
                return render_template("login.html", error=error_msg, student_id=student_id)

            password_hash, role, username, fail_count, locked = row
            if locked == 1:
                error_msg = "该账号登录失败3次，账号已被锁定，请联系管理员解锁"
                return render_template("login.html", error=error_msg, student_id=student_id)

            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                session["student_id"] = student_id
                session["username"] = username
                session["role"] = role
                session["is_guest"] = False  #登录成功，清除游客标记
                cur.execute("UPDATE user SET fail_count=0, last_login_time=? WHERE student_id=?",
                            (datetime.now(), student_id))
                add_login_log(student_id, "登录成功", conn)
                conn.commit()
                if role == "admin":
                    return redirect("/admin_home")
                else:
                    return redirect("/student_home")
            else:
                fail_count += 1
                if fail_count >= 3:
                    cur.execute("UPDATE user SET fail_count=?, locked=1 WHERE student_id=?", (fail_count, student_id))
                    error_msg = "密码连续错误3次，账号已锁定！联系管理员解锁"
                else:
                    cur.execute("UPDATE user SET fail_count=? WHERE student_id=?", (fail_count, student_id))
                    error_msg = f"密码错误！剩余尝试次数：{3 - fail_count}"
                add_login_log(student_id, "登录失败", conn)
                conn.commit()
                return render_template("login.html", error=error_msg, student_id=student_id)
        except Exception as e:
            traceback.print_exc()
            error_msg = "数据库异常！"
            return render_template("login.html", error=error_msg, student_id=student_id)
        finally:
            if conn is not None:
                conn.close()

    return render_template("login.html", error=error_msg, student_id=student_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    student_id = ""
    username = ""
    phone = ""
    password = ""
    password2 = ""
    error_msg = ""

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()
        password2 = request.form.get("password2", "").strip()

        # 学号格式校验，调用工具函数
        if not validate_student_id(student_id):
            error_msg = "学号格式错误：仅支持10开头10位新版本科号 或 13位旧式学籍号"
            return render_template("register.html", error=error_msg,
                                   student_id=student_id, username=username, phone=phone)

        if not student_id or not username or not password:
            error_msg = "学号、用户名、密码不能为空！"
            return render_template("register.html", error=error_msg,
                                   student_id=student_id, username=username, phone=phone)
        if password != password2:
            error_msg = "两次输入密码不一致！"
            return render_template("register.html", error=error_msg,
                                   student_id=student_id, username=username, phone=phone)
        if len(password) < 6:
            error_msg = "密码长度至少6位！"
            return render_template("register.html", error=error_msg,
                                   student_id=student_id, username=username, phone=phone)

        conn = get_db()
        exist_user = conn.execute("SELECT * FROM user WHERE student_id=?", (student_id,)).fetchone()
        if exist_user:
            error_msg = "该学号已经注册！"
            conn.close()
            return render_template("register.html", error=error_msg,
                                   student_id=student_id, username=username, phone=phone)

        pwd_hash = hash_password(password)
        now = datetime.now()
        conn.execute('''INSERT INTO user (student_id, username, phone, password_hash, role, create_time)
        VALUES (?, ?, ?, ?, ?, ?)''', (student_id, username, phone, pwd_hash, "student", now))
        conn.commit()
        conn.close()
        flash("注册成功，请登录！")
        return redirect(url_for("login"))

    return render_template("register.html", error=error_msg,
                           student_id=student_id, username=username, phone=phone)


@app.route("/student_home")
def student_home():
    is_guest = session.get("is_guest", False)
    username = session.get("username", "游客")
    return render_template("student_home.html", is_guest=is_guest, username=username)


@app.route('/admin_home')
def admin_home():
    if "student_id" not in session or session["role"] != "admin":
        flash("无权访问，请使用管理员账号登录")
        return redirect(url_for("login"))
    conn = get_db()
    logs = conn.execute("SELECT * FROM login_log ORDER BY login_time DESC LIMIT 10").fetchall()
    conn.close()
    return render_template("admin_home.html", user=session, logs=logs)


@app.route('/unlock/<sid>')
def unlock(sid):
    if "student_id" not in session or session["role"] != "admin":
        flash("无权操作！")
        return redirect(url_for("login"))
    conn = get_db()
    conn.execute("UPDATE user SET locked=0, fail_count=0 WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()
    flash(f"学号 {sid} 已解锁")
    return redirect(url_for("admin_home"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")


def create_admin():
    conn = get_db()
    admin = conn.execute("SELECT * FROM user WHERE student_id='admin001'").fetchone()
    if not admin:
        hash_p = hash_password("admin123")
        conn.execute('''INSERT INTO user (student_id, username, phone, password_hash, role, create_time, fail_count, locked)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0)''', ("admin001", "管理员", "11111111111", hash_p, "admin", datetime.now()))
        conn.commit()
    conn.close()


@app.route("/guest")
def guest():
    session["is_guest"] = True
    return redirect("/student_home")


if __name__ == "__main__":
    init_db()
    create_admin()
    app.run(debug=True)
