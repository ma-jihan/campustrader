import re
from app.config import STUDENT_ID_PATTERN

class StudentIdValidator:
    @staticmethod
    def validate(student_id: str) -> tuple[bool, str]:
        """
        返回 (是否合法, 提示信息)
        """
        if not student_id:
            return False, "学号不能为空！"
        if re.fullmatch(STUDENT_ID_PATTERN, student_id):
            return True, ""
        return False, "学号格式错误，仅支持10位或13位数字学号"
