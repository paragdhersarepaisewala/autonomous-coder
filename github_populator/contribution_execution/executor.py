import logging
import os
import time
from typing import Dict, List, Optional, Any
from github import Github, Repository, GithubException
from ..utils.github_client import GitHubClient
from ..utils.system_utils import safe_rmtree
import git


class ContributionExecutor:
    """Executes contributions to repositories (forking, branching, committing, PR creation)."""
    
    def __init__(self, github_client: GitHubClient):
        """Initialize the contribution executor."""
        self.github_client = github_client
        self.logger = logging.getLogger(__name__)
        self.github = Github(github_client.token)
    
    def fork_repository(self, repository: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fork a repository to the user's account."""
        try:
            self.logger.info(f"Forking repository {repository['full_name']}")
            
            # Get the repository object
            repo = self.github.get_repo(repository['full_name'])
            
            # Fork it
            fork = repo.create_fork()
            
            forked_repo = {
                'id': fork.id,
                'name': fork.name,
                'full_name': fork.full_name,
                'owner': fork.owner.login,
                'html_url': fork.html_url,
                'clone_url': fork.clone_url,
                'ssh_url': fork.ssh_url,
                'default_branch': fork.default_branch
            }
            
            self.logger.info(f"Successfully forked to {forked_repo['full_name']}")
            return forked_repo
            
        except GithubException as e:
            self.logger.error(f"GitHub error forking repository: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error forking repository: {e}")
            return None
    
    def create_feature_branch(self, repository: Dict[str, Any], branch_name: str) -> Optional[str]:
        """Create a feature branch in the forked repository."""
        try:
            self.logger.info(f"Creating branch {branch_name} in {repository['full_name']}")
            
            # Clone the forked repository
            temp_dir = os.path.join(os.getcwd(), "temp_forks")
            os.makedirs(temp_dir, exist_ok=True)
            
            repo_path = os.path.join(temp_dir, repository['name'])
            
            # Remove if exists
            safe_rmtree(repo_path)
            
            # Clone the fork
            repo_obj = git.Repo.clone_from(repository['clone_url'], repo_path)
            
            # Create and checkout new branch
            new_branch = repo_obj.create_head(branch_name)
            new_branch.checkout()
            
            # Push the branch to origin
            origin = repo_obj.remote(name='origin')
            origin.push(new_branch.name)
            
            self.logger.info(f"Successfully created and pushed branch {branch_name}")
            
            # Return the repo path for later use
            return repo_path
            
        except Exception as e:
            self.logger.error(f"Error creating feature branch: {e}")
            return None
    
    def implement_and_commit_feature(self, 
                                   repository: Dict[str, Any], 
                                   repo_path: str,
                                   feature_idea: Dict[str, Any],
                                   base_branch: str) -> bool:
        """Implement the feature and commit changes."""
        try:
            self.logger.info(f"Implementing feature in {repo_path}")
            
            # Get the git repo object
            repo_obj = git.Repo(repo_path)
            
            # Create or modify files as specified in the feature idea
            for file_info in feature_idea.get('files_to_create', []):
                file_path = os.path.join(repo_path, file_info['path'])
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Write the file content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info['content'])
                
                self.logger.info(f"Created file: {file_info['path']}")
            
            # Modify existing files (not implemented in this version for simplicity)
            # In a full implementation, you would modify existing files here
            
            # Add all changes
            repo_obj.git.add(A=True)
            
            # Check if there are any changes to commit
            if repo_obj.is_dirty() or len(repo_obj.untracked_files) > 0:
                # Create commit message
                commit_message = f"feat: {feature_idea['title']}\n\n{feature_idea['description']}\n\nCo-authored-by: autonomous-agent <noreply@github.com>"
                
                # Commit changes
                repo_obj.index.commit(commit_message)
                
                # Push changes
                origin = repo_obj.remote(name='origin')
                origin.push(repo_obj.head)
                
                self.logger.info(f"Successfully committed and pushed changes")
                return True
            else:
                self.logger.warning("No changes to commit")
                return False
                
        except Exception as e:
            self.logger.error(f"Error implementing and committing feature: {e}")
            return False
    
    def create_pull_request(self, 
                          forked_repo: Dict[str, Any],
                          branch_name: str,
                          feature_idea: Dict[str, Any],
                          original_repo: Dict[str, Any]) -> Optional[str]:
        """Create a pull request from the forked repository to the original repository."""
        try:
            self.logger.info(f"Creating pull request for {feature_idea['title']}")
            
            # Get the forked repository object
            forked_repo_obj = self.github.get_repo(forked_repo['full_name'])
            
            # Get the original repository object
            original_repo_obj = self.github.get_repo(original_repo['full_name'])
            
            # Create the pull request
            pr = forked_repo_obj.create_pull(
                title=feature_idea['title'],
                body=f"""{feature_idea['description']}

This pull request was created by the Autonomous GitHub Activity Populator agent.

Original repository: {original_repo['full_name']}
Feature type: {feature_idea.get('feature_type', 'utility')}
""",
                head=forked_repo['owner'] + ':' + branch_name,
                base=original_repo['default_branch']
            )
            
            pr_url = pr.html_url
            self.logger.info(f"Successfully created pull request: {pr_url}")
            return pr_url
            
        except GithubException as e:
            self.logger.error(f"GitHub error creating pull request: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating pull request: {e}")
            return None

