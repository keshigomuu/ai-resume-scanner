# backend/app.py

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Set
from resume_parser import extract_text_from_pdf
from summarizer import summarize_resume_via_chatgpt
from skill_matcher import extract_skills, compare_skills
from suggestions import generate_suggestions_via_chatgpt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Resume–JD Skill Matcher")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
class MatchResult(BaseModel):
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[str]

@app.post("/match/", response_model=MatchResult)
async def match_resume_jd(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...)
):
    # 1. Validate that resume is PDF
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF.")

    # 2. Extract full resume text
    resume_bytes = await resume_file.read()
    full_resume_text = extract_text_from_pdf(resume_bytes)

    # 3. Summarize resume
    try:
        resume_summary = summarize_resume_via_chatgpt(full_resume_text)
    except Exception:
        resume_summary = full_resume_text  # fallback if summarization fails

    # 4. JD text is passed in as plain text
    raw_jd = jd_text

    # 5. Extract skills from the summary and from the JD
    resume_skills = extract_skills(resume_summary)
    jd_skills = extract_skills(raw_jd)

    if not jd_skills:
        raise HTTPException(
            status_code=422,
            detail="No recognizable skills were found in the job description."
        )

    # 6. Compare skill sets
    comparison = compare_skills(resume_skills, jd_skills)

    # 7. Generate ChatGPT-powered suggestions
    chatgpt_suggestions = generate_suggestions_via_chatgpt(
        missing_skills=comparison["missing"],
        resume_summary=resume_summary,
        jd_text=raw_jd
    )

    # 8. Return final response
    return MatchResult(
        match_percentage=comparison["match_percentage"],
        matched_skills=comparison["matched"],
        missing_skills=comparison["missing"],
        suggestions=chatgpt_suggestions
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
