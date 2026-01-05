"""
Data Models
============
Pure data classes following Single Responsibility Principle.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SegmentType(Enum):
    """Available segment types."""
    TRADITIONALIST = "The Traditionalist"
    INNOVATOR = "The Innovator"
    EVIDENCE_PURIST = "The Evidence Purist"


@dataclass
class Segment:
    """Represents a physician segment/persona."""
    name: str
    description: str = ""
    traits: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    
    @property
    def slug(self) -> str:
        """Return URL-friendly name."""
        return self.name.lower().replace(" ", "_").replace("-", "_")


@dataclass
class Question:
    """Represents a question to ask the bot."""
    id: int
    text: str
    category: str = ""


@dataclass
class Response:
    """Represents a bot's response to a question."""
    segment: str
    question_id: int
    question_text: str
    response_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "vapi"  # "vapi", "mock", "manual"
    
    @property
    def is_empty(self) -> bool:
        return not self.response_text or not self.response_text.strip()
    
    @property
    def preview(self) -> str:
        """Return first 200 chars of response."""
        if len(self.response_text) > 200:
            return self.response_text[:200] + "..."
        return self.response_text


@dataclass
class Evaluation:
    """Represents an evaluation of a response."""
    segment: str
    question_id: int
    score: int  # 0-5
    comment: str = ""
    evaluator: str = "llm"  # "llm", "Aboubakr", "Thomas"
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def needs_comment(self) -> bool:
        """Comments required for low scores."""
        return self.score <= 3
    
    @property
    def is_passing(self) -> bool:
        """Score 4+ is passing."""
        return self.score >= 4


@dataclass
class EvaluationResult:
    """Complete evaluation result for a segment."""
    segment: str
    responses: List[Response] = field(default_factory=list)
    evaluations: List[Evaluation] = field(default_factory=list)
    
    @property
    def average_score(self) -> float:
        if not self.evaluations:
            return 0.0
        return sum(e.score for e in self.evaluations) / len(self.evaluations)
    
    @property
    def pass_rate(self) -> float:
        if not self.evaluations:
            return 0.0
        passing = sum(1 for e in self.evaluations if e.is_passing)
        return (passing / len(self.evaluations)) * 100

