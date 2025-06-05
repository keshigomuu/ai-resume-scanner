import os
import openai
import json
from typing import Dict, List, Any

# 1. Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

def generate_suggestions_via_chatgpt(
    missing_skills: List[str],
    resume_summary: str,
    jd_text: str,
    original_bullets: List[str]
) -> Dict[str, List[str]]:
    """
    Generate two sections via ChatGPT:
      1. 'rewritten_bullets': improved versions of the original resume bullets
         (only enhancing existing bullets without adding skills the candidate doesn't have).
      2. 'suggestions': actionable advice on missing skills or overall resume improvements.
    Uses:
      - A concise resume_summary (bullet points)
      - The full job description text (truncated if too long)
      - A list of missing skills
      - The original list of resume bullets to guide rewrites
    Returns a dict with keys "rewritten_bullets" and "suggestions", each a list of strings.
    """

    # If nothing is missing, still produce rewritten bullets and a single positive note
    if not missing_skills:
        return {
            "rewritten_bullets": original_bullets,
            "suggestions": ["• Your resume already covers all listed JD skills. Great job!"]
        }

    # 2. Truncate job description to about 3000 chars to avoid token overflow
    MAX_JD_CHARS = 3000
    if len(jd_text) > MAX_JD_CHARS:
        jd_excerpt = jd_text[:MAX_JD_CHARS] + "\n\n[...truncated...]"
    else:
        jd_excerpt = jd_text

    # Build numbered list of missing skills
    skill_list_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(missing_skills))

    # Build numbered list of original bullets to reference in the prompt
    bullets_list_text = "\n".join(f"{i+1}. {b}" for i, b in enumerate(original_bullets))

    system_message = {
        "role": "system",
        "content": (
            "You are a professional resume coach. Read a candidate’s resume bullets and a target job description, "
            "then produce two sections:\n"
            "1. rewritten_bullets: Improve each original bullet (keep each bullet's gist—do NOT add skills the candidate doesn’t have). "
            "Use numbers/metrics where possible and tie it back to the JD requirements.\n"
            "2. suggestions: For each missing skill, give one concise bullet with actionable advice on how to highlight or acquire that skill. "
            "Also include 2–3 general tips at the end for making the resume more attention-grabbing (use strong verbs, mirror JD keywords, quantify results).\n"
            "Keep every bullet under 40 words.\n"
            "Return your output as a valid JSON object with two arrays: {\"rewritten_bullets\": [...], \"suggestions\": [...] }."
        )
    }

    user_message = {
        "role": "user",
        "content": (
            "Here are the candidate’s original resume bullets:\n"
            "```\n"
            f"{bullets_list_text}\n"
            "```\n\n"
            "Here is the full job description:\n"
            "```\n"
            f"{jd_excerpt}\n"
            "```\n\n"
            "The resume does NOT mention these required skill(s):\n"
            f"{skill_list_text}\n\n"
            "First, rewrite each original bullet to be more impactful and aligned with the JD, "
            "adding metrics where possible—without introducing skills not already present.\n"
            "Then, for each missing skill above, provide exactly one bullet with actionable advice on how to include or obtain that skill. "
            "After those, list 2–3 general tips for making the resume more attention-grabbing (e.g., strong verbs, numbers, keywords).\n"
            "Return a JSON object:\n"
            "{\n"
            '  "rewritten_bullets": [ /* improved bullets */ ],\n'
            '  "suggestions": [ /* missing-skill advice + general tips */ ]\n'
            "}\n"
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
        # Fallback: return original bullets and generic advice
        fallback_rewrites = original_bullets
        fallback_suggestions = [
            f"• Consider adding '{skill}' to your resume and highlight it with a concrete example and metric."
            for skill in missing_skills
        ]
        fallback_suggestions += [
            "• Use strong action verbs (e.g., “Led,” “Reduced,” “Implemented”) to start each bullet.",
            "• Quantify every achievement with metrics (e.g., “Reduced costs by 30%”).",
            "• Mirror keywords from the job description so your resume passes ATS filters."
        ]
        return {
            "rewritten_bullets": fallback_rewrites,
            "suggestions": fallback_suggestions
        }

    raw = response.choices[0].message.content.strip()

    # Parse as JSON object
    try:
        # Strip code fences if present
        if raw.startswith("```"):
            raw = "\n".join(raw.splitlines()[1:-1])

        parsed = json.loads(raw)
        if (
            isinstance(parsed, dict)
            and "rewritten_bullets" in parsed and isinstance(parsed["rewritten_bullets"], list)
            and "suggestions" in parsed and isinstance(parsed["suggestions"], list)
        ):
            return {
                "rewritten_bullets": parsed["rewritten_bullets"],
                "suggestions": parsed["suggestions"]
            }
        else:
            # Fallback extraction: split by top-level keys if possible
            # Very crude: look for lines under “rewritten_bullets” and “suggestions” labels
            lines = raw.splitlines()
            rewritten, suggestions = [], []
            mode = None
            for line in lines:
                if '"rewritten_bullets"' in line:
                    mode = "rewritten"
                    continue
                if '"suggestions"' in line:
                    mode = "suggestions"
                    continue
                if mode == "rewritten" and line.strip().startswith("•"):
                    rewritten.append(line.strip())
                if mode == "suggestions" and line.strip().startswith("•"):
                    suggestions.append(line.strip())
            return {
                "rewritten_bullets": rewritten or original_bullets,
                "suggestions": suggestions or []
            }
    except Exception:
        # If JSON parsing fails, return raw text as single suggestion
        return {
            "rewritten_bullets": original_bullets,
            "suggestions": [raw]
        }
