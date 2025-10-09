"""
OneFlow.AI Aggregator
Author: Sergey Voronin
Description:
    This script is the entry point for the OneFlow.AI pricing and routing layer. It initializes
    the Router and PricingCalculator classes and demonstrates a simple workflow using them.
    The code is fully documented in English and Russian to support multilingual users.

Агрегатор OneFlow.AI
Автор: Сергей Воронин
Описание:
    Этот скрипт является точкой входа для ценового и маршрутизирующего слоя OneFlow.AI.
    Он инициализирует классы Router и PricingCalculator и демонстрирует простой рабочий
    процесс с их использованием. Код документирован на английском и русском языках
    для поддержки мультиязычных пользователей.
"""

from router import Router
from pricing import PricingCalculator


def main():
    """
    Entry point for running a sample OneFlow.AI workflow.

    Основная функция для запуска примерного сценария работы OneFlow.AI.
    """
    # Initialize pricing calculator and router
    pricing = PricingCalculator()
    router = Router()

    # Register example rates for different providers (in tokens per word)
    pricing.register_rate('gpt', 1)
    pricing.register_rate('imagen', 2)

    # Register example providers
    def gpt_provider(prompt: str, **kwargs):
        """A mock provider that returns a formatted string for demonstration."""
        return f"[GPT provider] Generated response for prompt: {prompt}"

    def imagen_provider(prompt: str, **kwargs):
        """A mock provider that returns a formatted string for demonstration."""
        return f"[Imagen provider] Generated images for prompt: {prompt}"

    router.register_provider('gpt', gpt_provider)
    router.register_provider('imagen', imagen_provider)

    # Example user input
    prompt = "Hello AI"
    model = 'gpt'

    # Estimate cost (assuming cost per word) and execute request
    cost_estimate = pricing.estimate_cost(model, len(prompt.split()))
    response = router.route_request(model, prompt)

    print(f"Estimated cost: {cost_estimate} tokens")
    print(f"Response: {response}")


if __name__ == "__main__":
    main()
