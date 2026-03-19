import logging
from typing import Dict, Any, Optional
from datetime import datetime
from github import Github, GithubException
from ..utils.github_client import GitHubClient
from ..utils.config import Config


class ActivityLogger:
    """
    Logs agent activities as private GitHub Gists.

    This approach keeps logs completely off the repository so users who
    clone the project never see or download them. Each run appends a new
    block to a persistent daily Gist owned by the authenticated user.
    """

    def __init__(self, github_client: GitHubClient):
        """Initialize the activity logger."""
        self.github_client = github_client
        self.logger = logging.getLogger(__name__)
        self.github = Github(github_client.token)
        self.config = Config()

        # Still keep TARGET_REPO for reference (shown in README / config)
        self.target_repo_name = self.config.get('TARGET_REPO', '')
        self.user = None
        self._init_user()

    def _init_user(self):
        """Load the authenticated github user."""
        try:
            self.user = self.github.get_user()
            self.logger.info(f"Activity logger ready (Gist-based) for {self.user.login}")
        except Exception as e:
            self.logger.error(f"Could not authenticate for Gist logging: {e}")
            self.user = None

    # ──────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────

    def log_contribution(self,
                         repository: Dict[str, Any],
                         feature_idea: Dict[str, Any],
                         pull_request_url: str,
                         forked_repo: Dict[str, Any]) -> bool:
        """Log a contribution entry to a private GitHub Gist."""
        try:
            entry = self._create_log_entry(repository, feature_idea, pull_request_url, forked_repo)
            return self._append_to_gist(entry, tag="Contribution")
        except Exception as e:
            self.logger.error(f"Error logging contribution: {e}")
            return False

    def log_agent_start(self) -> bool:
        """Log agent start event."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = (
                f"## [{timestamp}] Agent Started\n\n"
                f"- **User**: {self.github_client.username}\n"
                f"- **Status**: Autonomous GitHub Activity Populator started\n\n---\n"
            )
            return self._append_to_gist(entry, tag="AgentStart")
        except Exception as e:
            self.logger.error(f"Error logging agent start: {e}")
            return False

    def log_agent_stop(self) -> bool:
        """Log agent stop event."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = (
                f"## [{timestamp}] Agent Stopped\n\n"
                f"- **User**: {self.github_client.username}\n"
                f"- **Status**: Agent finished execution\n\n---\n"
            )
            return self._append_to_gist(entry, tag="AgentStop")
        except Exception as e:
            self.logger.error(f"Error logging agent stop: {e}")
            return False

    # ──────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────

    def _get_or_create_daily_gist(self) -> Optional[Any]:
        """
        Find or create a private Gist for today's activity log.

        Gist description format:  "[GH-Populator] Activity Log YYYY-MM-DD"
        This makes it easy to identify across your Gists list.
        """
        if not self.user:
            return None

        date_str = datetime.now().strftime("%Y-%m-%d")
        gist_description = f"[GH-Populator] Activity Log {date_str}"
        filename = f"activity_{date_str}.md"

        # Search existing Gists for today's log
        try:
            for gist in self.user.get_gists():
                if gist.description == gist_description:
                    self.logger.info(f"Found existing Gist for today: {gist.id}")
                    return gist
        except Exception as e:
            self.logger.warning(f"Error searching Gists: {e}")

        # Create a fresh one for today
        try:
            header = (
                f"# GitHub Activity Log – {date_str}\n"
                f"**User**: {self.github_client.username}  \n"
                f"**Source**: Autonomous GitHub Populator  \n\n---\n\n"
            )
            gist = self.user.create_gist(
                public=False,
                files={filename: {"content": header}},
                description=gist_description
            )
            self.logger.info(f"Created new private Gist for today: {gist.id}")
            return gist
        except Exception as e:
            self.logger.error(f"Failed to create Gist: {e}")
            return None

    def _append_to_gist(self, entry: str, tag: str = "Entry") -> bool:
        """Append a new log entry to the today's private Gist."""
        gist = self._get_or_create_daily_gist()
        if not gist:
            self.logger.warning("No Gist available — skipping log entry")
            return False

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"activity_{date_str}.md"

        try:
            # Get current content
            gist_file = gist.files.get(filename)
            current_content = gist_file.content if gist_file else ""

            # Append new entry
            new_content = current_content + entry + "\n"

            # Edit the Gist
            gist.edit(files={filename: {"content": new_content}})
            self.logger.info(f"Successfully logged [{tag}] to private Gist {gist.id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update Gist: {e}")
            return False

    def _create_log_entry(self,
                          repository: Dict[str, Any],
                          feature_idea: Dict[str, Any],
                          pull_request_url: str,
                          forked_repo: Dict[str, Any]) -> str:
        """Create a formatted markdown log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return (
            f"## [{timestamp}] Contribution Made\n\n"
            f"| Field | Value |\n"
            f"|-------|-------|\n"
            f"| **Target Repo** | [{repository['full_name']}]({repository.get('url', '')}) |\n"
            f"| **Feature** | {feature_idea['title']} |\n"
            f"| **Description** | {feature_idea.get('description', '')} |\n"
            f"| **Pull Request** | [View PR]({pull_request_url}) |\n"
            f"| **Fork** | {forked_repo['full_name']} |\n"
            f"| **Branch** | `{feature_idea.get('branch_name', 'unknown')}` |\n"
            f"| **Feature Type** | {feature_idea.get('feature_type', 'utility')} |\n\n"
            f"---\n"
        )