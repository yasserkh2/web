"""
LLM Evaluator
=============
Uses Large Language Models (GPT, Claude, etc.) to evaluate bot responses.
Follows Single Responsibility: Only handles LLM-based evaluation.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseEvaluator
from ..models import BotResponse, EvaluationResult, Question
from ..config import BotConfig, LLMConfig


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
        criteria = criteria or self.get_default_criteria()
        criteria_list = "\n".join([f"- {k}: {v*100:.0f}%" for k, v in criteria.items()])
        
        return f"""You are an expert evaluator assessing AI healthcare bot responses.

## Bot Being Evaluated
- Name: {bot_config.name}
- Persona: {bot_config.description}

## Evaluation Question
{question.text}

## Bot's Response
{response.response_text}

## Evaluation Criteria (with weights)
{criteria_list}

## Instructions
1. Evaluate the response against each criterion
2. Consider how well the response aligns with the bot's persona
3. Assess medical accuracy and appropriateness
4. Provide an overall score from 0-10

## Required Output Format
Score: [0-10]
Criteria Scores: accuracy=[0-10], persona_alignment=[0-10], tone=[0-10], clarity=[0-10], completeness=[0-10]
Evaluation: [2-3 sentence evaluation explaining the score]
"""
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        client = self._get_client()
        
        if self.config.provider == "openai":
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert medical AI evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
    
    def _parse_llm_response(self, llm_response: str) -> tuple:
        """
        Parse the LLM response to extract score, evaluation, and criteria scores.
        
        Returns:
            Tuple of (score, evaluation_text, criteria_scores)
        """
        score = None
        evaluation_text = llm_response
        criteria_scores = {}
        
        lines = llm_response.strip().split("\n")
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Extract main score
            if line_lower.startswith("score:"):
                try:
                    score_str = line.split(":")[1].strip()
                    # Handle formats like "8/10" or "8"
                    if "/" in score_str:
                        score_str = score_str.split("/")[0]
                    score = float(score_str)
                except (ValueError, IndexError):
                    pass
            
            # Extract criteria scores
            elif line_lower.startswith("criteria scores:"):
                try:
                    scores_part = line.split(":", 1)[1].strip()
                    # Parse format: accuracy=8, persona_alignment=7, ...
                    for item in scores_part.split(","):
                        if "=" in item:
                            key, value = item.split("=")
                            criteria_scores[key.strip()] = float(value.strip())
                except (ValueError, IndexError):
                    pass
            
            # Extract evaluation text
            elif line_lower.startswith("evaluation:"):
                evaluation_text = line.split(":", 1)[1].strip()
        
        return score, evaluation_text, criteria_scores

