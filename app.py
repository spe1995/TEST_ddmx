from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
import os
import requests
import config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if check_password_hash(config.PASSWORD_HASH, request.form.get('password', '')):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = '密码错误'
    return render_template('login.html', error=error)

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    message = None
    selected_info = []
    if request.method == 'POST':
        links = [line.strip() for line in request.form.get('links', '').splitlines() if line.strip()]
        selected_servers = request.form.getlist('servers')
        for idx, (name, base_url) in enumerate(config.SERVERS.items(), start=1):
            thread_str = request.form.get(f'threads{idx}', '1')
            try:
                threads = max(1, int(thread_str))
            except ValueError:
                threads = 1
            if base_url in selected_servers:
                selected_info.append({'id': idx, 'name': name, 'url': base_url})
                for link in links:
                    try:
                        requests.post(
                            base_url.rstrip('/') + '/task',
                            json={'link': link, 'threads': threads},
                            timeout=5,
                        )
                    except requests.RequestException:
                        pass
        message = '任务已分发'
    return render_template('index.html', servers=config.SERVERS, message=message, selected_info=selected_info)


@app.route('/status', methods=['POST'])
def status():
    if not session.get('logged_in'):
        return jsonify({}), 401
    data = request.get_json() or {}
    servers = data.get('servers', [])
    result = {}
    for s in servers:
        name = s.get('name')
        url = s.get('url')
        status_url = url.rstrip('/') + '/status'
        try:
            r = requests.get(status_url, timeout=5)
            result[name] = r.text
        except requests.RequestException:
            result[name] = '无法连接'
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
