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
from wallet import Wallet
from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider


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
    # Initialize wallet, pricing calculator, and router
    wallet = Wallet(initial_balance=100)
    pricing = PricingCalculator()
    router = Router()

    # Register rates for providers (cost per unit)
    pricing.register_rate('gpt', 1)  # cost per word
    pricing.register_rate('image', 10)  # cost per image generation
    pricing.register_rate('audio', 5)  # cost per audio generation
    pricing.register_rate('video', 20)  # cost per video generation

    # Initialize provider instances
    gpt_provider = GPTProvider(name='gpt')
    image_provider = ImageProvider(name='image')
    audio_provider = AudioProvider(name='audio')
    video_provider = VideoProvider(name='video')

    # Register providers in the router
    router.register_provider(gpt_provider)
    router.register_provider(image_provider)
    router.register_provider(audio_provider)
    router.register_provider(video_provider)

    # Prompt user for input
    model = input("Enter model type (gpt, image, audio, or video): ")
    prompt = input("Enter your prompt: ")

    # Determine cost units based on model type
    if model.lower() == 'gpt':
        cost_units = len(prompt.split())
    else:
        cost_units = 1

    # Estimate cost
    cost = pricing.estimate_cost(model.lower(), cost_units)
    print(f"Estimated cost for {model} request: {cost} credits")

    # Check if the wallet can afford the request
    if wallet.can_afford(cost):
        wallet.deduct(cost)
        # Create request dictionary for router
        request = {'type': model.lower(), 'prompt': prompt}
        response = router.route_request(request)
        print(f"Response from {model}: {response}")
        print(f"Remaining balance: {wallet.get_balance()} credits")
    else:
        print("Insufficient credits in wallet")

    main()
