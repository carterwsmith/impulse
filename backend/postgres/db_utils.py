import psycopg2
from psycopg2.extras import RealDictCursor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _db_session():
    engine = create_engine('postgresql://csmith@localhost/impulse_db')
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

def get_user_row(user_id):
    try:
        conn = psycopg2.connect("dbname=impulse_db user=csmith")
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_row = cur.fetchone()
        user_dict = dict(user_row)
        cur.close()
        conn.close()
        return user_dict
    except Exception as e:
        print("Error occurred: ", e)
        return None