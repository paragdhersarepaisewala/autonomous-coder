import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from github_populator.repository_discovery.discoverer import RepositoryDiscoverer
from github_populator.context_analysis.analyzer import ContextAnalyzer
from github_populator.contribution_execution.executor import ContributionExecutor
from github_populator.integration.logger import ActivityLogger
from github_populator.utils.config import Config
from github_populator.utils.github_client import GitHubClient
from github_populator.llm_generator.feature_synthesizer import LLMSynthesizedFeatureGenerator as FeatureGenerator


class AutonomousAgentController:
    """Main controller for the autonomous GitHub activity populator agent."""
    
    def __init__(self, config_path: str = ".env"):
        """Initialize the agent controller with configuration."""
        self.config = Config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize GitHub client
        self.github_client = GitHubClient(
            token=self.config.get('GITHUB_TOKEN'),
            username=self.config.get('GITHUB_USERNAME')
        )
        
        # Initialize modules
        self.repository_discoverer = RepositoryDiscoverer(self.github_client)
        self.context_analyzer = ContextAnalyzer()
        self.feature_generator = FeatureGenerator(config_obj=self.config)
        self.contribution_executor = ContributionExecutor(self.github_client)
        self.activity_logger = ActivityLogger(self.github_client)
        
        # Agent state
        self.is_running = False
        self.contributions_made = 0
        self.target_contributions = self.config.get_int('TARGET_CONTRIBUTIONS', 3)
        
    def start(self, interactive: bool = False, dry_run: bool = False):
        """Start the autonomous agent."""
        self.logger.info(f"Starting GitHub activity populator agent (interactive={interactive}, dry_run={dry_run})")
        self.is_running = True
        failed_repo_ids = set()  # Track failed repos to avoid retries
        
        try:
            while self.is_running and self.contributions_made < self.target_contributions:
                cycle_num = self.contributions_made + 1
                prefix = "[DRY-RUN] " if dry_run else ""
                print(f"\n{prefix}{'='*20} Cycle {cycle_num}/{self.target_contributions} {'='*20}")
                self.logger.info(f"Starting contribution cycle {cycle_num}/{self.target_contributions}")
                
                # Step 1: Discover suitable repositories
                target_repo = self._discover_target_repository(exclude_ids=failed_repo_ids, interactive=interactive)
                if not target_repo:
                    if interactive:
                        print("No repository selected. Exiting cycle.")
                        break
                    self.logger.warning("No suitable repositories found, waiting before retry")
                    time.sleep(self.config.get_int('RETRY_DELAY', 300))  # 5 minutes
                    failed_repo_ids.clear()  # Reset to try all repos again
                    continue
                
                # Step 2: Analyze repository context
                print(f"Analyzing repository: {target_repo['full_name']}...")
                context = self._analyze_repository_context(target_repo)
                if not context:
                    self.logger.warning(f"Failed to analyze repository context for {target_repo['full_name']}, trying another")
                    if interactive:
                        print("Analysis failed. Try another repository.")
                    else:
                        failed_repo_ids.add(target_repo['id'])
                    time.sleep(2)  # Brief pause before retry
                    continue
                
                # Step 3: Generate feature idea
                print(f"Generating feature ideas for {target_repo['name']}...")
                feature_idea = self._generate_feature_idea(target_repo, context, interactive=interactive)
                if not feature_idea:
                    self.logger.warning("Failed to generate feature idea")
                    if interactive:
                        print("No feature selected. Try again.")
                    continue
                
                # Step 4: Execute contribution
                if interactive:
                    confirm_text = f"Ready to SIMULATE contribution to {target_repo['full_name']}?" if dry_run else f"Ready to implement and contribute '{feature_idea['title']}' to {target_repo['full_name']}?"
                    confirm = input(f"\n{confirm_text} (y/n): ")
                    if confirm.lower() != 'y':
                        print("Contribution cancelled.")
                        continue

                if dry_run:
                    print(f"\n[DRY-RUN] Successfully simulated contribution: {feature_idea['title']}")
                    self.contributions_made += 1
                    success = True
                else:
                    print(f"Executing contribution: {feature_idea['title']}...")
                    success = self._execute_contribution(target_repo, feature_idea)
                    if success:
                        self.contributions_made += 1
                        print(f"\nSUCCESS: Contribution made to {target_repo['full_name']}")
                        self.logger.info(f"Contribution successful! Total: {self.contributions_made}/{self.target_contributions}")
                    else:
                        print(f"\nFAILED: Contribution to {target_repo['full_name']} failed.")
                        self.logger.warning("Contribution failed")
                
                # Wait before next cycle
                if self.contributions_made < self.target_contributions:
                    if interactive:
                        cont = input("\nContinue to next cycle? (y/n): ")
                        if cont.lower() != 'y':
                            break
                    else:
                        delay = self.config.get_int('CYCLE_DELAY', 1800)  # 30 minutes
                        self.logger.info(f"Waiting {delay} seconds before next cycle")
                        time.sleep(delay)
                    
        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user")
            print("\nAgent stopped by user")
        except Exception as e:
            self.logger.error(f"Agent encountered fatal error: {e}")
            print(f"\nFatal error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the autonomous agent."""
        self.logger.info("Stopping autonomous agent")
        self.is_running = False
    
    def _discover_target_repository(self, exclude_ids: set = None, interactive: bool = False) -> Optional[Dict]:
        """Discover a suitable repository for contribution."""
        if exclude_ids is None:
            exclude_ids = set()
            
        try:
            # Check if a specific repository is targeted via configuration
            target_repo_name = self.config.get('TARGET_REPO_OVERRIDE')
            if target_repo_name:
                self.logger.info(f"Using targeted repository from config: {target_repo_name}")
                repo = self.repository_discoverer.get_repository(target_repo_name)
                if repo:
                    return repo
                else:
                    self.logger.warning(f"Could not find targeted repository: {target_repo_name}")

            self.logger.info("Discovering target repositories...")
            repositories = self.repository_discoverer.find_suitable_repositories(
                language=self.config.get('TARGET_LANGUAGE', 'Python'),
                min_stars=self.config.get_int('MIN_STARS', 10),
                max_stars=self.config.get_int('MAX_STARS', 1000),
                excluded_topics=self.config.get_list('EXCLUDED_TOPICS', [])
            )
            
            if not repositories:
                self.logger.warning("No suitable repositories found")
                return None
            
            # Filter out already failed repositories
            if not interactive:
                available_repos = [repo for repo in repositories if repo['id'] not in exclude_ids]
            else:
                available_repos = repositories

            if not available_repos:
                self.logger.warning("All available repositories have been tried and failed")
                return None
            
            if interactive:
                print("\nDiscovered repositories:")
                for i, repo in enumerate(available_repos[:15], 1):
                    stars = repo.get('stargazers_count', 'N/A')
                    desc = repo.get('description', 'No description')
                    if desc:
                        desc = desc[:80] + "..." if len(desc) > 80 else desc
                    print(f" [{i}] {repo['full_name']} ({stars} stars)")
                    print(f"     {desc}")
                
                choice = input("\nSelect a repository number (or 'q' to quit): ")
                if choice.lower() == 'q':
                    return None
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(available_repos):
                        return available_repos[idx]
                except ValueError:
                    pass
                print("Invalid selection, picking the best one automatically.")

            # Select the most suitable repository from available ones
            selected_repo = self.repository_discoverer.select_best_repository(available_repos)
            if selected_repo:
                self.logger.info(f"Selected repository: {selected_repo['full_name']}")
                return selected_repo
            else:
                self.logger.warning("No suitable repository selected from candidates")
                return None
            
        except Exception as e:
            self.logger.error(f"Error discovering repositories: {e}")
            return None

    def _analyze_repository_context(self, repository: Dict) -> Optional[Dict]:
        """Analyze the context of a repository."""
        try:
            self.logger.info(f"Analyzing context for {repository['full_name']}")
            
            # Clone repository temporarily
            repo_path = self.context_analyzer.clone_repository(
                repository['clone_url'], 
                repository['name']
            )
            
            if not repo_path:
                self.logger.error("Failed to clone repository")
                return None
            
            # Analyze code structure
            context = self.context_analyzer.analyze_repository(repo_path)
            
            # Clean up cloned repository
            self.context_analyzer.cleanup_clone(repo_path)
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error analyzing repository context: {e}")
            return None

    def _generate_feature_idea(self, repository: Dict, context: Dict, interactive: bool = False) -> Optional[Dict]:
        """Generate a feature idea based on repository analysis."""
        try:
            self.logger.info("Generating feature idea...")
            
            feature_idea = self.feature_generator.generate_feature(
                repository=repository,
                context=context
            )
            
            if not feature_idea:
                return None

            if interactive:
                print(f"\nProposed Feature: {feature_idea['title']}")
                print(f"Description: {feature_idea['description']}")
                print(f"Branch: {feature_idea['branch_name']}")
                
                confirm = input("\nUse this feature idea? (y/n, or 'r' to regenerate): ")
                if confirm.lower() == 'y':
                    return feature_idea
                elif confirm.lower() == 'r':
                    # Recursive call for regeneration
                    return self._generate_feature_idea(repository, context, interactive=True)
                else:
                    return None
            
            self.logger.info(f"Generated feature idea: {feature_idea['title']}")
            return feature_idea
                
        except Exception as e:
            self.logger.error(f"Error generating feature idea: {e}")
            return None
    
    def _execute_contribution(self, repository: Dict, feature_idea: Dict) -> bool:
        """Execute the contribution process."""
        try:
            self.logger.info(f"Executing contribution: {feature_idea['title']}")
            
            # Fork repository
            forked_repo = self.contribution_executor.fork_repository(repository)
            if not forked_repo:
                self.logger.error("Failed to fork repository")
                return False
            
            # Create branch
            repo_path = self.contribution_executor.create_feature_branch(
                forked_repo, 
                feature_idea['branch_name']
            )
            if not repo_path:
                self.logger.error("Failed to create feature branch")
                return False
            
            # Generate and commit code
            commit_success = self.contribution_executor.implement_and_commit_feature(
                forked_repo,
                repo_path,
                feature_idea,
                repository['default_branch']
            )
            if not commit_success:
                self.logger.error("Failed to implement and commit feature")
                return False
            
            # Create pull request
            pr_url = self.contribution_executor.create_pull_request(
                forked_repo,
                feature_idea['branch_name'],
                feature_idea,
                repository
            )
            if not pr_url:
                self.logger.error("Failed to create pull request")
                return False
            
            # Log activity to user's repository
            self.activity_logger.log_contribution(
                repository=repository,
                feature_idea=feature_idea,
                pull_request_url=pr_url,
                forked_repo=forked_repo
            )
            
            self.logger.info(f"Contribution successful! PR: {pr_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing contribution: {e}")
            return False


def main():
    """Main entry point for the autonomous agent."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('github_populator.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create and start agent
    agent = AutonomousAgentController()
    agent.start()


if __name__ == "__main__":
    main()