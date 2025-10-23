"""
Streamlit frontend for resume screening application.
"""
import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from workflow import process_multiple_resumes
from langchain_community.document_loaders import PyPDFLoader
import tempfile

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("🤖 AI-Powered Resume Screening Application")
st.markdown("""
Screen multiple resumes against a job description using AI. 
Upload resumes, provide a JD, and get instant scores and insights.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Enter your Google Gemini API key"
    )
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    st.divider()
    
    st.header("📋 Job Description")
    
    jd_input_method = st.radio(
        "Input method:",
        ["Text", "PDF Upload"]
    )
    
    jd_text = ""
    
    if jd_input_method == "Text":
        jd_text = st.text_area(
            "Paste Job Description",
            height=300,
            placeholder="Enter the complete job description here..."
        )
    else:
        jd_file = st.file_uploader(
            "Upload JD PDF",
            type=["pdf"],
            key="jd_pdf"
        )
        
        if jd_file:
            with st.spinner("Extracting JD from PDF..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(jd_file.read())
                        tmp_path = tmp_file.name
                    
                    loader = PyPDFLoader(tmp_path)
                    pages = loader.load()
                    jd_text = "\n".join([page.page_content for page in pages])
                    
                    os.remove(tmp_path)
                    st.success("✅ JD extracted successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error extracting JD: {str(e)}")
    
    st.divider()
    
    st.info("""
    **How to use:**
    1. Enter your Gemini API key
    2. Provide job description
    3. Upload resume PDFs (max 10)
    4. Click "Screen Resumes"
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📁 Upload Resumes")
    
    resume_files = st.file_uploader(
        "Upload Resume PDFs (1-10 files, max 5MB each)",
        type=["pdf"],
        accept_multiple_files=True,
        key="resumes"
    )
    
    if resume_files:
        st.success(f"✅ {len(resume_files)} resume(s) uploaded")
        
        # Show file names
        with st.expander("View uploaded files"):
            for idx, file in enumerate(resume_files, 1):
                file_size = len(file.getvalue()) / (1024 * 1024)  # MB
                st.write(f"{idx}. {file.name} ({file_size:.2f} MB)")

with col2:
    st.header("🚀 Actions")
    
    screen_button = st.button(
        "🔍 Screen Resumes",
        type="primary",
        use_container_width=True,
        disabled=not (api_key and jd_text and resume_files)
    )
    
    if not api_key:
        st.warning("⚠️ Please enter API key")
    elif not jd_text:
        st.warning("⚠️ Please provide JD")
    elif not resume_files:
        st.warning("⚠️ Please upload resumes")

# Processing
if screen_button:
    # Validation
    if len(resume_files) > 10:
        st.error("❌ Maximum 10 resumes allowed per session")
    elif any(len(f.getvalue()) > 5 * 1024 * 1024 for f in resume_files):
        st.error("❌ One or more files exceed 5MB limit")
    else:
        # Prepare resume data
        resume_data = [(f.name, f.getvalue()) for f in resume_files]
        
        # Process resumes
        with st.spinner("🔄 Screening resumes... This may take a minute..."):
            try:
                results = process_multiple_resumes(jd_text, resume_data)
                
                # Store results in session state
                st.session_state["results"] = results
                
                st.success(f"✅ Screening complete! Processed {len(results)} resume(s)")
                
            except Exception as e:
                st.error(f"❌ Error during screening: {str(e)}")
                st.exception(e)

# Display results
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    
    st.divider()
    st.header("📊 Screening Results")
    
    # Create DataFrame
    df = pd.DataFrame([
        {
            "Candidate": r["candidate"],
            "Score": f"{r['score']}%",
            "Status": "✅ Strong Fit" if r["score"] >= 70 else "⚠️ Moderate Fit" if r["score"] >= 50 else "❌ Weak Fit"
        }
        for r in results
    ])
    
    # Sort by score
    df_sorted = df.sort_values(by="Score", ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
    
    # Display table
    st.subheader("📋 Candidate Summary")
    st.dataframe(
        df_sorted,
        use_container_width=True,
        hide_index=True
    )
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Score Distribution")
        
        # Bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=[r["candidate"] for r in sorted(results, key=lambda x: x["score"], reverse=True)],
                y=[r["score"] for r in sorted(results, key=lambda x: x["score"], reverse=True)],
                marker_color=['#00cc66' if r["score"] >= 70 else '#ffaa00' if r["score"] >= 50 else '#ff4444' 
                             for r in sorted(results, key=lambda x: x["score"], reverse=True)],
                text=[f"{r['score']}%" for r in sorted(results, key=lambda x: x["score"], reverse=True)],
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            yaxis_title="Score (%)",
            xaxis_title="Candidate",
            showlegend=False,
            height=400,
            yaxis_range=[0, 110]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Statistics")
        
        scores = [r["score"] for r in results]
        
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Average", f"{sum(scores)/len(scores):.1f}%")
        col_b.metric("Highest", f"{max(scores)}%")
        col_c.metric("Lowest", f"{min(scores)}%")
        
        st.divider()
        
        strong = sum(1 for s in scores if s >= 70)
        moderate = sum(1 for s in scores if 50 <= s < 70)
        weak = sum(1 for s in scores if s < 50)
        
        st.write("**Fit Distribution:**")
        st.write(f"✅ Strong Fit (≥70%): {strong}")
        st.write(f"⚠️ Moderate Fit (50-69%): {moderate}")
        st.write(f"❌ Weak Fit (<50%): {weak}")
    
    # Detailed results
    st.divider()
    st.subheader("📝 Detailed Analysis")
    
    for idx, result in enumerate(sorted(results, key=lambda x: x["score"], reverse=True), 1):
        with st.expander(f"#{idx} {result['candidate']} - Score: {result['score']}%"):
            
            if result.get("error"):
                st.error(f"⚠️ Error: {result['error']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Reasons for Score:**")
                for reason in result.get("reasons", []):
                    st.write(f"• {reason}")
                
                if result.get("matches"):
                    st.markdown("**🎯 Key Matches:**")
                    for match in result["matches"][:5]:
                        st.write(f"• {match}")
            
            with col2:
                if result.get("gaps"):
                    st.markdown("**⚠️ Gaps Identified:**")
                    for gap in result["gaps"][:5]:
                        st.write(f"• {gap}")
                
                if result.get("suggestions") and result["score"] < 50:
                    st.markdown("**💡 Suggestions:**")
                    for suggestion in result["suggestions"]:
                        st.write(f"• {suggestion}")
    
    # Download results
    st.divider()
    st.subheader("💾 Export Results")
    
    json_data = json.dumps(results, indent=2)
    
    st.download_button(
        label="📥 Download JSON Report",
        data=json_data,
        file_name="screening_results.json",
        mime="application/json",
        use_container_width=True
    )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with LangChain, LangGraph, Google Gemini, and Streamlit</p>
    <p>⚠️ Data processed in-memory only. No personal information is stored.</p>
</div>
""", unsafe_allow_html=True)