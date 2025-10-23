"""
LangGraph workflow for resume screening.
"""
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
from chains import extract_resume_data, match_to_jd, score_candidate


class ScreeningState(TypedDict):
    """State for the screening workflow."""
    jd: str
    resume_file_path: str
    resume_text: str
    resume_data: Dict[str, Any]
    match_data: Dict[str, Any]
    score: float
    reasons: List[str]
    suggestions: List[str]
    candidate_name: str
    error: str


def load_resume(state: ScreeningState) -> ScreeningState:
    """Load and extract text from resume PDF."""
    try:
        loader = PyPDFLoader(state["resume_file_path"])
        pages = loader.load()
        resume_text = "\n".join([page.page_content for page in pages])
        
        if not resume_text.strip():
            state["error"] = "Empty PDF or failed to extract text"
            state["resume_text"] = ""
        else:
            state["resume_text"] = resume_text
            state["error"] = ""
            
    except Exception as e:
        state["error"] = f"PDF loading error: {str(e)}"
        state["resume_text"] = ""
    
    return state


def extract_data(state: ScreeningState) -> ScreeningState:
    """Extract structured data from resume."""
    if state.get("error"):
        return state
    
    try:
        resume_data = extract_resume_data(state["resume_text"])
        state["resume_data"] = resume_data
        
        if "error" in resume_data:
            state["error"] = f"Extraction error: {resume_data['error']}"
            
    except Exception as e:
        state["error"] = f"Data extraction error: {str(e)}"
        state["resume_data"] = {}
    
    return state


def match_jd(state: ScreeningState) -> ScreeningState:
    """Match resume to job description."""
    if state.get("error"):
        return state
    
    try:
        match_data = match_to_jd(state["jd"], state["resume_data"])
        state["match_data"] = match_data
        
        if "error" in match_data:
            state["error"] = f"Matching error: {match_data['error']}"
            
    except Exception as e:
        state["error"] = f"JD matching error: {str(e)}"
        state["match_data"] = {}
    
    return state


def score_candidate_node(state: ScreeningState) -> ScreeningState:
    """Score the candidate."""
    if state.get("error"):
        state["score"] = 0
        state["reasons"] = [f"Processing failed: {state['error']}"]
        state["suggestions"] = []
        return state
    
    try:
        score_data = score_candidate(
            state["jd"],
            state["resume_data"],
            state["match_data"]
        )
        
        state["score"] = score_data.get("score", 0)
        state["reasons"] = score_data.get("reasons", [])
        state["suggestions"] = score_data.get("suggestions", [])
        
        if "error" in score_data:
            state["error"] = f"Scoring error: {score_data['error']}"
            
    except Exception as e:
        state["error"] = f"Candidate scoring error: {str(e)}"
        state["score"] = 0
        state["reasons"] = [f"Scoring failed: {str(e)}"]
        state["suggestions"] = []
    
    return state


def should_suggest_improvements(state: ScreeningState) -> str:
    """Conditional edge: check if score is low."""
    if state.get("score", 0) < 50:
        return "suggest"
    return "end"


def suggest_improvements(state: ScreeningState) -> ScreeningState:
    """Add improvement suggestions for low scores."""
    if not state.get("suggestions"):
        gaps = state.get("match_data", {}).get("gaps", [])
        if gaps:
            state["suggestions"] = [f"Develop skills/experience in: {gap}" for gap in gaps[:3]]
        else:
            state["suggestions"] = ["Consider gaining more relevant experience"]
    
    return state


def create_screening_workflow() -> StateGraph:
    """Create the LangGraph workflow."""
    workflow = StateGraph(ScreeningState)
    
    # Add nodes
    workflow.add_node("load_resume", load_resume)
    workflow.add_node("extract_data", extract_data)
    workflow.add_node("match_jd", match_jd)
    workflow.add_node("score_candidate", score_candidate_node)
    workflow.add_node("suggest_improvements", suggest_improvements)
    
    # Add edges
    workflow.set_entry_point("load_resume")
    workflow.add_edge("load_resume", "extract_data")
    workflow.add_edge("extract_data", "match_jd")
    workflow.add_edge("match_jd", "score_candidate")
    
    # Conditional edge based on score
    workflow.add_conditional_edges(
        "score_candidate",
        should_suggest_improvements,
        {
            "suggest": "suggest_improvements",
            "end": END
        }
    )
    workflow.add_edge("suggest_improvements", END)
    
    return workflow.compile()


def process_resume(jd: str, resume_file_path: str, candidate_name: str) -> Dict[str, Any]:
    """Process a single resume through the workflow."""
    workflow = create_screening_workflow()
    
    initial_state: ScreeningState = {
        "jd": jd,
        "resume_file_path": resume_file_path,
        "resume_text": "",
        "resume_data": {},
        "match_data": {},
        "score": 0,
        "reasons": [],
        "suggestions": [],
        "candidate_name": candidate_name,
        "error": ""
    }
    
    result = workflow.invoke(initial_state)
    
    return {
        "candidate": candidate_name,
        "score": result.get("score", 0),
        "reasons": result.get("reasons", []),
        "suggestions": result.get("suggestions", []),
        "matches": result.get("match_data", {}).get("matches", []),
        "gaps": result.get("match_data", {}).get("gaps", []),
        "error": result.get("error", "")
    }


def process_multiple_resumes(jd: str, resume_files: List[tuple]) -> List[Dict[str, Any]]:
    """Process multiple resumes."""
    results = []
    
    for file_name, file_content in resume_files:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            result = process_resume(jd, tmp_path, file_name)
            results.append(result)
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    return results