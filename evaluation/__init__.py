"""
Evaluation Package
==================
A modular evaluation system for AI bots following SOLID principles.

Structure:
- config.py: Configuration and bot mappings
- models.py: Data models and entities
- evaluators/: Evaluation strategy implementations
- services/: Business logic services
"""

from .config import BotConfig, EvaluationConfig
from .models import Bot, Question, EvaluationResult

__all__ = [
    "BotConfig",
    "EvaluationConfig", 
    "Bot",
    "Question",
    "EvaluationResult"
]




