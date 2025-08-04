from flask import Flask, render_template, request, redirect, url_for, session
import requests
import config

app = Flask(__name__)
app.secret_key = 'replace-with-random-secret-key'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == config.PASSWORD:
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
    if request.method == 'POST':
        links = [line.strip() for line in request.form.get('links', '').splitlines() if line.strip()]
        selected_servers = request.form.getlist('servers')
        for server_url in selected_servers:
            for link in links:
                try:
                    requests.post(server_url, json={'link': link}, timeout=5)
                except requests.RequestException:
                    pass
        message = '任务已分发'
    return render_template('index.html', servers=config.SERVERS, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
