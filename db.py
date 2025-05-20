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

def seed_original_prompts():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.edited == False).all()
    if existing:
        session.close()
        return  # Already seeded

    base_prompts = {
        "Simplified": "You are a teacher simplifying lesson content for a student with a reading age of 9 years. Rewrite the following resource using simpler vocabulary, shorter sentences, and clear structure while preserving meaning and core knowledge.",
        "Challenge Extension": "You are a gifted and talented coordinator. Extend the following task to provide a greater challenge for high-attaining students. Add one open-ended question, and one creative application or real-world connection.",
        "EAL Support": "You are an EAL support specialist. Modify the following resource to include sentence starters and a glossary of key terms with definitions in simple English.",
        "SEND Support": "You are a SEND teacher. Adapt this activity for students with moderate learning difficulties. Break the task into small, guided steps and use supportive language.",
        "Dyslexia-Friendly": "You are supporting students with dyslexia. Rewrite the following resource using short sentences and high-frequency words. Present content in readable chunks.",
        "Tiered": "You are creating a tiered version of this resource for a mixed-ability classroom. Provide:\n1. A simplified version\n2. A standard version\n3. A challenge version.",
        "Sentence Starters": "You are helping students develop structured responses. Rewrite this worksheet to include sentence starters or writing frames for each question."
    }

    for category, prompt_text in base_prompts.items():
        new_prompt = PromptEntry(
            category=category,
            prompt_text=prompt_text,
            edited=False,
            rating=None,
            feedback_comment=None
        )
        session.add(new_prompt)

    session.commit()
    session.close()
