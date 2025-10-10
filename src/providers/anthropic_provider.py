"""
Адаптер для Anthropic API (Claude)
"""
from typing import Optional
import anthropic
from .base import Provider, ProviderConfig, ProviderResponse, ProviderStatus, ProviderError
import time

class AnthropicProvider(Provider):
    """Провайдер для Anthropic Claude"""
    
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }
    
    def __init__(self, config: ProviderConfig, feature_flags: Optional[dict] = None):
        super().__init__(config)
        self.features = feature_flags or {}
        self._client = None
    
    def _get_client(self):
        """Ленивая инициализация клиента"""
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
        return self._client
    
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> ProviderResponse:
        """Генерация через Claude"""
        
        if not self.features.get("anthropic_enabled", True):
            raise ProviderError("Anthropic provider is disabled")
        
        start_time = time.time()
        
        try:
            client = self._get_client()
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens or 1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=response.content[0].text,
                cost=self._calculate_cost(response.usage, model),
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                model_used=model,
                latency_ms=latency_ms,
                provider_name="anthropic"
            )
        
        except anthropic.APIError as e:
            raise ProviderError(f"Anthropic API error: {str(e)}")
    
    async def estimate_cost(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        model: str = "claude-3-sonnet-20240229"
    ) -> float:
        """Оценка стоимости"""
        input_tokens = len(prompt) // 4
        output_tokens = max_tokens or 100
        
        pricing = self.PRICING.get(model, self.PRICING["claude-3-sonnet"])
        
        return (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
    
    async def health_check(self) -> ProviderStatus:
        """Проверка доступности"""
        try:
            # Простой тестовый запрос
            await self.generate("test", max_tokens=1)
            return ProviderStatus.HEALTHY
        except:
            return ProviderStatus.UNAVAILABLE
    
    def _calculate_cost(self, usage, model: str) -> float:
        """Расчет стоимости"""
        model_key = "claude-3-sonnet" if "sonnet" in model else "claude-3-opus"
        pricing = self.PRICING.get(model_key, self.PRICING["claude-3-sonnet"])
        
        return (
            (usage.input_tokens / 1000) * pricing["input"] +
            (usage.output_tokens / 1000) * pricing["output"]
        )
