from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import check_password_hash
import threading
import time
import uuid
import os
import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')

# --- 数据结构 ---
servers = {s['id']: dict(s, used=0) for s in config.INIT_SERVERS}
# 按分组统计总能力
capacity = {'L4': 0, 'L7': 0}
for s in servers.values():
    capacity[s['group']] += s['max']
used_capacity = {'L4': 0, 'L7': 0}

tasks = {}  # id -> task info
task_queue = []
lock = threading.Lock()

# --- 工具函数 ---
def get_available(group):
    return capacity.get(group, 0) - used_capacity.get(group, 0)

def check_queue():
    with lock:
        for task in list(task_queue):
            if get_available(task['layer']) >= task['concurrency']:
                task_queue.remove(task)
                _start_task(task)

def _start_task(task):
    used_capacity[task['layer']] += task['concurrency']
    task['status'] = '执行中'
    task['progress'] = 0
    t = threading.Thread(target=run_task, args=(task,), daemon=True)
    t.start()

def run_task(task):
    duration = task['duration']
    start = time.time()
    while True:
        time.sleep(1)
        elapsed = time.time() - start
        with lock:
            task['progress'] = min(100, int(elapsed / duration * 100))
            if elapsed >= duration:
                task['status'] = '已完成'
                used_capacity[task['layer']] -= task['concurrency']
                break
    check_queue()

# --- 路由 ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if check_password_hash(config.ADMIN_PASSWORD_HASH, pwd):
            session['logged_in'] = True
            session['role'] = 'admin'
            return redirect(url_for('index'))
        elif check_password_hash(config.USER_PASSWORD_HASH, pwd):
            session['logged_in'] = True
            session['role'] = 'user'
            return redirect(url_for('index'))
        else:
            error = '密码错误'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    max_concurrency = config.DEFAULT_MAX_CONCURRENCY
    max_duration = config.DEFAULT_MAX_DURATION
    layer_methods = config.LAYER_METHODS
    message = None
    if request.method == 'POST':
        targets = [t.strip() for t in request.form.get('targets', '').splitlines() if t.strip()]
        layer = request.form.get('layer')
        concurrency = int(request.form.get('concurrency', 1))
        duration = int(request.form.get('duration', 1))
        method = request.form.get('method')
        if not targets:
            flash('目标地址不能为空')
        elif layer not in layer_methods:
            flash('攻击层级无效')
        elif method not in layer_methods.get(layer, []):
            flash('攻击方法无效')
        else:
            tid = str(uuid.uuid4())[:8]
            task = {
                'id': tid,
                'targets': targets,
                'layer': layer,
                'concurrency': concurrency,
                'duration': duration,
                'method': method,
                'status': '排队中',
                'progress': 0
            }
            with lock:
                tasks[tid] = task
                if get_available(layer) >= concurrency:
                    _start_task(task)
                else:
                    task_queue.append(task)
            message = f'任务已提交，ID: {tid}'
    queue_len = len(task_queue)
    return render_template('index.html',
                           max_concurrency=max_concurrency,
                           max_duration=max_duration,
                           layer_methods=layer_methods,
                           message=message,
                           queue_len=queue_len,
                           role=session.get('role'))

@app.route('/tasks')
def task_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('tasks.html', role=session.get('role'))

@app.route('/api/tasks')
def api_tasks():
    if not session.get('logged_in'):
        return jsonify([]), 401
    with lock:
        return jsonify(list(tasks.values()))

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/api/servers')
def api_servers():
    if session.get('role') != 'admin':
        return jsonify([]), 401
    with lock:
        return jsonify(list(servers.values()))

@app.route('/admin/server/<sid>/toggle', methods=['POST'])
def toggle_server(sid):
    if session.get('role') != 'admin':
        return 'forbidden', 403
    with lock:
        s = servers.get(sid)
        if not s:
            return 'not found', 404
        if s['status'] == 'online':
            s['status'] = 'offline'
            capacity[s['group']] -= s['max']
        else:
            s['status'] = 'online'
            capacity[s['group']] += s['max']
    check_queue()
    return 'ok'

@app.route('/agent/register', methods=['POST'])
def agent_register():
    data = request.get_json() or {}
    sid = data.get('id') or str(uuid.uuid4())
    ip = data.get('ip', '')
    group = data.get('group', 'L4')
    maxc = int(data.get('max', 0))
    with lock:
        if sid in servers:
            # 更新能力
            capacity[servers[sid]['group']] -= servers[sid]['max']
        servers[sid] = {'id': sid, 'ip': ip, 'group': group, 'max': maxc, 'status': 'online', 'used': 0}
        capacity[group] = capacity.get(group, 0) + maxc
    check_queue()
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
