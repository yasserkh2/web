"""
Configuration classes for the evaluation system.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LLMConfig:
    """Configuration for LLM-based evaluation."""
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    temperature: float = 0.3


@dataclass
class BotConfig:
    """Configuration for a bot/persona."""
    name: str = ""
    assistant_id: str = ""
    description: str = ""
    response_column: str = ""
    eval_column: str = ""
    comment_column: str = ""


@dataclass
class VAPIConfig:
    """Configuration for VAPI integration."""
    api_key: str = field(default_factory=lambda: os.environ.get("VAPI_API_KEY", ""))
    base_url: str = "https://api.vapi.ai"


@dataclass
class EvaluationConfig:
    """Main evaluation configuration."""
    excel_path: str = "bot_evaluation.xlsx"
    bots: List[BotConfig] = field(default_factory=list)
    
    def get_bot(self, name: str) -> Optional[BotConfig]:
        """Get bot config by name."""
        for bot in self.bots:
            if bot.name == name:
                return bot
        return None


# Default questions for evaluation
DEFAULT_QUESTIONS = [
    "Hey, doctor. Um, help me understand. How do you make treatment decisions?",
    "A new therapy is just approved. What makes you start using it in practice?",
    "What kind of evidence convinces you most—real-world data, RCTs, meta-analyses, expert opinion?",
]
