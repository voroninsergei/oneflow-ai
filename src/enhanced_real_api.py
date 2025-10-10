"""
OneFlow.AI - Enhanced Real API Integration
Улучшенная интеграция с реальными API

Complete implementation with retry logic, rate limiting, and error handling.
Полная реализация с retry логикой, rate limiting и обработкой ошибок.
"""

import os
import time
import json
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datetime import datetime, timedelta
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== Utility Classes ====================

class RateLimiter:
    """
    Rate limiter to prevent API abuse.
    Ограничитель запросов для предотвращения превышения лимитов API.
    """
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed.
            time_window: Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_proceed(self) -> bool:
        """Check if request can proceed."""
        now = datetime.now()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < timedelta(seconds=self.time_window)]
        
        return len(self.requests) < self.max_requests
    
    def add_request(self):
        """Record a new request."""
        self.requests.append(datetime.now())
    
    def wait_time(self) -> float:
        """Calculate wait time until next request is allowed."""
        if not self.requests:
            return 0.0
        
        oldest = min(self.requests)
        elapsed = (datetime.now() - oldest).total_seconds()
        
        if elapsed >= self.time_window:
            return 0.0
        
        return self.time_window - elapsed


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retry logic with exponential backoff.
    Декоратор для retry логики с экспоненциальной задержкой.
    
    Args:
        max_retries: Maximum number of retries.
        base_delay: Base delay in seconds.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            
        return wrapper
    return decorator


class APIKeyManager:
    """
    Manage API keys from environment or config file.
    Управление API ключами из окружения или конфигурационного файла.
    """
    
    def __init__(self, config_file: str = '.api_keys.json'):
        self.config_file = config_file
        self.keys = {}
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from file and environment."""
        # Try to load from file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.keys = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load API keys from file: {e}")
        
        # Override with environment variables
        env_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'stability': os.getenv('STABILITY_API_KEY'),
            'elevenlabs': os.getenv('ELEVENLABS_API_KEY'),
        }
        
        for provider, key in env_keys.items():
            if key:
                self.keys[provider] = key
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        return self.keys.get(provider.lower())
    
    def has_key(self, provider: str) -> bool:
        """Check if API key exists."""
        return provider.lower() in self.keys and bool(self.keys[provider.lower()])


# Global instances
_key_manager = APIKeyManager()
_rate_limiters = {
    'openai': RateLimiter(max_requests=60, time_window=60),
    'anthropic': RateLimiter(max_requests=50, time_window=60),
    'stability': RateLimiter(max_requests=150, time_window=60),
    'elevenlabs': RateLimiter(max_requests=120, time_window=60),
}


# ==================== OpenAI Provider ====================

class EnhancedOpenAIProvider:
    """
    Enhanced OpenAI provider with retry and rate limiting.
    Улучшенный OpenAI провайдер с retry и rate limiting.
    """
    
    def __init__(self, name: str = 'openai'):
        self.name = name
        self.rate_limiter = _rate_limiters['openai']
        
        if not _key_manager.has_key('openai'):
            logger.warning("OpenAI API key not configured. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _call_gpt(self, prompt: str, model: str = 'gpt-3.5-turbo', 
                  temperature: float = 0.7, max_tokens: int = 500) -> Dict[str, Any]:
        """Call OpenAI GPT API with retry logic."""
        if self.mock_mode:
            return {
                'provider': self.name,
                'model': model,
                'response': f'[Mock] GPT response for: {prompt[:50]}...',
                'tokens_used': len(prompt.split()) * 2,
                'cost': 0.0
            }
        
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            import openai
            openai.api_key = _key_manager.get_key('openai')
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            self.rate_limiter.add_request()
            
            # Calculate cost based on model
            cost_per_1k = {
                'gpt-3.5-turbo': 0.002,
                'gpt-4': 0.03,
                'gpt-4-turbo': 0.01
            }.get(model, 0.002)
            
            tokens_used = response.usage.total_tokens
            cost = (tokens_used / 1000) * cost_per_1k
            
            return {
                'provider': self.name,
                'model': response.model,
                'response': response.choices[0].message.content,
                'tokens_used': tokens_used,
                'cost': cost,
                'finish_reason': response.choices[0].finish_reason
            }
            
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _call_dalle(self, prompt: str, size: str = '1024x1024', 
                    quality: str = 'standard', n: int = 1) -> Dict[str, Any]:
        """Call OpenAI DALL-E API with retry logic."""
        if self.mock_mode:
            return {
                'provider': self.name,
                'model': 'dall-e-3',
                'image_url': f'[Mock] Image URL for: {prompt[:50]}...',
                'cost': 0.0
            }
        
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            import openai
            openai.api_key = _key_manager.get_key('openai')
            
            response = openai.Image.create(
                prompt=prompt,
                n=n,
                size=size,
                quality=quality
            )
            
            self.rate_limiter.add_request()
            
            # Calculate cost based on size and quality
            cost_map = {
                ('1024x1024', 'standard'): 0.040,
                ('1024x1024', 'hd'): 0.080,
                ('512x512', 'standard'): 0.018,
            }
            cost = cost_map.get((size, quality), 0.040)
            
            return {
                'provider': self.name,
                'model': 'dall-e-3',
                'image_url': response.data[0].url,
                'revised_prompt': response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None,
                'cost': cost
            }
            
        except ImportError:
            logger.error("OpenAI package not installed. Run: pip install openai")
            raise
        except Exception as e:
            logger.error(f"DALL-E API error: {e}")
            raise
    
    def __call__(self, prompt: str, task_type: str = 'text', **kwargs) -> Dict[str, Any]:
        """
        Execute request based on task type.
        
        Args:
            prompt: Input prompt.
            task_type: 'text' for GPT or 'image' for DALL-E.
            **kwargs: Additional parameters.
        """
        try:
            if task_type == 'text':
                return self._call_gpt(prompt, **kwargs)
            elif task_type == 'image':
                return self._call_dalle(prompt, **kwargs)
            else:
                raise ValueError(f"Unknown task_type: {task_type}")
        except Exception as e:
            return {
                'provider': self.name,
                'error': str(e),
                'response': f'[Error] {str(e)}'
            }


# ==================== Anthropic Provider ====================

class EnhancedAnthropicProvider:
    """
    Enhanced Anthropic Claude provider.
    Улучшенный Anthropic Claude провайдер.
    """
    
    def __init__(self, name: str = 'anthropic'):
        self.name = name
        self.rate_limiter = _rate_limiters['anthropic']
        
        if not _key_manager.has_key('anthropic'):
            logger.warning("Anthropic API key not configured. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def __call__(self, prompt: str, model: str = 'claude-3-sonnet-20240229',
                 max_tokens: int = 1024, temperature: float = 1.0) -> Dict[str, Any]:
        """
        Call Anthropic Claude API.
        
        Args:
            prompt: Input prompt.
            model: Model name (claude-3-sonnet, claude-3-opus, claude-3-haiku).
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
        """
        if self.mock_mode:
            return {
                'provider': self.name,
                'model': model,
                'response': f'[Mock] Claude response for: {prompt[:50]}...',
                'tokens_used': len(prompt.split()) * 2,
                'cost': 0.0
            }
        
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(
                api_key=_key_manager.get_key('anthropic')
            )
            
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            self.rate_limiter.add_request()
            
            # Calculate cost based on model
            cost_per_1k = {
                'claude-3-opus-20240229': 0.015,
                'claude-3-sonnet-20240229': 0.003,
                'claude-3-haiku-20240307': 0.00025,
            }.get(model, 0.003)
            
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = (tokens_used / 1000) * cost_per_1k
            
            return {
                'provider': self.name,
                'model': response.model,
                'response': response.content[0].text,
                'tokens_used': tokens_used,
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'cost': cost,
                'stop_reason': response.stop_reason
            }
            
        except ImportError:
            logger.error("Anthropic package not installed. Run: pip install anthropic")
            return {
                'provider': self.name,
                'error': 'Anthropic package not installed',
                'response': f'[Mock] Claude response for: {prompt[:50]}...'
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


# ==================== Stability AI Provider ====================

class EnhancedStabilityProvider:
    """
    Enhanced Stability AI provider for image generation.
    Улучшенный Stability AI провайдер для генерации изображений.
    """
    
    def __init__(self, name: str = 'stability'):
        self.name = name
        self.rate_limiter = _rate_limiters['stability']
        
        if not _key_manager.has_key('stability'):
            logger.warning("Stability AI API key not configured. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def __call__(self, prompt: str, width: int = 1024, height: int = 1024,
                 steps: int = 30, cfg_scale: float = 7.0, 
                 samples: int = 1) -> Dict[str, Any]:
        """
        Generate image with Stability AI.
        
        Args:
            prompt: Image description.
            width: Image width (must be multiple of 64).
            height: Image height (must be multiple of 64).
            steps: Number of diffusion steps.
            cfg_scale: Guidance scale.
            samples: Number of images to generate.
        """
        if self.mock_mode:
            return {
                'provider': self.name,
                'model': 'stable-diffusion-xl',
                'image_base64': '[Mock] Base64 image data',
                'cost': 0.0
            }
        
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            import requests
            
            api_key = _key_manager.get_key('stability')
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "text_prompts": [{"text": prompt, "weight": 1}],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": samples,
                "steps": steps
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"Stability AI API error: {response.status_code} - {response.text}")
            
            self.rate_limiter.add_request()
            
            data = response.json()
            
            # Cost calculation (Stability uses credits)
            cost = 0.03  # Approximate cost per image
            
            return {
                'provider': self.name,
                'model': 'stable-diffusion-xl-1024-v1-0',
                'image_base64': data['artifacts'][0]['base64'],
                'seed': data['artifacts'][0]['seed'],
                'finish_reason': data['artifacts'][0]['finishReason'],
                'cost': cost
            }
            
        except ImportError:
            logger.error("Requests package not installed. Run: pip install requests")
            raise
        except Exception as e:
            logger.error(f"Stability AI API error: {e}")
            raise


# ==================== ElevenLabs Provider ====================

class EnhancedElevenLabsProvider:
    """
    Enhanced ElevenLabs provider for text-to-speech.
    Улучшенный ElevenLabs провайдер для text-to-speech.
    """
    
    def __init__(self, name: str = 'elevenlabs'):
        self.name = name
        self.rate_limiter = _rate_limiters['elevenlabs']
        
        if not _key_manager.has_key('elevenlabs'):
            logger.warning("ElevenLabs API key not configured. Using mock mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def __call__(self, text: str, voice_id: str = '21m00Tcm4TlvDq8ikWAM',
                 model_id: str = 'eleven_monolingual_v1',
                 stability: float = 0.5, similarity_boost: float = 0.5) -> Dict[str, Any]:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech.
            voice_id: Voice ID to use.
            model_id: Model ID (eleven_monolingual_v1, eleven_multilingual_v2).
            stability: Voice stability (0-1).
            similarity_boost: Voice similarity (0-1).
        """
        if self.mock_mode:
            return {
                'provider': self.name,
                'audio_bytes': b'[Mock] Audio data',
                'character_count': len(text),
                'cost': 0.0
            }
        
        # Rate limiting
        if not self.rate_limiter.can_proceed():
            wait_time = self.rate_limiter.wait_time()
            logger.info(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            import requests
            
            api_key = _key_manager.get_key('elevenlabs')
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
            
            self.rate_limiter.add_request()
            
            # Cost calculation (based on character count)
            character_count = len(text)
            cost = (character_count / 1000) * 0.30
            
            return {
                'provider': self.name,
                'audio_bytes': response.content,
                'character_count': character_count,
                'cost': cost,
                'format': 'audio/mpeg'
            }
            
        except ImportError:
            logger.error("Requests package not installed. Run: pip install requests")
            raise
        except Exception as e:
            logger.error(f"ElevenLabs API error: {e}")
            raise


# ==================== Provider Factory ====================

def create_enhanced_provider(provider_type: str) -> Any:
    """
    Factory function to create enhanced providers.
    Фабричная функция для создания улучшенных провайдеров.
    
    Args:
        provider_type: Type of provider ('gpt', 'image', 'audio').
    
    Returns:
        Provider instance.
    """
    providers = {
        'gpt': EnhancedOpenAIProvider,
        'openai': EnhancedOpenAIProvider,
        'anthropic': EnhancedAnthropicProvider,
        'claude': EnhancedAnthropicProvider,
        'image': EnhancedStabilityProvider,
        'stability': EnhancedStabilityProvider,
        'audio': EnhancedElevenLabsProvider,
        'elevenlabs': EnhancedElevenLabsProvider,
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return provider_class()


# ==================== Demo/Test Function ====================

def demo_enhanced_api():
    """
    Demonstrate enhanced API integration.
    Демонстрация улучшенной интеграции API.
    """
    print("=" * 60)
    print("Enhanced Real API Integration - Demo")
    print("=" * 60)
    
    # Test OpenAI GPT
    print("\n1. Testing OpenAI GPT...")
    openai_provider = create_enhanced_provider('gpt')
    result = openai_provider('Write a haiku about AI', task_type='text', model='gpt-3.5-turbo')
    print(f"   Response: {result.get('response', result.get('error'))}")
    print(f"   Tokens: {result.get('tokens_used', 'N/A')}")
    print(f"   Cost: ${result.get('cost', 0):.4f}")
    
    # Test Anthropic Claude
    print("\n2. Testing Anthropic Claude...")
    claude_provider = create_enhanced_provider('claude')
    result = claude_provider('Explain quantum computing in simple terms')
    print(f"   Response: {result.get('response', result.get('error'))[:100]}...")
    print(f"   Tokens: {result.get('tokens_used', 'N/A')}")
    print(f"   Cost: ${result.get('cost', 0):.4f}")
    
    # Test Stability AI
    print("\n3. Testing Stability AI...")
    stability_provider = create_enhanced_provider('stability')
    result = stability_provider('A beautiful sunset over mountains')
    print(f"   Image: {result.get('image_base64', result.get('error'))[:50]}...")
    print(f"   Cost: ${result.get('cost', 0):.4f}")
    
    # Test ElevenLabs
    print("\n4. Testing ElevenLabs...")
    elevenlabs_provider = create_enhanced_provider('elevenlabs')
    result = elevenlabs_provider('Hello, this is a test of text to speech.')
    print(f"   Audio size: {len(result.get('audio_bytes', b''))} bytes")
    print(f"   Characters: {result.get('character_count', 'N/A')}")
    print(f"   Cost: ${result.get('cost', 0):.4f}")
    
    print("\n" + "=" * 60)
    print("✓ Demo completed!")
    print("=" * 60)


if __name__ == '__main__':
    demo_enhanced_api()
