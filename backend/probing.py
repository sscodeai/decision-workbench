"""The three probing questions that force the option space open.

These are injected into the divergence stage. They exist to break the
decision-maker's (and the models') anchoring:
  1. "Why did you NOT consider X?" — forces out excluded options.
  2. "Give one non-mainstream option with a real reason" — kicks the model
     out of its training distribution.
  3. "What is the weakest point of your preferred option?" — cross-examination
     that a single model never performs on itself.
"""

from typing import Dict, List

from .config import PROBING_QUESTIONS


def probing_questions() -> List[Dict[str, str]]:
    """Return the probing question definitions."""
    return list(PROBING_QUESTIONS)


def build_probing_prompt(question: Dict[str, str], user_input: str) -> str:
    """Build the full prompt for one probing question.

    The mock provider detects the question id / phrasing to return the right
    canned answer; real providers just get the instruction.
    """
    return (
        f"PROBING QUESTION: {question['question']}\n\n"
        f"INSTRUCTION: {question['instruction']}\n\n"
        f"The decision being made:\n{user_input}\n\n"
        "Output an option in this exact format:\n"
        "OPTION: <canonical-id>\n"
        "CANONICAL: <dedup-key>\n"
        "NOVELTY: you_probably_didnt_know | you_already_knew\n"
        "REASON: <why this option>\n"
        "TARGET: <option this attacks, for weakest_point only, or omit>"
    )
