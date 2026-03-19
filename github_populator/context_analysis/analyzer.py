import os
import shutil
import logging
import ast
from typing import Dict, List, Optional, Any
import git
from ..utils.system_utils import safe_rmtree


class ContextAnalyzer:
    """Analyzes repository context to understand code structure and patterns."""
    
    def __init__(self):
        """Initialize the context analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def clone_repository(self, clone_url: str, repo_name: str) -> Optional[str]:
        """Clone a repository to a temporary directory."""
        try:
            # Create temp directory
            temp_dir = os.path.join(os.getcwd(), "temp_repos")
            os.makedirs(temp_dir, exist_ok=True)
            
            repo_path = os.path.join(temp_dir, repo_name)
            
            # Remove if exists
            safe_rmtree(repo_path)
            
            # Clone repository
            self.logger.info(f"Cloning repository {repo_name} to {repo_path}")
            git.Repo.clone_from(clone_url, repo_path)
            
            return repo_path
            
        except Exception as e:
            self.logger.error(f"Error cloning repository {clone_url}: {e}")
            return None
    
    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the cloned repository to understand its structure."""
        try:
            self.logger.info(f"Analyzing repository at {repo_path}")
            
            analysis = {
                'language': self._detect_primary_language(repo_path),
                'structure': self._analyze_directory_structure(repo_path),
                'patterns': self._detect_code_patterns(repo_path),
                'dependencies': self._analyze_dependencies(repo_path),
                'conventions': self._analyze_coding_conventions(repo_path),
                'missing_features': self._identify_potential_improvements(repo_path)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing repository at {repo_path}: {e}")
            return {}
    
    def cleanup_clone(self, repo_path: str):
        """Remove the cloned repository."""
        import time
        import gc
        try:
            temp_dir = os.path.dirname(repo_path)
            if os.path.exists(repo_path):
                # Force garbage collection to release file handles
                gc.collect()
                
                # Try to remove the directory with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        safe_rmtree(repo_path)
                        self.logger.info(f"Cleaned up cloned repository at {repo_path}")
                        break
                    except PermissionError as e:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"Cleanup attempt {attempt + 1} failed, retrying in 1 second...")
                            time.sleep(1)
                            gc.collect()
                        else:
                            self.logger.warning(f"Could not fully clean up repository {repo_path}: {e}")
            
            # Remove temp directory if empty
            if os.path.exists(temp_dir):
                try:
                    if not os.listdir(temp_dir):
                        os.rmdir(temp_dir)
                except:
                    pass
                
        except Exception as e:
            self.logger.warning(f"Error cleaning up repository {repo_path}: {e}")
    
    def _detect_primary_language(self, repo_path: str) -> str:
        """Detect the primary programming language of the repository."""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        
        extension_count = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories that aren't source code
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', 'venv', 'env', 'build', 'dist'}]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in language_extensions:
                    language = language_extensions[ext]
                    extension_count[language] = extension_count.get(language, 0) + 1
        
        if extension_count:
            # Find language with maximum count
            return max(extension_count.items(), key=lambda x: x[1])[0]
        return 'Unknown'
    
    def _analyze_directory_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the directory structure of the repository."""
        structure = {
            'has_tests': False,
            'has_docs': False,
            'has_examples': False,
            'main_directories': [],
            'file_count': 0,
            'python_packages': [] if self._detect_primary_language(repo_path) == 'Python' else None
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-source directories
            rel_root = os.path.relpath(root, repo_path)
            if rel_root.startswith('.') or any(part in rel_root for part in ['__pycache__', 'node_modules', '.git']):
                continue
                
            # Check for special directories
            dir_name = os.path.basename(root)
            if dir_name in ['test', 'tests']:
                structure['has_tests'] = True
            elif dir_name in ['docs', 'doc']:
                structure['has_docs'] = True
            elif dir_name in ['examples', 'example']:
                structure['has_examples'] = True
            
            # Count files
            structure['file_count'] += len([f for f in files if not f.startswith('.')])
            
            # For Python, identify packages
            if self._detect_primary_language(repo_path) == 'Python' and '__init__.py' in files:
                rel_path = os.path.relpath(root, repo_path)
                if rel_path != '.':
                    structure['python_packages'].append(rel_path.replace(os.sep, '.'))
        
        # Get main directories (top level)
        try:
            items = os.listdir(repo_path)
            structure['main_directories'] = [
                item for item in items 
                if os.path.isdir(os.path.join(repo_path, item)) and not item.startswith('.')
            ]
        except Exception:
            pass
        
        return structure
    
    def _detect_code_patterns(self, repo_path: str) -> Dict[str, Any]:
        """Detect common code patterns in the repository."""
        patterns = {
            'has_classes': False,
            'has_functions': False,
            'has_async_code': False,
            'uses_type_hints': False,
            'has_context_managers': False,
            'has_decorators': False,
            'common_design_patterns': []
        }
        
        # Only analyze Python files for now
        if self._detect_primary_language(repo_path) != 'Python':
            return patterns
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', 'build', 'dist'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Parse AST
                        try:
                            tree = ast.parse(content)
                            
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    patterns['has_classes'] = True
                                elif isinstance(node, ast.FunctionDef):
                                    patterns['has_functions'] = True
                                    if node.returns:
                                        patterns['uses_type_hints'] = True
                                    for arg in node.args.args:
                                        if arg.annotation:
                                            patterns['uses_type_hints'] = True
                                elif isinstance(node, ast.AsyncFunctionDef):
                                    patterns['has_async_code'] = True
                                elif isinstance(node, ast.With):
                                    patterns['has_context_managers'] = True
                                elif isinstance(node, ast.FunctionDef) and node.decorator_list:
                                    patterns['has_decorators'] = True
                        except SyntaxError:
                            # Skip files with syntax errors
                            continue
                            
                    except Exception:
                        # Skip unreadable files
                        continue
        
        return patterns
    
    def _analyze_dependencies(self, repo_path: str) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            'package_managers': [],
            'dependencies': [],
            'dev_dependencies': []
        }
        
        # Check for common dependency files
        dep_files = {
            'requirements.txt': 'pip',
            'setup.py': 'setuptools',
            'pyproject.toml': 'poetry/flit',
            'Pipfile': 'pipenv',
            'package.json': 'npm/yarn',
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'Cargo.toml': 'cargo',
            'go.mod': 'go modules'
        }
        
        for dep_file, manager in dep_files.items():
            file_path = os.path.join(repo_path, dep_file)
            if os.path.exists(file_path):
                dependencies['package_managers'].append(manager)
                
                # Parse the file for actual dependencies (simplified)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Very basic parsing - in reality you'd want proper parsers
                        if manager == 'pip' and dep_file == 'requirements.txt':
                            lines = content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('#') and '==' in line or '>=' in line or '<=' in line:
                                    pkg = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                                    if pkg:
                                        dependencies['dependencies'].append(pkg)
                except Exception:
                    pass  # Failed to read/parse, continue
        
        return dependencies
    
    def _analyze_coding_conventions(self, repo_path: str) -> Dict[str, Any]:
        """Analyze coding conventions used in the repository."""
        conventions = {
            'indent_style': 'unknown',
            'indent_size': 4,
            'max_line_length': 88,  # Default for black/formatter
            'quote_style': 'double',
            'has_linter_config': False,
            'has_formatter_config': False
        }
        
        # Check for config files
        config_indicators = {
            '.flake8': 'flake8',
            'setup.cfg': 'setuptools',
            'pyproject.toml': 'black/flake8/isort',
            '.eslintrc.js': 'eslint',
            '.eslintrc.json': 'eslint',
            'tsconfig.json': 'typescript'
        }
        
        for config_file, indicator in config_indicators.items():
            if os.path.exists(os.path.join(repo_path, config_file)):
                conventions['has_linter_config'] = True
                if indicator in ['black', 'pyproject.toml']:
                    conventions['has_formatter_config'] = True
        
        # Analyze a sample of Python files for indentation style
        if self._detect_primary_language(repo_path) == 'Python':
            indent_spaces = []
            indent_tabs = []
            
            for root, dirs, files in os.walk(repo_path):
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', 'build', 'dist'}]
                
                for file in files[:5]:  # Sample first 5 files
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                for i, line in enumerate(f):
                                    if i > 50:  # Only check first 50 lines
                                        break
                                    if line.startswith(' ') or line.startswith('\t'):
                                        if line.startswith(' '):
                                            # Count leading spaces
                                            indent_spaces.append(len(line) - len(line.lstrip(' ')))
                                        elif line.startswith('\t'):
                                            indent_tabs.append(1)
                                        break
                        except Exception:
                            continue
            
            if indent_spaces:
                conventions['indent_style'] = 'spaces'
                if indent_spaces:
                    # Find most common indentation size
                    from collections import Counter
                    indent_counter = Counter(indent_spaces)
                    if indent_counter:
                        conventions['indent_size'] = indent_counter.most_common(1)[0][0]
                    else:
                        conventions['indent_size'] = 4
                else:
                    conventions['indent_size'] = 4
            elif indent_tabs:
                conventions['indent_style'] = 'tabs'
        
        return conventions
    
    def _identify_potential_improvements(self, repo_path: str) -> List[Dict[str, str]]:
        """Identify potential areas for improvement in the repository."""
        improvements = []
        
        # Check for missing common files
        common_files = {
            'README.md': 'Missing README file',
            'LICENSE': 'Missing license file',
            '.gitignore': 'Missing .gitignore file',
            'requirements.txt': 'Missing requirements.txt (for Python)',
            'setup.py': 'Missing setup.py/pyproject.toml (for Python packaging)',
            'tests/': 'Missing tests directory',
            'docs/': 'Missing documentation directory'
        }
        
        for file_path, description in common_files.items():
            full_path = os.path.join(repo_path, file_path)
            if not os.path.exists(full_path):
                improvements.append({
                    'type': 'missing_file',
                    'description': description,
                    'suggested_solution': f'Add {file_path}'
                })
        
        # For Python projects, check for missing type hints
        if self._detect_primary_language(repo_path) == 'Python':
            type_hint_usage = self._detect_code_patterns(repo_path).get('uses_type_hints', False)
            if not type_hint_usage:
                improvements.append({
                    'type': 'missing_feature',
                    'description': 'Missing type hints in function signatures',
                    'suggested_solution': 'Add type hints to improve code clarity and IDE support'
                })
        
        return improvements

