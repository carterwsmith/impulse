from datetime import datetime
import sqlite3

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('flask/db/app.db')
    except sqlite3.error as e:
        print(e)
    return conn

@socketio.on('mouseUpdate')
def handle_mouse_update(data):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO MouseMovements (session_id, pagevisit_token, position_x, position_y, recorded_at) VALUES (?, ?, ?, ?, ?)",
                    (data['session_id'], data['pageVisitToken'], data['mousePos']['x'], data['mousePos']['y'], data['recordedAt']))
    conn.commit()
    conn.close()

@socketio.on('pageVisit')
def handle_page_visit(data):
    conn = db_connection()
    cursor = conn.cursor()
    
    ## create session if needed
    # Check if the session exists
    cursor.execute("SELECT id FROM Sessions WHERE id = ?", (data['session_id'],))
    session = cursor.fetchone()
    
    # If the session does not exist, create it
    if not session:
        cursor.execute("INSERT INTO Sessions (id) VALUES (?)", (data['session_id'],))

    cursor.execute("INSERT INTO PageVisits (session_id, pagevisit_token, page_path, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
                    (data['session_id'], data['pageVisitToken'], data['pagePath'], data['startTime'], None))
    conn.commit()
    conn.close()

@socketio.on('pageVisitEnd')
def handle_page_visit_end(data):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE PageVisits SET end_time = ? WHERE pagevisit_token = ?",
                    (data['endTime'], data['pageVisitToken']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    socketio.run(app)