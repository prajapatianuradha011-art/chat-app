from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, send
import sqlite3
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = "secret123"

# IMPORTANT
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 🔹 Create DB
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # messages table
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        msg TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# 🟢 SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()

        except:
            conn.close()
            return "Username already exists!"

        conn.close()
        return redirect('/login')

    return render_template('signup.html')


# 🟢 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("chat.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/')

        else:
            return "Invalid login!"

    return render_template('login.html')


# 🟢 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# 🟢 HOME
@app.route('/')
def home():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'chat.html',
        username=session['user']
    )


# 🟢 SOCKET MESSAGE
@socketio.on('message')
def handle_message(data):

    username = session.get('user')

    # save message
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages (username, msg) VALUES (?, ?)",
        (username, data['msg'])
    )

    conn.commit()
    conn.close()

    send({
        "username": username,
        "msg": data['msg']
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)