#!/usr/bin/env python3
"""Test script to verify imports work correctly"""

import sys
import os

# Add the github_populator directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'github_populator'))

print("Testing imports...")
print("Python path:", sys.path[:3])

try:
    from agent_core.controller import AutonomousAgentController
    print("[OK] agent_core.controller imported successfully")
except Exception as e:
    print("[FAIL] Failed to import agent_core.controller:", e)
    import traceback
    traceback.print_exc()

try:
    from llm_generator.feature_synthesizer import LLMSynthesizedFeatureGenerator
    print("[OK] llm_generator.feature_synthesizer imported successfully")
except Exception as e:
    print("[FAIL] Failed to import llm_generator.feature_synthesizer:", e)
    import traceback
    traceback.print_exc()

try:
    from utils.config import config
    print("[OK] utils.config imported successfully")
except Exception as e:
    print("[FAIL] Failed to import utils.config:", e)
    import traceback
    traceback.print_exc()

try:
    from utils.github_client import GitHubClient
    print("[OK] utils.github_client imported successfully")
except Exception as e:
    print("[FAIL] Failed to import utils.github_client:", e)
    import traceback
    traceback.print_exc()

print("\nAll import tests completed.")