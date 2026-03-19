#!/usr/bin/env python3
"""
Main entry point for the Autonomous GitHub Activity Populator Agent
"""

import os
import sys

# Add the parent directory of github_populator to the path so we can import github_populator as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
github_populator_dir = current_dir
parent_dir = os.path.dirname(github_populator_dir)
sys.path.insert(0, parent_dir)

# Now we can import using the package structure
from github_populator.agent_core.controller import AutonomousAgentController
import logging


import argparse
from github_populator.agent_core.controller import AutonomousAgentController
import logging


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('github_populator.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_setup(agent):
    """Run interactive setup to configure the agent."""
    print("\n--- GitHub Populator Setup ---")
    
    token = input(f"GitHub Token [{agent.config.get('GITHUB_TOKEN', 'not set')}]: ")
    if token: agent.config.set('GITHUB_TOKEN', token)
    
    username = input(f"GitHub Username [{agent.config.get('GITHUB_USERNAME', 'not set')}]: ")
    if username: agent.config.set('GITHUB_USERNAME', username)
    
    gemini_key = input(f"Gemini API Key [{agent.config.get('GEMINI_API_KEY', 'not set')}]: ")
    if gemini_key: agent.config.set('GEMINI_API_KEY', gemini_key)
    
    lang = input(f"Target Language [{agent.config.get('TARGET_LANGUAGE', 'Python')}]: ")
    if lang: agent.config.set('TARGET_LANGUAGE', lang)
    
    print("Activity Logging: Private GitHub Gists (automatic)")
    
    contrib_repo = input(f"Specific Repo to Contribute to (leave blank to search) [{agent.config.get('TARGET_REPO_OVERRIDE', 'none')}]: ")
    if contrib_repo: agent.config.set('TARGET_REPO_OVERRIDE', contrib_repo)
    
    agent.config.save()
    print("\nConfiguration saved to .env file.")


def main():
    """Main function to run the autonomous agent."""
    parser = argparse.ArgumentParser(description="Autonomous GitHub Activity Populator Agent")
    
    # Mode selection
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    parser.add_argument("--auto", "-a", action="store_true", help="Run in fully automated mode (default)")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard to configure .env")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without making actual contributions")
    
    # Config overrides
    parser.add_argument("--repo", help="Specific repository to target (e.g. owner/repo)")
    parser.add_argument("--lang", help="Target programming language")
    parser.add_argument("--count", type=int, help="Number of contributions to make")
    parser.add_argument("--type", help="Feature type (utility, feature, fix, documentation)")
    
    # Config persistence
    parser.add_argument("--save", action="store_true", help="Save provided arguments to .env for next use")
    
    args = parser.parse_args()
    
    print("\nGitHub Activity Populator")
    print("=" * 30)
    
    setup_logging()
    logger = logging.getLogger("github_populator")
    
    try:
        # Create the agent
        agent = AutonomousAgentController()
        
        # Handle setup wizard
        if args.setup:
            run_setup(agent)
            return 0
            
        # Check if GH token is set
        if agent.config.get('GITHUB_TOKEN') == 'your_github_personal_access_token_here' or not agent.config.get('GITHUB_TOKEN'):
            print("\nWARNING: GitHub Token not configured!")
            print("Please run with --setup or edit the .env file.")
            if not args.interactive:
                return 1

        # Apply CLI overrides to config cache
        if args.lang: agent.config.set('TARGET_LANGUAGE', args.lang)
        if args.count: agent.config.set('TARGET_CONTRIBUTIONS', args.count)
        if args.type: agent.config.set('FEATURE_TYPE', args.type)
        if args.repo: agent.config.set('TARGET_REPO_OVERRIDE', args.repo)
        
        # Update target_contributions in agent state if count was overridden
        if args.count: agent.target_contributions = args.count

        # Save config if requested
        if args.save:
            agent.config.save()
            print("Configuration updated and saved to .env")

        # Log agent start
        logger.info(f"Agent initialized. Mode: {'Interactive' if args.interactive else 'Auto'}")
        print(f"Target: Make {agent.target_contributions} contributions")
        print(f"Language: {agent.config.get('TARGET_LANGUAGE')}")
        
        # Start the agent
        # If neither --interactive nor --auto is specified, default to interactive if no args, 
        # but the user asked for "option to automate all without asking", 
        # so I'll default to interactive if no --auto is present, or vice-versa.
        # Actually, let's default to interactive mode unless --auto is passed.
        is_interactive = args.interactive or not args.auto
        
        agent.start(interactive=is_interactive, dry_run=args.dry_run)
        
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"\nAgent failed: {e}")
        logger.error(f"Agent failed: {e}", exc_info=True)
        return 1
    
    print("\nExecution completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())