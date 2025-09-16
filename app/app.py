import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in a real application

DATABASE_FILE = 'database.json'

def read_users():
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_users(users):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def get_user_by_username(username):
    users = read_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

def get_user_by_id(user_id):
    users = read_users()
    for user in users:
        if user['id'] == user_id:
            return user
    return None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('user_list'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = read_users()
        user_id = len(users) + 1
        new_user = {
            'id': user_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'contact': request.form['contact'],
            'username': request.form['username'],
            'password': request.form['password'] # In a real app, hash this!
        }

        if get_user_by_username(new_user['username']):
            flash('Username already exists!', 'danger')
            return render_template('signup.html')

        users.append(new_user)
        write_users(users)
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        if user and user['password'] == password:
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('user_list'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/list')
def user_list():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    users = read_users()
    return render_template('list.html', users=users)

@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('user_list'))

    if request.method == 'POST':
        users = read_users()
        for u in users:
            if u['id'] == user_id:
                u['name'] = request.form['name']
                u['email'] = request.form['email']
                u['contact'] = request.form['contact']
                # Not allowing username/password update for simplicity
                break
        write_users(users)
        flash('User updated successfully!', 'success')
        return redirect(url_for('user_list'))

    return render_template('update.html', user=user)

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    users = read_users()
    users = [user for user in users if user['id'] != user_id]
    write_users(users)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('user_list'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
