import sqlite3

# From a session UUID, extract all of the associated page visits and mouse positions to construct a string suitable for an LLM prompt.
def session_tostring(session_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('backend/db/app.db')
    cursor = conn.cursor()

    # Get all page visits for the session
    cursor.execute('SELECT pagevisit_token, page_path, start_time, end_time FROM PageVisits WHERE session_id = ?', (session_id,))
    page_visits = cursor.fetchall()

    # Get all mouse positions for the session
    cursor.execute('SELECT pagevisit_token, position_x, position_y, text_or_tag_hovered, recorded_at FROM MouseMovements WHERE session_id = ?', (session_id,))
    mouse_positions = cursor.fetchall()

    # Close the connection
    conn.close()

    # Construct the string
    result = ''
    for i, page_visit in enumerate(page_visits):
        page_visit_length = ''
        try:
            page_visit_length = f'{round((int(page_visit[3]) - int(page_visit[2])) / 1000, 2)} seconds'
        except:
            page_visit_length = 'unknown time'
        if i == len(page_visits) - 1:
            page_visit_length = 'last page in session'
        result += f'Visited page "{page_visit[1]}" ({page_visit_length})\n'
        prev_mouse_position = None
        mouse_position_count = 0
        for mouse_position in mouse_positions:
            if mouse_position[0] == page_visit[0]:
                if mouse_position[3] == prev_mouse_position:
                    mouse_position_count += 1
                else:
                    if prev_mouse_position is not None and mouse_position_count > 1:
                        result += f' ({mouse_position_count} seconds)\n'
                    elif mouse_position_count == 1:
                        result += "\n"
                    result += f'<t>{mouse_position[3].replace('\n', ' ')}</t>'
                    prev_mouse_position = mouse_position[3]
                    mouse_position_count = 1
        # if prev_mouse_position is not None:
        #     result += f' ({mouse_position_count} seconds)\n'
        result += "\n\n"

    return result