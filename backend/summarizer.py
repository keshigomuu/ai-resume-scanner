import os
import openai

# 1. Initialize the OpenAI client from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")

def summarize_resume_via_chatgpt(resume_text: str, max_tokens: int = 250) -> str:
    """
    Summarize the given resume_text into bullet points highlighting:
      - Core technical skills
      - Key projects or experiences
      - Major achievements
    Returns a plain-text summary (bullet-pointed) via the v1 OpenAI API.
    """

    # 2. Truncate resume to avoid exceeding token limits (about 3000 chars)
    MAX_CHARS = 3000
    if len(resume_text) > MAX_CHARS:
        resume_excerpt = resume_text[:MAX_CHARS] + "\n\n[...truncated...]"
    else:
        resume_excerpt = resume_text

    system_message = {
        "role": "system",
        "content": (
            "You are a helpful assistant that summarizes resumes. "
            "Produce a concise bullet-point summary emphasizing key technical skills, "
            "major projects or roles, and significant achievements. Each bullet should be under 25 words."
        )
    }

    user_message = {
        "role": "user",
        "content": (
            "Here is a candidate’s resume (possibly long):\n\n"
            "```\n"
            f"{resume_excerpt}\n"
            "```\n\n"
            "Please return a bullet-point summary (plain text, no JSON) capturing:\n"
            "- Core technical skills (e.g., languages, frameworks, tools)\n"
            "- Key projects or positions and responsibilities\n"
            "- Significant measurable outcomes (e.g., “Improved X by 30%”)\n\n"
            "Keep the entire summary under 8 bullets."
        )
    }

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
            temperature=0.3,
            max_tokens=max_tokens
        )
    except openai.OpenAIError as e:
        # If the API call fails, raise or return a fallback
        raise RuntimeError(f"OpenAI API error during summarization: {e}")

    summary = response.choices[0].message.content.strip()
    return summary
