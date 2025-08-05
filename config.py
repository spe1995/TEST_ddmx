import os
from werkzeug.security import generate_password_hash

PASSWORD_HASH = os.environ.get(
    'PASSWORD_HASH', generate_password_hash('admin123')
)

# 服务器基础地址，任务分发默认调用 /task，状态查询默认调用 /status
SERVERS = {
    '服务器1': 'http://server1.example.com',
    '服务器2': 'http://server2.example.com',
}
