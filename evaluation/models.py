"""
Models Module
=============
Data models and entities for the evaluation system.
Follows Single Responsibility - only defines data structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class EvaluationStatus(Enum):
    """Status of an evaluation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Bot:
    """Represents an AI bot to be evaluated."""
    name: str
    assistant_id: str
    description: str = ""
    
    def is_configured(self) -> bool:
        """Check if the bot has a valid assistant ID."""
        return bool(self.assistant_id and self.assistant_id.strip())


@dataclass
class Question:
    """Represents an evaluation question."""
    index: int
    text: str
    category: Optional[str] = None


@dataclass
class BotResponse:
    """Represents a bot's response to a question."""
    bot_name: str
    question_index: int
    question_text: str
    response_text: str
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: Optional[int] = None
    
    def is_empty(self) -> bool:
        """Check if the response is empty."""
        return not self.response_text or not self.response_text.strip()


@dataclass
class EvaluationResult:
    """Represents the evaluation of a bot's response."""
    bot_name: str
    question_index: int
    response: BotResponse
    score: Optional[float] = None  # 0-10 scale
    evaluation_text: str = ""
    criteria_scores: dict = field(default_factory=dict)  # Individual criteria scores
    evaluator_type: str = "manual"  # "manual", "llm", etc.
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_evaluated(self) -> bool:
        """Check if this result has been evaluated."""
        return self.score is not None or bool(self.evaluation_text.strip())


@dataclass
class EvaluationSession:
    """Represents a complete evaluation session for all bots."""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: EvaluationStatus = EvaluationStatus.PENDING
    questions: List[Question] = field(default_factory=list)
    responses: List[BotResponse] = field(default_factory=list)
    evaluations: List[EvaluationResult] = field(default_factory=list)
    
    def get_responses_for_bot(self, bot_name: str) -> List[BotResponse]:
        """Get all responses for a specific bot."""
        return [r for r in self.responses if r.bot_name == bot_name]
    
    def get_evaluations_for_bot(self, bot_name: str) -> List[EvaluationResult]:
        """Get all evaluations for a specific bot."""
        return [e for e in self.evaluations if e.bot_name == bot_name]
    
    def get_completion_percentage(self) -> float:
        """Calculate the completion percentage of the session."""
        total_expected = len(self.questions) * 3  # 3 bots
        completed = len([e for e in self.evaluations if e.is_evaluated()])
        return (completed / total_expected * 100) if total_expected > 0 else 0

