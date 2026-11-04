import os
from datetime import timedelta
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import text
from .config import *

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

db = SQLAlchemy()
bcrypt = Bcrypt()
session = Session()

def create_app():
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=SESSION_EXPIRE_SEC)

    db.init_app(app)
    bcrypt.init_app(app)
    session.init_app(app)

    from app.controller.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    @app.route("/test_db")
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return "✅ 数据库连接成功！"
        except Exception as e:
            return f"❌ 连接失败：{str(e)}"

    return app
