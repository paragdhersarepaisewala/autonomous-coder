import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from .gemini_client import GeminiAIClient
from .prompt_engineer import PromptEngineer
from .safety_validator import SafetyValidator
from ..context_analysis.analyzer import ContextAnalyzer
from ..feature_generation.generator import FeatureGenerator as TemplateFeatureGenerator
from ..utils.config import config


class LLMSynthesizedFeatureGenerator:
    """Generates features using LLM with fallback to template-based generation."""
    
    def __init__(self):
        """Initialize the LLM feature synthesizer."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        try:
            self.llm_client = GeminiAIClient()
            self.llm_available = self.llm_client.is_available()
            if self.llm_available:
                self.logger.info("Gemini AI client is available for feature generation")
            else:
                self.logger.warning("Gemini AI client not available, will use template fallback")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI client: {e}")
            self.llm_available = False
            self.llm_client = None
        
        self.prompt_engineer = PromptEngineer()
        self.safety_validator = SafetyValidator()
        self.context_analyzer = ContextAnalyzer()
        self.template_generator = TemplateFeatureGenerator()
        
        # Configuration
        self.feature_type = config.get('FEATURE_TYPE', 'utility')
        self.use_llm_first = config.get('USE_LLM_FIRST', 'true').lower() == 'true'
        self.fallback_to_templates = config.get('FALLBACK_TO_TEMPLATES', 'true').lower() == 'true'
        self.max_llm_retries = config.get_int('MAX_LLM_RETRIES', 2)
        self.llm_retry_delay = config.get_int('LLM_RETRY_DELAY', 2)  # seconds
    
    def generate_feature(self, 
                        repository: Dict[str, Any], 
                        context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a feature using LLM with template fallback.
        
        Returns:
            Feature idea dictionary or None if generation failed
        """
        self.logger.info(f"Generating feature for {repository['full_name']} using {'LLM' if self.use_llm_first and self.llm_available else 'template'} approach")
        
        # Try LLM generation first if configured and available
        if self.use_llm_first and self.llm_available:
            feature_idea = self._generate_via_llm(repository, context)
            if feature_idea:
                self.logger.info("Successfully generated feature using LLM")
                return feature_idea
            else:
                self.logger.warning("LLM feature generation failed")
        
        # Fallback to template generation
        if self.fallback_to_templates:
            self.logger.info("Falling back to template-based feature generation")
            return self._generate_via_templates(repository, context)
        else:
            self.logger.error("LLM generation failed and template fallback is disabled")
            return None
    
    def _generate_via_llm(self, 
                         repository: Dict[str, Any], 
                         context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate feature using LLM with self-correction loop."""
        last_raw_response = None
        last_validation_issues = []
        
        for attempt in range(self.max_llm_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"LLM generation attempt {attempt + 1}/{self.max_llm_retries + 1} (Self-Correction)")
                    time.sleep(self.llm_retry_delay)
                
                # Engineer the prompt
                try:
                    if attempt == 0 or not last_validation_issues:
                        # Initial attempt
                        prompt = self.prompt_engineer.engineer_prompt(
                            repository, 
                            context, 
                            self.feature_type
                        )
                    else:
                        # Repair attempt using feedback from previous failure
                        self.logger.info(f"Attempting to repair code based on {len(last_validation_issues)} issues")
                        prompt = self.prompt_engineer.engineer_repair_prompt(
                            last_raw_response,
                            last_validation_issues
                        )
                except Exception as prompt_error:
                    self.logger.error(f"Error engineering prompt: {prompt_error}")
                    break  # Don't retry if the prompt itself has an error
                
                # Generate content using LLM
                raw_response = self.llm_client.generate_content(
                    prompt,
                    temperature=0.7 if attempt == 0 else 0.4,  # Lower temperature for repair attempts
                    max_output_tokens=4096
                )
                
                if not raw_response:
                    self.logger.warning("LLM returned empty response")
                    continue
                
                last_raw_response = raw_response
                
                # Parse the LLM response
                parsed_result = self._parse_llm_response(raw_response)
                if not parsed_result:
                    self.logger.warning("Failed to parse LLM response")
                    last_validation_issues = ["Failed to parse the response format. Ensure you follow the === FILE: path === format."]
                    continue
                
                files_to_create, feature_description = parsed_result
                
                # Validate each file for safety
                all_files_valid = True
                validation_issues = []
                
                for file_info in files_to_create:
                    file_path = file_info['path']
                    file_content = file_info['content']
                    
                    # Determine language from file extension
                    language = self._get_language_from_extension(file_path)
                    
                    # Validate the code
                    is_valid, issues = self.safety_validator.validate_code(
                        file_content, 
                        language=language,
                        filename=file_path
                    )
                    
                    if not is_valid:
                        all_files_valid = False
                        validation_issues.extend([f"File '{file_path}': {issue}" for issue in issues])
                        self.logger.warning(f"Safety validation failed for {file_path}: {issues}")
                
                if not all_files_valid:
                    self.logger.warning(f"LLM-generated code failed safety validation: {validation_issues}")
                    last_validation_issues = validation_issues
                    continue  # Retry with feedback instead of breaking
                
                # If we got here, we have valid code
                feature_idea = {
                    'title': self._generate_feature_title(files_to_create, feature_description),
                    'description': feature_description,
                    'branch_name': f'llm-{self.feature_type}-{self._random_string(8)}',
                    'files_to_create': files_to_create,
                    'files_to_modify': [],  # We're only creating new files for safety
                    'repository_id': repository['id'],
                    'repository_name': repository['full_name'],
                    'generated_at': str(time.time()),
                    'feature_type': self.feature_type,
                    'generation_method': 'llm'
                }
                
                self.logger.info(f"Successfully generated and validated LLM feature: {feature_idea['title']}")
                return feature_idea
                
            except Exception as e:
                self.logger.error(f"Error in LLM generation attempt {attempt + 1}: {e}")
                if attempt == self.max_llm_retries:
                    self.logger.error("Max LLM retries exceeded")
        
        return None
    
    def _generate_via_templates(self, 
                               repository: Dict[str, Any], 
                               context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate feature using template-based approach."""
        try:
            self.logger.info("Generating feature using template-based approach")
            feature_idea = self.template_generator.generate_feature(
                repository, 
                context, 
                self.feature_type
            )
            
            if feature_idea:
                feature_idea['generation_method'] = 'template'
                self.logger.info(f"Successfully generated template feature: {feature_idea['title']}")
            
            return feature_idea
        except Exception as e:
            self.logger.error(f"Error in template-based feature generation: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Tuple[List[Dict[str, Any]], str]]:
        """Parse the LLM response to extract files and description.
        
        Expected format:
        === FILE: path/to/file.py ===
        [file content]
        === FILE: path/to/another_file.js ===
        [file content]
        FEATURE DESCRIPTION: [explanation]
        """
        try:
            self.logger.debug(f"Parsing LLM response of length {len(response)}")
            
            # Split by file markers
            sections = response.split('=== FILE: ')
            
            files_to_create = []
            feature_description = ""
            
            # Process each section
            for section in sections[1:]:  # Skip first empty section if present
                # Find the end of the file header
                if ' ===' not in section:
                    continue
                    
                # Split into header and content
                parts = section.split(' ===', 1)
                if len(parts) < 2:
                    continue
                
                file_path = parts[0].strip()
                remaining_content = parts[1].strip()
                
                # Check if this is the feature description section
                if file_path.startswith('FEATURE DESCRIPTION:'):
                    feature_description = file_path[len('FEATURE DESCRIPTION:'):].strip()
                    break
                
                # Extract the file content (everything after the first newline)
                content_parts = remaining_content.split('\n', 1)
                if len(content_parts) < 2:
                    # No content after the header
                    file_content = ""
                else:
                    file_content = content_parts[1].rstrip()  # Remove trailing whitespace
                
                # Validate that we have a reasonable file path
                if not file_path or '/' in file_path and '..' in file_path:
                    self.logger.warning(f"Suspicious file path: {file_path}")
                    continue
                
                files_to_create.append({
                    'path': file_path,
                    'content': file_content
                })
            
            # If we didn't find a feature description, look for it at the end
            if not feature_description and 'FEATURE DESCRIPTION:' in response:
                desc_start = response.find('FEATURE DESCRIPTION:')
                feature_description = response[desc_start + len('FEATURE DESCRIPTION:'):].strip()
                # Remove the description from the sections to avoid duplicate processing
                response = response[:desc_start]
                # Re-parse sections without the description
                sections = response.split('=== FILE: ')
                files_to_create = []
                for section in sections[1:]:
                    if ' ===' not in section:
                        continue
                    parts = section.split(' ===', 1)
                    if len(parts) < 2:
                        continue
                    file_path = parts[0].strip()
                    remaining_content = parts[1].strip()
                    
                    if file_path.startswith('FEATURE DESCRIPTION:'):
                        break
                    
                    content_parts = remaining_content.split('\n', 1)
                    if len(content_parts) < 2:
                        file_content = ""
                    else:
                        file_content = content_parts[1].rstrip()
                    
                    if file_path and '..' not in file_path:
                        files_to_create.append({
                            'path': file_path,
                            'content': file_content
                        })
            
            # Validate that we have at least one file
            if not files_to_create:
                self.logger.warning("No valid files found in LLM response")
                return None
            
            # If we still don't have a feature description, create a generic one
            if not feature_description:
                feature_description = f"Generated {len(files_to_create)} file(s) with useful functionality for the repository"
            
            self.logger.info(f"Parsed LLM response: {len(files_to_create)} files, description length {len(feature_description)}")
            return (files_to_create, feature_description)
            
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return None
    
    def _generate_feature_title(self, 
                               files_to_create: List[Dict[str, Any]], 
                               feature_description: str) -> str:
        """Generate a concise title for the feature."""
        if not files_to_create:
            return "Unknown Feature"
        
        # Use the first file to generate a title
        first_file = files_to_create[0]['path']
        
        # Extract meaningful name from file path
        if first_file.endswith('.py'):
            name = first_file[:-3]  # Remove .py
        elif first_file.endswith('.js') or first_file.endswith('.ts'):
            name = first_file[:-3]  # Remove .js or .ts
        else:
            name = first_file.split('.')[0]  # Remove extension
        
        # Convert snake_case or kebab-case to Title Case
        name = name.replace('_', ' ').replace('-', ' ').title()
        
        # If the name is too generic, make it more descriptive
        if name.lower() in ['utils', 'utility', 'helper', 'helpers']:
            name = f"Utility Module"
        elif 'test' in name.lower():
            name = f"Test Helper"
        elif 'api' in name.lower():
            name = f"API Client"
        elif 'valid' in name.lower():
            name = f"Validation Module"
        
        return f"Add {name}"
    
    def _get_language_from_extension(self, file_path: str) -> str:
        """Determine programming language from file extension."""
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        
        language_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'cs': 'C#',
            'go': 'Go',
            'rs': 'Rust',
            'php': 'PHP',
            'rb': 'Ruby',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'scala': 'Scala'
        }
        
        return language_map.get(extension, 'Unknown')
    
    def _random_string(self, length: int) -> str:
        """Generate a random string of fixed length."""
        import random
        import string
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))

