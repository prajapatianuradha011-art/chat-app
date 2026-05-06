from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

@app.route('/')
def home():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(data):
    send(data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)