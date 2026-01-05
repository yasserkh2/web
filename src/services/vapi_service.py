"""
VAPI Service
=============
Handles interaction with VAPI API for getting bot responses.
Single Responsibility: Only VAPI-related operations.
"""

import os
import time
from typing import Optional, Dict, List

import requests

from ..models import Response, Segment
from ..config import vapi_config


# VAPI Assistant IDs from environment
ASSISTANT_IDS: Dict[str, str] = {
    "The Traditionalist": os.environ.get("VAPI_ASSISTANT_ID_1", ""),
    "The Innovator": os.environ.get("VAPI_ASSISTANT_ID_2", ""),
    "The Patient-Centered Physician": os.environ.get("VAPI_ASSISTANT_ID_3", ""),
    "The Financially Driven Prescriber": os.environ.get("VAPI_ASSISTANT_ID_4", ""),
    "The Evidence Purist": os.environ.get("VAPI_ASSISTANT_ID_5", ""),
    "The Cost-Conscious Prescriber": os.environ.get("VAPI_ASSISTANT_ID_6", ""),
}


class VAPIService:
    """Service for interacting with VAPI API."""
    
    def __init__(self):
        self._api_key = vapi_config.api_key
        self._base_url = vapi_config.base_url
    
    @property
    def is_available(self) -> bool:
        """Check if VAPI is configured."""
        return vapi_config.is_configured
    
    def get_assistant_id(self, segment_name: str) -> Optional[str]:
        """Get the VAPI assistant ID for a segment."""
        return ASSISTANT_IDS.get(segment_name)
    
    def get_response(self, segment_name: str, question: str, question_id: int = 0) -> Response:
        """
        Get a response from VAPI for a given question using chat API.
        
        Args:
            segment_name: The segment/persona to use
            question: The question to ask
            question_id: ID for tracking
            
        Returns:
            Response object with the assistant's response
        """
        assistant_id = self.get_assistant_id(segment_name)
        
        if not assistant_id:
            return Response(
                segment=segment_name,
                question_id=question_id,
                question_text=question,
                response_text="[No VAPI assistant configured for this segment]",
                source="error"
            )
        
        if not self.is_available:
            return Response(
                segment=segment_name,
                question_id=question_id,
                question_text=question,
                response_text="[VAPI API not configured]",
                source="error"
            )
        
        try:
            # Use VAPI chat endpoint to get text response
            response = requests.post(
                f"{self._base_url}/chat",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "assistantId": assistant_id,
                    "input": question
                },
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                # Extract assistant response - try multiple fields
                assistant_response = (
                    data.get("output") or 
                    data.get("message") or 
                    data.get("content") or
                    data.get("response") or
                    data.get("text") or
                    ""
                )
                
                # Handle different response formats
                if isinstance(assistant_response, dict):
                    assistant_response = assistant_response.get("content", str(assistant_response))
                elif isinstance(assistant_response, list):
                    # If it's a list of messages, get the last assistant message
                    for msg in reversed(assistant_response):
                        if isinstance(msg, dict) and msg.get("role") == "assistant":
                            assistant_response = msg.get("content", "")
                            break
                    else:
                        assistant_response = str(assistant_response)
                
                # If still empty, return the full response for debugging
                if not assistant_response:
                    return Response(
                        segment=segment_name,
                        question_id=question_id,
                        question_text=question,
                        response_text=f"[VAPI returned empty - raw: {str(data)[:200]}]",
                        source="error"
                    )
                
                return Response(
                    segment=segment_name,
                    question_id=question_id,
                    question_text=question,
                    response_text=str(assistant_response),
                    source="vapi"
                )
            else:
                return Response(
                    segment=segment_name,
                    question_id=question_id,
                    question_text=question,
                    response_text=f"[VAPI Error: {response.status_code} - {response.text[:100]}]",
                    source="error"
                )
                
        except requests.exceptions.Timeout:
            return Response(
                segment=segment_name,
                question_id=question_id,
                question_text=question,
                response_text="[VAPI Timeout - request took too long]",
                source="error"
            )
        except Exception as e:
            return Response(
                segment=segment_name,
                question_id=question_id,
                question_text=question,
                response_text=f"[VAPI Error: {str(e)[:100]}]",
                source="error"
            )
    
    def get_call_transcript(self, call_id: str) -> Optional[str]:
        """
        Fetch transcript from a completed VAPI call.
        
        Args:
            call_id: The VAPI call ID
            
        Returns:
            The call transcript or None
        """
        if not self.is_available:
            return None
        
        try:
            response = requests.get(
                f"{self._base_url}/call/{call_id}",
                headers={"Authorization": f"Bearer {self._api_key}"}
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("transcript", "")
            
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None
    
    def list_recent_calls(self, limit: int = 10) -> List[dict]:
        """
        List recent calls from VAPI.
        
        Args:
            limit: Maximum number of calls to fetch
            
        Returns:
            List of call data dictionaries
        """
        if not self.is_available:
            return []
        
        try:
            response = requests.get(
                f"{self._base_url}/call",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error listing calls: {e}")
            return []

