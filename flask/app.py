from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('interaction_data')
def handle_interaction_data(data):
    res = process(data)
    emit('example', res)

def process(data):
    # Do some processing
    return "foo"

if __name__ == '__main__':
    socketio.run(app)