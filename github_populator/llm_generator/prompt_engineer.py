import logging
from typing import Dict, Any, List, Optional


class PromptEngineer:
    """Engineers prompts for LLM-based feature generation."""
    
    def __init__(self):
        """Initialize the prompt engineer."""
        self.logger = logging.getLogger(__name__)
    
    def engineer_prompt(self, 
                       repository: Dict[str, Any],
                       context: Dict[str, Any],
                       feature_type: str = "utility") -> str:
        """Create a detailed prompt for the LLM based on repository analysis."""
        try:
            self.logger.info(f"Engineering prompt for {str(repository.get('full_name', 'Unknown'))} - {str(feature_type)} feature")
            
            # Extract key information from repository
            repo_name = str(repository.get('name', 'Unknown'))
            repo_full_name = str(repository.get('full_name', 'Unknown'))
            repo_description = str(repository.get('description', 'No description available'))
            repo_language = str(repository.get('language', 'Unknown'))
            repo_stars = int(repository.get('stars', 0))
            repo_topics = [str(t) for t in repository.get('topics', [])]
            
            # Extract key information from context analysis
            context_language = str(context.get('language', 'Unknown'))
            structure = context.get('structure', {})
            patterns = context.get('patterns', {})
            dependencies = context.get('dependencies', {})
            missing_features = context.get('missing_features', [])
            
            # Format directory structure
            main_dirs = [str(d) for d in structure.get('main_directories', [])]
            has_tests = bool(structure.get('has_tests', False))
            has_docs = bool(structure.get('has_docs', False))
            python_packages = [str(p) for p in structure.get('python_packages', [])]
            
            # Format code patterns
            has_classes = patterns.get('has_classes', False)
            has_functions = patterns.get('has_functions', False)
            has_async = patterns.get('has_async_code', False)
            uses_type_hints = patterns.get('uses_type_hints', False)
            has_context_managers = patterns.get('has_context_managers', False)
            has_decorators = patterns.get('has_decorators', False)
            
            # Format dependencies
            package_managers = dependencies.get('package_managers', [])
            deps_list = dependencies.get('dependencies', [])
            
            # Ensure all dependencies are strings
            package_managers = [str(pm) for pm in package_managers]
            deps_list = [str(dep) for dep in deps_list]
            
            # Format missing features/improvements
            missing_descriptions = [str(mf.get('description', '')) for mf in missing_features if mf.get('description')]
            
            # Build the prompt
            prompt_parts = [
                "# ROLE: Expert Software Engineer",
                "",
                "You are an expert software engineer tasked with generating a genuinely useful feature for an open source repository. Your goal is to create code that solves real problems and follows best practices.",
                "",
                "## REPOSITORY CONTEXT",
                f"- **Name**: {repo_name}",
                f"- **Full Name**: {repo_full_name}",
                f"- **Description**: {repo_description}",
                f"- **Primary Language**: {repo_language} (detected as {context_language} from analysis)",
                f"- **Stars**: {repo_stars}",
                f"- **Topics**: {', '.join(repo_topics) if repo_topics else 'None'}",
                "",
                "## CODEBASE STRUCTURE",
                f"- **Main Directories**: {', '.join(main_dirs) if main_dirs else 'None detected'}",
                f"- **Has Tests**: {'Yes' if has_tests else 'No'}",
                f"- **Has Documentation**: {'Yes' if has_docs else 'No'}",
                f"- **Python Packages**: {', '.join(python_packages) if python_packages else 'None'}",
                "",
                "## CODE PATTERNS DETECTED",
                f"- **Has Classes**: {'Yes' if has_classes else 'No'}",
                f"- **Has Functions**: {'Yes' if has_functions else 'No'}",
                f"- **Uses Async/Await**: {'Yes' if has_async else 'No'}",
                f"- **Uses Type Hints**: {'Yes' if uses_type_hints else 'No'}",
                f"- **Uses Context Managers**: {'Yes' if has_context_managers else 'No'}",
                f"- **Uses Decorators**: {'Yes' if has_decorators else 'No'}",
                "",
                "## DEPENDENCIES",
                f"- **Package Managers**: {', '.join(package_managers) if package_managers else 'None detected'}",
                f"- **Key Dependencies**: {', '.join(deps_list[:10]) if deps_list else 'None detected'}{'...' if len(deps_list) > 10 else ''}",
                "",
                "## RECENTLY IDENTIFIED GAPS/OPPORTUNITIES",
            ]
            
            if missing_descriptions:
                for i, desc in enumerate(missing_descriptions[:5], 1):  # Limit to top 5
                    prompt_parts.append(f"{i}. {desc}")
                if len(missing_descriptions) > 5:
                    prompt_parts.append(f"... and {len(missing_descriptions) - 5} more")
            else:
                prompt_parts.append("- No specific gaps identified from analysis")
            
            prompt_parts.extend([
                "",
                "## TASK: GENERATE A USEFUL FEATURE",
                f"Generate a {feature_type} feature that would be genuinely valuable to this repository.",
                "",
                "## REQUIREMENTS:",
                "1. Create production-quality, useful code - not trivial or toy examples",
                "2. Focus on solving real problems developers might face in this project",
                "3. Follow the repository's language conventions and best practices",
                "4. For the detected language, use idiomatic patterns and standard libraries",
                "5. Include appropriate documentation (docstrings/comments) explaining usage",
                "6. Make the feature self-contained where possible - minimize dependencies on existing code",
                "7. Do NOT suggest modifications to existing files unless it's a clear logical extension",
                "8. Focus on ADDITIVE features (new files/modules) that extend functionality",
                "9. Ensure the code is secure, efficient, and follows common software engineering principles",
                "",
                "## SUGGESTED FEATURE TYPES (based on context):",
            ])
            
            # Add contextual suggestions based on analysis
            suggestions = self._generate_contextual_suggestions(context, repository)
            if suggestions:
                for suggestion in suggestions:
                    prompt_parts.append(f"- {suggestion}")
            else:
                prompt_parts.append("- Create a utility module with helpful functions for common tasks")
                prompt_parts.append("- Add data validation or input sanitization helpers")
                prompt_parts.append("- Generate testing helpers or mock objects")
                prompt_parts.append("- Implement performance optimizations like caching or batching")
            
            prompt_parts.extend([
                "",
                "## OUTPUT FORMAT:",
                "Provide ONLY the code content for the new file(s).",
                "If generating multiple files, use this EXACT format:",
                "=== FILE: path/to/file.py ===",
                "[file content here]",
                "=== FILE: path/to/another_file.js ===",
                "[file content here]",
                "",
                "After the file(s), add:",
                "FEATURE DESCRIPTION: [Clear explanation of what this feature adds and why it's useful]",
                "",
                "## IMPORTANT CONSTRAINTS:",
                "- Generate ONLY code - no explanations outside the specified format",
                "- Do not include markdown code blocks or backticks",
                "- Ensure all file paths are relative to the repository root",
                "- Generate code that can stand alone and be immediately useful",
                "",
                "Now generate the feature:"
            ])
            
            prompt = "\n".join(prompt_parts)
            self.logger.debug(f"Generated prompt of length {len(prompt)} characters")
            return prompt
            
        except Exception as e:
            self.logger.error(f"Error engineering prompt: {e}")
            # Fallback to a simple prompt
            return self._create_fallback_prompt(repository, feature_type)
    
    def _generate_contextual_suggestions(self, 
                                       context: Dict[str, Any],
                                       repository: Dict[str, Any]) -> List[str]:
        """Generate contextual feature suggestions based on analysis."""
        suggestions = []
        language = context.get('language', 'Unknown')
        patterns = context.get('patterns', {})
        structure = context.get('structure', {})
        missing_features = context.get('missing_features', [])
        
        # Language-specific suggestions
        if language == 'Python':
            if not patterns.get('uses_type_hints', False):
                suggestions.append("Add type hints to improve code clarity and IDE support")
            if not patterns.get('has_context_managers', False):
                suggestions.append("Create context manager utilities for resource handling")
            if structure.get('has_tests', False):
                suggestions.append("Generate test helpers or mock objects to improve testability")
            else:
                suggestions.append("Create a basic test suite structure")
            if not any('valid' in mf.get('description', '').lower() for mf in missing_features):
                suggestions.append("Add input validation or data sanitization utilities")
                
        elif language in ['JavaScript', 'TypeScript']:
            suggestions.append("Create utility functions for common DOM or Node.js operations")
            suggestions.append("Add async/await helpers or promise utilities")
            if not structure.get('has_tests', False):
                suggestions.append("Generate a basic testing setup")
                
        elif language == 'Java':
            suggestions.append("Create helper classes for common Java enterprise patterns")
            suggestions.append("Add utility methods for collections or string processing")
            
        # General suggestions based on missing features
        missing_descriptions = ' '.join([mf.get('description', '').lower() for mf in missing_features])
        if 'readme' in missing_descriptions:
            suggestions.append("Create a comprehensive README with usage examples")
        if 'license' in missing_descriptions:
            suggestions.append("Add an appropriate open source license file")
        if 'test' in missing_descriptions:
            suggestions.append("Generate test files to improve test coverage")
        if 'doc' in missing_descriptions:
            suggestions.append("Create documentation or code comments for complex parts")
            
        # Dependency-based suggestions
        dependencies = context.get('dependencies', {})
        deps = dependencies.get('dependencies', [])
        if any('request' in dep.lower() for dep in deps) or any('http' in dep.lower() for dep in deps):
            suggestions.append("Create HTTP client utilities or wrapper functions")
        if any('data' in dep.lower() for dep in deps):
            suggestions.append("Add data processing or transformation helpers")
            
        # Limit suggestions to avoid overwhelming the prompt
        return suggestions[:5]
    
    def _create_fallback_prompt(self, 
                              repository: Dict[str, Any],
                              feature_type: str) -> str:
        """Create a simple fallback prompt if engineering fails."""
        repo_name = repository.get('name', 'Unknown')
        repo_description = repository.get('description', 'a software project')
        language = repository.get('language', 'Unknown')
        
        return f"""You are an expert software engineer. Generate a useful {feature_type} feature for a {language} repository called '{repo_name}' which is described as: {repo_description}

Create production-quality code that would be genuinely helpful to developers working on this project. Focus on practical utility.

OUTPUT FORMAT:
=== FILE: path/to/file.py ===
[file content]
FEATURE DESCRIPTION: [Explanation of what this feature adds and why it's useful]

Generate the feature now:"""

    def engineer_repair_prompt(self, 
                              original_response: str, 
                              validation_issues: List[str]) -> str:
        """Engineer a prompt to fix errors in a previous LLM response."""
        issues_str = "\n".join([f"- {issue}" for issue in validation_issues])
        
        return f"""# ROLE: Expert Software Engineer (Review and Repair)

Your previous response had the following validation issues:
{issues_str}

## ORIGINAL RESPONSE (with errors):
---
{original_response}
---

## TASK:
Fix the errors in the code while preserving the intended functionality. 

## REQUIREMENTS:
1. Return the COMPLETE fixed files.
2. Maintain the EXHIBITED structure and style (unifiing quotes, line length, etc.).
3. Fix the specific issues identified (e.g., syntax errors, unterminated strings, security risks).
4. Ensure the output format remains EXACTLY the same.

## OUTPUT FORMAT:
=== FILE: path/to/file.py ===
[fixed file content here]
...
FEATURE DESCRIPTION: [updated explanation]

Repair the code now:"""

