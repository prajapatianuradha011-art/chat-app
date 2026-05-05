from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app)

# store online users
online_users = set()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect('/chat')
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect('/')
    return render_template('index.html', username=session['username'])

# 🔥 Real-time connection
@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        online_users.add(session['username'])
        emit('user_list', list(online_users), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'username' in session:
        online_users.discard(session['username'])
        emit('user_list', list(online_users), broadcast=True)

# 💬 Message handling
@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = session['username']

    emit('message', {
        'username': username,
        'msg': msg
    }, broadcast=True)
    
if __name__ == "__main__":
    socketio.run(app)