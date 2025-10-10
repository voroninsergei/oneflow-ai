"""
OneFlow.AI - Provider Manager
Менеджер провайдеров OneFlow.AI

Centralized management of all AI providers with automatic fallbacks.
Централизованное управление всеми AI провайдерами с автоматическими fallback.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Provider status enum."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class ProviderMetrics:
    """Provider performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_error: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100


class ProviderManager:
    """
    Centralized provider management with automatic fallbacks.
    Централизованное управление провайдерами с автоматическими fallback.
    """
    
    def __init__(self):
        """Initialize provider manager."""
        self.providers = {}
        self.metrics = {}
        self.fallback_chains = {}
        
        # Default fallback chains
        self._setup_fallback_chains()
    
    def _setup_fallback_chains(self):
        """Setup default fallback chains for different tasks."""
        self.fallback_chains = {
            'text': ['openai', 'anthropic'],  # GPT -> Claude
            'image': ['stability', 'openai'],  # Stability -> DALL-E
            'audio': ['elevenlabs'],
        }
    
    def register_provider(self, name: str, provider: Any, task_types: List[str]):
        """
        Register a provider.
        
        Args:
            name: Provider name.
            provider: Provider instance.
            task_types: List of supported task types.
        """
        self.providers[name] = {
            'instance': provider,
            'task_types': task_types,
            'status': ProviderStatus.AVAILABLE
        }
        self.metrics[name] = ProviderMetrics()
        logger.info(f"✓ Registered provider: {name} for tasks {task_types}")
    
    def set_fallback_chain(self, task_type: str, provider_names: List[str]):
        """
        Set fallback chain for a task type.
        
        Args:
            task_type: Task type (text, image, audio).
            provider_names: Ordered list of provider names.
        """
        self.fallback_chains[task_type] = provider_names
        logger.info(f"✓ Fallback chain for {task_type}: {' -> '.join(provider_names)}")
    
    def get_provider(self, name: str) -> Optional[Any]:
        """Get provider by name."""
        if name in self.providers:
            return self.providers[name]['instance']
        return None
    
    def get_providers_for_task(self, task_type: str) -> List[str]:
        """
        Get available providers for a task type in fallback order.
        
        Args:
            task_type: Task type.
        
        Returns:
            List of provider names.
        """
        # Get providers from fallback chain
        chain = self.fallback_chains.get(task_type, [])
        
        # Filter only available providers
        available = []
        for name in chain:
            if name in self.providers:
                provider_info = self.providers[name]
                if (provider_info['status'] == ProviderStatus.AVAILABLE and 
                    task_type in provider_info['task_types']):
                    available.append(name)
        
        return available
    
    def execute_with_fallback(self, task_type: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Execute request with automatic fallback.
        Выполнить запрос с автоматическим fallback.
        
        Args:
            task_type: Task type (text, image, audio).
            prompt: Input prompt.
            **kwargs: Additional parameters.
        
        Returns:
            dict: Result with provider info.
        """
        providers = self.get_providers_for_task(task_type)
        
        if not providers:
            return {
                'status': 'error',
                'error': f'No providers available for task type: {task_type}',
                'provider': None
            }
        
        # Try each provider in order
        last_error = None
        for provider_name in providers:
            try:
                logger.info(f"Attempting request with provider: {provider_name}")
                
                provider = self.get_provider(provider_name)
                metrics = self.metrics[provider_name]
                
                # Execute request
                import time
                start_time = time.time()
                
                # Different call signatures for different providers
                if provider_name in ['openai', 'gpt']:
                    result = provider(prompt, task_type=task_type, **kwargs)
                else:
                    result = provider(prompt, **kwargs)
                
                elapsed = time.time() - start_time
                
                # Check for errors in result
                if isinstance(result, dict) and 'error' in result:
                    raise Exception(result['error'])
                
                # Update metrics on success
                metrics.total_requests += 1
                metrics.successful_requests += 1
                metrics.total_cost += result.get('cost', 0.0)
                
                # Update average response time
                if metrics.average_response_time == 0:
                    metrics.average_response_time = elapsed
                else:
                    metrics.average_response_time = (
                        metrics.average_response_time * 0.9 + elapsed * 0.1
                    )
                
                logger.info(f"✓ Request successful with {provider_name} ({elapsed:.2f}s)")
                
                # Add provider info to result
                result['provider_name'] = provider_name
                result['response_time'] = elapsed
                result['status'] = 'success'
                
                return result
                
            except Exception as e:
                logger.warning(f"✗ Provider {provider_name} failed: {e}")
                
                # Update metrics on failure
                metrics = self.metrics[provider_name]
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.last_error = str(e)
                
                last_error = str(e)
                
                # Continue to next provider
                continue
        
        # All providers failed
        return {
            'status': 'error',
            'error': f'All providers failed. Last error: {last_error}',
            'provider': None,
            'attempted_providers': providers
        }
    
    def get_provider_status(self, name: str) -> Dict[str, Any]:
        """
        Get status and metrics for a provider.
        
        Args:
            name: Provider name.
        
        Returns:
            dict: Provider status and metrics.
        """
        if name not in self.providers:
            return {'error': f'Provider {name} not found'}
        
        provider_info = self.providers[name]
        metrics = self.metrics[name]
        
        return {
            'name': name,
            'status': provider_info['status'].value,
            'task_types': provider_info['task_types'],
            'metrics': {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'success_rate': f"{metrics.success_rate:.1f}%",
                'error_rate': f"{metrics.error_rate:.1f}%",
                'total_cost': f"${metrics.total_cost:.2f}",
                'average_response_time': f"{metrics.average_response_time:.2f}s",
                'last_error': metrics.last_error
            }
        }
    
    def get_all_providers_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all providers."""
        return {
            name: self.get_provider_status(name)
            for name in self.providers.keys()
        }
    
    def reset_metrics(self, name: Optional[str] = None):
        """
        Reset metrics for provider(s).
        
        Args:
            name: Provider name, or None to reset all.
        """
        if name:
            if name in self.metrics:
                self.metrics[name] = ProviderMetrics()
                logger.info(f"✓ Reset metrics for {name}")
        else:
            for provider_name in self.metrics.keys():
                self.metrics[provider_name] = ProviderMetrics()
            logger.info("✓ Reset metrics for all providers")
    
    def mark_provider_unavailable(self, name: str, reason: str = None):
        """Mark a provider as unavailable."""
        if name in self.providers:
            self.providers[name]['status'] = ProviderStatus.UNAVAILABLE
            if reason:
                self.metrics[name].last_error = reason
            logger.warning(f"⚠ Provider {name} marked as unavailable: {reason}")
    
    def mark_provider_available(self, name: str):
        """Mark a provider as available."""
        if name in self.providers:
            self.providers[name]['status'] = ProviderStatus.AVAILABLE
            logger.info(f"✓ Provider {name} marked as available")
    
    def get_best_provider(self, task_type: str) -> Optional[str]:
        """
        Get best provider for a task based on metrics.
        
        Args:
            task_type: Task type.
        
        Returns:
            str: Best provider name or None.
        """
        providers = self.get_providers_for_task(task_type)
        
        if not providers:
            return None
        
        # Sort by success rate and response time
        def score_provider(name: str) -> float:
            metrics = self.metrics[name]
            if metrics.total_requests == 0:
                return 100.0  # Untested providers get high priority
            
            # Score based on success rate (70%) and response time (30%)
            success_score = metrics.success_rate * 0.7
            
            # Normalize response time (lower is better)
            time_score = max(0, 100 - metrics.average_response_time * 10) * 0.3
            
            return success_score + time_score
        
        best = max(providers, key=score_provider)
        return best
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all metrics.
        
        Returns:
            dict: Metrics summary.
        """
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_successful = sum(m.successful_requests for m in self.metrics.values())
        total_failed = sum(m.failed_requests for m in self.metrics.values())
        total_cost = sum(m.total_cost for m in self.metrics.values())
        
        return {
            'total_requests': total_requests,
            'successful_requests': total_successful,
            'failed_requests': total_failed,
            'overall_success_rate': f"{(total_successful / total_requests * 100) if total_requests > 0 else 0:.1f}%",
            'total_cost': f"${total_cost:.2f}",
            'providers': self.get_all_providers_status()
        }


# ==================== Initialization Helper ====================

def initialize_provider_manager(use_real_api: bool = True) -> ProviderManager:
    """
    Initialize provider manager with all available providers.
    Инициализировать менеджер провайдеров со всеми доступными провайдерами.
    
    Args:
        use_real_api: Whether to use real API or mock providers.
    
    Returns:
        ProviderManager: Initialized manager.
    """
    manager = ProviderManager()
    
    if use_real_api:
        try:
            from enhanced_real_api import (
                EnhancedOpenAIProvider,
                EnhancedAnthropicProvider,
                EnhancedStabilityProvider,
                EnhancedElevenLabsProvider
            )
            
            # Register OpenAI (supports both text and image)
            openai_provider = EnhancedOpenAIProvider(name='openai')
            manager.register_provider('openai', openai_provider, ['text', 'image'])
            
            # Register Anthropic (text only)
            anthropic_provider = EnhancedAnthropicProvider(name='anthropic')
            manager.register_provider('anthropic', anthropic_provider, ['text'])
            
            # Register Stability AI (image only)
            stability_provider = EnhancedStabilityProvider(name='stability')
            manager.register_provider('stability', stability_provider, ['image'])
            
            # Register ElevenLabs (audio only)
            elevenlabs_provider = EnhancedElevenLabsProvider(name='elevenlabs')
            manager.register_provider('elevenlabs', elevenlabs_provider, ['audio'])
            
            logger.info("✓ Real API providers initialized")
            
        except ImportError as e:
            logger.warning(f"Could not load real API providers: {e}")
            logger.warning("Falling back to mock providers")
            _initialize_mock_providers(manager)
    else:
        _initialize_mock_providers(manager)
    
    return manager


def _initialize_mock_providers(manager: ProviderManager):
    """Initialize mock providers for testing."""
    from providers.gpt_provider import GPTProvider
    from providers.image_provider import ImageProvider
    from providers.audio_provider import AudioProvider
    from providers.video_provider import VideoProvider
    
    # Register mock providers
    manager.register_provider('gpt', GPTProvider(name='gpt'), ['text'])
    manager.register_provider('image', ImageProvider(name='image'), ['image'])
    manager.register_provider('audio', AudioProvider(name='audio'), ['audio'])
    manager.register_provider('video', VideoProvider(name='video'), ['video'])
    
    logger.info("✓ Mock providers initialized")


# ==================== Demo ====================

def demo_provider_manager():
    """
    Demonstrate provider manager functionality.
    Демонстрация функциональности менеджера провайдеров.
    """
    print("=" * 60)
    print("Provider Manager - Demo")
    print("=" * 60)
    
    # Initialize manager
    manager = initialize_provider_manager(use_real_api=True)
    
    # Show all providers
    print("\n1. All Providers:")
    status = manager.get_all_providers_status()
    for name, info in status.items():
        print(f"   {name}: {info['status']} - {info['task_types']}")
    
    # Test text generation with fallback
    print("\n2. Text Generation (with fallback):")
    result = manager.execute_with_fallback('text', 'Write a haiku about technology')
    print(f"   Provider: {result.get('provider_name', 'N/A')}")
    print(f"   Status: {result.get('status')}")
    print(f"   Response: {result.get('response', result.get('error'))[:100]}...")
    
    # Test image generation
    print("\n3. Image Generation:")
    result = manager.execute_with_fallback('image', 'A beautiful sunset over mountains')
    print(f"   Provider: {result.get('provider_name', 'N/A')}")
    print(f"   Status: {result.get('status')}")
    print(f"   Cost: ${result.get('cost', 0):.4f}")
    
    # Show metrics
    print("\n4. Metrics Summary:")
    summary = manager.get_metrics_summary()
    print(f"   Total requests: {summary['total_requests']}")
    print(f"   Success rate: {summary['overall_success_rate']}")
    print(f"   Total cost: {summary['total_cost']}")
    
    # Show best provider
    print("\n5. Best Providers:")
    for task in ['text', 'image', 'audio']:
        best = manager.get_best_provider(task)
        print(f"   {task}: {best}")
    
    print("\n" + "=" * 60)
    print("✓ Demo completed!")
    print("=" * 60)


if __name__ == '__main__':
    demo_provider_manager()
