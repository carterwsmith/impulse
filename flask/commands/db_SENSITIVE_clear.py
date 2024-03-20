import sqlite3

# Connect to the SQLite database. It will be created if it doesn't exist.
conn = sqlite3.connect('flask/db/app.db')

# Create a cursor object using the cursor() method
cursor = conn.cursor()

# Delete all rows from the Sessions table
cursor.execute('DELETE FROM Sessions')

# Delete all rows from the PageVisits table
cursor.execute('DELETE FROM PageVisits')

# Delete all rows from the MouseMovements table
cursor.execute('DELETE FROM MouseMovements')

# Commit the changes and close the connection
conn.commit()
conn.close()