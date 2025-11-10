"""
LLM Integration Layer - Interface for various LLM providers
"""

import os
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # For future local model support


class LLMMessage(BaseModel):
    """A message in the LLM conversation"""
    role: str  # "system", "user", "assistant"
    content: str


class LLMClient:
    """Client for interacting with LLM providers"""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Set model based on provider if not specified
        if model is None:
            if provider == LLMProvider.OPENAI:
                model = "gpt-4"
            elif provider == LLMProvider.ANTHROPIC:
                model = "claude-3-opus-20240229"
            else:
                model = "local"
        
        self.model = model
        
        # Initialize provider clients
        if provider == LLMProvider.OPENAI:
            if openai is None:
                raise ImportError("openai package is required for OpenAI provider")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.client = openai.OpenAI(api_key=api_key)
        
        elif provider == LLMProvider.ANTHROPIC:
            if anthropic is None:
                raise ImportError("anthropic package is required for Anthropic provider")
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.client = anthropic.Anthropic(api_key=api_key)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM"""
        if self.provider == LLMProvider.OPENAI:
            return self._generate_openai(messages, system_prompt, **kwargs)
        elif self.provider == LLMProvider.ANTHROPIC:
            return self._generate_anthropic(messages, system_prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_openai(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate using OpenAI"""
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    def _generate_anthropic(
        self,
        messages: List[LLMMessage],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate using Anthropic"""
        formatted_messages = []
        
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        response = self.client.messages.create(
            model=self.model,
            messages=formatted_messages,
            system=system_prompt or "",
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.content[0].text
    
    def reason(
        self,
        query: str,
        context: List[str],
        available_skills: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Reason about a query and determine what actions to take"""
        context_text = "\n".join([f"- {c}" for c in context])
        skills_text = "\n".join([
            f"- {s['name']}: {s['description']}" for s in available_skills
        ])
        
        system_prompt = """You are a reasoning agent that helps users accomplish tasks.
You have access to a memory graph with context and a set of skills (actions) you can execute.

Your job is to:
1. Understand the user's intent
2. Determine which skills to use
3. Extract parameters for those skills
4. Provide a clear reasoning for your decisions

Respond in JSON format with:
{
    "reasoning": "Your reasoning process",
    "intent": "What the user wants to accomplish",
    "skills": [
        {
            "name": "skill_name",
            "params": {"param1": "value1"}
        }
    ],
    "response": "Natural language response to the user"
}
"""
        
        user_message = f"""User Query: {query}

Available Context:
{context_text}

Available Skills:
{skills_text}

Analyze the query and determine what actions to take."""
        
        messages = [LLMMessage(role="user", content=user_message)]
        
        try:
            response = self.generate(messages, system_prompt=system_prompt)
            # Try to parse JSON from response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                return {
                    "reasoning": response,
                    "intent": query,
                    "skills": [],
                    "response": response
                }
        except Exception as e:
            return {
                "reasoning": f"Error during reasoning: {str(e)}",
                "intent": query,
                "skills": [],
                "response": "I encountered an error while processing your request."
            }


