import os
from typing import Optional
from .config import config


class GitHubClient:
    """GitHub API client wrapper."""
    
    def __init__(self, token: Optional[str] = None, username: Optional[str] = None):
        """Initialize GitHub client with token and username."""
        self.token = token or config.get('GITHUB_TOKEN')
        self.username = username or config.get('GITHUB_USERNAME')
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN in .env file")
        
        if not self.username:
            raise ValueError("GitHub username is required. Set GITHUB_USERNAME in .env file")
        
        # Validate that token looks like a GitHub token
        if not self.token.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')) and len(self.token) < 20:
            # This is a basic check - real GitHub tokens are more complex
            pass  # We'll let the GitHub library handle validation
    
    def get_auth_header(self) -> dict:
        """Get authorization header for GitHub API requests."""
        return {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }