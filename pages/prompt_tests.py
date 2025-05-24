import streamlit as st

st.set_page_config(page_title="Test Prompts", layout="centered")

st.title("🧪 Test Prompts")
st.markdown("I have used these test inputs to evaluate and refine the LLM prompt outputs.")

tabs = st.tabs([
    "Differentiate Resource",
    "Generate Parent Message",
    "Plan & Print",
    "Reformat & Repurpose"
])

# ---------- DIFFERENTIATE RESOURCE ----------
with tabs[0]:
    st.subheader("Differentiate Resource – Test Inputs")
    st.markdown("Test how well the model adapts content for different learner levels.")

    short = ["Photosynthesis", "World War II", "Quadratic equations"]
    medium = [
        "The water cycle involves the continuous movement of water between the earth’s surface and atmosphere. This includes processes like evaporation, condensation, and precipitation.",
        "The Roman Empire was known for its vast territorial control, complex road networks, and advancements in architecture.",
        "In mathematics, a prime number is a natural number greater than 1 that cannot be formed by multiplying two smaller natural numbers."
    ]
    long = [
        """Global warming refers to the long-term heating of Earth’s climate system due to human activities, primarily the release of greenhouse gases from fossil fuel combustion. It is a major contributor to climate change, leading to rising sea levels, extreme weather events, and shifts in biodiversity. Students should learn about the causes, impacts, and possible solutions to mitigate global warming through renewable energy and sustainable practices.""",
        """Macbeth, one of Shakespeare’s most famous tragedies, explores the psychological consequences of unchecked ambition. The play follows the title character, a Scottish general, whose desire for power leads him down a dark and destructive path. Key themes include guilt, fate vs free will, and the corrupting influence of power. This passage is suitable for literary analysis in secondary school.""",        
        """In biology, cellular respiration is the process by which cells break down glucose to produce energy in the form of ATP. It involves three main stages: glycolysis, the Krebs cycle, and the electron transport chain. Unlike photosynthesis, which stores energy, respiration releases it, and it occurs in both plant and animal cells. Understanding this process is key for students studying metabolic pathways.""",
        """The Treaty of Versailles, signed in 1919, officially ended World War I. It imposed heavy reparations on Germany, redrew national boundaries, and established the League of Nations. Many historians believe the harsh terms contributed to political and economic instability in Germany, ultimately setting the stage for World War II. This text can be used to discuss historical cause and effect, nationalism, and peace treaties in a modern context."""
    ]

    with st.expander("🔹 Short Inputs"):
        for i in short:
            st.code(i)

    with st.expander("🔸 Medium Inputs"):
        for i in medium:
            st.code(i)

    with st.expander("🔶 Long Inputs"):
        for i in long:
            st.code(i)

# ---------- GENERATE PARENT MESSAGE ----------
with tabs[1]:
    st.subheader("Generate Parent Message – Test Inputs")
    parent_inputs = [
        "Jamie completed their homework early and added some extra reading. Please pass on our praise.",
        "Lena has missed two assignments in a row and seems distracted in class.",
        "I want to update you that Maya helped another student today without being prompted.",
        "Tom was involved in a disagreement at break time with another student.",
        "We're noticing improved focus and effort from Aisha over the past few weeks.",
        "Luke consistently submits homework late and doesn’t respond to feedback.",
        "Ella has shown great progress in her reading ability this term.",
        "Josh’s behaviour has improved, but his attendance is still below 90%.",
        "Isabelle completed an outstanding project on climate change and presented it to the class.",
        "There’s been some confusion regarding homework instructions and I wanted to clarify."
    ]
    for i in parent_inputs:
        st.code(i)

# ---------- PLAN & PRINT ----------
with tabs[2]:
    st.subheader("Plan & Print – Test Inputs")
    st.markdown("These inputs test the LLM's ability to create structured lesson plans for different levels and topics.")

    plan_print_inputs = [
        "The Water Cycle",  # very short
        "Fractions",  # one word math topic
        "Causes of World War I",  # standard topic title
        "Explain the process of photosynthesis for KS3 students.",
        "How do tectonic plates cause earthquakes?",
        "Design a lesson on the French Revolution focusing on causes and consequences.",
        "Create a lesson plan for KS4 students explaining the concept of opportunity cost using real-world examples.",
        "Plan a computing lesson that introduces basic Python programming to Year 9 students.",
        "Develop a lesson on the respiratory system, including diagrams, class activities, and a quiz at the end.",
        """I need a lesson plan for Year 6 on persuasive writing. The lesson should include examples of persuasive techniques, a group discussion, a collaborative planning task, and an independent writing section where students write a letter to persuade their local council to improve a park. Finish with a peer review task and optional homework."""
    ]

    for i in plan_print_inputs:
        st.code(i)


# ---------- REFORMAT & REPURPOSE ----------
with tabs[3]:
    st.subheader("Reformat & Repurpose – Test Inputs")
    reformat_inputs = [
        "Plants need sunlight, water, and carbon dioxide to perform photosynthesis. The process takes place in the chloroplasts and produces glucose and oxygen.",
        "A democracy is a form of government where citizens have the power to elect their leaders. It is based on the principles of majority rule and individual rights.",
        "The water cycle is the process by which water circulates between the earth’s oceans, atmosphere, and land, involving precipitation, drainage, and evaporation.",
        "In computing, an algorithm is a set of instructions designed to perform a specific task or solve a particular problem.",
        "Romeo and Juliet is a tragedy written by William Shakespeare that tells the story of two young lovers whose deaths ultimately reconcile their feuding families.",
        "A triangle has three sides and three angles. The sum of its internal angles always equals 180 degrees.",
        "A habitat is the natural home or environment of an animal, plant, or other organism. Examples include forests, deserts, and oceans.",
        "Magnetism is a force that can attract or repel objects that have a magnetic material like iron.",
        "The digestive system breaks down food into nutrients the body can use. It includes the mouth, esophagus, stomach, intestines, and other organs.",
        "The Treaty of Versailles was one of the peace treaties that ended World War I. It placed strict limitations on Germany and redrew parts of Europe."
    ]
    for i in reformat_inputs:
        st.code(i)
