import sys
import os
sys.path.insert(0, 'github_populator')

# Test Gemini API directly
from google import genai

print('Testing Gemini API...')
api_key = 'AQ.Ab8RN6LsZIWAmrCtyswnQ6nhoHNvxFNLjtjXZ40Ebo7y8neR1w'

print(f'API Key: {api_key[:10]}...')

try:
    client = genai.Client(api_key=api_key)
    print('Client initialized successfully')
    
    # List available models
    print('Listing available models...')
    models = client.models.list()
    print('Available models:')
    for model in list(models)[:20]:  # Show first 20
        print(f'  - {model.name}')
    
    # Try gemini-2.5-flash
    print('\nTrying gemini-2.5-flash...')
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say OK if you can hear me',
            config={
                'temperature': 0.1,
                'max_output_tokens': 50,
            },
        )
        print(f'Response received: {response}')
        if response and response.text:
            print('SUCCESS with gemini-2.5-flash! Response:', response.text)
        else:
            print('Response has no text content')
            print('Response candidates:', response.candidates if hasattr(response, 'candidates') else 'N/A')
    except Exception as e:
        print('gemini-2.5-flash failed:', str(e)[:200])
    
    # Try gemini-2.0-flash
    print('\nTrying gemini-2.0-flash...')
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Say OK if you can hear me',
            config={
                'temperature': 0.1,
                'max_output_tokens': 10,
            },
        )
        if response and response.text:
            print('SUCCESS with gemini-2.0-flash! Response:', response.text)
    except Exception as e:
        print('gemini-2.0-flash failed:', str(e)[:100])
        
except Exception as e:
    print('ERROR:', e)
    import traceback
    traceback.print_exc()
