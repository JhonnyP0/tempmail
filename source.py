import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# database config
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:mytotallysecurepassword@db:3306/tempmaildb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#models
class Mailbox(Base):
    __tablename__ = "mailboxes"
    id = Column(Integer, primary_key=True, index=True)
    email_address = Column(String(255), unique=True, index=True)
    session_token = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="mailbox", cascade="all, delete-orphan", order_by="desc(Message.received_at)")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    mailbox_id = Column(Integer, ForeignKey("mailboxes.id"))
    sender = Column(String(255))
    subject = Column(String(255), default="(Brak tematu)")
    body_text = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)
    
    mailbox = relationship("Mailbox", back_populates="messages")