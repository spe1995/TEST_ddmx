# TEST_ddmx

基于 Flask 的压力测试任务管理示例，提供普通用户和管理员两类界面。

## 功能概览
- 用户通过 Web 页面提交任务：支持多目标地址、选择 L4/L7 层级、并发数与测试时长滑动条、攻击方法自动联动下拉框。
- 后端根据各子服务器上报的能力自动分配资源，能力不足时任务进入队列等待，资源释放后自动执行。
- 任务列表页面实时展示执行进度和状态。
- 管理员后台可查看/管理子服务器分组、最大并发与状态，支持手动下线或上线服务器。
- 子服务器启动后调用管理端 `/agent/register` 自动上报自身能力。

整体界面采用白底蓝色主调的简洁风格，按钮和进度条基于 Bootstrap，交互友好。

## 使用方法
1. 安装依赖：`pip install -r requirements.txt`
2. 运行管理端：`python app.py`
3. 浏览器访问 `http://localhost:5000`，使用默认密码登录
   - 普通用户密码：`user123`
   - 管理员密码：`admin123`
4. 子服务器可运行 `worker.py`，并通过设置 `MANAGER_URL` 环境变量自动向管理端注册。

攻击层级与方法绑定关系可在 `config.py` 的 `LAYER_METHODS` 中自定义。

## 服务器端脚本 `worker.py`

1. 安装依赖：`pip install Flask requests`
2. （可选）环境变量
   - `GO_EXEC`：Go 可执行文件路径，默认 `./go_task`
   - `MANAGER_URL`：管理端地址，如 `http://manager:5000`
   - `AGENT_ID`/`AGENT_GROUP`/`AGENT_MAX`：上报信息
3. 启动脚本：`python worker.py`

接口说明：
- `POST /task`：接受 `{"link":"http://...","threads":2}`，将参数传给 Go 程序
- `GET /status`：返回最近一次任务执行状态
