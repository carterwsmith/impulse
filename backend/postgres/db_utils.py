from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'postgresql://csmith@localhost/impulse_db',
    # echo=True,  # If you want to see the log for debugging
    pool_size=100,
    max_overflow=10,
    pool_timeout=30,  # seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800  # forces connections to be reconnected after 30 minutes
)
Session = sessionmaker(bind=engine)

@contextmanager
def _db_session():
    try:
        session = Session()
        yield session
    finally:
        if session:
            session.close()

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