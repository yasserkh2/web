"""
Base Evaluator
==============
Abstract base class for all evaluators.
Follows:
- Interface Segregation Principle: Focused interface
- Dependency Inversion Principle: High-level modules depend on abstractions
- Liskov Substitution Principle: Subtypes are substitutable
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..models import BotResponse, EvaluationResult, Question
from ..config import BotConfig


class BaseEvaluator(ABC):
    """
    Abstract base class for response evaluators.
    
    All evaluators must implement the evaluate() method.
    This allows for different evaluation strategies (LLM, manual, rule-based, etc.)
    """
    
    def __init__(self, name: str = "base"):
        self.name = name
    
    @abstractmethod
    def evaluate(
        self,
        response: BotResponse,
        bot_config: BotConfig,
        question: Question,
        criteria: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a bot's response.
        
        Args:
            response: The bot's response to evaluate
            bot_config: Configuration of the bot being evaluated
            question: The question that was asked
            criteria: Optional evaluation criteria
            
        Returns:
            EvaluationResult with score and evaluation text
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this evaluator is available (e.g., API key configured).
        
        Returns:
            True if the evaluator can be used
        """
        pass
    
    def get_default_criteria(self) -> Dict[str, float]:
        """
        Get default evaluation criteria with weights.
        Override in subclasses for custom criteria.
        
        Returns:
            Dictionary of criteria names to weights (should sum to 1.0)
        """
        return {
            "accuracy": 0.25,
            "persona_alignment": 0.25,
            "tone_appropriateness": 0.20,
            "clarity": 0.15,
            "completeness": 0.15
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

