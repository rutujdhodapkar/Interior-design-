import os
import json
from datetime import datetime
from urllib.parse import quote
from flask import Flask, send_from_directory, abort, request, redirect, make_response, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)

FILES = {
    '': 'home.html',
    'home': 'home.html',
    'login': 'login.html',
    'signup': 'signup.html',
    'chat': 'chat.html',
    'loading': 'loading.html',
    'error': 'error.html',
    'logorsign': 'logorsign.html'
}

def _send_file(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(path):
        return send_from_directory(BASE_DIR, filename)
    abort(404)

for route, filename in FILES.items():
    endpoint = '/' if route == '' else f'/{route}'

    def make_view(fn, route_name):
        def view():
            return _send_file(fn)
        view.__name__ = f'view_{route_name or "root"}_{fn.replace(".", "_")}'
        return view

    endpoint_name = f'endpoint_{route or "root"}'
    app.add_url_rule(endpoint, endpoint_name, view_func=make_view(filename, route))
    filename_path = f'/{filename}'
    endpoint_name_file = f'{endpoint_name}_file'
    app.add_url_rule(filename_path, endpoint_name_file, view_func=make_view(filename, route))

@app.route('/files/<path:filename>')
def files(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(path):
        return send_from_directory(BASE_DIR, filename)
    abort(404)


@app.route('/signup', methods=['POST'])
def handle_signup():
    form = request.form
    username = (form.get('username') or '').strip()
    email = (form.get('email') or '').strip()
    first = (form.get('first') or '').strip()
    last = (form.get('last') or '').strip()
    password = (form.get('password') or '').strip()
    age = (form.get('age') or '').strip()
    role = (form.get('role') or '').strip()

    if not username or not email or not first or not password:
        msg = "Missing required fields"
        return redirect(f'/signup.html?error={quote(msg)}')
    if "@" not in email or "." not in email:
        msg = "Invalid email address"
        return redirect(f'/signup.html?error={quote(msg)}')

    users_path = os.path.join(BASE_DIR, 'users.json')
    try:
        if os.path.exists(users_path):
            with open(users_path, 'r', encoding='utf-8') as fh:
                try:
                    users = json.load(fh)
                except Exception:
                    users = []
        else:
            users = []

        for u in users:
            if u.get('username') == username:
                return redirect(f'/signup.html?error={quote("Username already exists")}')
            if u.get('email') == email:
                return redirect(f'/signup.html?error={quote("Email already registered")}')

        user_obj = {
            "username": username,
            "email": email,
            "first": first,
            "last": last,
            "password": password,
            "age": age,
            "role": role,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        users.append(user_obj)
        with open(users_path, 'w', encoding='utf-8') as fh:
            json.dump(users, fh, indent=2, ensure_ascii=False)

        return redirect('/login.html')
    except Exception as e:
        return redirect(f'/signup.html?error={quote("Server error: " + str(e))}')


@app.route('/login', methods=['POST'])
def handle_login():
    form = request.form
    email = (form.get('email') or '').strip()
    password = (form.get('password') or '').strip()

    if not email or not password:
        return redirect(f'/login.html?error={quote("Missing email or password")}')

    users_path = os.path.join(BASE_DIR, 'users.json')
    try:
        if os.path.exists(users_path):
            with open(users_path, 'r', encoding='utf-8') as fh:
                try:
                    users = json.load(fh)
                except Exception:
                    users = []
        else:
            users = []

        user = None
        for u in users:
            if u.get('email') == email:
                user = u
                break

        if not user or user.get('password') != password:
            return redirect(f'/login.html?error={quote("Invalid email or password")}')

        resp = make_response(redirect('/chat.html'))
        resp.set_cookie('user_id', user.get('username') or '', httponly=True)
        resp.set_cookie('device_id', datetime.utcnow().isoformat() + "Z", httponly=True)
        return resp
    except Exception as e:
        return redirect(f'/login.html?error={quote("Server error: " + str(e))}')


@app.route('/get_user_info')
def get_user_info():
    username = request.cookies.get('user_id') or ''
    if not username:
        return jsonify({}), 200

    users_path = os.path.join(BASE_DIR, 'users.json')
    try:
        if os.path.exists(users_path):
            with open(users_path, 'r', encoding='utf-8') as fh:
                try:
                    users = json.load(fh)
                except Exception:
                    users = []
        else:
            users = []

        user = None
        for u in users:
            if u.get('username') == username:
                user = u
                break

        if not user:
            return jsonify({}), 200

        safe_user = {
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'first': user.get('first', ''),
            'last': user.get('last', ''),
            'age': user.get('age', ''),
            'role': user.get('role', '')
        }
        return jsonify(safe_user)
    except Exception:
        return jsonify({}), 200


@app.route('/logout')
def logout():
    resp = make_response(jsonify({'ok': True}))
    resp.set_cookie('user_id', '', expires=0)
    resp.set_cookie('device_id', '', expires=0)
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

