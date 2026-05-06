from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = set()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')

        if not username:
            return "Username is required"

        session['username'] = username
        return redirect('/chat')

    return render_template('login.html')


@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/')
    return render_template('index.html', username=session['username'])


@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        online_users.add(username)
        emit('user_list', list(online_users), broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        online_users.discard(username)
        emit('user_list', list(online_users), broadcast=True)


@socketio.on('message')
def handle_message(data):
    username = session.get('username', 'Guest')
    msg = data.get('msg')

    emit('message', {
        'username': username,
        'msg': msg
    }, broadcast=True)


if __name__ == "__main__":
    socketio.run(app)
