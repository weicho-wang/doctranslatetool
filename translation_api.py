"""
Translation API Module
Handles communication with the DeepSeek API for document translation.
"""
import os
import json
import requests
import logging
from time import sleep

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSeekTranslator:
    """
    Handles translation using DeepSeek API
    """
    def __init__(self, api_key=None, api_url=None):
        """
        Initialize translator with API credentials
        
        Args:
            api_key (str, optional): DeepSeek API key
            api_url (str, optional): DeepSeek API URL
        """
        # Load API key from config if not provided
        if api_key is None:
            api_key = self._load_api_key()
            
        self.api_key = api_key
        self.api_url = api_url or "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"  # Default model
        self.rate_limit_delay = 0.5  # Delay between API calls to avoid rate limiting (seconds)
        
        # Check if API key is available
        if not self.api_key:
            logger.warning("No API key provided. Translation will not work.")

    def _load_api_key(self):
        """
        Load API key from config file or environment variable
        
        Returns:
            str: API key if found, None otherwise
        """
        # Try loading from api_config.json
        try:
            with open('api_config.json') as f:
                config = json.load(f)
                if config.get("api_key"):
                    return config["api_key"]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
        # Try loading from API/API_Key.txt
        try:
            api_key_path = os.path.join("API", "API_Key.txt")
            if os.path.exists(api_key_path):
                with open(api_key_path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
        except Exception:
            pass
            
        # Try loading from environment variable
        return os.environ.get("DEEPSEEK_API_KEY")

    def translate_text(self, text, source_lang="zh", target_lang="en", preserve_format=True):
        """
        Translate text using DeepSeek API
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
            preserve_format (bool): Whether to preserve format markers
            
        Returns:
            str: Translated text
        """
        if not self.api_key:
            logger.error("Cannot translate: No API key provided")
            return text
            
        if not text.strip():
            return text
            
        # Create translation prompt
        if preserve_format:
            prompt = self._create_format_preserving_prompt(text, source_lang, target_lang)
        else:
            prompt = self._create_standard_prompt(text, source_lang, target_lang)
            
        try:
            # Calculate appropriate token limit
            # Adaptive token limit - 2x original text length but capped at valid range
            token_limit = min(max(len(text) * 2, 1000), 8000)
            
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,  # Lower temperature for more accurate translations
                    "max_tokens": token_limit,  # Adjusted to be within valid range
                    "stream": False  # Non-streaming response
                }
            )
            
            # Add delay to avoid rate limiting
            sleep(self.rate_limit_delay)
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                # Clean up the response if needed
                translated_text = self._clean_response(translated_text)
                return translated_text
            else:
                logger.error(f"API request failed: {response.status_code}, {response.text}")
                return text  # Return original text on error
                
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text on error
            
    def _create_standard_prompt(self, text, source_lang, target_lang):
        """
        Create a standard translation prompt
        
        Args:
            text (str): Text to translate
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            str: Formatted prompt
        """
        # Map language codes to full names if needed
        lang_map = {
            "zh": "Chinese",
            "en": "English",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "ru": "Russian"
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        return f"""Translate the following text from {source} to {target}. 
Maintain a professional tone and preserve the meaning accurately.

TEXT TO TRANSLATE:
{text}

TRANSLATION:
"""

    def _create_format_preserving_prompt(self, text, source_lang, target_lang):
        """
        Create a prompt that preserves formatting markers
        
        Args:
            text (str): Text to translate with format markers
            source_lang (str): Source language code
            target_lang (str): Target language code
            
        Returns:
            str: Formatted prompt
        """
        # Map language codes to full names if needed
        lang_map = {
            "zh": "Chinese",
            "en": "English",
            "ja": "Japanese",
            "ko": "Korean",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "ru": "Russian"
        }
        
        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)
        
        return f"""Translate the following text from {source} to {target}.
Important: Preserve ALL formatting markers exactly as they appear 
(such as HTML-like tags, markdown symbols, etc.)
Do not translate or modify anything inside angle brackets, curly braces, or other formatting markers.

TEXT TO TRANSLATE:
{text}

TRANSLATION (with all formatting markers preserved):
"""

    def _clean_response(self, response_text):
        """
        Clean up API response text
        
        Args:
            response_text (str): Raw response from API
            
        Returns:
            str: Cleaned translated text
        """
        # Remove "TRANSLATION:" prefix if present
        if response_text.strip().startswith("TRANSLATION:"):
            response_text = response_text.strip()[12:].strip()
            
        # Remove quotes if the entire text is quoted
        if (response_text.startswith('"') and response_text.endswith('"')) or \
           (response_text.startswith("'") and response_text.endswith("'")):
            response_text = response_text[1:-1]
            
        return response_text

    def set_model(self, model_name):
        """
        Set the model to use for translation
        
        Args:
            model_name (str): Model name
        """
        self.model = model_name
        logger.info(f"Set translation model to: {model_name}")
        
    def test_translation(self):
        """
        Test translation functionality
        
        Returns:
            bool: True if test passes, False otherwise
        """
        test_text = "This is a test sentence to check if the translation function is working properly."
        try:
            translated = self.translate_text(test_text, "zh", "en")
            logger.info(f"Translation test result: {translated}")
            return bool(translated and translated != test_text)
        except Exception as e:
            logger.error(f"Translation test failed: {str(e)}")
            return False

# Create a global instance for easy import
translator = DeepSeekTranslator()

if __name__ == "__main__":
    # When run directly, test the translator
    translator = DeepSeekTranslator()
    if translator.api_key:
        test_result = translator.test_translation()
        print(f"Translation test {'passed' if test_result else 'failed'}")
    else:
        print("No API key configured. Please set up your API key first.") 