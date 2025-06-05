# backend/app.py

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Set, Dict, Any
from resume_parser import extract_text_from_pdf
from summarizer import summarize_resume_via_chatgpt
from skill_matcher import extract_skills
from suggestions import generate_suggestions_via_chatgpt  # now expects original_bullets

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
    rewritten_bullets: List[str]
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

    # 3. Summarize the resume (optional, but speeds up extraction & removes noise)
    try:
        resume_summary = summarize_resume_via_chatgpt(full_resume_text)
    except Exception:
        resume_summary = full_resume_text

    # 4. JD text is passed in as plain text
    raw_jd = jd_text

    # 5. Token-based skill matching using the static list
    resume_skills = extract_skills(resume_summary)
    jd_skills     = extract_skills(raw_jd)

    if not jd_skills:
        raise HTTPException(
            status_code=422,
            detail="No recognizable skills were found in the job description."
        )

    # 6. Compare skill sets (case-insensitive comparison via extract_skills)
    matched = sorted([s for s in resume_skills if s in jd_skills])
    missing = sorted([s for s in jd_skills if s not in resume_skills])
    match_percentage = round(len(matched) / len(jd_skills) * 100.0, 2) if jd_skills else 0.0

    # 7. Prepare original bullets from resume_summary
    original_bullets = [line.strip() for line in resume_summary.splitlines() if line.strip()]

    # 8. Generate ChatGPT-based rewritten bullets and suggestions
    output = generate_suggestions_via_chatgpt(
        missing_skills=missing,
        resume_summary=resume_summary,
        jd_text=raw_jd,
        original_bullets=original_bullets
    )
    rewritten_bullets = output["rewritten_bullets"]
    chatgpt_suggestions = output["suggestions"]

    # 9. Return full response
    return {
        "match_percentage": match_percentage,
        "matched_skills": matched,
        "missing_skills": missing,
        "rewritten_bullets": rewritten_bullets,
        "suggestions": chatgpt_suggestions
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
