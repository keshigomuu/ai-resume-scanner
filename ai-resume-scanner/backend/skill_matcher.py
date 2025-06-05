import json
import re
from pathlib import Path
from typing import List, Set, Dict

# 1. Load and preprocess skill patterns
skill_list_path = Path(__file__).parent / "skill_patterns.json"
with open(skill_list_path, "r", encoding="utf-8") as f:
    raw_skill_patterns: List[str] = json.load(f)

# Convert each skill into a list of lowercase tokens, e.g. "Amazon Web Services" → ["amazon","web","services"]
def tokenize(text: str) -> List[str]:
    # A very simple tokenizer: split on non-alphanumeric (keeps + and # as part of words if you like)
    # For more accuracy, you can use nltk.word_tokenize or spaCy, but this suffices.
    tokens = re.findall(r"[A-Za-z0-9\+\#\.]+", text.lower())
    return tokens

# Build a map { canonical_skill: [list of lowercased tokens] }
SKILL_TOKEN_MAP: Dict[str, List[str]] = {}
for skill in raw_skill_patterns:
    # Lowercase and tokenize the skill name itself
    tokens = tokenize(skill)
    if tokens:
        SKILL_TOKEN_MAP[skill] = tokens


def extract_skills(text: str) -> Set[str]:
    """
    Given free-form text, return the set of canonical skills (keys from SKILL_TOKEN_MAP)
    whose token sequence appears in the text's token list.
    """
    found: Set[str] = set()
    text_tokens = tokenize(text)

    # For each skill, attempt to find its token sequence in text_tokens
    for skill, skill_tokens in SKILL_TOKEN_MAP.items():
        if not skill_tokens:
            continue

        # If the skill is a single token (e.g. ["python"]), just check membership
        if len(skill_tokens) == 1:
            if skill_tokens[0] in text_tokens:
                found.add(skill)
            continue

        # Otherwise, for multi-word skills, do a sliding window over text_tokens
        window_size = len(skill_tokens)
        for i in range(len(text_tokens) - window_size + 1):
            if text_tokens[i : i + window_size] == skill_tokens:
                found.add(skill)
                break

    return found


def split_sentences(text: str) -> List[str]:
    """
    A simple sentence splitter—splits on end-of-sentence punctuation.
    (You can swap in nltk.sent_tokenize for more robustness.)
    """
    # Keep the punctuation with the sentence using a regex:
    sentences = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def find_skill_context(text: str, missing_skills: List[str]) -> Dict[str, List[str]]:
    """
    For each skill in missing_skills, return a list of sentences from text
    in which that skill (case-insensitive) appears.
    """
    contexts: Dict[str, List[str]] = {}
    sentences = split_sentences(text)
    lower_sentences = [s.lower() for s in sentences]

    for skill in missing_skills:
        skill_lower = skill.lower()
        found_sents: List[str] = []
        for idx, sent_lower in enumerate(lower_sentences):
            # Check exact substring; this captures multi-word skills even if token boundaries differ
            if skill_lower in sent_lower:
                found_sents.append(sentences[idx])
        contexts[skill] = found_sents or ["(No exact-sentence context found)"]
    return contexts
