"""
Configuration Module
====================
Centralized configuration for bots, VAPI, and evaluation settings.
Follows Single Responsibility Principle - only handles configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class BotConfig:
    """Configuration for a single bot."""
    name: str
    assistant_id: str
    description: str
    response_column: str
    eval_column: str
    comment_column: str
    color_response: str = "E8F4EA"  # Light color for response
    color_eval: str = "C8E6C9"      # Darker color for eval
    color_comment: str = "F5F5F5"   # Light gray for comments


@dataclass
class VAPIConfig:
    """VAPI API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("VAPI_API_KEY", ""))
    public_key: str = field(default_factory=lambda: os.getenv("VAPI_PUBLIC_KEY", ""))
    base_url: str = "https://api.vapi.ai"


@dataclass
class LLMConfig:
    """LLM configuration for automated evaluation."""
    provider: str = "openai"  # openai, anthropic, etc.
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4o-mini"
    temperature: float = 0.3


@dataclass
class MLflowConfig:
    """MLflow experiment tracking configuration."""
    tracking_uri: str = field(default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "mlruns"))
    experiment_name: str = field(default_factory=lambda: os.getenv("MLFLOW_EXPERIMENT_NAME", "bot_evaluation"))
    run_name_prefix: str = "eval"
    log_artifacts: bool = True
    log_system_metrics: bool = True
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass 
class EvaluationConfig:
    """Main evaluation configuration."""
    excel_file: str = "bot_evaluation.xlsx"
    bots: Dict[str, BotConfig] = field(default_factory=dict)
    vapi: VAPIConfig = field(default_factory=VAPIConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    mlflow: MLflowConfig = field(default_factory=MLflowConfig)
    
    @classmethod
    def default(cls) -> "EvaluationConfig":
        """Create default configuration with the 3 bots."""
        config = cls()
        config.bots = {
            "The Traditionalist": BotConfig(
                name="The Traditionalist",
                assistant_id=os.getenv("VAPI_ASSISTANT_ID_1", ""),
                description="Relies on established, time-tested treatments",
                response_column="B",
                eval_column="C",
                comment_column="D",
                color_response="E8F4EA",
                color_eval="C8E6C9",
                color_comment="D7CCC8"  # Light brown
            ),
            "The Innovator": BotConfig(
                name="The Innovator",
                assistant_id=os.getenv("VAPI_ASSISTANT_ID_2", ""),
                description="Early adopter of new treatments and technologies",
                response_column="E",
                eval_column="F",
                comment_column="G",
                color_response="FFF3E0",
                color_eval="FFE0B2",
                color_comment="FFE082"  # Light amber
            ),
            "The Evidence Purist": BotConfig(
                name="The Evidence Purist",
                assistant_id=os.getenv("VAPI_ASSISTANT_ID_5", ""),
                description="Strictly follows clinical evidence and data",
                response_column="H",
                eval_column="I",
                comment_column="J",
                color_response="E3F2FD",
                color_eval="BBDEFB",
                color_comment="90CAF9"  # Light blue
            ),
        }
        return config
    
    def get_bot(self, name: str) -> Optional[BotConfig]:
        """Get bot configuration by name."""
        return self.bots.get(name)
    
    def get_all_bot_names(self) -> List[str]:
        """Get list of all bot names."""
        return list(self.bots.keys())


# Default questions for evaluation
DEFAULT_QUESTIONS: List[str] = [
    "How does the bot handle initial greeting?",
    "Does the bot understand the medical context correctly?",
    "How well does the bot respond to patient concerns?",
    "Is the response clinically appropriate?",
    "Does the bot maintain conversation flow?",
    "How accurate is the medical information provided?",
    "Does the bot handle follow-up questions well?",
    "Is the bot's tone appropriate for the persona?",
    "Does the bot handle edge cases gracefully?",
    "Overall evaluation score (1-10)",
]


