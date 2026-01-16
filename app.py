import os
import json
from datetime import datetime
from urllib.parse import quote
from flask import Flask, send_from_directory, abort, request, redirect, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)

# --- Encryption Setup ---
KEY_FILE = os.path.join(BASE_DIR, 'secret.key')

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    with open(KEY_FILE, 'rb') as key_file:
        return key_file.read()

cipher = Fernet(load_key())

def encrypt_val(value):
    if not value: return ""
    return cipher.encrypt(value.encode()).decode()

def decrypt_val(value):
    if not value: return ""
    try:
        return cipher.decrypt(value.encode()).decode()
    except:
        return value  # Return original if decryption fails (fallback)
# ------------------------

@app.before_request
def enforce_https():
    if request.headers.get("X-Forwarded-Proto") == "http":
        return redirect(request.url.replace("http://", "https://"), code=301)

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
            # Decrypt email to check for duplicates
            stored_email = decrypt_val(u.get('email'))
            if stored_email == email:
                return redirect(f'/signup.html?error={quote("Email already registered")}')

        user_obj = {
            "username": username,
            "email": encrypt_val(email),
            "first": encrypt_val(first),
            "last": encrypt_val(last),
            "password": generate_password_hash(password),
            "age": encrypt_val(age),
            "role": encrypt_val(role),
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
                # This check is tricky if email is encrypted. 
                # We usually lookup by username, but form sends email.
                # Strategy: iterate and decrypt email to find user.
                pass 

        # Optimization: Since we login by Email, we have to scan.
        target_user = None
        for u in users:
            if decrypt_val(u.get('email')) == email:
                target_user = u
                break
        
        if not target_user:
             return redirect(f'/login.html?error={quote("Invalid email or password")}')

        # Verify password (hash)
        if not check_password_hash(target_user.get('password'), password):
            return redirect(f'/login.html?error={quote("Invalid email or password")}')

        resp = make_response(redirect('/chat.html'))
        resp.set_cookie('user_id', target_user.get('username') or '', httponly=True, secure=True, samesite='Lax')
        resp.set_cookie('device_id', datetime.utcnow().isoformat() + "Z", httponly=True, secure=True, samesite='Lax')
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
            'email': decrypt_val(user.get('email', '')),
            'first': decrypt_val(user.get('first', '')),
            'last': decrypt_val(user.get('last', '')),
            'age': decrypt_val(user.get('age', '')),
            'role': decrypt_val(user.get('role', ''))
        }
        return jsonify(safe_user)
    except Exception:
        return jsonify({}), 200


@app.route('/logout')
def logout():
    resp = make_response(jsonify({'ok': True}))
    resp.set_cookie('user_id', '', expires=0, secure=True, httponly=True, samesite='Lax')
    resp.set_cookie('device_id', '', expires=0, secure=True, httponly=True, samesite='Lax')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

