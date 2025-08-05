from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

last_status = "等待任务"
GO_EXEC = os.environ.get('GO_EXEC', './go_task')

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
    app.run(host='0.0.0.0', port=8000)
