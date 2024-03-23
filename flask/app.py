from datetime import datetime
import sqlite3
import threading
import time

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from constants import ACTIVE_SESSION_TIMEOUT_MINUTES, SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS
from utils import prompt_claude_session_context

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

def get_active_sessions(timeout_minutes=ACTIVE_SESSION_TIMEOUT_MINUTES):
    conn = db_connection()
    cursor = conn.cursor()
    now_ms = int(time.time() * 1000)
    one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
    cursor.execute("SELECT DISTINCT session_id FROM MouseMovements WHERE CAST(recorded_at AS INTEGER) > ?", (one_minute_ago,))
    res = cursor.fetchall()

    # Set the end_time of all hanging (end_time = NULL) page_visits in INACTIVE sessions to now_ms
    # cursor.execute("UPDATE PageVisits SET end_time = ? WHERE session_id NOT IN (SELECT session_id FROM MouseMovements WHERE CAST(recorded_at AS INTEGER) > ?) AND end_time IS NULL", (now_ms, one_minute_ago))

    conn.commit()
    conn.close()

    return [session[0] for session in res]

def prompt_claude_and_store_response(session_id):
    response = prompt_claude_session_context(session_id)
    timestamp = str(int(time.time()))

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO LLMResponses (session_id, response, recorded_at) VALUES (?, ?, ?)", (session_id, response, timestamp))
    conn.commit()
    conn.close()
    
    return response, timestamp

def prompt_active_sessions_background_task():
    while True:
        active_sessions = get_active_sessions()
        #print(active_sessions)
        for session_id in active_sessions:
            response, timestamp = prompt_claude_and_store_response(session_id)
        socketio.sleep(SOCKETIO_BACKGROUND_TASK_DELAY_SECONDS)

def should_log_mouse_update(session_id, new_x, new_y):
    conn = db_connection()
    cursor = conn.cursor()
    now_ms = int(time.time() * 1000)
    one_minute_ago = now_ms - (ACTIVE_SESSION_TIMEOUT_MINUTES * 60000)
    cursor.execute("SELECT position_x, position_y FROM MouseMovements WHERE session_id = ? AND CAST(recorded_at AS INTEGER) > ? ORDER BY recorded_at LIMIT 1",
                   (session_id, one_minute_ago))
    last_position = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM MouseMovements WHERE session_id = ?", (session_id,))
    has_mouse_movements = cursor.fetchone()[0] > 0
    conn.close()
    return (not last_position and not has_mouse_movements) or last_position[0] != new_x or last_position[1] != new_y

@socketio.on('mouseUpdate')
def handle_mouse_update(data):
    if should_log_mouse_update(data['session_id'], data['mousePos']['x'], data['mousePos']['y']):
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO MouseMovements (session_id, pagevisit_token, position_x, position_y, text_or_tag_hovered, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (data['session_id'], data['pageVisitToken'], data['mousePos']['x'], data['mousePos']['y'], data['hovered'], data['recordedAt']))
        conn.commit()

        # also check if there is a llmresponse that is not emitted
        cursor.execute("SELECT response FROM LLMResponses WHERE is_emitted = FALSE AND session_id = ? ORDER BY recorded_at DESC LIMIT 1", (data['session_id'],))
        llm_response = cursor.fetchone()
        if llm_response:
            emit('llmResponse', llm_response[0])
            # Set the is_emitted of the most recent llmresponse for that session_id to TRUE
            cursor.execute("UPDATE LLMResponses SET is_emitted = TRUE WHERE session_id = ? AND id = (SELECT id FROM LLMResponses WHERE session_id = ? ORDER BY recorded_at DESC LIMIT 1)", (data['session_id'], data['session_id']))
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
    socketio.start_background_task(prompt_active_sessions_background_task)
    socketio.run(app)