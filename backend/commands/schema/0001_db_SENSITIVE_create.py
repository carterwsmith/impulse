import sqlite3

# Connect to the SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('backend/db/app.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Create table for Sessions
cursor.execute('''
CREATE TABLE IF NOT EXISTS Sessions (
    id TEXT PRIMARY KEY
)
''')

# Create table for Page Visits
cursor.execute('''
CREATE TABLE IF NOT EXISTS PageVisits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    pagevisit_token TEXT NOT NULL,
    page_path TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    FOREIGN KEY (session_id) REFERENCES Sessions(id)
)
''')

# Create table for Mouse Movements
cursor.execute('''
CREATE TABLE IF NOT EXISTS MouseMovements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    pagevisit_token TEXT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    text_or_tag_hovered TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Sessions(id),
    FOREIGN KEY (pagevisit_token) REFERENCES PageVisits(pagevisit_token)
)
''')

# Create table for LLM Responses
cursor.execute('''
CREATE TABLE IF NOT EXISTS LLMResponses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    response TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES Sessions(id)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()