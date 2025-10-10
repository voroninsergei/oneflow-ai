"""
Real API Integration module for OneFlow.AI.
Модуль интеграции с реальными API для OneFlow.AI.

This module provides real implementations for AI provider integrations.
Этот модуль предоставляет реальные реализации интеграций с AI провайдерами.
"""

import os
import json
from typing import Optional, Dict, Any
from api_keys_module import get_key_manager


class RealGPTProvider:
    """
    Real GPT provider using OpenAI or Anthropic API.
    Реальный GPT провайдер с использованием OpenAI или Anthropic API.
    """
    
    def __init__(self, name: str = 'gpt', preferred_api: str = 'openai'):
        """
        Initialize real GPT provider.
        Инициализировать реальный GPT провайдер.
        
        Args:
            name: Provider name.
            preferred_api: Preferred API ('openai' or 'anthropic').
        """
        self.name = name
        self.preferred_api = preferred_api
        self.key_manager = get_key_manager()
        
    def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using real API.
        Генерация текста с использованием реального API.
        
        Args:
            prompt: Text prompt.
            **kwargs: Additional parameters (temperature, max_tokens, etc.).
        
        Returns:
            dict: Response with provider name and generated text.
        """
        # Try OpenAI first if preferred and available
        if self.preferred_api == 'openai' and self.key_manager.has_key('openai'):
            return self._call_openai(prompt, **kwargs)
        
        # Try Anthropic if available
        if self.key_manager.has_key('anthropic'):
            return self._call_anthropic(prompt, **kwargs)
        
        # Try OpenAI as fallback
        if self.key_manager.has_key('openai'):
            return self._call_openai(prompt, **kwargs)
        
        # Return error if no API keys available
        return {
            'provider': self.name,
            'error': 'No API keys configured for text generation',
            'response': f'[Mock] Response for: {prompt}'
        }
    
    def _call_openai(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Call OpenAI API.
        Вызов OpenAI API.
        """
        try:
            import openai
            openai.api_key = self.key_manager.get_key('openai')
            
            response = openai.ChatCompletion.create(
                model=kwargs.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 500)
            )
            
            return {
                'provider': f'{self.name}_openai',
                'response': response.choices[0].message.content,
                'model': response.model,
                'tokens_used': response.usage.total_tokens
            }
        except ImportError:
            return {
                'provider': self.name,
                'error': 'OpenAI package not installed. Run: pip install openai',
                'response': f'[Mock] Response for: {prompt}'
            }
        except Exception as e:
            return {
                'provider': self.name,
                'error': f'OpenAI API error: {str(e)}',
                'response': f'[Mock] Response for: {prompt}'
            }
    
    def _call_anthropic(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Call Anthropic API.
        Вызов Anthropic API.
        """
        try:
            import anthropic
            client = anthropic.Anthropic(
                api_key=self.key_manager.get_key('anthropic')
            )
            
            response = client.messages.create(
                model=kwargs.get('model', 'claude-3-sonnet-20240229'),
                max_tokens=kwargs.get('max_tokens', 1024),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'provider': f'{self.name}_anthropic',
                'response': response.content[0].text,
                'model': response.model,
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens
            }
        except ImportError:
            return {
                'provider': self.name,
                'error': 'Anthropic package not installed. Run: pip install anthropic',
                'response': f'[Mock] Response for: {prompt}'
            }
        except Exception as e:
            return {
                'provider': self.name,
                'error': f'Anthropic API error: {str(e)}',
                'response': f'[Mock] Response for: {prompt}'
            }


class RealImageProvider:
    """
    Real image provider using Stability AI or OpenAI DALL-E.
    Реальный провайдер изображений с использованием Stability AI или OpenAI DALL-E.
    """
    
    def __init__(self, name: str = 'image', preferred_api: str = 'stability'):
        """
        Initialize real image provider.
        Инициализировать реальный провайдер изображений.
        
        Args:
            name: Provider name.
            preferred_api: Preferred API ('stability' or 'openai').
        """
        self.name = name
        self.preferred_api = preferred_api
        self.key_manager = get_key_manager()
    
    def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate image using real API.
        Генерация изображения с использованием реального API.
        
        Args:
            prompt: Image description prompt.
            **kwargs: Additional parameters (size, quality, etc.).
        
        Returns:
            dict: Response with provider name and image URL/data.
        """
        # Try preferred API first
        if self.preferred_api == 'stability' and self.key_manager.has_key('stability'):
            return self._call_stability(prompt, **kwargs)
        
        # Try OpenAI DALL-E as fallback
        if self.key_manager.has_key('openai'):
            return self._call_openai_dalle(prompt, **kwargs)
        
        # Try Stability as fallback
        if self.key_manager.has_key('stability'):
            return self._call_stability(prompt, **kwargs)
        
        return {
            'provider': self.name,
            'error': 'No API keys configured for image generation',
            'image': f'[Mock] Image for: {prompt}'
        }
    
    def _call_stability(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Call Stability AI API.
        Вызов Stability AI API.
        """
        try:
            import requests
            
            api_key = self.key_manager.get_key('stability')
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": kwargs.get('cfg_scale', 7),
                    "height": kwargs.get('height', 1024),
                    "width": kwargs.get('width', 1024),
                    "samples": kwargs.get('samples', 1),
                    "steps": kwargs.get('steps', 30)
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'provider': f'{self.name}_stability',
                    'image': data['artifacts'][0]['base64'],
                    'seed': data['artifacts'][0]['seed'],
                    'format': 'base64'
                }
            else:
                return {
                    'provider': self.name,
                    'error': f'Stability API error: {response.status_code}',
                    'image': f'[Mock] Image for: {prompt}'
                }
        except ImportError:
            return {
                'provider': self.name,
                'error': 'Requests package not installed. Run: pip install requests',
                'image': f'[Mock] Image for: {prompt}'
            }
        except Exception as e:
            return {
                'provider': self.name,
                'error': f'Stability API error: {str(e)}',
                'image': f'[Mock] Image for: {prompt}'
            }
    
    def _call_openai_dalle(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Call OpenAI DALL-E API.
        Вызов OpenAI DALL-E API.
        """
        try:
            import openai
            openai.api_key = self.key_manager.get_key('openai')
            
            response = openai.Image.create(
                prompt=prompt,
                n=kwargs.get('n', 1),
                size=kwargs.get('size', '1024x1024')
            )
            
            return {
                'provider': f'{self.name}_openai',
                'image': response['data'][0]['url'],
                'format': 'url'
            }
        except Exception as e:
            return {
                'provider': self.name,
                'error': f'OpenAI DALL-E error: {str(e)}',
                'image': f'[Mock] Image for: {prompt}'
            }


class RealAudioProvider:
    """
    Real audio provider using ElevenLabs.
    Реальный аудио провайдер с использованием ElevenLabs.
    """
    
    def __init__(self, name: str = 'audio'):
        """
        Initialize real audio provider.
        Инициализировать реальный аудио провайдер.
        
        Args:
            name: Provider name.
        """
        self.name = name
        self.key_manager = get_key_manager()
    
    def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate audio using real API.
        Генерация аудио с использованием реального API.
        
        Args:
            prompt: Text to convert to speech.
            **kwargs: Additional parameters (voice_id, etc.).
        
        Returns:
            dict: Response with provider name and audio data.
        """
        if not self.key_manager.has_key('elevenlabs'):
            return {
                'provider': self.name,
                'error': 'No API key configured for audio generation',
                'audio': f'[Mock] Audio for: {prompt}'
            }
        
        return self._call_elevenlabs(prompt, **kwargs)
    
    def _call_elevenlabs(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Call ElevenLabs API.
        Вызов ElevenLabs API.
        """
        try:
            import requests
            
            api_key = self.key_manager.get_key('elevenlabs')
            voice_id = kwargs.get('voice_id', '21m00Tcm4TlvDq8ikWAM')  # Default voice
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            response = requests.post(
                url,
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": prompt,
                    "model_id": kwargs.get('model_id', 'eleven_monolingual_v1'),
                    "voice_settings": {
                        "stability": kwargs.get('stability', 0.5),
                        "similarity_boost": kwargs.get('similarity_boost', 0.5)
                    }
                }
            )
            
            if response.status_code == 200:
                return {
                    'provider': f'{self.name}_elevenlabs',
                    'audio': response.content,
                    'format': 'audio/mpeg'
                }
            else:
                return {
                    'provider': self.name,
                    'error': f'ElevenLabs API error: {response.status_code}',
                    'audio': f'[Mock] Audio for: {prompt}'
                }
        except ImportError:
            return {
                'provider': self.name,
                'error': 'Requests package not installed',
                'audio': f'[Mock] Audio for: {prompt}'
            }
        except Exception as e:
            return {
                'provider': self.name,
                'error': f'ElevenLabs API error: {str(e)}',
                'audio': f'[Mock] Audio for: {prompt}'
            }


class RealVideoProvider:
    """
    Real video provider using Runway ML.
    Реальный видео провайдер с использованием Runway ML.
    """
    
    def __init__(self, name: str = 'video'):
        """
        Initialize real video provider.
        Инициализировать реальный видео провайдер.
        
        Args:
            name: Provider name.
        """
        self.name = name
        self.key_manager = get_key_manager()
    
    def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate video using real API.
        Генерация видео с использованием реального API.
        
        Args:
            prompt: Video description prompt.
            **kwargs: Additional parameters.
        
        Returns:
            dict: Response with provider name and video URL/data.
        """
        if not self.key_manager.has_key('runway'):
            return {
                'provider': self.name,
                'error': 'No API key configured for video generation',
                'video': f'[Mock] Video for: {prompt}'
            }
        
        return {
            'provider': self.name,
            'message': 'Runway ML API integration coming soon',
            'video': f'[Mock] Video for: {prompt}'
        }


# Factory function to create providers
def create_provider(provider_type: str, use_real_api: bool = True):
    """
    Factory function to create provider instances.
    Фабричная функция для создания экземпляров провайдеров.
    
    Args:
        provider_type: Type of provider ('gpt', 'image', 'audio', 'video').
        use_real_api: Whether to use real API or mock implementation.
    
    Returns:
        Provider instance.
    """
    if not use_real_api:
        # Return mock providers
        from providers.gpt_provider import GPTProvider
        from providers.image_provider import ImageProvider
        from providers.audio_provider import AudioProvider
        from providers.video_provider import VideoProvider
        
        providers = {
            'gpt': GPTProvider,
            'image': ImageProvider,
            'audio': AudioProvider,
            'video': VideoProvider
        }
        return providers[provider_type](name=provider_type)
    
    # Return real API providers
    providers = {
        'gpt': RealGPTProvider,
        'image': RealImageProvider,
        'audio': RealAudioProvider,
        'video': RealVideoProvider
    }
    return providers[provider_type](name=provider_type)
