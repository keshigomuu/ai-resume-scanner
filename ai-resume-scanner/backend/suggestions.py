import os
import openai
import json
from typing import List

# 1. Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

def generate_suggestions_via_chatgpt(
    missing_skills: List[str],
    resume_summary: str,
    jd_text: str
) -> List[str]:
    """
    Generate one bullet-point suggestion per missing skill, using ChatGPT with context from:
      - A concise resume_summary (bullet points)
      - The full job description text (truncated if too long)
    Returns a list of JSON-array strings (one bullet per missing skill).
    """

    if not missing_skills:
        return ["• Your resume already covers all listed JD skills. Great job!"]

    # 2. Truncate job description to about 3000 chars to avoid token overflow
    MAX_JD_CHARS = 3000
    if len(jd_text) > MAX_JD_CHARS:
        jd_excerpt = jd_text[:MAX_JD_CHARS] + "\n\n[...truncated...]"
    else:
        jd_excerpt = jd_text

    # 3. Build numbered list of missing skills
    skill_list_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(missing_skills))

    system_message = {
        "role": "system",
        "content": (
            "You are an expert career-coach assistant. "
            "Given a resume summary and a job description, produce concise, actionable bullet-point suggestions "
            "for each missing skill. Each bullet-point should be under 40 words."
        )
    }

    user_message = {
        "role": "user",
        "content": (
            "The candidate’s resume (summarized) is:\n"
            "```\n"
            f"{resume_summary}\n"
            "```\n\n"
            "The job description is:\n"
            "```\n"
            f"{jd_excerpt}\n"
            "```\n\n"
            "The resume does NOT mention these required skill(s):\n"
            f"{skill_list_text}\n\n"
            "For each missing skill, generate EXACTLY one bullet-point suggestion in the format:\n"
            "• [actionable advice—how to highlight or acquire that skill].\n"
            "Return as a JSON array of strings in the same order as the missing skills."
        )
    }

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
            temperature=0.7,
            max_tokens=800
        )
    except openai.OpenAIError:
        # Fallback: if the API fails, emit a simple generic template for each skill
        return [
            f"• Consider adding '{skill}' to your resume and highlighting relevant experience or coursework."
            for skill in missing_skills
        ]

    raw = response.choices[0].message.content.strip()

    # 4. Parse as JSON array of strings
    try:
        # If ChatGPT wrapped the array in ```json ... ``` fences, strip them
        if raw.startswith("```"):
            raw = "\n".join(raw.splitlines()[1:-1])

        suggestions = json.loads(raw)
        if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
            return suggestions
        else:
            # Fallback: extract lines starting with a bullet
            lines = [line.strip() for line in raw.splitlines() if line.strip().startswith("•")]
            if len(lines) == len(missing_skills):
                return lines
            return [raw]
    except Exception:
        # If JSON parsing fails, return the raw text as a single-element list
        return [raw]
