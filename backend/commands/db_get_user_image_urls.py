from constants import initialize_command
initialize_command()

from backend.postgres.db_utils import _db_session
from backend.postgres.schema import Sessions, Promotions

# From a session UUID, extract the user and return a list of all image urls used on their active promotions
def get_user_image_urls(session_id):
    # Connect to the PostgreSQL database
    session = _db_session()

    # Query the database for the impulse_user_id
    session_obj = session.query(Sessions).filter(Sessions.id == session_id).first()
    
    if session_obj: # if session exists
        user_impulse_id = session_obj.impulse_user_id

         # Query the database for the promotions
        user_promotions = session.query(Promotions).filter(Promotions.impulse_user_id == user_impulse_id).all()

        session.close()
        return [promotion.image_url for promotion in user_promotions]
    else:
        session.close()
        return []