from app.repository.user_repository import UserRepository
from app.service.student_id_validator import StudentIdValidator
from app.service.crypto_service import CryptoService
from app.service.account_lock_service import AccountLockService
from app.service.session_service import SessionService

class LoginRegisterService:
    @staticmethod
    def register(student_id: str, nickname: str, phone: str, raw_pwd: str):
        """注册业务编排"""
        # 1.学号校验委派组件
        valid_sid, msg_sid = StudentIdValidator.validate(student_id)
        if not valid_sid:
            raise ValueError(msg_sid)
        # 2.校验学号是否已注册
        exist = UserRepository.find_by_student_id(student_id)
        if exist:
            raise ValueError("该学号已经注册！")
        # 3.密码加密委派CryptoService
        pwd_hash = CryptoService.hash_pwd(raw_pwd)
        # 4.数据库写入
        uid = UserRepository.insert_user(student_id, nickname, phone, pwd_hash)
        return uid

    @staticmethod
    def login(student_id: str, raw_pwd: str):
        """登录业务编排"""
        user_row = UserRepository.find_by_student_id(student_id)
        if not user_row:
            # 安全：统一返回账号或密码错误，防止学号枚举
            raise ValueError("账号或密码错误")

        user_id = user_row.id
        fail_count = user_row.pwd_error_count
        lock_expire = user_row.lock_expire_time

        # 【委派锁定组件】判断锁定；过期自动解锁
        can_login, lock_msg = AccountLockService.is_can_login(lock_expire)
        if not can_login:
            raise ValueError(lock_msg)
        if lock_expire is not None:
            # 已经过期，重置锁定状态
            UserRepository.reset_lock(user_id)
            fail_count = 0

        # 密码校验委派CryptoService
        ok = CryptoService.verify_pwd(raw_pwd, user_row.pwd_hash)
        if not ok:
            new_fail = fail_count + 1
            if AccountLockService.need_lock(new_fail):
                lock_time = AccountLockService.calc_lock_expire()
                UserRepository.update_pwd_fail_counter(user_id, new_fail, lock_time)
                raise ValueError(AccountLockService.is_can_login(lock_time)[1])
            else:
                UserRepository.update_pwd_fail_counter(user_id, new_fail, None)
                remain = 3 - new_fail
                raise ValueError(f"账号或密码错误，剩余尝试次数：{remain}")

        # 登录成功：重置错误计数，创建会话
        UserRepository.update_pwd_fail_counter(user_id, 0, None)
        SessionService.create_session(user_id, student_id)
        return user_id
