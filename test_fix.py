
import logging
import sys
import os

# Set up logging to stdout
logging.basicConfig(level=logging.INFO)

# Add current directory to sys.path
sys.path.append(os.getcwd())

from github_populator.llm_generator.feature_synthesizer import LLMSynthesizedFeatureGenerator
from github_populator.utils.config import config

def test_generation():
    generator = LLMSynthesizedFeatureGenerator()
    
    # Mock data from log
    repository = {
        'id': 12345,
        'full_name': "jkanner/streamlit-dataview",
        'name': "streamlit-dataview",
        'description': "Data visualization with streamlit",
        'language': "Python",
        'stars': 100,
        'topics': ["streamlit"],
        'clone_url': "https://github.com/jkanner/streamlit-dataview.git",
        'default_branch': "main"
    }
    
    context = {
        'language': 'Python',
        'structure': {
            'main_directories': ['src'], 
            'has_tests': True, 
            'has_docs': False, 
            'python_packages': ['src'],
            'file_count': 10
        },
        'patterns': {
            'has_classes': True, 
            'has_functions': True, 
            'has_async_code': False, 
            'uses_type_hints': False,
            'has_context_managers': False,
            'has_decorators': False
        },
        'dependencies': {
            'package_managers': ['pip'], 
            'dependencies': ['streamlit', 'pandas']
        },
        'missing_features': [
            {'type': 'missing_file', 'description': 'README'}
        ]
    }
    
    print("Testing generate_feature...")
    try:
        # We need to mock the LLM client to avoid real API calls
        if generator.llm_client:
            generator.llm_client.generate_content = lambda *args, **kwargs: (
                "=== FILE: test_tool.py ===\ndef hello():\n    print('hello')\nFEATURE DESCRIPTION: A test tool."
            )
        
        feature = generator.generate_feature(repository, context)
        if feature:
            print(f"Success! Generated feature: {feature['title']}")
        else:
            print("Failed to generate feature (returned None)")
    except Exception as e:
        print(f"FAILED with unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
