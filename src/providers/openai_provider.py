"""
Адаптер для OpenAI API
"""
import time
from typing import Optional
import openai
from .base import Provider, ProviderConfig, ProviderResponse, ProviderStatus, ProviderError

class OpenAIProvider(Provider):
    """Провайдер для OpenAI (GPT, DALL-E)"""
    
    PRICING = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
    }
    
    def __init__(self, config: ProviderConfig, feature_flags: Optional[dict] = None):
        super().__init__(config)
        self.features = feature_flags or {}
        self._client = None
    
    def _get_client(self):
        """Ленивая инициализация клиента (изоляция)"""
        if self._client is None:
            self._client = openai.AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        return self._client
    
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> ProviderResponse:
        """Генерация текста через OpenAI"""
        
        # Проверка feature flag
        if not self.features.get("openai_enabled", True):
            raise ProviderError("OpenAI provider is disabled by feature flag")
        
        if not self.config.enabled:
            raise ProviderError("OpenAI provider is disabled in config")
        
        start_time = time.time()
        
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return ProviderResponse(
                content=response.choices[0].message.content,
                cost=self._calculate_cost(response.usage, model),
                tokens_used=response.usage.total_tokens,
                model_used=model,
                latency_ms=latency_ms,
                provider_name="openai"
            )
        
        except openai.APIError as e:
            raise ProviderError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise ProviderError(f"Unexpected error: {str(e)}")
    
    async def estimate_cost(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        model: str = "gpt-3.5-turbo"
    ) -> float:
        """Оценка стоимости"""
        # Примерная оценка токенов (4 символа = 1 токен)
        input_tokens = len(prompt) // 4
        output_tokens = max_tokens or 100
        
        pricing = self.PRICING.get(model, self.PRICING["gpt-3.5-turbo"])
        
        cost = (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
        
        return cost
    
    async def health_check(self) -> ProviderStatus:
        """Проверка доступности"""
        try:
            client = self._get_client()
            await client.models.list()
            return ProviderStatus.HEALTHY
        except Exception:
            return ProviderStatus.UNAVAILABLE
    
    def _calculate_cost(self, usage, model: str) -> float:
        """Расчет реальной стоимости"""
        pricing = self.PRICING.get(model, self.PRICING["gpt-3.5-turbo"])
        
        return (
            (usage.prompt_tokens / 1000) * pricing["input"] +
            (usage.completion_tokens / 1000) * pricing["output"]
        )
