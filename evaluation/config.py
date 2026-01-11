"""
Evaluation Configuration
========================
Configuration for all bot personas, VAPI integration, and evaluation settings.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class VAPIConfig:
    """VAPI API configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("VAPI_API_KEY", ""))
    public_key: str = field(default_factory=lambda: os.getenv("VAPI_PUBLIC_KEY", ""))
    base_url: str = "https://api.vapi.ai"


@dataclass
class BotConfig:
    """Configuration for a single bot persona."""
    name: str
    display_name: str
    assistant_id: str
    description: str
    prompt_file: str  # Path to the segment markdown file
    response_column: str  # Excel column for responses
    evaluation_column: str  # Excel column for evaluations
    avatar_emoji: str = "🤖"
    customer_segment: str = "Healthcare Providers"
    
    def get_prompt_content(self) -> str:
        """Load the prompt/persona description from the markdown file."""
        if os.path.exists(self.prompt_file):
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        return self.description
    
    def is_configured(self) -> bool:
        """Check if VAPI assistant is configured."""
        return bool(self.assistant_id and self.assistant_id.strip())


class EvaluationConfig:
    """
    Main configuration class for the evaluation system.
    Links all 6 segments with their VAPI IDs and prompt files.
    """
    
    # Base path for segment prompt files
    SEGMENTS_PATH = Path(__file__).parent.parent / "segments"
    DATASETS_PATH = Path(__file__).parent.parent / "datasets"
    
    def __init__(self):
        self.vapi = VAPIConfig()
        self._bots: Dict[str, BotConfig] = {}
        self._initialize_bots()
    
    def _initialize_bots(self):
        """Initialize all 6 bot personas with their configurations."""
        
        # Bot configurations with VAPI Assistant IDs from environment
        bot_configs = [
            {
                "name": "The Traditionalist",
                "display_name": "The Traditionalist",
                "assistant_id_env": "VAPI_ASSISTANT_ID_1",
                "prompt_file": "the_traditionalist.md",
                "response_column": "B",
                "evaluation_column": "C",
                "avatar_emoji": "👨‍⚕️",
                "customer_segment": "Healthcare Providers",
                "description": "Relies on established, well-documented, time-tested treatments. Skeptical of new drugs without extensive long-term real-world data."
            },
            {
                "name": "The Innovator",
                "display_name": "The Innovator",
                "assistant_id_env": "VAPI_ASSISTANT_ID_2",
                "prompt_file": "the_innovator.md",
                "response_column": "D",
                "evaluation_column": "E",
                "avatar_emoji": "🚀",
                "customer_segment": "Healthcare Providers",
                "description": "Eager to adopt cutting-edge therapies with novel mechanisms. Wants to be at the forefront of medical advancement."
            },
            {
                "name": "The Patient-Centered Physician",
                "display_name": "The Patient-Centered Physician",
                "assistant_id_env": "VAPI_ASSISTANT_ID_3",
                "prompt_file": "the_patient_centered.md",
                "response_column": "F",
                "evaluation_column": "G",
                "avatar_emoji": "💚",
                "customer_segment": "Healthcare Providers",
                "description": "Focuses on holistic well-being and patient experience. Considers quality of life, convenience, and affordability."
            },
            {
                "name": "The Financially Driven Prescriber",
                "display_name": "The Financially Driven Prescriber",
                "assistant_id_env": "VAPI_ASSISTANT_ID_4",
                "prompt_file": "the_financially_driven.md",
                "response_column": "H",
                "evaluation_column": "I",
                "avatar_emoji": "💰",
                "customer_segment": "Healthcare Institutions",
                "description": "Motivated by economic factors like reimbursement, practice profitability, and cost-effectiveness."
            },
            {
                "name": "The Evidence Purist",
                "display_name": "The Evidence Purist",
                "assistant_id_env": "VAPI_ASSISTANT_ID_5",
                "prompt_file": "the_evidence_purist.md",
                "response_column": "J",
                "evaluation_column": "K",
                "avatar_emoji": "📊",
                "customer_segment": "Healthcare Providers",
                "description": "Demands highest level of clinical evidence. Skeptical of promotional claims and non-peer-reviewed data."
            },
            {
                "name": "The Cost-Conscious Prescriber",
                "display_name": "The Cost-Conscious Prescriber",
                "assistant_id_env": "VAPI_ASSISTANT_ID_6",
                "prompt_file": "the_cost_conscious.md",
                "response_column": "L",
                "evaluation_column": "M",
                "avatar_emoji": "💵",
                "customer_segment": "Healthcare Providers",
                "description": "Operates within systems prioritizing cost containment. Focuses on budget predictability and generic alternatives."
            },
        ]
        
        for config in bot_configs:
            assistant_id = os.getenv(config["assistant_id_env"], "")
            prompt_path = str(self.SEGMENTS_PATH / config["prompt_file"])
            
            bot = BotConfig(
                name=config["name"],
                display_name=config["display_name"],
                assistant_id=assistant_id,
                description=config["description"],
                prompt_file=prompt_path,
                response_column=config["response_column"],
                evaluation_column=config["evaluation_column"],
                avatar_emoji=config["avatar_emoji"],
                customer_segment=config["customer_segment"]
            )
            self._bots[config["name"]] = bot
    
    def get_bot(self, name: str) -> Optional[BotConfig]:
        """Get a bot configuration by name."""
        return self._bots.get(name)
    
    def get_all_bots(self) -> List[BotConfig]:
        """Get all bot configurations."""
        return list(self._bots.values())
    
    def get_configured_bots(self) -> List[BotConfig]:
        """Get only bots that have VAPI assistant IDs configured."""
        return [bot for bot in self._bots.values() if bot.is_configured()]
    
    def get_dataset_path(self, bot_name: str) -> Path:
        """Get the path to a bot's evaluation dataset."""
        # Convert bot name to filename format
        filename = bot_name.lower().replace(" ", "_").replace("-", "_")
        filename = filename.replace("the_", "the_")  # Keep the_ prefix
        return self.DATASETS_PATH / f"{filename}.json"
    
    def get_prompt_path(self, bot_name: str) -> Path:
        """Get the path to a bot's prompt/segment file."""
        bot = self.get_bot(bot_name)
        if bot:
            return Path(bot.prompt_file)
        return None


# Singleton instance for easy access
_config_instance: Optional[EvaluationConfig] = None


def get_config() -> EvaluationConfig:
    """Get the singleton configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = EvaluationConfig()
    return _config_instance


# Export commonly used items
__all__ = [
    'VAPIConfig',
    'BotConfig', 
    'EvaluationConfig',
    'get_config'
]
