from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('interaction_data')
def handle_interaction_data(data):
    res = process(data)
    emit('message', res)

def process(data):
    # Do some processing
    return "foo"

if __name__ == '__main__':
    socketio.run(app)