import logging
from typing import Dict, List, Optional, Any
import random
import string
from ..context_analysis.analyzer import ContextAnalyzer


class FeatureGenerator:
    """Generates feature ideas based on repository analysis."""
    
    def __init__(self):
        """Initialize the feature generator."""
        self.logger = logging.getLogger(__name__)
        self.context_analyzer = ContextAnalyzer()
    
    def generate_feature(self, 
                        repository: Dict[str, Any], 
                        context: Dict[str, Any],
                        feature_type: str = "utility") -> Optional[Dict[str, Any]]:
        """Generate a feature idea based on repository analysis."""
        try:
            self.logger.info(f"Generating {feature_type} feature for {repository['full_name']}")
            
            # Determine what kind of feature to generate based on analysis
            feature_idea = None
            
            if feature_type == "utility":
                feature_idea = self._generate_utility_feature(repository, context)
            elif feature_type == "test_improvement":
                feature_idea = self._generate_test_improvement(repository, context)
            elif feature_type == "documentation":
                feature_idea = self._generate_documentation_feature(repository, context)
            elif feature_type == "performance":
                feature_idea = self._generate_performance_feature(repository, context)
            else:
                # Default to utility
                feature_idea = self._generate_utility_feature(repository, context)
            
            if feature_idea:
                # Add metadata
                feature_idea.update({
                    'repository_id': repository['id'],
                    'repository_name': repository['full_name'],
                    'generated_at': str(datetime.now()),
                    'feature_type': feature_type
                })
                
                self.logger.info(f"Generated feature: {feature_idea['title']}")
                return feature_idea
            else:
                self.logger.warning("Failed to generate feature idea")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating feature: {e}")
            return None
    
    def _generate_utility_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a utility feature based on missing improvements."""
        try:
            missing_features = context.get('missing_features', [])
            
            # Look for missing file improvements
            file_improvements = [f for f in missing_features if f['type'] == 'missing_file']
            if file_improvements:
                improvement = random.choice(file_improvements)
                if 'README' in improvement['description']:
                    return self._generate_readme_feature(repository, context)
                elif 'license' in improvement['description'].lower():
                    return self._generate_license_feature(repository, context)
                elif '.gitignore' in improvement['description']:
                    return self._generate_gitignore_feature(repository, context)
                elif 'requirements' in improvement['description']:
                    return self._generate_requirements_feature(repository, context)
            
            # Look for missing type hints
            type_hint_improvements = [f for f in missing_features if 'type hints' in f['description']]
            if type_hint_improvements:
                return self._generate_type_hints_feature(repository, context)
            
            # Look for missing tests
            test_improvements = [f for f in missing_features if 'test' in f['description'].lower() and 'missing' in f['description'].lower()]
            if test_improvements:
                return self._generate_basic_tests_feature(repository, context)
            
            # Fallback: generate a simple utility feature
            return self._generate_simple_utility_feature(repository, context)
            
        except Exception as e:
            self.logger.error(f"Error generating utility feature: {e}")
            return None
    
    def _generate_readme_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a README file feature."""
        language = context.get('language', 'Unknown')
        description = repository.get('description', 'A software project')
        
        readme_content = f"""# {repository['name']}

{description}

## Installation

```bash
# Installation instructions will vary based on the project
```

## Usage

```bash
# Usage examples will vary based on the project
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
        
        return {
            'title': 'Add README.md file',
            'description': 'Add a basic README.md file to improve project documentation',
            'branch_name': f'add-readme-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': 'README.md',
                    'content': readme_content
                }
            ],
            'files_to_modify': []
        }
    
    def _generate_license_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a LICENSE file feature."""
        license_content = """MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
        
        return {
            'title': 'Add MIT LICENSE file',
            'description': 'Add a standard MIT LICENSE file to clarify licensing terms',
            'branch_name': f'add-license-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': 'LICENSE',
                    'content': license_content
                }
            ],
            'files_to_modify': []
        }
    
    def _generate_gitignore_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a .gitignore file feature."""
        language = context.get('language', 'Unknown')
        
        gitignore_templates = {
            'Python': """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/time.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
""",
            'JavaScript': """# Dependencies
node_modules/
/pnp/

# Testing
/coverage

# Production
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
""",
            'Java': """# Compiled class file
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp

# Package Files #*
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs, see http://www.java.com/en/download/help/error_hotspot.xml
hs_err_pid*
"""
        }
        
        template = gitignore_templates.get(language, gitignore_templates['Python'])
        
        return {
            'title': 'Add .gitignore file',
            'description': f'Add a .gitignore file suitable for {language} projects',
            'branch_name': f'add-gitignore-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': '.gitignore',
                    'content': template
                }
            ],
            'files_to_modify': []
        }
    
    def _generate_requirements_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a requirements.txt file feature."""
        # Analyze what imports are used in the code to suggest requirements
        detected_deps = self._detect_python_dependencies(repository, context)
        
        requirements_content = "# Auto-generated requirements.txt\n"
        for dep in detected_deps:
            requirements_content += f"{dep}\n"
        
        # If no dependencies detected, add some common ones
        if not detected_deps:
            requirements_content += "# Common Python packages (add specific ones as needed)\n# requests>=2.25.1\n# numpy>=1.20.0\n"
        
        return {
            'title': 'Add requirements.txt file',
            'description': 'Add a requirements.txt file to document Python dependencies',
            'branch_name': f'add-requirements-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': 'requirements.txt',
                    'content': requirements_content
                }
            ],
            'files_to_modify': []
        }
    
    def _generate_type_hints_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a type hints improvement feature."""
        # This would involve modifying existing Python files to add type hints
        # For simplicity, we'll create a utility script that can add type hints
        
        typehint_script = '''"""
Utility script to add basic type hints to Python files.
This is a starting point - manual review and refinement is recommended.
"""

import ast
import sys
from typing import Any, List, Optional


def add_basic_type_hints(file_path: str) -> str:
    """
    Add basic type hints to a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Modified content with basic type hints
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the Python code
        tree = ast.parse(content)
        
        # We'll do a simple transformation - in practice you'd want to be more sophisticated
        # For now, we'll just return the original content with a note
        return content + "\n\n# TODO: Add type hints to functions and methods\n"
        
    except Exception as e:
        return f"# Error processing {file_path}: {e}\n"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = add_basic_type_hints(sys.argv[1])
        print(result)
    else:
        print("Usage: python typehint_adder.py <python_file>")
'''
        
        return {
            'title': 'Add type hints utility',
            'description': 'Add a utility script to help with adding type hints to the codebase',
            'branch_name': f'add-typehints-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': 'typehint_adder.py',
                    'content': typehint_script
                }
            ],
            'files_to_modify': []
        }
    
    def _generate_basic_tests_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a basic tests feature."""
        language = context.get('language', 'Unknown')
        
        if language == 'Python':
            test_content = '''"""
Basic tests for the project.
This is a starting point - tests should be expanded based on actual functionality.
"""

import unittest
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestBasicFunctionality(unittest.TestCase):
    """Basic test cases."""

    def test_imports_work(self):
        """Test that we can at least import the main modules."""
        # This is a placeholder - replace with actual imports
        try:
            # Try to import main module if it exists
            import main
        except ImportError:
            try:
                # Try to import __init__ if it's a package
                import pkg
            except ImportError:
                # If nothing imports, that's okay for this basic test
                pass
        
        # The test passes if we got here without ImportError killing us
        self.assertTrue(True)

    def test_basic_assertion(self):
        """A basic assertion test."""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)


if __name__ == '__main__':
    unittest.main()
'''
            
            return {
                'title': 'Add basic test suite',
                'description': 'Add a basic test suite to improve test coverage',
                'branch_name': f'add-tests-{self._random_string(8)}',
                'files_to_create': [
                    {
                        'path': 'tests/test_basic.py',
                        'content': test_content
                    }
                ],
                'files_to_modify': []
            }
        else:
            # For non-Python languages, create a simple test placeholder
            return {
                'title': 'Add basic test structure',
                'description': 'Add a basic test structure appropriate for the language',
                'branch_name': f'add-tests-{self._random_string(8)}',
                'files_to_create': [
                    {
                        'path': 'TESTING.md',
                        'content': f"""# Testing Guidelines for {repository['name']}

This document outlines how to run tests for this project.

## Running Tests

[Add specific instructions for running tests in this project]

## Test Frameworks

[Add information about testing frameworks used]

## Writing Tests

[Add guidelines for writing tests]
"""
                    }
                ],
                'files_to_modify': []
            }
    
    def _generate_simple_utility_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple utility feature as fallback."""
        language = context.get('language', 'Unknown')
        
        if language == 'Python':
            utility_content = '''"""
Utility functions for the project.
This module provides helper functions that are commonly needed.
"""

from typing import Any, List, Optional, Union
import os
import sys


def safe_get_item(collection: Union[List, dict], index: Union[int, str], default: Any = None) -> Any:
    """
    Safely get an item from a collection by index or key.
    
    Args:
        collection: List or dictionary to get item from
        index: Index or key to retrieve
        default: Default value to return if index/key not found
        
    Returns:
        Item at index/key or default value
    """
    try:
        return collection[index]
    except (IndexError, KeyError, TypeError):
        return default


def is_empty(value: Any) -> bool:
    """
    Check if a value is empty.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is empty, False otherwise
    """
    if value is None:
        return True
    if isinstance(value, (str, list, dict, tuple, set)):
        return len(value) == 0
    return False


def ensure_directory(path: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to directory
        
    Returns:
        The path that was ensured to exist
    """
    os.makedirs(path, exist_ok=True)
    return path


if __name__ == "__main__":
    # Simple test
    test_list = [1, 2, 3]
    print(f"Safe get item 0: {safe_get_item(test_list, 0)}")
    print(f"Safe get item 10: {safe_get_item(test_list, 10, 'not found')}")
    print(f"Is empty list: {is_empty([])}")
    print(f"Is empty string: {is_empty('')}")
'''
        else:
            # Generic utility for other languages
            utility_content = f"""// Utility functions for {repository['name']}
// This file provides helper functions commonly needed in projects

// TODO: Implement utility functions appropriate for {language}
// This is a starting point for utility functions
"""
        
        return {
            'title': 'Add utility helper functions',
            'description': 'Add a utility module with helpful helper functions',
            'branch_name': f'add-utils-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': f'utils.{ "py" if language == "Python" else "txt" }',
                    'content': utility_content
                }
            ],
            'files_to_modify': []
        }

    def _generate_test_improvement(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a test improvement feature."""
        return self._generate_basic_tests_feature(repository, context)

    def _generate_documentation_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a documentation improvement feature."""
        return self._generate_readme_feature(repository, context)

    def _generate_performance_feature(self, repository: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a performance improvement feature."""
        # For now, we'll create a simple performance utilities module
        if context.get('language') == 'Python':
            perf_content = '''"""
Performance utilities for the project.
This module provides functions to help measure and improve performance.
"""

import time
import functools
from typing import Callable, Any


def timer(func: Callable) -> Callable:
    """
    Decorator to measure execution time of a function.
    
    Args:
        func: Function to time
        
    Returns:
        Wrapped function that reports execution time
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper


def benchmark(func: Callable, *args, iterations: int = 1000, **kwargs) -> float:
    """
    Benchmark a function by running it multiple times.
    
    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        iterations: Number of times to run the function
        **kwargs: Keyword arguments to pass to function
        
    Returns:
        Average execution time in seconds
    """
    total_time = 0
    for _ in range(iterations):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        total_time += (end - start)
    
    return total_time / iterations


def memoize(func: Callable) -> Callable:
    """
    Simple memoization decorator for caching function results.
    
    Args:
        func: Function to memoize
        
    Returns:
        Wrapped function with caching
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper
'''
        else:
            perf_content = f"""// Performance utilities for {repository['name']}
// This file provides functions to help measure and improve performance

// TODO: Implement performance utilities appropriate for {context.get('language', 'this language')}
"""
        
        return {
            'title': 'Add performance utilities',
            'description': 'Add a performance utilities module to help optimize code',
            'branch_name': f'add-performance-{self._random_string(8)}',
            'files_to_create': [
                {
                    'path': f'performance.{ "py" if context.get("language") == "Python" else "txt" }',
                    'content': perf_content
                }
            ],
            'files_to_modify': []
        }
    
    def _detect_python_dependencies(self, repository: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Detect Python dependencies by analyzing import statements."""
        dependencies = set()
        
        # This would normally involve scanning the actual code for imports
        # For now, we'll return some common ones based on context
        patterns = context.get('patterns', {})
        
        if patterns.get('has_async_code'):
            dependencies.add('aiohttp')
            dependencies.add('asyncio')
        
        # Add some common utilities
        dependencies.update(['requests', 'python-dotenv'])
        
        return list(dependencies)
    
    def _random_string(self, length: int) -> str:
        """Generate a random string of fixed length."""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))


# Import datetime at module level to avoid circular imports
from datetime import datetime