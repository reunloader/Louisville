"""
AI Service
Handles AI integration with Gemini and OpenAI for chatbot responses.
"""

import os
from typing import Optional
from openai import OpenAI
import google.generativeai as genai


class AIService:
    def __init__(self, provider: str = "gemini"):
        """
        Initialize AI service with specified provider.

        Args:
            provider: Either "gemini" or "openai"
        """
        self.provider = provider.lower()

        if self.provider == "gemini":
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✓ Initialized Gemini AI")

        elif self.provider == "openai":
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            print("✓ Initialized OpenAI")

        else:
            raise ValueError(f"Unknown AI provider: {provider}. Use 'gemini' or 'openai'")

    def generate_response(self, user_message: str, scanner_data: str, conversation_history: list = None) -> str:
        """
        Generate a chatbot response based on user message and scanner data.

        Args:
            user_message: The user's question
            scanner_data: Formatted scanner update data
            conversation_history: Previous messages for context

        Returns:
            AI-generated response
        """
        system_prompt = self._build_system_prompt(scanner_data)

        if self.provider == "gemini":
            return self._generate_gemini_response(system_prompt, user_message, conversation_history)
        elif self.provider == "openai":
            return self._generate_openai_response(system_prompt, user_message, conversation_history)

    def _build_system_prompt(self, scanner_data: str) -> str:
        """Build the system prompt with scanner data context."""
        return f"""You are a helpful assistant for Derby City Watch, a real-time public safety monitoring service for Louisville, Kentucky. You help users find information about recent emergency incidents, traffic, police activity, fire responses, and medical calls in the Louisville area.

Your data comes from live police, fire, and EMS scanner traffic. You have access to the most recent scanner updates below.

**Important Guidelines:**
- Be conversational and helpful
- When asked about locations, search for mentions of street names, neighborhoods, or landmarks
- When asked about routes or traffic between two locations, look for traffic incidents, accidents, or road closures near those areas
- Provide specific incident details including location, time, and status when available
- If you don't find relevant information, say so clearly
- Include disclaimers that this is based on scanner traffic and may not be comprehensive
- Use casual, friendly language while being informative
- Cite the date/time of incidents you reference

**Available Scanner Data:**

{scanner_data}

Remember: Focus on being helpful and accurate. If a user asks about a location or route and you don't find anything in the data, clearly state that there are no recent incidents reported in the scanner data for that area."""

    def _generate_gemini_response(self, system_prompt: str, user_message: str, conversation_history: list = None) -> str:
        """Generate response using Gemini."""
        try:
            # Gemini handles conversation history differently
            # We'll combine system prompt + history + user message
            full_prompt = system_prompt + "\n\n"

            if conversation_history:
                for msg in conversation_history[-6:]:  # Last 3 exchanges
                    role = "User" if msg['role'] == 'user' else "Assistant"
                    full_prompt += f"{role}: {msg['content']}\n\n"

            full_prompt += f"User: {user_message}\n\nAssistant:"

            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            print(f"Gemini error: {e}")
            return f"I'm having trouble processing your request right now. Error: {str(e)}"

    def _generate_openai_response(self, system_prompt: str, user_message: str, conversation_history: list = None) -> str:
        """Generate response using OpenAI."""
        try:
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 3 exchanges

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"OpenAI error: {e}")
            return f"I'm having trouble processing your request right now. Error: {str(e)}"

    def switch_provider(self, new_provider: str):
        """Switch to a different AI provider."""
        self.__init__(new_provider)
