import requests
from prompts import user_prompts

def call_llm(prompt, user_input):
    response = requests.post(
        LLM_API_URL,
        json={
            "messages": [
                {"role": "system", "content": prompt.strip()},
                {"role": "user", "content": user_input.strip()},
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

def differentiate_resource_chain(user_input):
    # Step 1: Analysis
    analysis_prompt = (
        "Analyze the following teaching resource content for subject, topic, and complexity. "
        "If the input is vague or short, infer a likely classroom topic and scope. "
        "Output as: Subject: ...; Topic: ...; Complexity: ..."
    )
    analysis_output = call_llm(analysis_prompt, user_input)

    # Step 2: Differentiation
    # Prepend analysis output to user input for the next prompt
    combined_input = f"{analysis_output}\n\n{user_input}"
    differentiation_prompt = user_prompts["Differentiate Resource"]
    differentiated_output = call_llm(differentiation_prompt, combined_input)

    return differentiated_output
