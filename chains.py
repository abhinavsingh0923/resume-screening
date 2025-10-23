"""
LangChain chains for resume screening operations.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables at module import
load_dotenv()


def get_llm():
    """Initialize Gemini LLM with lazy loading."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please add it to your .env file or enter it in the Streamlit sidebar.")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.3,
        convert_system_message_to_human=True
    )


# Define prompts (without LLM initialization)
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert resume parser. Extract key information from the resume text and return it as JSON.

Extract the following:
- skills: List of technical and professional skills
- experience: List of work experiences with company, role, and duration
- education: List of educational qualifications with degree and institution

Return ONLY valid JSON in this exact format:
{{
    "skills": ["skill1", "skill2"],
    "experience": [
        {{"company": "Company Name", "role": "Job Title", "duration": "Years"}}
    ],
    "education": [
        {{"degree": "Degree Name", "institution": "School Name"}}
    ]
}}"""),
    ("human", "Resume text:\n{resume_text}")
])

matching_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert recruiter. Compare the candidate's resume data to the job description.

Identify:
1. Matching qualifications (skills, experience, education that align)
2. Gaps (missing requirements from the JD)

Return ONLY valid JSON in this format:
{{
    "matches": ["match1", "match2"],
    "gaps": ["gap1", "gap2"]
}}"""),
    ("human", """Job Description:
{jd}

Candidate Data:
Skills: {skills}
Experience: {experience}
Education: {education}""")
])

scoring_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert recruiter. Score the candidate's fit for the job (0-100%).

Consider:
- Skill alignment (40% weight)
- Experience relevance (40% weight)
- Education requirements (20% weight)

Return ONLY valid JSON in this format:
{{
    "score": 75,
    "reasons": [
        "Strong match: 8/10 required skills present",
        "Relevant experience in similar role",
        "Gap: Missing certification X"
    ],
    "suggestions": ["Acquire skill Y", "Gain experience in Z"]
}}

Provide 3-5 concise reasons and suggestions."""),
    ("human", """Job Description:
{jd}

Matches:
{matches}

Gaps:
{gaps}

Candidate Experience:
{experience}""")
])


def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Extract structured data from resume text."""
    try:
        # Create chain with lazy LLM initialization
        chain = extraction_prompt | get_llm() | JsonOutputParser()
        return chain.invoke({"resume_text": resume_text})
    except Exception as e:
        return {
            "skills": [],
            "experience": [],
            "education": [],
            "error": str(e)
        }


def match_to_jd(jd: str, resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Match resume to job description."""
    try:
        # Create chain with lazy LLM initialization
        chain = matching_prompt | get_llm() | JsonOutputParser()
        return chain.invoke({
            "jd": jd,
            "skills": resume_data.get("skills", []),
            "experience": resume_data.get("experience", []),
            "education": resume_data.get("education", [])
        })
    except Exception as e:
        return {
            "matches": [],
            "gaps": [],
            "error": str(e)
        }


def score_candidate(jd: str, resume_data: Dict[str, Any], match_data: Dict[str, Any]) -> Dict[str, Any]:
    """Score candidate fit."""
    try:
        # Create chain with lazy LLM initialization
        chain = scoring_prompt | get_llm() | JsonOutputParser()
        return chain.invoke({
            "jd": jd,
            "matches": match_data.get("matches", []),
            "gaps": match_data.get("gaps", []),
            "experience": resume_data.get("experience", [])
        })
    except Exception as e:
        return {
            "score": 0,
            "reasons": ["Error in scoring"],
            "suggestions": [],
            "error": str(e)
        }