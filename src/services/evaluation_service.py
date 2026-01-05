"""
Evaluation Service
===================
Handles LLM-based evaluation of responses.
Single Responsibility: Only evaluation logic.
Dependency Inversion: Depends on abstractions (SegmentService).
"""

import json
import re
from typing import Optional

from openai import OpenAI

from ..models import Response, Evaluation
from ..config import openai_config
from .segment_service import SegmentService


class EvaluationService:
    """Service for evaluating bot responses using LLM."""
    
    def __init__(self, segment_service: Optional[SegmentService] = None):
        self.segment_service = segment_service or SegmentService()
        self._client: Optional[OpenAI] = None
    
    @property
    def is_available(self) -> bool:
        """Check if OpenAI is configured."""
        return openai_config.is_configured
    
    def _get_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            self._client = OpenAI(api_key=openai_config.api_key)
        return self._client
    
    def evaluate(self, response: Response) -> Evaluation:
        """
        Evaluate a response against its segment.
        
        Args:
            response: The Response object to evaluate
            
        Returns:
            Evaluation with score and comment
        """
        if not self.is_available:
            return Evaluation(
                segment=response.segment,
                question_id=response.question_id,
                score=0,
                comment="[LLM not configured - API key missing]",
                evaluator="llm"
            )
        
        if response.is_empty:
            return Evaluation(
                segment=response.segment,
                question_id=response.question_id,
                score=0,
                comment="[No response to evaluate]",
                evaluator="llm"
            )
        
        # Build prompt
        prompt = self._build_prompt(response)
        
        try:
            # Call LLM
            result = self._call_llm(prompt)
            
            # Parse result
            score, comment = self._parse_response(result)
            
            return Evaluation(
                segment=response.segment,
                question_id=response.question_id,
                score=score,
                comment=comment,
                evaluator="llm"
            )
            
        except Exception as e:
            return Evaluation(
                segment=response.segment,
                question_id=response.question_id,
                score=0,
                comment=f"[Error: {str(e)[:100]}]",
                evaluator="llm"
            )
    
    def _build_prompt(self, response: Response) -> str:
        """Build the evaluation prompt."""
        segment_json = self.segment_service.get_segment_json(response.segment)
        segment_str = json.dumps(segment_json, indent=2, ensure_ascii=False)
        
        return f"""You are a strict evaluator. Judge whether the assistant's response matches the target doctor segment.

SEGMENT:
{segment_str}

USER MESSAGE:
{response.question_text}

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
        """Call the OpenAI API."""
        client = self._get_client()
        
        model = openai_config.model
        
        # o4-mini and o1 models don't support response_format or temperature
        if model.startswith("o4") or model.startswith("o1"):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": f"You are a strict segment evaluator. Respond with valid JSON only.\n\n{prompt}"}
                ]
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a strict segment evaluator. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=openai_config.temperature,
                max_tokens=openai_config.max_tokens,
                response_format={"type": "json_object"}
            )
        
        return response.choices[0].message.content
    
    def _parse_response(self, llm_response: str) -> tuple:
        """Parse LLM response to extract score and comment."""
        try:
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(llm_response)
            
            score = int(data.get("score", 0))
            comment = str(data.get("comment", ""))
            
            return score, comment
            
        except (json.JSONDecodeError, ValueError):
            # Fallback: try regex
            score_match = re.search(r'"?score"?\s*:\s*(\d+)', llm_response)
            score = int(score_match.group(1)) if score_match else 0
            return score, llm_response[:200]

