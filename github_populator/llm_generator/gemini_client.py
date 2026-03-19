import os
import logging
from typing import Optional, Dict, Any
from google import genai
from ..utils.config import config


class GeminiAIClient:
    """Client for interacting with Google Gemini AI models using direct API key."""
    
    def __init__(self):
        """Initialize the Gemini AI client."""
        self.logger = logging.getLogger(__name__)
        
        # Get configuration
        self.api_key = config.get('GEMINI_API_KEY')
        self.model_name = config.get('GEMINI_MODEL', 'gemini-2.5-flash')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Please set it in the .env file.")
        
        # Initialize the client with the API key
        try:
            self.client = genai.Client(api_key=self.api_key)
            self.logger.info(f"Initialized Gemini AI client with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI client: {e}")
            raise
    
    def generate_content(self, 
                        prompt: str, 
                        temperature: float = 0.7,
                        max_output_tokens: int = 8192) -> Optional[str]:
        """Generate content using the Gemini model."""
        try:
            self.logger.info(f"Generating content with model {self.model_name}")
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )
            
            if response and response.text:
                self.logger.info("Successfully generated content")
                return response.text.strip()
            else:
                self.logger.warning("Empty response from Gemini AI")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating content with Gemini AI: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the Gemini AI client is properly configured and available."""
        try:
            if not self.api_key:
                self.logger.warning("Gemini API key not configured")
                return False
            
            # Try a simple generation to verify connectivity
            test_response = self.generate_content(
                "Say 'OK' if you can hear me.",
                temperature=0.1,
                max_output_tokens=50
            )
            
            if test_response and len(test_response) > 0:
                self.logger.info("Gemini AI client is available")
                return True
            else:
                self.logger.warning("Gemini AI returned empty response")
                return False
                
        except Exception as e:
            self.logger.error(f"Gemini AI availability check failed: {e}")
            return False
