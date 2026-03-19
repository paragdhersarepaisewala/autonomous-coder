
import logging
import time

repo_dict = {
    'id': 12345,
    'full_name': "test/repo",
    'name': "repo",
    'description': "desc",
    'language': "Python",
    'stars': 100,
    'topics': ["test"],
    'clone_url': "https://github.com/test/repo.git",
    'default_branch': "main"
}

context_dict = {
    'language': 'Python',
    'structure': {'main_directories': ['src'], 'has_tests': True, 'has_docs': False, 'python_packages': ['src']},
    'patterns': {'has_classes': True, 'has_functions': True, 'has_async_code': False, 'uses_type_hints': False},
    'dependencies': {'package_managers': ['pip'], 'dependencies': ['requests']},
    'missing_features': [{'type': 'missing_file', 'description': 'README'}]
}

try:
    print("Testing string + int:")
    try:
        s = "test " + 123
        print(f"Result: {s}")
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
        
    print("\nTesting string % int:")
    try:
        s = "test %d" % "abc"
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")

except Exception as e:
    print(f"General error: {e}")
