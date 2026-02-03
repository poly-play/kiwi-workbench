import os
from google import genai
from google.genai import types
from typing import Dict, Any, Optional
from engine.clients.base_client import BaseClient

class GeminiClient(BaseClient):
    """
    Client for interacting with Google Gemini API using the official Google GenAI SDK (V1).
    """
    def __init__(self, config: Dict[str, Any] = None, model: str = None):
        # Allow overriding model via init
        self.model_override = model
        super().__init__(config)

    def _validate_config(self):
        # 1. API Key
        self.api_key = self.config.get('api_key') or os.environ.get('GEMINI_API_KEY') or os.environ.get('VERTEX_API_KEY')
        if not self.api_key:
            raise ValueError("API Key is missing. Set GEMINI_API_KEY or VERTEX_API_KEY in .env.")
            
        # 2. Model Selection
        # Priority: Init Argument > Config > Default
        self.model_name = self.model_override or self.config.get('model', 'gemini-3-flash-preview')
        
        # 3. Client Initialization
        # The new SDK uses a client instance directly
        self.client = genai.Client(api_key=self.api_key)

    def generate_content(self, prompt: str) -> str:
        """
        Wrapper to generate content from text prompt.
        """
        try:
            # Configurable Generation Config
            # The V1 SDK uses types.GenerateContentConfig
            gen_config_dict = self.config.get('generation_config', {
                "temperature": 0.7,
            })
            
            # Map dict to config object if needed, or pass as kwargs if supported.
            # The client.models.generate_content supports config dict in some versions, 
            # but let's stick to basic kwargs for now to be safe, or just config=types.GenerateContentConfig(...)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**gen_config_dict)
            )
            
            if response.text:
                return response.text
            return ""
            
        except Exception as e:
            print(f"[Error] Gemini SDK Call Failed: {e}")
            return ""

    def generate_image(self, prompt: str, output_path: str, model: str = "gemini-3-pro-image-preview") -> Optional[str]:
        """
        Generate an image using the Gemini model and save it to the output path.
        Supports both 'gemini' (via generate_content) and 'imagen' (via generate_images) models.
        
        Args:
            prompt: The image description.
            output_path: Absolute path to save the generated image.
            model: Model to use (default: gemini-3-pro-image-preview).
            
        Returns:
            output_path if successful, None otherwise.
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            print(f"[GeminiClient] Generating image with model '{model}'...")
            
            # Hybrid Strategy:
            # 1. Gemini Models (e.g. gemini-3-pro-image-preview) use generate_content returning inline_data
            if "gemini" in model.lower():
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=None # Do not enforce mime_type, let model decide
                )
                
                # Extract image processing
                if response.candidates:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            with open(output_path, "wb") as f:
                                f.write(part.inline_data.data)
                            print(f"[GeminiClient] Image saved to: {output_path}")
                            return output_path
                print("[GeminiClient] No inline image data found in response.")
                return None

            # 2. Imagen Models (e.g. imagen-3.0) use generate_images
            else:
                response = self.client.models.generate_images(
                    model=model,
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                    )
                )
                
                if response.generated_images:
                    image_bytes = response.generated_images[0].image.image_bytes
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    print(f"[GeminiClient] Image saved to: {output_path}")
                    return output_path
                    
                print("[GeminiClient] No image returned in response.")
                return None
            
        except Exception as e:
            print(f"[Error] Gemini Image Generation Failed: {e}")
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
        # Load from project root (assuming script is run from project root or engine root)
        # Try a few paths
        load_dotenv(".env") 
        load_dotenv("engine/.env")
    except ImportError:
        print("python-dotenv not installed, assuming env vars are set manually.")

    try:
        # Ensure GEMINI_API_KEY is set in env
        client = GeminiClient()
        print(f"Testing Model: {client.model_name}")
        print(client.generate_content("Say 'Hello, I am connected to Gemini via SDK!'"))
    except Exception as e:
        print(f"Test Failed: {e}")
