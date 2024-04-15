from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _db_session():
    engine = create_engine('postgresql://csmith@localhost/impulse_db')
    Session = sessionmaker(bind=engine)
    session = Session()

    return session