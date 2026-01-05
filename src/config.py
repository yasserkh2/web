"""
Configuration
==============
Centralized configuration following Open/Closed Principle.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Paths:
    """File paths configuration."""
    root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    
    @property
    def segments_dir(self) -> Path:
        return self.root / "segments"
    
    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"
    
    @property
    def excel_file(self) -> Path:
        return self.root / "bot_evaluation_with_comments.xlsx"


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str = field(default_factory=lambda: os.environ.get("OPENAI_API_KEY", ""))
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 500
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())


@dataclass
class VAPIConfig:
    """VAPI API configuration."""
    api_key: str = field(default_factory=lambda: os.environ.get("VAPI_API_KEY", ""))
    base_url: str = "https://api.vapi.ai"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())


# Excel column mapping for each segment
# Format: segment_name -> (response_col, eval_col, comment_col)
EXCEL_COLUMNS: Dict[str, Tuple[str, str, str]] = {
    "The Traditionalist": ("B", "C", "D"),
    "The Innovator": ("I", "J", "K"),
    "The Evidence Purist": ("P", "Q", "R"),
}

# Full column headers (A-V)
EXCEL_HEADERS: Dict[str, str] = {
    "A": "Question",
    # The Traditionalist (B-H)
    "B": "The Traditionalist",
    "C": "The Traditionalist Eval",
    "D": "The Traditionalist Comment",
    "E": "The Traditionalist Eval_Aboubakr",
    "F": "The Traditionalist Comment_Aboubakr",
    "G": "The Traditionalist Eval_Thomas",
    "H": "The Traditionalist Comment_Thomas",
    # The Innovator (I-O)
    "I": "The Innovator",
    "J": "The Innovator Eval",
    "K": "The Innovator Comment",
    "L": "The Innovator Eval_Aboubakr",
    "M": "The Innovator Comment_Aboubakr",
    "N": "The Innovator Eval_Thomas",
    "O": "The Innovator Comment_Thomas",
    # The Evidence Purist (P-V)
    "P": "The Evidence Purist",
    "Q": "The Evidence Purist Eval",
    "R": "The Evidence Purist Comment",
    "S": "The Evidence Purist Eval_Aboubakr",
    "T": "The Evidence Purist Comment_Aboubakr",
    "U": "The Evidence Purist Eval_Thomas",
    "V": "The Evidence Purist Comment_Thomas",
}

# Segments to evaluate
SEGMENTS = [
    "The Traditionalist",
    "The Innovator",
    "The Evidence Purist",
]


# Singleton instances
paths = Paths()
openai_config = OpenAIConfig()
vapi_config = VAPIConfig()

