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

def seed_prompt_variants():
    session = SessionLocal()

    # Check if variants already exist
    existing = session.query(PromptEntry).filter(PromptEntry.edited == False).all()
    techniques_seeded = any("Technique:" in p.prompt_text for p in existing)
    if techniques_seeded:
        session.close()
        return

    # New variant prompts by technique
    prompt_variants = [
        {
            "category": "Simplified",
            "technique": "Role-Based",
            "prompt_text": "Technique: Role-Based\n\nAct as a literacy support assistant for a student with a reading age of 9. Your job is to simplify this worksheet so it's accessible, without removing any core learning. Use plain language, short sentences, and direct instructions. Keep the task engaging and age-appropriate.\n\n[PASTE WORKSHEET HERE]"
        },
        {
            "category": "Simplified",
            "technique": "Explicit Constraints",
            "prompt_text": "Technique: Explicit Constraints\n\nRewrite the following resource using:\n- Maximum sentence length: 10 words\n- No technical terms unless defined\n- Simple structure: step-by-step or bullet points\n\nMake it suitable for learners with low reading ages while keeping the key educational content intact.\n\n[PASTE WORKSHEET HERE]"
        },
        {
            "category": "Challenge Extension",
            "technique": "Chain-of-Thought",
            "prompt_text": "Technique: Chain-of-Thought\n\nYou're creating an extension task for high-attaining students. First, identify the core concept of the worksheet. Then, create one open-ended question that requires critical thinking, and one creative application task that connects it to the real world.\n\nOutput each of these with a heading:\n- Concept Summary\n- Challenge Question\n- Creative Application\n\n[PASTE WORKSHEET HERE]"
        },
        {
            "category": "Challenge Extension",
            "technique": "Few-Shot",
            "prompt_text": "Technique: Few-Shot\n\nHere are some examples of extending a standard worksheet:\n\n**Original Task:** Match animal names with their habitats.  \n**Extension:** Research one animal's habitat and present how climate change affects it.\n\n**Original Task:** Solve 5 addition problems.  \n**Extension:** Create a real-life scenario using addition and explain it to a classmate.\n\nNow apply this to the following worksheet to create a challenge task for advanced learners:\n\n[PASTE WORKSHEET HERE]"
        },
        {
            "category": "Scaffolded",
            "technique": "Persona + Structure",
            "prompt_text": "Technique: Persona + Structure\n\nYou are an EAL support teacher. Adapt this worksheet for a learner who needs support with sentence structure and vocabulary. \n\nFor each question or instruction, provide:\n1. A sentence starter\n2. A list of 3 key vocabulary words with definitions\n3. A visual support suggestion (if applicable)\n\n[PASTE WORKSHEET HERE]"
        },
        {
            "category": "Scaffolded",
            "technique": "Instruction-Tuned",
            "prompt_text": "Technique: Instruction-Tuned\n\nTask: Add sentence starters and vocabulary scaffolds to this worksheet to support EAL learners.\n\nRequirements:\n- Use a friendly, clear tone\n- Keep the original task intact\n- Include definitions for any challenging words\n\n[PASTE WORKSHEET HERE]"
        }
    ]

    for p in prompt_variants:
        session.add(PromptEntry(
            category=p["category"],
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()
