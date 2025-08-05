# TEST_ddmx

简单的任务分发管理页面示例，界面采用 Bootstrap 配合自定义渐变背景与半透明卡片，整体科技感十足且简洁大方。支持分发后实时查询各服务器任务状态，并可在页面右上角更换背景图。

## 使用方法

1. 安装依赖：`pip install -r requirements.txt`
2. 运行程序：`python app.py`
3. 浏览器访问 `http://localhost:5000`，输入密码后即可操作。

可通过环境变量 `PASSWORD_HASH` 和 `SECRET_KEY` 提升安全性，服务器地址在 `config.py` 中配置（基础地址，自动调用 `/task` 与 `/status`）。
