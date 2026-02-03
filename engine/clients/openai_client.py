import os
from typing import Dict, Any, Optional
from openai import OpenAI
from engine.clients.base_client import BaseClient

class OpenAIClient(BaseClient):
    """
    Client for interacting with OpenAI API.
    """
    def __init__(self, config: Dict[str, Any] = None, model: str = None):
        # Allow overriding model via init
        self.model_override = model
        super().__init__(config)

    def _validate_config(self):
        # 1. API Key
        # Supports reading from config 'api_key' or env var 'OPENAI_API_KEY'
        self.api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API Key is missing. Set OPENAI_API_KEY in .env or config.")
            
        # 2. Model Selection
        # Priority: Init Argument > Config > Default
        self.model_name = self.model_override or self.config.get('model', 'gpt-4o')
        
        # 3. Base URL (Optional, for proxies or custom endpoints)
        self.base_url = self.config.get('base_url') or os.environ.get('OPENAI_BASE_URL')
        
        # 4. Client Initialization
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate_content(self, prompt: str) -> str:
        """
        Simple wrapper to generate text content from a prompt.
        Uses chat.completions with a system/user message structure.
        """
        try:
            # 1. Prepare Messages
            # If prompt needs system context, it should probably be passed in differently,
            # but for a basic 'generate_content' interface, we treat it as a user message.
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 2. Configurable Generation Config
            gen_config_dict = self.config.get('generation_config', {
                "temperature": 0.7,
            })
            
            # 3. Call API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **gen_config_dict
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return ""
            
        except Exception as e:
            print(f"[Error] OpenAI API Call Failed: {e}")
            return ""

    def chat_completion(self, messages: list, **kwargs) -> Any:
        """
        Direct access to chat completion for more complex message structures (system, user, assistant).
        """
        try:
            # Merge defaults
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7
            }
            # Update with kwargs
            params.update(kwargs)
            
            response = self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            print(f"[Error] OpenAI Chat Completion Failed: {e}")
            return None

# Test stub
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
        
    try:
        from dotenv import load_dotenv
        # Try a few paths
        load_dotenv(".env") 
        load_dotenv("engine/.env")
    except ImportError:
        pass

    try:
        # Ensure OPENAI_API_KEY is set in env before running
        client = OpenAIClient()
        print(f"Testing Model: {client.model_name}")
        print(client.generate_content("Say 'Hello, I am connected to OpenAI!'"))
    except Exception as e:
        print(f"Test Failed: {e}")
