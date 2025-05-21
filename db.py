from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

def wrap_prompt(role_instruction: str, subject_content: str) -> str:
    return f"""<role>
{role_instruction.strip()}
</role>

<subject>
{subject_content.strip()}
</subject>"""

# --- DATABASE CONFIG ---
DB_FILE = "prompt_history.db"
engine = create_engine(f"sqlite:///{DB_FILE}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# --- TABLE SCHEMA ---
class PromptEntry(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String)  # 🔁 renamed from category
    prompt_text = Column(Text)
    edited = Column(Boolean)
    rating = Column(Integer, nullable=True)
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- INIT + SAVE FUNCTIONS ---
def setup_db():
    if not os.path.exists(DB_FILE):
        Base.metadata.create_all(bind=engine)

def save_prompt_to_db(task_name, prompt_text, edited, rating=None, feedback_comment=None):
    session = SessionLocal()
    new_entry = PromptEntry(
        task_name=task_name,
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
        "Simplified": wrap_prompt("You are a teacher simplifying lesson content for a student with a reading age of 9 years. Rewrite the following resource using simpler vocabulary, shorter sentences, and clear structure while preserving meaning and core knowledge."),
        "Challenge Extension": wrap_prompt("You are a gifted and talented coordinator. Extend the following task to provide a greater challenge for high-attaining students. Add one open-ended question, and one creative application or real-world connection."),
        "EAL Support": wrap_prompt("You are an EAL support specialist. Modify the following resource to include sentence starters and a glossary of key terms with definitions in simple English."),
        "SEND Support": wrap_prompt("You are a SEND teacher. Adapt this activity for students with moderate learning difficulties. Break the task into small, guided steps and use supportive language."),
        "Dyslexia-Friendly": wrap_prompt("You are supporting students with dyslexia. Rewrite the following resource using short sentences and high-frequency words. Present content in readable chunks."),
        "Tiered": wrap_prompt("You are creating a tiered version of this resource for a mixed-ability classroom. Provide:\n1. A simplified version\n2. A standard version\n3. A challenge version."),
        "Sentence Starters": wrap_prompt("You are helping students develop structured responses. Rewrite this worksheet to include sentence starters or writing frames for each question.")
    }

    for category, prompt_text in base_prompts.items():
        new_prompt = PromptEntry(
            task_name=category,
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
            "prompt_text": wrap_prompt("Technique: Role-Based\n\nAct as a literacy support assistant for a student with a reading age of 9. Your job is to simplify this worksheet so it's accessible, without removing any core learning. Use plain language, short sentences, and direct instructions. Keep the task engaging and age-appropriate.\n\n")
        },
        {
            "category": "Simplified",
            "technique": "Explicit Constraints",
            "prompt_text": wrap_prompt("Technique: Explicit Constraints\n\nRewrite the following resource using:\n- Maximum sentence length: 10 words\n- No technical terms unless defined\n- Simple structure: step-by-step or bullet points\n\nMake it suitable for learners with low reading ages while keeping the key educational content intact.\n\n")
        },
        {
            "category": "Challenge Extension",
            "technique": "Chain-of-Thought",
            "prompt_text": wrap_prompt("Technique: Chain-of-Thought\n\nYou're creating an extension task for high-attaining students. First, identify the core concept of the worksheet. Then, create one open-ended question that requires critical thinking, and one creative application task that connects it to the real world.\n\nOutput each of these with a heading:\n- Concept Summary\n- Challenge Question\n- Creative Application\n\n")
        },
        {
            "category": "Challenge Extension",
            "technique": "Few-Shot",
            "prompt_text": wrap_prompt("Technique: Few-Shot\n\nHere are some examples of extending a standard worksheet:\n\n**Original Task:** Match animal names with their habitats.  \n**Extension:** Research one animal's habitat and present how climate change affects it.\n\n**Original Task:** Solve 5 addition problems.  \n**Extension:** Create a real-life scenario using addition and explain it to a classmate.\n\nNow apply this to the following worksheet to create a challenge task for advanced learners:\n\n")
        },
        {
            "category": "Scaffolded",
            "technique": "Persona + Structure",
            "prompt_text": wrap_prompt("Technique: Persona + Structure\n\nYou are an EAL support teacher. Adapt this worksheet for a learner who needs support with sentence structure and vocabulary. \n\nFor each question or instruction, provide:\n1. A sentence starter\n2. A list of 3 key vocabulary words with definitions\n3. A visual support suggestion (if applicable)\n\n")
        },
        {
            "category": "Scaffolded",
            "technique": "Instruction-Tuned",
            "prompt_text": wrap_prompt("Technique: Instruction-Tuned\n\nTask: Add sentence starters and vocabulary scaffolds to this worksheet to support EAL learners.\n\nRequirements:\n- Use a friendly, clear tone\n- Keep the original task intact\n- Include definitions for any challenging words\n\n")
        }
    ]

    for p in prompt_variants:
        session.add(PromptEntry(
            task_name=p["category"],
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()


def seed_lesson_plan_variants():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.task_name == "Generate Lesson Plan + Resources").all()
    if existing:
        session.close()
        return  # Already seeded

    prompts = [
        {
            "technique": "Role-Based",
            "prompt_text": """Technique: Role-Based

<role>
You are a highly experienced secondary school teacher. Create a detailed lesson plan for the given topic, year group, and lesson duration. Your output should include:

1. Learning objectives  
2. Suggested lesson structure (starter, main, plenary)  
3. Key concepts to cover  
4. Differentiated activities (support/challenge)  
5. Assessment for learning (AFL) ideas
</role>

<subject>
Topic: {topic}  
Year Group: {year_group}  
Duration: {duration} minutes  

Chapter content:  
{chapter_text}
</subject>"""
        },
        {
            "technique": "Few-Shot",
            "prompt_text": """Technique: Few-Shot

<role>
Use the following example format to generate a lesson plan.

Example:  
Topic: Fractions  
Year Group: Year 4  
Duration: 45 minutes  
Objectives: Understand halves and quarters.  
Structure:  
- Starter: Pizza fraction activity  
- Main: Colouring shapes  
- Plenary: Quiz and discussion  
Differentiation: Use blocks for support, challenge problems  
AFL: Exit ticket quiz  

Now create a lesson plan using this structure.
</role>

<subject>
Topic: {topic}  
Year Group: {year_group}  
Duration: {duration} minutes  

Chapter content:  
{chapter_text}
</subject>"""
        },
        {
            "technique": "Format-Constrained",
            "prompt_text": """Technique: Format-Constrained

<role>
Generate a lesson plan using the following markdown format:

- **Topic**:  
- **Year Group**:  
- **Duration**:  
- **Learning Objectives**:  
- **Lesson Structure**:  
  - Starter  
  - Main  
  - Plenary  
- **Differentiation**:  
  - Support  
  - Challenge  
- **AFL Opportunities**:
</role>

<subject>
Topic: {topic}  
Year Group: {year_group}  
Duration: {duration} minutes  

Chapter content:  
{chapter_text}
</subject>"""
        }
    ]

    for p in prompts:
        session.add(PromptEntry(
            task_name="Generate Lesson Plan + Resources",
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()

def seed_parent_comms_variants():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.task_name == "Parent Comms Assistant").all()
    if existing:
        session.close()
        return

    prompts = [
        {
            "technique": "Role-Based",
            "prompt_text": """Technique: Role-Based

<role>
You are a professional teacher writing to a student's parents. Write a clear, polite message about the following concern. Use the tone provided. Make it sound human, empathetic, and supportive of the student.
</role>

<subject>
Concern: {concern}  
Tone: {tone}  
Context: {note}
</subject>"""
        },
        {
            "technique": "Tone-Driven",
            "prompt_text": """Technique: Tone-Driven

<role>
Compose a short message to a parent. The message should be respectful, helpful, and actionable. End on a supportive note.
</role>

<subject>
Concern: {concern}  
Tone: {tone}  
Extra context: {note}
</subject>"""
        },
        {
            "technique": "Format-Constrained",
            "prompt_text": """Technique: Format-Constrained

<role>
Write a message using the following structure:

- Greeting  
- Main concern  
- Additional info  
- Clear next steps  
- Polite closing  

Use the tone provided. Keep the message concise and parent-appropriate.
</role>

<subject>
Concern: {concern}  
Tone: {tone}  
Additional info: {note}
</subject>"""
        }
    ]

    for p in prompts:
        session.add(PromptEntry(
            task_name="Parent Comms Assistant",
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()


def seed_mcq_variants():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.task_name == "Convert to MCQ").all()
    if existing:
        session.close()
        return

    prompts = [
        {
            "technique": "Role-Based",
            "prompt_text": """Technique: Role-Based

<role>
You are an experienced exam question writer. Based on the resource provided, generate {num} multiple-choice questions that test understanding of the material. Each question should have:
- A question stem
- Four answer options
- One clearly correct answer
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Format-Constrained",
            "prompt_text": """Technique: Format-Constrained

<role>
Generate {num} multiple-choice questions in the following format:

Q: [question]  
A. Option 1  
B. Option 2  
C. Option 3  
D. Option 4  
Answer: [Correct Option Letter]
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Difficulty-Scaled",
            "prompt_text": """Technique: Difficulty-Scaled

<role>
Based on the text, generate {num} multiple-choice questions divided as:
- Easy (1/3)
- Medium (1/3)
- Hard (1/3)

For each question, provide:
- Question
- 4 answer options
- Indicate the correct answer
</role>

<subject>
{text}
</subject>"""
        }
    ]

    for p in prompts:
        session.add(PromptEntry(
            task_name="Convert to MCQ",
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()

def seed_flashcard_variants():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.task_name == "Convert to Flashcards").all()
    if existing:
        session.close()
        return

    prompts = [
        {
            "technique": "QA-Pair Format",
            "prompt_text": """Technique: QA-Pair Format

<role>
Convert the following text into flashcards. Each flashcard should be in Q&A format:
Q: [question]  
A: [answer]
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Definition-Driven",
            "prompt_text": """Technique: Definition-Driven

<role>
Extract key terms from the text and create flashcards using this format:

Front: Term  
Back: Simple definition
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Cloze Deletion",
            "prompt_text": """Technique: Cloze Deletion

<role>
Turn the content into flashcards using the cloze deletion format (fill-in-the-blank). Example:

Front: Photosynthesis occurs in the ______ of plant cells.  
Back: chloroplasts
</role>

<subject>
{text}
</subject>"""
        }
    ]

    for p in prompts:
        session.add(PromptEntry(
            task_name="Convert to Flashcards",
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()


def seed_group_task_variants():
    session = SessionLocal()

    existing = session.query(PromptEntry).filter(PromptEntry.task_name == "Convert to Group Task").all()
    if existing:
        session.close()
        return

    prompts = [
        {
            "technique": "Collaborative Role-Based",
            "prompt_text": """Technique: Collaborative Role-Based

<role>
Act as an instructional designer. Convert the content into a collaborative group activity suitable for classroom discussion. Provide:

1. Group goal
2. Instructions for each student role
3. Materials needed
4. Key learning outcomes
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Inquiry-Based Learning",
            "prompt_text": """Technique: Inquiry-Based Learning

<role>
Design a group task based on the content that promotes inquiry and peer discussion. Include a guiding question and instructions for structured dialogue.
</role>

<subject>
{text}
</subject>"""
        },
        {
            "technique": "Scenario-Based",
            "prompt_text": """Technique: Scenario-Based

<role>
Create a scenario-based group activity where students must apply the knowledge from this resource in a real-world context. Include prompts for group roles and expected outcomes.
</role>

<subject>
{text}
</subject>"""
        }
    ]

    for p in prompts:
        session.add(PromptEntry(
            task_name="Convert to Group Task",
            prompt_text=p["prompt_text"],
            edited=False,
            rating=None,
            feedback_comment=f"Technique: {p['technique']}"
        ))

    session.commit()
    session.close()

