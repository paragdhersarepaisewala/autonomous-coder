import os
from typing import Any, List, Optional, Union
from dotenv import load_dotenv


class Config:
    """Configuration manager for the autonomous agent."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialize configuration from environment variables."""
        self.env_file = env_file
        self.config_cache = {}
        
        # Load environment variables
        if os.path.exists(env_file):
            load_dotenv(env_file)
            # Cache the loaded values for easier saving
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.config_cache[key.strip()] = value.strip()
        else:
            # Create a default .env file if it doesn't exist
            self._create_default_env(env_file)
            load_dotenv(env_file)
    
    def _create_default_env(self, env_file: str):
        """Create a default .env file with placeholder values."""
        default_content = """# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username_here

# Agent Behavior Settings
TARGET_LANGUAGE=Python
TARGET_CONTRIBUTIONS=3
FEATURE_TYPE=utility
MIN_STARS=10
MAX_STARS=1000
EXCLUDED_TOPICS=

# Timing Settings (in seconds)
CYCLE_DELAY=1800
RETRY_DELAY=300
"""
        
        with open(env_file, 'w') as f:
            f.write(default_content)
        
        print(f"Created default configuration file at {env_file}")
        print("Please edit it to add your GitHub token and username")
        
        # Parse default content into cache
        for line in default_content.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                self.config_cache[key.strip()] = value.strip()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        # Use cache if available, otherwise fallback to os.getenv
        value = self.config_cache.get(key)
        if value is None:
            value = os.getenv(key)
        if value is None:
            return default
        return value

    def set(self, key: str, value: Any):
        """Update a configuration value in cache."""
        self.config_cache[key] = str(value)
        # Also update environment variable so it's reflected in current process
        os.environ[key] = str(value)

    def save(self):
        """Save the current configuration cache back to the .env file."""
        new_lines = []
        existing_keys = set()
        
        # Read existing file to preserve comments and structure if possible
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        key = stripped.split('=', 1)[0].strip()
                        if key in self.config_cache:
                            new_lines.append(f"{key}={self.config_cache[key]}\n")
                            existing_keys.add(key)
                            continue
                    new_lines.append(line)
        
        # Add any new keys that weren't in the original file
        for key, value in self.config_cache.items():
            if key not in existing_keys:
                new_lines.append(f"{key}={value}\n")
        
        with open(self.env_file, 'w') as f:
            f.writelines(new_lines)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get a configuration value as integer."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a configuration value as float."""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a configuration value as boolean."""
        value = self.get(key)
        if value is None:
            return default
        return str(value).lower() in ('true', '1', 'yes', 'on')
    
    def get_list(self, key: str, default: Optional[List[str]] = None) -> List[str]:
        """Get a configuration value as list (comma-separated)."""
        if default is None:
            default = []
        value = self.get(key)
        if value is None:
            return default
        return [item.strip() for item in str(value).split(',') if item.strip()]


# Global config instance
config = Config()