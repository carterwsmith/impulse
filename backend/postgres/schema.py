from sqlalchemy import create_engine, Column, Integer, Float, Boolean, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid

# Replace the connection string with your actual database connection details
engine = create_engine('postgresql://csmith@localhost/impulse_db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class ImpulseUser(Base):
    __tablename__ = 'ImpulseUser'
    id = Column(Integer, primary_key=True)
    root_domain = Column(String(255), nullable=True)
    is_domain_configured = Column(Boolean, default=False)

class Sessions(Base):
    __tablename__ = 'Sessions'
    id = Column(Text, primary_key=True)
    impulse_user_id = Column(Integer, ForeignKey('ImpulseUser.id'))
    impulse_user = relationship("ImpulseUser", back_populates="sessions")

ImpulseUser.sessions = relationship("Sessions", order_by=Sessions.id, back_populates="ImpulseUser")

class PageVisits(Base):
    __tablename__ = 'PageVisits'
    pagevisit_token = Column(Text, unique=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(Text, ForeignKey('Sessions.id'))
    session = relationship("Sessions", back_populates="PageVisits")
    page_path = Column(Text)
    start_time = Column(Text)
    end_time = Column(Text, nullable=True)

Sessions.page_visits = relationship("PageVisits", order_by=PageVisits.pagevisit_token, back_populates="Sessions")

class MouseMovements(Base):
    __tablename__ = 'MouseMovements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Text, ForeignKey('Sessions.id'))
    session = relationship("Sessions", back_populates="MouseMovements")
    pagevisit_token_id = Column(Text, ForeignKey('PageVisits.pagevisit_token'))
    pagevisit_token = relationship("PageVisits", back_populates="MouseMovements")
    position_x = Column(Integer)
    position_y = Column(Integer)
    text_or_tag_hovered = Column(Text)
    recorded_at = Column(Text)

PageVisits.mouse_movements = relationship("MouseMovements", order_by=MouseMovements.id, back_populates="PageVisits")

class LLMResponses(Base):
    __tablename__ = 'LLMResponses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Text, ForeignKey('Sessions.id'))
    session = relationship("Sessions", back_populates="LLMResponses")
    response = Column(Text)
    recorded_at = Column(Text)
    is_emitted = Column(Boolean, default=False)
    response_html = Column(Text, nullable=True)

Sessions.llm_responses = relationship("LLMResponses", order_by=LLMResponses.id, back_populates="Sessions")

class Promotions(Base):
    __tablename__ = 'Promotions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    impulse_user_id = Column(Integer, ForeignKey('ImpulseUser.id'))
    impulse_user = relationship("ImpulseUser")
    is_ai_generated = Column(Boolean, default=False)
    ai_description = Column(Text, nullable=True)
    ai_discount_percent_min = Column(Float, nullable=True)
    ai_discount_percent_max = Column(Float, nullable=True)
    ai_discount_dollars_min = Column(Float, nullable=True)
    ai_discount_dollars_max = Column(Float, nullable=True)
    promotion_name = Column(String(100))
    image_url = Column(String(150), nullable=True)
    display_title = Column(String(100), nullable=True)
    display_description = Column(Text, nullable=True)
    discount_percent = Column(Float, nullable=True)
    discount_dollars = Column(Float, nullable=True)
    discount_code = Column(String(50), nullable=True)

Base.metadata.create_all(engine)