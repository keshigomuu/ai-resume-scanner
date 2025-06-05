# backend/skill_matcher.py

import spacy
from spacy.matcher import PhraseMatcher
from pathlib import Path
import json
from typing import Set

# 1. Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# 2. Load our canonical skill list from skill_list.json
skill_list_path = Path(__file__).parent / "skill_patterns.json"
with open(skill_list_path, "r", encoding="utf-8") as f:
    skill_terms = json.load(f)  # e.g. ["Python", "Java", "Docker", ...]

# 3. Create a PhraseMatcher that does case-insensitive matching (attr="LOWER")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(term) for term in skill_terms]
matcher.add("SKILL", patterns)


def extract_skills(text: str) -> Set[str]:
    """
    Use PhraseMatcher to find any of the canonical skill_terms (case-insensitive)
    in the given text. Returns a set of matched skill strings (exactly as in skill_terms).
    """
    doc = nlp(text)
    matches = matcher(doc)
    found_skills = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        # span.text might be "python" or "Docker"; we want the canonical form
        # We can normalize by comparing span.lower_ to each skill_term.lower()
        matched_text = span.text
        # Find which canonical term this corresponds to (case-insensitive)
        for term in skill_terms:
            if term.lower() == matched_text.lower():
                found_skills.add(term)
                break
    return found_skills


def compare_skills(resume_skills: Set[str], jd_skills: Set[str]) -> dict:
    """
    Given two sets of canonical skill strings:
      - resume_skills: skills found in resume (e.g. {"Python","Docker"})
      - jd_skills: skills extracted from job description
    Returns a dict with:
      - matched: sorted list of skills in both
      - missing: sorted list of jd_skills not in resume_skills
      - match_percentage: float = (|matched| / |jd_skills|) * 100, or 0 if jd_skills empty
    """
    matched = resume_skills.intersection(jd_skills)
    missing = jd_skills.difference(resume_skills)
    pct = 0.0
    if jd_skills:
        pct = len(matched) / len(jd_skills) * 100.0
    return {
        "matched": sorted(matched),
        "missing": sorted(missing),
        "match_percentage": round(pct, 2),
    }
