import os
import logging
from typing import Optional, Dict, Any
from google import genai
from ..utils.config import config


class VertexAIClient:
    """Client for interacting with Vertex AI Gemini models."""
    
    def __init__(self):
        """Initialize the Vertex AI client."""
        self.logger = logging.getLogger(__name__)
        self.project_id = config.get('VERTEX_AI_PROJECT_ID')
        self.location = config.get('VERTEX_AI_LOCATION', 'us-central1')
        self.model_name = config.get('VERTEX_AI_MODEL', 'gemini-pro')
        self.credentials_path = config.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Set up authentication if credentials file is specified
        if self.credentials_path and os.path.exists(self.credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            self.logger.info(f"Using Google credentials from {self.credentials_path}")
        
        # Set up Vertex AI environment variables
        if self.project_id:
            os.environ['GOOGLE_CLOUD_PROJECT'] = self.project_id
        if self.location:
            os.environ['GOOGLE_CLOUD_LOCATION'] = self.location
        os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'true'
        
        # Initialize the client
        try:
            self.client = genai.Client()
            self.logger.info(f"Initialized Vertex AI client for project {self.project_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vertex AI client: {e}")
            raise
    
    def generate_content(self, 
                        prompt: str, 
                        temperature: float = 0.7,
                        max_output_tokens: int = 2048) -> Optional[str]:
        """Generate content using the Gemini model."""
        try:
            self.logger.info(f"Generating content with model {self.model_name}")
            
            # Generate content using a dict for config
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
                self.logger.warning("Empty response from Vertex AI")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating content with Vertex AI: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if the Vertex AI client is properly configured and available."""
        try:
            # Check if required configuration is present
            if not self.project_id:
                self.logger.warning("Vertex AI project ID not configured")
                return False
            
            # Try a simple generation to verify connectivity
            # We'll use a minimal prompt to avoid wasting tokens
            test_response = self.generate_content(
                "Say 'OK' if you can hear me.",
                temperature=0.1,
                max_output_tokens=10
            )
            
            return test_response is not None and len(test_response) > 0
        except Exception as e:
            self.logger.error(f"Vertex AI availability check failed: {e}")
            return False