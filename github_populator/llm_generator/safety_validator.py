import ast
import logging
import re
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Tuple, Optional
from ..context_analysis.analyzer import ContextAnalyzer


class SafetyValidator:
    """Validates LLM-generated code for safety and quality."""
    
    def __init__(self):
        """Initialize the safety validator."""
        self.logger = logging.getLogger(__name__)
        self.context_analyzer = ContextAnalyzer()
        
        # Dangerous patterns to check for
        self.dangerous_patterns = [
            (r'eval\s*\(', 'Use of eval() can be dangerous'),
            (r'exec\s*\(', 'Use of exec() can be dangerous'),
            (r'__import__\s*\(', 'Dynamic imports can be risky'),
            (r'open\s*\([^)]*[\'\"].*[\'\"].*[\'\"w]', 'File opening with write modes'),
            (r'subprocess\.call|subprocess\.run|subprocess\.Popen', 'Subprocess usage'),
            (r'os\.system|os\.popen', 'OS system calls'),
            (r'pickle\.loads?|marshal\.loads?', 'Unsafe deserialization'),
            (r'input\s*\(', 'Raw input() usage (in generated context)'),
            (r'requests\.get|requests\.post|urllib', 'HTTP requests without context'),
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [(re.compile(pattern, re.IGNORECASE), msg) 
                                for pattern, msg in self.dangerous_patterns]
    
    def validate_code(self, 
                     code: str, 
                     language: str = "Python",
                     filename: str = "generated_file") -> Tuple[bool, List[str]]:
        """Validate generated code for safety and basic correctness.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not code or not code.strip():
            issues.append("Generated code is empty")
            return False, issues
        
        # Language-specific validation
        if language.lower() == "python":
            is_valid, lang_issues = self._validate_python_code(code, filename)
            issues.extend(lang_issues)
            if not is_valid:
                return False, issues
        elif language.lower() in ["javascript", "typescript"]:
            is_valid, lang_issues = self._validate_javascript_code(code, filename)
            issues.extend(lang_issues)
            if not is_valid:
                return False, issues
        else:
            # For other languages, do basic checks
            is_valid, lang_issues = self._validate_generic_code(code, filename, language)
            issues.extend(lang_issues)
            if not is_valid:
                return False, issues
        
        # Security pattern checking
        sec_issues = self._check_security_patterns(code)
        issues.extend(sec_issues)
        
        # Basic quality checks
        qual_issues = self._check_quality(code, language)
        issues.extend(qual_issues)
        
        # If we have issues, determine if they're severe enough to reject
        if issues:
            # Filter out warnings - only reject on serious issues
            serious_issues = [issue for issue in issues 
                            if not issue.startswith("WARNING:")]
            if serious_issues:
                return False, serious_issues
        
        return True, issues
    
    def _validate_python_code(self, code: str, filename: str) -> Tuple[bool, List[str]]:
        """Validate Python code syntax."""
        issues = []
        try:
            # Parse the code to check for syntax errors
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Python syntax error: {str(e)}")
            return False, issues
        except Exception as e:
            issues.append(f"Error parsing Python code: {str(e)}")
            return False, issues
        
        return True, issues
    
    def _validate_javascript_code(self, code: str, filename: str) -> Tuple[bool, List[str]]:
        """Validate JavaScript/TypeScript code syntax using node."""
        issues = []
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_filename = f.name
            
            # Try to check syntax with node
            try:
                result = subprocess.run(
                    ['node', '--check', temp_filename],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    issues.append(f"JavaScript syntax error: {result.stderr.strip()}")
                    return False, issues
                    
            except FileNotFoundError:
                # Node not available, skip syntax check but warn
                issues.append("WARNING: Node.js not available for JavaScript syntax validation")
            except subprocess.TimeoutExpired:
                issues.append("WARNING: JavaScript syntax check timed out")
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_filename)
                except:
                    pass
                    
        except Exception as e:
            issues.append(f"Error validating JavaScript code: {str(e)}")
            return False, issues
        
        return True, issues
    
    def _validate_generic_code(self, code: str, filename: str, language: str) -> Tuple[bool, List[str]]:
        """Validate code for languages we don't have specific validators for."""
        issues = []
        
        # Basic checks - at least some non-whitespace content
        if not code.strip():
            issues.append("Generated code is empty or only whitespace")
            return False, issues
        
        # Warn that we can't do thorough validation
        issues.append(f"WARNING: Limited validation available for {language} language")
        
        return True, issues
    
    def _check_security_patterns(self, code: str) -> List[str]:
        """Check for dangerous patterns in the code."""
        issues = []
        
        for pattern, message in self.compiled_patterns:
            if pattern.search(code):
                issues.append(f"SECURITY WARNING: {message}")
        
        # Additional specific checks
        # Check for hardcoded credentials patterns
        credential_patterns = [
            r'password\s*[\'"][\w!@#$%^&*()_+]{3,}[\'"]',
            r'api[_-]?key\s*[\'"][\w\-_]{10,}[\'"]',
            r'secret\s*[\'"][\w\-_]{10,}[\'"]',
            r'token\s*[\'"][\w\-_]{10,}[\'"]',
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("SECURITY WARNING: Potential hardcoded credentials detected")
                break  # Only report once to avoid spam
        
        return issues
    
    def _check_quality(self, code: str, language: str) -> List[str]:
        """Perform basic quality checks on the code."""
        issues = []
        lines = code.split('\n')
        
        # Check for obvious placeholder content
        placeholder_indicators = [
            'TODO',
            'FIXME',
            'XXX',
            'PLACEHOLDER',
            'YOUR CODE HERE',
            'IMPLEMENT ME',
            'lst[',
            'dict{',
        ]
        
        placeholder_count = 0
        for line in lines:
            for indicator in placeholder_indicators:
                if indicator in line.upper():
                    placeholder_count += 1
                    break
        
        if placeholder_count > len(lines) * 0.3:  # More than 30% placeholders
            issues.append("WARNING: Code contains too many placeholder comments")
        
        # Check for extremely short code (likely not useful)
        if len(code.strip()) < 20:
            issues.append("WARNING: Generated code is extremely short and likely not useful")
        
        # Check for excessive blank lines or whitespace
        non_empty_lines = [line for line in lines if line.strip()]
        if len(non_empty_lines) < 3:
            issues.append("WARNING: Generated code has very few substantive lines")
        
        # Language-specific quality checks
        if language.lower() == "python":
            # Check for missing docstrings in functions/classes
            try:
                tree = ast.parse(code)
                functions_without_docs = 0
                classes_without_docs = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function has a docstring
                        if not (node.body and isinstance(node.body[0], ast.Expr) 
                               and isinstance(node.body[0].value, ast.Constant) 
                               and isinstance(node.body[0].value.value, str)):
                            functions_without_docs += 1
                    elif isinstance(node, ast.ClassDef):
                        # Check if class has a docstring
                        if not (node.body and isinstance(node.body[0], ast.Expr) 
                               and isinstance(node.body[0].value, ast.Constant) 
                               and isinstance(node.body[0].value.value, str)):
                            classes_without_docs += 1
                
                total_funcs_classes = functions_without_docs + classes_without_docs
                if total_funcs_classes > 0:
                    issues.append(f"INFO: {total_funcs_classes} functions/classes missing docstrings")
                    
            except:
                pass  # If we can't parse, skip this check
        
        return issues