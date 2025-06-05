# backend/app.py

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Set
from resume_parser import extract_text_from_pdf
from skill_matcher import extract_skills, compare_skills
from suggestions import generate_suggestions

app = FastAPI(title="AI Resume–JD Skill Matcher")

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
    # 1. Ensure resume is PDF
    if not resume_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF.")

    # 2. Read resume bytes & extract text
    resume_bytes = await resume_file.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # 3. JD is already plain text (from the textarea)
    raw_jd = jd_text

    # 4. Extract skill sets (both case-insensitive, using PhraseMatcher)
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(raw_jd)

    # 5. If jd_skills is empty, return a quick warning
    if not jd_skills:
        raise HTTPException(
            status_code=422,
            detail="No recognizable skills were found in the job description. "
                   "Please make sure you’ve pasted known skill keywords (e.g., Python, Docker, AWS, etc.)."
        )

    # 6. Compare skill sets & generate suggestions
    comparison = compare_skills(resume_skills, jd_skills)
    suggestions = generate_suggestions(comparison["missing"])

    # 7. Return JSON
    result = MatchResult(
        match_percentage=comparison["match_percentage"],
        matched_skills=comparison["matched"],
        missing_skills=comparison["missing"],
        suggestions=suggestions
    )
    return result


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
