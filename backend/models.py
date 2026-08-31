"""Pydantic schemas for Decision Workbench API."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class DecideRequest(BaseModel):
    """The user's decision framing."""

    input: str


class ConstraintRequest(BaseModel):
    """Selected real-world constraints for weighted evaluation."""

    decision_id: str
    constraints: List[str]


class HumanDecisionRequest(BaseModel):
    """The human's final decision (the system never picks a winner)."""

    decision_id: str
    chosen_option: str
    rationale: str = ""


class Option(BaseModel):
    option: str
    canonical: str
    novelty: str = "you_probably_didnt_know"
    reason: str = ""
    support_count: int = 0
    near_variant_of: Optional[str] = None
    weighted_score: Optional[float] = None
    fit_breakdown: Optional[Dict[str, float]] = None
    tradeoffs: Optional[str] = None


class OptionSpaceMap(BaseModel):
    consensus_zone: List[Option] = []
    true_divergence_zone: List[Option] = []
    false_divergence_zone: List[Option] = []


class DecideResponse(BaseModel):
    decision_id: str
    input: str
    scenario: str
    bias_flags: List[Dict[str, str]] = []
    stance_divergence: List[Dict[str, Any]] = []
    probing_questions: List[Dict[str, str]] = []
    probing_answers: List[Dict[str, str]] = []
    option_space_map: OptionSpaceMap
    constraint_evaluation: Optional[List[Any]] = None
    human_decision: Dict[str, str]
