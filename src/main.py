import os
import streamlit as st

# ---- DOCX PACKAGE CHECK & FORCE INSTALL ----
try:
    import docx
except ImportError:
    import os
    os.system('pip install python-docx')
    import docx

import fitz
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from mistralai import Mistral

# Local development ke liye
load_dotenv(Path(__file__).parent.parent / ".env")

# Local .env ya Streamlit secrets dono support
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or st.secrets.get("TAVILY_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or st.secrets.get("MISTRAL_API_KEY")

def extract_text_from_cv(uploaded_file) -> str:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name.lower()
    
    if file_name.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    
    elif file_name.endswith(".docx"):
        import io
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    else:
        raise ValueError("Sirf PDF ya DOCX upload karein!")

def analyze_cv(cv_text: str) -> dict:
    # UPDATED: MistralClient ki jagah naya Mistral use kiya hai
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are a CV analyzer. Extract key information from the CV and return ONLY a JSON object with these keys:
                - name: candidate name
                - field: main field of study/work (e.g. Computer Science, Medicine, Engineering)
                - education_level: current level (e.g. Undergraduate, Masters, PhD)
                - skills: list of top 5 skills
                - gpa: GPA if mentioned, else null
                - search_query: a good scholarship search query based on this profile
                Return only JSON, no explanation."""
            },
            {
                "role": "user",
                "content": f"Analyze this CV:\n\n{cv_text[:3000]}"
            }
        ]
    )
    
    import json
    raw = response.choices[0].message.content
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def search_scholarships(query: str) -> str:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    results = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )
    
    combined = ""
    for r in results["results"]:
        combined += f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n\n"
    
    return combined

def summarize_with_mistral(raw_data: str, user_query: str) -> str:
    # UPDATED: MistralClient ki jagah naya Mistral use kiya hai
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": """You are a scholarship advisor helping Pakistani students find scholarships.
                Given raw search data, extract and present scholarships clearly with:
                - Scholarship name
                - Country/University
                - Eligibility
                - Deadline (if mentioned)
                - Application link
                Present in a clean, readable format."""
            },
            {
                "role": "user",
                "content": f"User searched for: {user_query}\n\nRaw search data:\n{raw_data}"
            }
        ]
    )
    
    return response.choices[0].message.content

def find_scholarships(query: str) -> str:
    print(f"🔍 Searching for: {query}")
    raw_data = search_scholarships(query)
    print("✅ Search done! Summarizing...")
    summary = summarize_with_mistral(raw_data, query)
    return summary

def find_scholarships_by_cv(uploaded_file) -> tuple:
    cv_text = extract_text_from_cv(uploaded_file)
    cv_info = analyze_cv(cv_text)
    query = cv_info.get("search_query", f"scholarships for {cv_info.get('field', 'students')} Pakistani students")
    results = find_scholarships(query)
    return cv_info, results

if __name__ == "__main__":
    result = find_scholarships("fully funded scholarships for Pakistani students 2026")
    print(result)