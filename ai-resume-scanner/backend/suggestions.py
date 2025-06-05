from typing import List

def generate_suggestions(missing_skills: List[str]) -> List[str]:
    """
    For each missing skill, return a suggestion string.
    E.g., "Consider adding 'Docker' if you have experience or coursework with it."
    """
    suggestions = []
    for skill in missing_skills:
        s = (
            f"• Consider including '{skill}' in your resume. "
            f"If you have hands-on experience (projects, certifications, or coursework), highlight it."
        )
        suggestions.append(s)
    if not suggestions:
        suggestions = ["• Your resume already covers all listed JD skills. Great job!"]
    return suggestions
