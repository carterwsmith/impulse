from constants import initialize_command
initialize_command()

from backend.postgres.db_utils import _db_session
from backend.postgres.schema import PageVisits, MouseMovements

# From a session UUID, extract all of the associated page visits and mouse positions to construct a string suitable for an LLM prompt.
def session_tostring(session_id):
    # Connect to the PostgreSQL database
    session = _db_session()

    # Get all page visits for the session
    page_visits = session.query(PageVisits).filter(PageVisits.session_id == session_id).all()

    # Get all mouse positions for the session
    mouse_positions = session.query(MouseMovements).filter(MouseMovements.session_id == session_id).all()

    # Close the connection
    session.close()

    # Construct the string
    result = ''
    for i, page_visit in enumerate(page_visits):
        page_visit_length = ''
        try:
            page_visit_length = f'{round((int(page_visit.end_time) - int(page_visit.start_time)) / 1000, 2)} seconds'
        except:
            page_visit_length = 'unknown time'
        if i == len(page_visits) - 1:
            page_visit_length = 'last page in session'
        result += f'Visited page "{page_visit.page_path}" ({page_visit_length})\n'
        prev_mouse_position = None
        mouse_position_count = 0
        for mouse_position in mouse_positions:
            if mouse_position.pagevisit_token_id == page_visit.pagevisit_token:
                if mouse_position.text_or_tag_hovered == prev_mouse_position:
                    mouse_position_count += 1
                else:
                    if prev_mouse_position is not None and mouse_position_count > 1:
                        result += f' ({mouse_position_count} seconds)\n'
                    elif mouse_position_count == 1:
                        result += "\n"
                    result += f'<t>{mouse_position.text_or_tag_hovered.replace('\n', ' ')}</t>'
                    prev_mouse_position = mouse_position.text_or_tag_hovered
                    mouse_position_count = 1
        # if prev_mouse_position is not None:
        #     result += f' ({mouse_position_count} seconds)\n'
        result += "\n\n"

    return result