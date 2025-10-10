def test_unknown_provider_returns_zero():
    """English: Ensure that requesting cost for an unregistered provider returns 0.0.

    Русская версия:
    Убедитесь, что запрос стоимости для незарегистрированного провайдера возвращает 0.0.
    """
    pc = PricingCalculator()
    pc.register_rate("gpt", 0.05)
    # Request cost for a provider that has not been registered
    assert pc.estimate_cost("unknown", 50) == 0.0