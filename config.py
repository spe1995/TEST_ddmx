import os
from werkzeug.security import generate_password_hash

# 普通用户与管理员密码哈希，可通过环境变量覆盖
ADMIN_PASSWORD_HASH = os.environ.get(
    'ADMIN_PASSWORD_HASH', generate_password_hash('admin123')
)
USER_PASSWORD_HASH = os.environ.get(
    'USER_PASSWORD_HASH', generate_password_hash('user123')
)

# 默认最大并发与时长，可根据实际资源动态调整
DEFAULT_MAX_CONCURRENCY = 100
DEFAULT_MAX_DURATION = 300

# 初始服务器列表，实际使用中由子服务器自动上报
INIT_SERVERS = [
    {'id': 's1', 'ip': '127.0.0.1', 'group': 'L4', 'max': 50, 'status': 'online'},
    {'id': 's2', 'ip': '127.0.0.1', 'group': 'L7', 'max': 50, 'status': 'online'},
]
