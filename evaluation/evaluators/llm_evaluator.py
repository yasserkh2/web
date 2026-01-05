"""
LLM Evaluator
=============
Uses Large Language Models (GPT, Claude, etc.) to evaluate bot responses.
Follows Single Responsibility: Only handles LLM-based evaluation.
"""

import os
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseEvaluator
from ..models import BotResponse, EvaluationResult, Question
from ..config import BotConfig, LLMConfig

# Path to segments folder
SEGMENTS_DIR = Path(__file__).parent.parent.parent / "segments"


class LLMEvaluator(BaseEvaluator):
    """
    Evaluator that uses LLM (OpenAI, Anthropic, etc.) to assess responses.
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(name="llm")
        self.config = config or LLMConfig()
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of the API client."""
        if self._client is None:
            if self.config.provider == "openai":
                try:
                    from openai import OpenAI
                    self._client = OpenAI(api_key=self.config.api_key)
                except ImportError:
                    raise ImportError("openai package not installed. Run: pip install openai")
            # Add other providers here (anthropic, etc.)
        return self._client
    
    def is_available(self) -> bool:
        """Check if the LLM API is configured."""
        return bool(self.config.api_key and self.config.api_key.strip())
    
    def _load_segment_description(self, bot_name: str) -> dict:
        """
        Load segment description from the segments folder.
        
        Args:
            bot_name: Name of the bot/segment (e.g., "The Innovator")
            
        Returns:
            Dictionary with segment information
        """
        # Convert bot name to filename format (e.g., "The Innovator" -> "the_innovator.md")
        filename = bot_name.lower().replace(" ", "_").replace("-", "_") + ".md"
        segment_path = SEGMENTS_DIR / filename
        
        segment_data = {
            "name": bot_name,
            "description": "",
            "traits": [],
            "behavioral_patterns": [],
            "speech_markers": []
        }
        
        if segment_path.exists():
            try:
                content = segment_path.read_text(encoding="utf-8")
                
                # Truncate description to reduce token usage (max ~1500 chars for low rate limits)
                max_desc_length = 1500
                if len(content) > max_desc_length:
                    segment_data["description"] = content[:max_desc_length] + "\n...[truncated]"
                else:
                    segment_data["description"] = content
                
                # Extract key traits from the markdown content
                lines = content.split("\n")
                for line in lines:
                    # Look for bullet points with key traits
                    if line.strip().startswith("•") or line.strip().startswith("-"):
                        trait = line.strip().lstrip("•-").strip()
                        if trait and len(trait) < 200:
                            segment_data["traits"].append(trait)
                            if len(segment_data["traits"]) >= 10:  # Limit traits
                                break
                            
            except Exception as e:
                segment_data["description"] = f"Error loading segment: {str(e)}"
        else:
            segment_data["description"] = f"Segment file not found: {filename}"
            
        return segment_data
    
    def evaluate(
        self,
        response: BotResponse,
        bot_config: BotConfig,
        question: Question,
        criteria: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate a response using LLM.
        
        Args:
            response: The bot's response to evaluate
            bot_config: Configuration of the bot
            question: The question asked
            criteria: Optional custom criteria
            
        Returns:
            EvaluationResult with LLM-generated evaluation
        """
        if not self.is_available():
            return EvaluationResult(
                bot_name=response.bot_name,
                question_index=response.question_index,
                response=response,
                score=None,
                evaluation_text="[LLM not configured - API key missing]",
                evaluator_type=self.name
            )
        
        if response.is_empty():
            return EvaluationResult(
                bot_name=response.bot_name,
                question_index=response.question_index,
                response=response,
                score=0,
                evaluation_text="[No response to evaluate]",
                evaluator_type=self.name
            )
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(response, bot_config, question, criteria)
        
        try:
            # Call LLM
            result = self._call_llm(prompt)
            
            # Parse result
            score, evaluation_text, criteria_scores = self._parse_llm_response(result)
            
            return EvaluationResult(
                bot_name=response.bot_name,
                question_index=response.question_index,
                response=response,
                score=score,
                evaluation_text=evaluation_text,
                criteria_scores=criteria_scores,
                evaluator_type=self.name,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return EvaluationResult(
                bot_name=response.bot_name,
                question_index=response.question_index,
                response=response,
                score=None,
                evaluation_text=f"[Evaluation error: {str(e)}]",
                evaluator_type=self.name
            )
    
    def _build_evaluation_prompt(
        self,
        response: BotResponse,
        bot_config: BotConfig,
        question: Question,
        criteria: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the evaluation prompt for the LLM."""
        # Load full segment description from segments folder
        segment_data = self._load_segment_description(bot_config.name)
        segment_json = json.dumps(segment_data, indent=2, ensure_ascii=False)
        
        return f"""You are a strict evaluator. Judge whether the assistant's response matches the target doctor segment.

SEGMENT:
{segment_json}

USER MESSAGE:
{question.text}

ASSISTANT RESPONSE TO EVALUATE:
{response.response_text}

SCORING (0-5):
- 0 = not the segment at all
- 1 = mostly wrong, few weak hints
- 2 = mixed, clear drift into other segments
- 3 = acceptable but inconsistent / noticeable leaks
- 4 = strong match with minor issues
- 5 = perfect, no leaks

RULES:
- If score <= 3, comment MUST include: what's wrong and how to fix it
- If score >= 4, comment should briefly explain why it matches well
- Keep comment concise (max 100 words)

OUTPUT FORMAT (JSON only):
{{"score": <0-5>, "comment": "<explanation>"}}
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        client = self._get_client()
        
        if self.config.provider == "openai":
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a strict segment evaluator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        
        raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _parse_llm_response(self, llm_response: str) -> tuple:
        """
        Parse the LLM response JSON: {"score": <0-5>, "comment": "<text>"}
        
        Returns:
            Tuple of (score, comment, criteria_scores)
        """
        score = None
        comment = ""
        criteria_scores = {}
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
            else:
                data = json.loads(llm_response)
            
            # Extract score (0-5 scale)
            score = data.get("score", 0)
            comment = data.get("comment", "")
            
            # Store raw data
            criteria_scores = {
                "score": score,
                "comment": comment,
                "_raw_evaluation": data
            }
            
        except json.JSONDecodeError:
            # Fallback: try to extract score from text
            comment = llm_response
            score_match = re.search(r'"?score"?\s*:\s*(\d+)', llm_response)
            if score_match:
                score = int(score_match.group(1))
        
        return score, comment, criteria_scores




