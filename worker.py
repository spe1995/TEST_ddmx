
from flask import Flask, request, jsonify
import subprocess
import os
import requests
import threading

app = Flask(__name__)

last_status = "等待任务"
GO_EXEC = os.environ.get('GO_EXEC', './go_task')
MANAGER_URL = os.environ.get('MANAGER_URL')
AGENT_ID = os.environ.get('AGENT_ID', 'agent1')
AGENT_GROUP = os.environ.get('AGENT_GROUP', 'L4')
AGENT_MAX = int(os.environ.get('AGENT_MAX', '100'))

def report():
    if MANAGER_URL:
        try:
            requests.post(
                MANAGER_URL.rstrip('/') + '/agent/register',
                json={'id': AGENT_ID, 'ip': os.environ.get('AGENT_IP', ''),
                      'group': AGENT_GROUP, 'max': AGENT_MAX}, timeout=5
            )
        except requests.RequestException:
            pass

@app.route('/task', methods=['POST'])
def task():
    global last_status
    data = request.get_json() or {}
    link = data.get('link')
    threads = str(data.get('threads', 1))
    if not link:
        last_status = '缺少链接参数'
        return jsonify({'error': 'missing link'}), 400
    try:
        result = subprocess.run([GO_EXEC, link, threads], capture_output=True, text=True, check=True)
        last_status = result.stdout.strip() or '已完成'
        return jsonify({'status': 'ok'})
    except FileNotFoundError:
        last_status = 'Go 程序不存在'
        return jsonify({'error': 'go program not found'}), 500
    except subprocess.CalledProcessError as e:
        last_status = e.stderr.strip() or '执行失败'
        return jsonify({'error': 'go program failed'}), 500

@app.route('/status', methods=['GET'])
def status():
    return last_status

if __name__ == '__main__':
    threading.Thread(target=report, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
