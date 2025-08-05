# TEST_ddmx

头杵不周山

## 使用方法

1. 安装依赖：`pip install -r requirements.txt`
2. 运行程序：`python app.py`
3. 浏览器访问 `http://localhost:5000`，输入密码后即可操作。

可通过环境变量 `PASSWORD_HASH` 和 `SECRET_KEY` 提升安全性，服务器地址在 `config.py` 中配置（基础地址，自动调用 `/task` 与 `/status`）。
<img width="929" height="590" alt="image" src="https://github.com/user-attachments/assets/f99b7275-50be-4c84-ab23-fa2282e94938" />

<img width="1272" height="1041" alt="image" src="https://github.com/user-attachments/assets/b90ba97b-0c2f-47a6-af23-a41e5337a79d" />

## 服务器端脚本

在每台 Linux 服务器上可运行 `worker.py` 来接收管理端分发的任务，脚本会把收到的链接与线程数传递给 Go 程序执行。

1. 安装依赖：`pip install Flask`
2. （可选）通过环境变量 `GO_EXEC` 指定 Go 可执行文件路径，默认 `./go_task`
3. 启动脚本：`python worker.py`

接口说明：

- `POST /task`：接受形如 `{"link": "http://...", "threads": 2}` 的 JSON，调用 Go 程序
- `GET /status`：返回最近一次任务执行的输出或错误信息
