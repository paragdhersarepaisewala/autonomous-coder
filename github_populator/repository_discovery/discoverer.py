import logging
from typing import List, Dict, Optional
from datetime import datetime
from github import Github
from ..utils.github_client import GitHubClient


class RepositoryDiscoverer:
    """Discovers suitable repositories for contribution."""
    
    def __init__(self, github_client: GitHubClient):
        """Initialize the repository discoverer."""
        self.github_client = github_client
        self.logger = logging.getLogger(__name__)
        self.github = Github(github_client.token)
    
    def find_suitable_repositories(self, 
                                 language: str = "Python",
                                 min_stars: int = 10,
                                 max_stars: int = 1000,
                                 excluded_topics: Optional[List[str]] = None) -> List[Dict]:
        """Find suitable repositories for contribution."""
        if excluded_topics is None:
            excluded_topics = []
        
        self.logger.info(f"Searching for {language} repositories with {min_stars}-{max_stars} stars")
        
        try:
            # Search for repositories
            query = f"language:{language} stars:{min_stars}..{max_stars} archived:false"
            repositories = self.github.search_repositories(query=query, sort="updated", order="desc")
            
            suitable_repos = []
            count = 0
            max_repos_to_check = 50  # Limit to avoid rate limits
            
            for repo in repositories:
                if count >= max_repos_to_check:
                    break
                    
                # Skip if it's the user's own repository
                if repo.full_name.lower() == self.github_client.username.lower() + "/" + repo.name.lower():
                    count += 1
                    continue
                
                # Check excluded topics
                if excluded_topics and any(topic in repo.topics for topic in excluded_topics):
                    count += 1
                    continue
                
                # Skip forks if desired (can be configured)
                if repo.fork:
                    count += 1
                    continue
                
                # Skip if no recent activity (last push > 6 months ago)
                # This is a simplified check - in practice you might want more sophisticated logic
                
                suitable_repos.append({
                    'id': repo.id,
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'url': repo.html_url,
                    'clone_url': repo.clone_url,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'open_issues': repo.open_issues_count,
                    'topics': repo.topics,
                    'default_branch': repo.default_branch,
                    'created_at': repo.created_at,
                    'updated_at': repo.updated_at,
                    'pushed_at': repo.pushed_at,
                    'size': repo.size
                })
                
                count += 1
            
            self.logger.info(f"Found {len(suitable_repos)} suitable repositories")
            return suitable_repos
            
        except Exception as e:
            self.logger.error(f"Error searching for repositories: {e}")
            return []
    
    def get_repository(self, full_name: str) -> Optional[Dict]:
        """Get details for a specific repository by its full name."""
        try:
            self.logger.info(f"Retrieving repository: {full_name}")
            repo = self.github.get_repo(full_name)
            
            return {
                'id': repo.id,
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'url': repo.html_url,
                'clone_url': repo.clone_url,
                'language': repo.language,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'topics': repo.topics,
                'default_branch': repo.default_branch,
                'created_at': repo.created_at,
                'updated_at': repo.updated_at,
                'pushed_at': repo.pushed_at,
                'size': repo.size
            }
        except Exception as e:
            self.logger.error(f"Error getting repository {full_name}: {e}")
            return None

    def select_best_repository(self, repositories: List[Dict]) -> Optional[Dict]:
        """Select the best repository from a list of candidates."""
        if not repositories:
            return None
        
        # Simple scoring algorithm
        scored_repos = []
        for repo in repositories:
            score = 0
            
            # Prefer recently updated repositories
            if repo['pushed_at']:
                days_since_push = (datetime.now() - repo['pushed_at'].replace(tzinfo=None)).days
                if days_since_push < 30:
                    score += 10
                elif days_since_push < 90:
                    score += 5
            
            # Prefer repositories with moderate activity (not too busy, not abandoned)
            if 1 <= repo['open_issues'] <= 20:
                score += 10
            elif repo['open_issues'] == 0:
                score += 5  # Still okay, but less opportunity
            
            # Prefer repositories with good documentation (has README, etc.)
            # This would require checking the repo contents, simplified for now
            
            # Prefer smaller codebases (easier to understand)
            if repo['size'] < 10000:  # Less than 10MB
                score += 10
            elif repo['size'] < 50000:  # Less than 50MB
                score += 5
            
            # Prefer popular but not too popular repositories
            if 50 <= repo['stars'] <= 500:
                score += 15
            elif repo['stars'] < 50:
                score += 5  # Still okay
            
            scored_repos.append((repo, score))
        
        # Sort by score descending and return the best
        scored_repos.sort(key=lambda x: x[1], reverse=True)
        return scored_repos[0][0] if scored_repos else None