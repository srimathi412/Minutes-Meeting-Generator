import os
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

def process_transcript(transcript: str) -> str:
    """Processes the transcript using LangChain and Groq LLM."""
    import os
    import streamlit as st
    from dotenv import load_dotenv

    env_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".env"
    )

    load_dotenv(dotenv_path=env_path)

    api_key_str = os.getenv("GROQ_API_KEY")

    if not api_key_str:
        try:
            api_key_str = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key_str = None

    if not api_key_str:
        raise ValueError(
            "Groq API Key not configured."
        )

    api_keys = [
        k.strip()
        for k in api_key_str.split(",")
        if k.strip()
    ]
        
    api_key = api_keys[0]
    
    try:
        # Initialize LLM
        llm = ChatGroq(
            temperature=0.2, 
            model_name="llama-3.3-70b-versatile",
            api_key=api_key
        )

        # Use exact prompt requested
        prompt_template = """You are an intelligent meeting assistant.

Analyze the meeting transcript and generate:

1. Meeting Summary
2. Key Discussion Points
3. Action Items
4. Minutes of Meeting

Return output exactly in this structure:

Meeting Summary:
...

Key Discussion Points:
• Point 1
• Point 2

Action Items:
• Person → Task

Minutes of Meeting:
Topic:
Attendees:
Discussion:
Decisions Taken:

Transcript:
{transcript}
"""

        prompt = PromptTemplate(template=prompt_template, input_variables=["transcript"])
        
        chain = prompt | llm
        response = chain.invoke({"transcript": transcript})
        return response.content
    except Exception as e:
        raise Exception(f"Error processing transcript with LLM: {str(e)}")

def parse_llm_output(llm_output: str):
    """Parses the LLM output into sections for the UI and PDF."""
    sections = {
        "summary": "",
        "key_points": "",
        "action_items": "",
        "mom": ""
    }
    
    current_section = None
    lines = llm_output.split('\n')
    
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("Meeting Summary:"):
            current_section = "summary"
            continue
        elif stripped_line.startswith("Key Discussion Points:"):
            current_section = "key_points"
            continue
        elif stripped_line.startswith("Action Items:"):
            current_section = "action_items"
            continue
        elif stripped_line.startswith("Minutes of Meeting:"):
            current_section = "mom"
            continue
            
        if current_section:
            sections[current_section] += line + "\n"
            
    # Clean up empty newlines at the beginning/end
    for k in sections:
        sections[k] = sections[k].strip()
        
    return sections
