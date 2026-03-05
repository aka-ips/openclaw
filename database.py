from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    content = Column(String)
    category = Column(String)
    summary = Column(String)
    priority = Column(String)
    engine = Column(String)
    created_at = Column(DateTime, default=datetime.now)

engine = create_engine("sqlite:///openclaw.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_message(content, category, summary, priority, eng):
    session = Session()
    msg = Message(
        content=content,
        category=category,
        summary=summary,
        priority=priority,
        engine=eng
    )
    session.add(msg)
    session.commit()
    session.close()

def get_messages():
    session = Session()
    msgs = session.query(Message).order_by(Message.created_at.desc()).all()
    session.close()
    return msgs
