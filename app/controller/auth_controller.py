from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.service.login_register_service import LoginRegisterService
from app.service.session_service import SessionService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    try:
        student_id = request.form.get("student_id", "").strip()
        nickname = request.form.get("nickname", "").strip()
        phone = request.form.get("phone", "").strip()
        pwd = request.form.get("password", "")
        pwd2 = request.form.get("password2", "")

        if not student_id:
            return render_template("register.html", error="请输入学号",
                                   student_id=student_id, username=nickname, phone=phone)
        if not nickname:
            return render_template("register.html", error="请输入昵称",
                                   student_id=student_id, username=nickname, phone=phone)
        if not phone:
            return render_template("register.html", error="请输入手机号",
                                   student_id=student_id, username=nickname, phone=phone)
        if len(pwd) < 6:
            return render_template("register.html", error="密码长度至少为6位！",
                                   student_id=student_id, username=nickname, phone=phone)
        if pwd != pwd2:
            return render_template("register.html", error="两次密码不一致！",
                                   student_id=student_id, username=nickname, phone=phone)

        LoginRegisterService.register(student_id, nickname, phone, pwd)
        flash("注册成功，请登录！")
        return redirect(url_for("auth.login"))
    except ValueError as e:
        return render_template("register.html", error=str(e),
                               student_id=student_id, username=nickname, phone=phone)
    except Exception:
        return render_template("register.html", error="系统繁忙，请稍后重试",
                               student_id=student_id, username=nickname, phone=phone)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    try:
        student_id = request.form.get("student_id", "").strip()
        pwd = request.form.get("password", "")
        if not student_id or not pwd:
            return render_template("login.html", error="学号和密码不能为空", student_id=student_id)
        LoginRegisterService.login(student_id, pwd)
        return redirect(url_for("auth.student_home"))
    except ValueError as e:
        return render_template("login.html", error=str(e), student_id=student_id)
    except Exception:
        return render_template("login.html", error="系统繁忙，请稍后重试", student_id=student_id)

@auth_bp.route("/logout")
def logout():
    SessionService.destroy_session()
    return redirect(url_for("auth.login"))

@auth_bp.route("/student_home")
def student_home():
    uid = session.get("user_id")
    is_guest = session.get("is_guest", False)
    if not uid and not is_guest:
        flash("请先登录")
        return redirect(url_for("auth.login"))
    username = session.get("student_id", "游客")
    guest_notice = '<div style="background:#ffeeba; color:#856404; padding:12px; border-radius:8px; text-align:center; font-size:16px; margin-bottom:20px;">⚠️ 当前为【游客模式】，仅可浏览，发布、收藏等功能不可用。<a href="' + url_for("auth.login") + '" style="color:#0066ff;">点击登录获取完整权限</a></div>' if is_guest else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>校园二手贸易 - 首页</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f0f7ff; font-family: "Microsoft Yahei", sans-serif; }}
        .navbar {{ background-color: #1677ff !important; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">校园二手贸易账号登录系统</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{url_for('auth.logout')}">退出登录</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container">
        {guest_notice}
        <h2 style="text-align:center; color:#0066ff;">欢迎，{username}</h2>
        <div style="text-align:center; margin-top:20px;">
            <a href="{url_for('auth.logout')}">
                <button style="padding:12px 24px; font-size:16px; background-color:#6c757d; color:white; border:none; border-radius:6px;">退出登录</button>
            </a>
        </div>
    </div>
</body>
</html>"""

@auth_bp.route("/guest")
def guest():
    session["is_guest"] = True
    return redirect(url_for("auth.student_home"))
