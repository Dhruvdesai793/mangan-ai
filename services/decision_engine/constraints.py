"""Prototype operational constraints kept separate from decision logic."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionConstraints:
    max_recommended_actions: int = 3
    recommendations_require_human_approval: bool = True


DEFAULT_CONSTRAINTS = DecisionConstraints()
