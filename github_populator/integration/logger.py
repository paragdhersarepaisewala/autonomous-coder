import logging
import os
from typing import Dict, Any, Optional
from github import Github, GithubException
from ..utils.github_client import GitHubClient
from ..utils.config import Config


class ActivityLogger:
    """Logs agent activities to the user's autonomous-coder repository."""
    
    def __init__(self, github_client: GitHubClient):
        """Initialize the activity logger."""
        self.github_client = github_client
        self.logger = logging.getLogger(__name__)
        self.github = Github(github_client.token)
        self.config = Config()
        
        # Get target repository for logging
        self.target_repo_name = self.config.get('TARGET_REPO', 'paragdhersarepaisewala/autonomous-coder')
        self.target_repo = None
        self._init_target_repo()
    
    def _init_target_repo(self):
        """Initialize the target repository for logging activities."""
        try:
            self.target_repo = self.github.get_repo(self.target_repo_name)
            self.logger.info(f"Connected to target repository: {self.target_repo_name}")
        except GithubException as e:
            self.logger.error(f"Failed to connect to target repository {self.target_repo_name}: {e}")
            self.target_repo = None
        except Exception as e:
            self.logger.error(f"Error initializing target repository: {e}")
            self.target_repo = None
    
    def log_contribution(self, 
                        repository: Dict[str, Any],
                        feature_idea: Dict[str, Any],
                        pull_request_url: str,
                        forked_repo: Dict[str, Any]) -> bool:
        """Log a contribution to the target repository."""
        try:
            if not self.target_repo:
                self.logger.warning("Target repository not available for logging")
                return False
            
            self.logger.info(f"Logging contribution to {self.target_repo_name}")
            
            # Create log entry
            log_entry = self._create_log_entry(repository, feature_idea, pull_request_url, forked_repo)
            
            # Determine log file path (using date-based organization)
            from datetime import datetime
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file_path = f"logs/{date_str}_activity.log"
            
            # Try to get existing log file or create new one
            try:
                contents = self.target_repo.get_contents(log_file_path)
                # If we get a list, it means the path is a directory, so we treat it as if the file doesn't exist.
                if isinstance(contents, list):
                    raise Exception("Path is a directory")
                existing_content = contents.decoded_content.decode('utf-8')
                sha = contents.sha
            except Exception:
                # File doesn't exist yet (or is a directory)
                existing_content = f"# GitHub Activity Log for {self.github_client.username}\n"
                existing_content += f"# Started logging on {datetime.now().strftime('%Y-%m-%d')}\n\n"
                sha = None
            
            # Append new log entry
            new_content = existing_content + log_entry + "\n"
            
            # Commit the log file
            if sha:
                # Update existing file
                self.target_repo.update_file(
                    path=log_file_path,
                    message=f"Log: {feature_idea['title']} contribution to {repository['full_name']}",
                    content=new_content,
                    sha=sha
                )
            else:
                # Create new file
                self.target_repo.create_file(
                    path=log_file_path,
                    message=f"Initial log: {feature_idea['title']} contribution to {repository['full_name']}",
                    content=new_content
                )
            
            self.logger.info(f"Successfully logged contribution to {log_file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging contribution: {e}")
            return False
    
    def _create_log_entry(self, 
                         repository: Dict[str, Any],
                         feature_idea: Dict[str, Any],
                         pull_request_url: str,
                         forked_repo: Dict[str, Any]) -> str:
        """Create a formatted log entry."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = f"""## [{timestamp}] Contribution Made

- **Agent**: {self.github_client.username}
- **Target Repository**: {repository['full_name']}
- **Feature**: {feature_idea['title']}
- **Description**: {feature_idea['description']}
- **Pull Request**: {pull_request_url}
- **Fork Repository**: {forked_repo['full_name']}
- **Branch**: {feature_idea.get('branch_name', 'unknown')}
- **Feature Type**: {feature_idea.get('feature_type', 'utility')}

---
"""
        return entry
    
    def log_agent_start(self) -> bool:
        """Log when the agent starts."""
        try:
            if not self.target_repo:
                return False
                
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""## [{timestamp}] Agent Started

- **Agent**: {self.github_client.username}
- **Status**: Autonomous GitHub Activity Populator agent started
- **Target Repository for Contributions**: Configured
- **Logging Repository**: {self.target_repo_name}

---
"""
            
            # Append to today's log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file_path = f"logs/{date_str}_activity.log"
            
            try:
                contents = self.target_repo.get_contents(log_file_path)
                existing_content = contents.decoded_content.decode('utf-8')
                sha = contents.sha
            except GithubException:
                existing_content = f"# GitHub Activity Log for {self.github_client.username}\n"
                existing_content += f"# Started logging on {datetime.now().strftime('%Y-%m-%d')}\n\n"
                sha = None
            
            new_content = existing_content + log_entry + "\n"
            
            if sha:
                self.target_repo.update_file(
                    path=log_file_path,
                    message="Log: Agent started",
                    content=new_content,
                    sha=sha
                )
            else:
                self.target_repo.create_file(
                    path=log_file_path,
                    message="Initial log: Agent started",
                    content=new_content
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Error logging agent start: {e}")
            return False
    
    def log_agent_stop(self) -> bool:
        """Log when the agent stops."""
        try:
            if not self.target_repo:
                return False
                
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""## [{timestamp}] Agent Stopped

- **Agent**: {self.github_client.username}
- **Status**: Autonomous GitHub Activity Populator agent stopped
- **Total Contributions Made**: [This would be tracked by the agent]

---
"""
            
            # Append to today's log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file_path = f"logs/{date_str}_activity.log"
            
            try:
                contents = self.target_repo.get_contents(log_file_path)
                existing_content = contents.decoded_content.decode('utf-8')
                sha = contents.sha
            except GithubException:
                existing_content = f"# GitHub Activity Log for {self.github_client.username}\n"
                existing_content += f"# Started logging on {datetime.now().strftime('%Y-%m-%d')}\n\n"
                sha = None
            
            new_content = existing_content + log_entry + "\n"
            
            if sha:
                self.target_repo.update_file(
                    path=log_file_path,
                    message="Log: Agent stopped",
                    content=new_content,
                    sha=sha
                )
            else:
                self.target_repo.create_file(
                    path=log_file_path,
                    message="Initial log: Agent stopped",
                    content=new_content
                )
            
            return True
        except Exception as e:
            self.logger.error(f"Error logging agent stop: {e}")
            return False