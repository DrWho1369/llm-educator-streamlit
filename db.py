from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# --- DATABASE CONFIG ---
DB_FILE = "prompt_history.db"
engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --- TABLE SCHEMA ---
class PromptEntry(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    prompt_text = Column(Text)
    edited = Column(Boolean)
    rating = Column(Integer, nullable=True)
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- INIT + SAVE FUNCTIONS ---
def setup_db():
    if not os.path.exists(DB_FILE):
        Base.metadata.create_all(bind=engine)

def save_prompt_to_db(category, prompt_text, edited, rating=None, feedback_comment=None):
    session = SessionLocal()
    new_entry = PromptEntry(
        category=category,
        prompt_text=prompt_text,
        edited=edited,
        rating=rating,
        feedback_comment=feedback_comment
    )
    session.add(new_entry)
    session.commit()
    session.close()
