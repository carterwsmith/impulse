import sqlite3

# From a session UUID, extract the user and return a list of all image urls used on their active promotions
def get_user_image_urls(session_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('backend/db/app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT django_user_id FROM app_sessions WHERE id = ?', (session_id,))
    django_user_id = cursor.fetchone()[0]

    cursor.execute('SELECT image_url FROM app_promotions WHERE django_user_id = ?', (django_user_id,))
    image_urls = cursor.fetchall()

    conn.close()

    return [promotion[0] for promotion in image_urls]
