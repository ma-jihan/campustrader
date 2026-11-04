from flask import session
from app.config import SESSION_EXPIRE_SEC

class SessionService:
    @staticmethod
    def create_session(user_id: int, student_id: str):
        """登录成功，创建会话"""
        session.permanent = True
        session["user_id"] = user_id
        session["student_id"] = student_id
        session.permanent_session_lifetime = SESSION_EXPIRE_SEC

    @staticmethod
    def validate_session() -> dict | None:
        """校验会话，未登录返回None"""
        uid = session.get("user_id")
        sid = session.get("student_id")
        if uid and sid:
            return {"user_id": uid, "student_id": sid}
        return None

    @staticmethod
    def destroy_session():
        """退出登录销毁会话"""
        session.clear()
