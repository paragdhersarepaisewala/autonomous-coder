import os
from typing import Any, Optional
from dotenv import load_dotenv
from .config import Config


class VertexAIConfig:
    """Configuration manager for Vertex AI settings."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize Vertex AI configuration from environment variables."""
        # Load environment variables from the main config
        self.config = Config(env_file)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a Vertex AI configuration value."""
        # First try to get from the main config with VERTEX_AI_ prefix
        value = self.config.get(f'VERTEX_AI_{key}', default)
        if value is not None:
            return value
        
        # Then try without prefix for backward compatibility
        return self.config.get(key, default)
    
    def get_str(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value as string."""
        value = self.get(key)
        if value is None:
            return default
        return str(value)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a configuration value as boolean."""
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get a configuration value as integer."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a configuration value as float."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default


# Global vertex AI config instance
vertex_ai_config = VertexAIConfig()