from datetime import datetime, timedelta
from app.config import MAX_PWD_FAIL, LOCK_DURATION_MINUTE

class AccountLockService:
    @staticmethod
    def is_can_login(lock_expire_time: datetime | None) -> tuple[bool, str]:
        """
        判断账号是否允许登录
        return (允许登录:bool, message)
        """
        now = datetime.now()
        if lock_expire_time is None:
            return True, ""
        if lock_expire_time > now:
            remain = int((lock_expire_time - now).total_seconds() // 60)
            msg = f"密码错误三次，账号已锁定！{remain}分钟后自动解锁"
            return False, msg
        # 锁定已经过期，可以自动解锁
        return True, ""

    @staticmethod
    def calc_lock_expire() -> datetime:
        """计算锁定到期时间：当前时间 + 15分钟"""
        return datetime.now() + timedelta(minutes=LOCK_DURATION_MINUTE)

    @staticmethod
    def need_lock(fail_count: int) -> bool:
        return fail_count + 1 >= MAX_PWD_FAIL
