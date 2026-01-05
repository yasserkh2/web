"""
Bot Service
===========
Handles interaction with AI bots via VAPI.
Follows Single Responsibility: Only handles bot communication.
"""

import os
import requests
from typing import Optional, List
from datetime import datetime

from ..models import Bot, BotResponse, Question
from ..config import BotConfig, VAPIConfig


class BotService:
    """
    Service for interacting with AI bots via VAPI.
    
    Responsibilities:
    - Send questions to bots
    - Retrieve responses
    - Manage bot connections
    """
    
    def __init__(self, vapi_config: Optional[VAPIConfig] = None):
        self.config = vapi_config or VAPIConfig()
    
    def is_configured(self) -> bool:
        """Check if VAPI is properly configured."""
        return bool(
            self.config.api_key and 
            self.config.api_key.strip() and
            self.config.api_key != "your_api_key"
        )
    
    def get_bot(self, bot_config: BotConfig) -> Bot:
        """Create a Bot instance from configuration."""
        return Bot(
            name=bot_config.name,
            assistant_id=bot_config.assistant_id,
            description=bot_config.description
        )
    
    def send_question(
        self,
        bot_config: BotConfig,
        question: Question
    ) -> BotResponse:
        """
        Send a question to a bot and get the response.
        
        Args:
            bot_config: Configuration of the bot to query
            question: The question to ask
            
        Returns:
            BotResponse with the bot's answer
        """
        if not bot_config.assistant_id:
            return BotResponse(
                bot_name=bot_config.name,
                question_index=question.index,
                question_text=question.text,
                response_text="[No assistant ID configured]"
            )
        
        if not self.is_configured():
            # Generate mock response based on persona using LLM
            mock_response = self.generate_mock_response(bot_config, question)
            return BotResponse(
                bot_name=bot_config.name,
                question_index=question.index,
                question_text=question.text,
                response_text=mock_response,
                timestamp=datetime.now()
            )
        
        # TODO: Implement actual VAPI API call
        # For now, return placeholder
        # 
        # When implementing VAPI:
        # 1. Create a conversation/call
        # 2. Send the question via the assistant
        # 3. Wait for and capture the response
        # 4. Return the transcript
        
        try:
            response_text = self._call_vapi(bot_config, question)
            return BotResponse(
                bot_name=bot_config.name,
                question_index=question.index,
                question_text=question.text,
                response_text=response_text,
                timestamp=datetime.now()
            )
        except Exception as e:
            return BotResponse(
                bot_name=bot_config.name,
                question_index=question.index,
                question_text=question.text,
                response_text=f"[Error: {str(e)}]"
            )
    
    def _call_vapi(self, bot_config: BotConfig, question: Question) -> str:
        """
        Make actual VAPI API call to get response from assistant.
        
        Uses VAPI's chat endpoint to send text and get responses.
        """
        try:
            url = f"{self.config.base_url}/chat"
            
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # VAPI chat API format
            payload = {
                "assistantId": bot_config.assistant_id,
                "input": question.text
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # 200 or 201 are both success
            if response.status_code in [200, 201]:
                data = response.json()
                # Extract the assistant's response text
                if isinstance(data, dict):
                    # Try different response formats based on VAPI's response structure
                    
                    # Check for output field (main response)
                    if "output" in data:
                        output = data["output"]
                        if isinstance(output, list) and len(output) > 0:
                            # Output is array of messages
                            for msg in output:
                                if isinstance(msg, dict) and msg.get("role") == "assistant":
                                    return msg.get("content", str(msg))
                            # Return last message if no assistant role found
                            last_msg = output[-1]
                            if isinstance(last_msg, dict):
                                return last_msg.get("content", str(last_msg))
                            return str(last_msg)
                        elif isinstance(output, str):
                            return output
                        return str(output)
                    
                    # Check for messages array
                    elif "messages" in data:
                        messages = data["messages"]
                        if isinstance(messages, list):
                            for msg in reversed(messages):
                                if isinstance(msg, dict) and msg.get("role") == "assistant":
                                    return msg.get("content", str(msg))
                    
                    # Other possible fields
                    elif "message" in data:
                        msg = data["message"]
                        if isinstance(msg, dict):
                            return msg.get("content", str(msg))
                        return str(msg)
                    elif "response" in data:
                        return str(data["response"])
                    elif "text" in data:
                        return data["text"]
                    elif "content" in data:
                        return data["content"]
                    elif "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        if "message" in choice:
                            return choice["message"].get("content", "")
                        return str(choice)
                    
                    # Return full response for debugging if no known format
                    return f"[VAPI Response: {str(data)[:500]}]"
                return str(data)
            else:
                error_text = response.text[:200] if len(response.text) > 200 else response.text
                return f"[VAPI Error {response.status_code}: {error_text}]"
                
        except requests.exceptions.Timeout:
            return "[VAPI Timeout - request took too long]"
        except requests.exceptions.RequestException as e:
            return f"[VAPI Request Error: {str(e)}]"
        except Exception as e:
            return f"[VAPI Error: {str(e)}]"
    
    def generate_mock_response(self, bot_config: BotConfig, question: Question) -> str:
        """
        Generate a simulated response based on the bot's persona.
        Uses OpenAI if available, otherwise returns a placeholder.
        """
        try:
            from openai import OpenAI
            import os
            
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                return f"[Mock response for {bot_config.name} - configure OPENAI_API_KEY for actual responses]"
            
            client = OpenAI(api_key=api_key)
            
            # Build persona prompt
            persona_prompts = {
                "The Traditionalist": """You are "The Traditionalist" physician. You:
- Rely on established, well-documented, time-tested treatments
- Are skeptical of new drugs without extensive long-term real-world data
- Value landmark clinical trials and "gold standard" treatments
- Are heavily influenced by established KOLs and major medical society guidelines
- Resist change unless there's overwhelming evidence of superiority
- Your motto: "If it isn't broken, don't fix it"
Keep responses concise (2-4 sentences), natural, and in character.""",

                "The Innovator": """You are "The Innovator" physician. You:
- Are eager to adopt cutting-edge therapies with novel mechanisms
- Want to be at the forefront of medical advancement
- Actively seek info on new drugs at conferences and journals
- Are open to meeting sales reps for deep scientific discussions
- Are less price-sensitive if clinical benefit is substantial
- Driven by scientific curiosity and desire to lead your field
Keep responses concise (2-4 sentences), natural, and in character.""",

                "The Evidence Purist": """You are "The Evidence Purist" physician. You:
- Demand the highest level of clinical evidence
- Are skeptical of promotional claims and non-peer-reviewed data
- Rank systematic reviews and meta-analyses (Cochrane) as highest evidence
- Prefer head-to-head comparative trials over placebo-controlled studies
- Focus on hard clinical endpoints over surrogate markers
- Wait for broad evidence base before adopting new treatments
Keep responses concise (2-4 sentences), natural, and in character."""
            }
            
            system_prompt = persona_prompts.get(
                bot_config.name, 
                f"You are a physician named {bot_config.name}. {bot_config.description}"
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question.text}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            return f"[Install openai package: pip install openai]"
        except Exception as e:
            return f"[Error generating response: {str(e)}]"
    
    def send_questions_batch(
        self,
        bot_config: BotConfig,
        questions: List[Question]
    ) -> List[BotResponse]:
        """
        Send multiple questions to a bot.
        
        Args:
            bot_config: Configuration of the bot
            questions: List of questions to ask
            
        Returns:
            List of BotResponse objects
        """
        responses = []
        for question in questions:
            response = self.send_question(bot_config, question)
            responses.append(response)
        return responses
    
    def validate_bot_connection(self, bot_config: BotConfig) -> dict:
        """
        Validate that we can connect to a bot.
        
        Returns:
            Dictionary with 'success' boolean and 'message' string
        """
        if not bot_config.assistant_id:
            return {
                "success": False,
                "message": f"No assistant ID configured for {bot_config.name}"
            }
        
        if not self.is_configured():
            return {
                "success": False,
                "message": "VAPI API key not configured"
            }
        
        # TODO: Actually test the connection
        return {
            "success": True,
            "message": f"Bot {bot_config.name} is configured (ID: {bot_config.assistant_id[:20]}...)"
        }




