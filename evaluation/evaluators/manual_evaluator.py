"""
Manual Evaluator
================
Handles manual/human evaluation input.
Follows Single Responsibility: Only handles manual evaluation.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseEvaluator
from ..models import BotResponse, EvaluationResult, Question
from ..config import BotConfig


class ManualEvaluator(BaseEvaluator):
    """
    Evaluator for manual/human evaluation input.
    Used when responses need to be evaluated by a human evaluator.
    """
    
    def __init__(self):
        super().__init__(name="manual")
    
    def is_available(self) -> bool:
        """Manual evaluation is always available."""
        return True
    
    def evaluate(
        self,
        response: BotResponse,
        bot_config: BotConfig,
        question: Question,
        criteria: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Create a placeholder evaluation result for manual input.
        
        The actual evaluation will be filled in by a human.
        """
        return EvaluationResult(
            bot_name=response.bot_name,
            question_index=response.question_index,
            response=response,
            score=None,
            evaluation_text="[Pending manual evaluation]",
            evaluator_type=self.name,
            timestamp=datetime.now()
        )
    
    def set_evaluation(
        self,
        result: EvaluationResult,
        score: float,
        evaluation_text: str,
        criteria_scores: Optional[Dict[str, float]] = None
    ) -> EvaluationResult:
        """
        Set the manual evaluation values.
        
        Args:
            result: The evaluation result to update
            score: The score (0-10)
            evaluation_text: The evaluation text
            criteria_scores: Optional individual criteria scores
            
        Returns:
            Updated EvaluationResult
        """
        result.score = score
        result.evaluation_text = evaluation_text
        result.criteria_scores = criteria_scores or {}
        result.timestamp = datetime.now()
        return result
    
    def create_evaluation(
        self,
        bot_name: str,
        question_index: int,
        response_text: str,
        score: float,
        evaluation_text: str
    ) -> EvaluationResult:
        """
        Create a complete manual evaluation result.
        
        Args:
            bot_name: Name of the bot
            question_index: Index of the question
            response_text: The bot's response
            score: The evaluation score
            evaluation_text: The evaluation text
            
        Returns:
            Complete EvaluationResult
        """
        response = BotResponse(
            bot_name=bot_name,
            question_index=question_index,
            question_text="",  # Will be filled by service
            response_text=response_text
        )
        
        return EvaluationResult(
            bot_name=bot_name,
            question_index=question_index,
            response=response,
            score=score,
            evaluation_text=evaluation_text,
            evaluator_type=self.name,
            timestamp=datetime.now()
        )




