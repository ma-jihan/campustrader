from app import db
from datetime import datetime
from sqlalchemy import text

class UserRepository:
    @staticmethod
    def find_by_student_id(student_id: str):
        sql = text("""
            SELECT id, student_id, nickname, phone, pwd_hash, pwd_error_count, lock_expire_time
            FROM user WHERE student_id = :student_id
        """)
        return db.session.execute(sql, {"student_id": student_id}).fetchone()

    @staticmethod
    def insert_user(student_id, nickname, phone, pwd_hash):
        sql = text("""
        INSERT INTO user(student_id, nickname, phone, pwd_hash, pwd_error_count, lock_expire_time)
        VALUES (:student_id, :nickname, :phone, :pwd_hash, 0, NULL)
        """)
        db.session.execute(sql, {"student_id": student_id, "nickname": nickname,
                                  "phone": phone, "pwd_hash": pwd_hash})
        db.session.commit()
        result = db.session.execute(text("SELECT LAST_INSERT_ID()"))
        return result.scalar()

    @staticmethod
    def update_pwd_fail_counter(user_id: int, new_fail_count: int, lock_expire: datetime | None):
        sql = text("""
        UPDATE user SET pwd_error_count=:new_fail_count, lock_expire_time=:lock_expire WHERE id=:user_id
        """)
        db.session.execute(sql, {"new_fail_count": new_fail_count,
                                  "lock_expire": lock_expire, "user_id": user_id})
        db.session.commit()

    @staticmethod
    def reset_lock(user_id: int):
        sql = text("UPDATE user SET pwd_error_count=0, lock_expire_time=NULL WHERE id=:user_id")
        db.session.execute(sql, {"user_id": user_id})
        db.session.commit()
