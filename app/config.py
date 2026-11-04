import datetime

# 学号规则：支持10位、13位纯数字
STUDENT_ID_PATTERN = r'^(\d{10}|\d{13})$'
# 密码最小长度
PASSWORD_MIN_LEN = 6
# 密码错误最大尝试次数
MAX_PWD_FAIL = 3
# 账号锁定时长：15分钟
LOCK_DURATION_MINUTE = 15
# bcrypt迭代轮次，兼顾安全与性能（对应文档性能风险）
BCRYPT_ROUNDS = 10
# session会话超时，单位秒
SESSION_EXPIRE_SEC = 3600

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/campus_auth?charset=utf8mb4"
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = "your-secret-key-here-campustrader"
