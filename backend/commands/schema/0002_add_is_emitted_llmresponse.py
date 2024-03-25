import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('backend/db/app.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Add a new column is_emitted to the LLMResponses table
cursor.execute('ALTER TABLE LLMResponses ADD COLUMN is_emitted BOOLEAN DEFAULT FALSE')

# Commit the changes and close the connection
conn.commit()
conn.close()