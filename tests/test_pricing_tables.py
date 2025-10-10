"""
Tests for token-based pricing system
"""

import pytest
from src.pricing_tables import (
    calculate_cost_in_credits,
    get_model_info,
    estimate_tokens_from_text,
    convert_legacy_request,
    PROVIDER_PRICING,
    CREDIT_RATE,
)


class TestPricingTables:
    """Test suite for pricing tables and calculations"""

    def test_provider_pricing_structure(self):
        """Verify pricing tables have correct structure"""
        assert "openai" in PROVIDER_PRICING
        assert "anthropic" in PROVIDER_PRICING
        
        # Check OpenAI models
        assert "gpt-4" in PROVIDER_PRICING["openai"]
        assert "gpt-3.5-turbo" in PROVIDER_PRICING["openai"]
        
        # Check Anthropic models
        assert "claude-3-opus" in PROVIDER_PRICING["anthropic"]
        assert "claude-3-sonnet" in PROVIDER_PRICING["anthropic"]

    def test_model_pricing_attributes(self):
        """Verify model pricing objects have required attributes"""
        gpt4 = PROVIDER_PRICING["openai"]["gpt-4"]
        
        assert hasattr(gpt4, "input_price_per_token")
        assert hasattr(gpt4, "output_price_per_token")
        assert hasattr(gpt4, "context_window")
        assert hasattr(gpt4, "supports_vision")
        assert hasattr(gpt4, "supports_function_calling")

    def test_calculate_cost_basic(self):
        """Test basic cost calculation"""
        # GPT-3.5: $0.5/1M input, $1.5/1M output
        # 1000 input tokens = $0.0005 = 0.0005 / 0.00001 = 50 credits
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1000, 0)
        assert cost == 50.0

    def test_calculate_cost_with_output(self):
        """Test cost calculation with both input and output tokens"""
        # GPT-3.5: 1000 in ($0.0005) + 500 out ($0.00075) = $0.00125 = 125 credits
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1000, 500)
        assert cost == 125.0

    def test_calculate_cost_expensive_model(self):
        """Test cost calculation for expensive model (Claude Opus)"""
        # Claude 3 Opus: $15/1M in, $75/1M out
        # 1000 in = $0.015, 1000 out = $0.075
        # Total = $0.09 = 9000 credits
        cost = calculate_cost_in_credits("anthropic", "claude-3-opus", 1000, 1000)
        assert cost == 9000.0

    def test_calculate_cost_invalid_provider(self):
        """Test error handling for invalid provider"""
        with pytest.raises(ValueError, match="Unknown provider"):
            calculate_cost_in_credits("invalid_provider", "model", 1000, 0)

    def test_calculate_cost_invalid_model(self):
        """Test error handling for invalid model"""
        with pytest.raises(ValueError, match="Unknown model"):
            calculate_cost_in_credits("openai", "gpt-99", 1000, 0)

    def test_get_model_info(self):
        """Test model information retrieval"""
        info = get_model_info("openai", "gpt-4")
        
        assert info["provider"] == "openai"
        assert info["model"] == "gpt-4"
        assert "input_price_per_1m_tokens" in info
        assert "output_price_per_1m_tokens" in info
        assert "context_window" in info
        assert "supports_vision" in info
        assert "supports_function_calling" in info
        
        # GPT-4 supports function calling but not vision
        assert info["supports_function_calling"] is True
        assert info["supports_vision"] is False

    def test_get_model_info_vision_support(self):
        """Test model info for vision-capable models"""
        info = get_model_info("openai", "gpt-4o")
        assert info["supports_vision"] is True

    def test_estimate_tokens_from_text(self):
        """Test token estimation from text"""
        # Rough estimation: ~4 chars per token
        text = "Hello world! This is a test."  # 29 chars
        tokens = estimate_tokens_from_text(text)
        assert tokens == 7  # 29 // 4

    def test_estimate_tokens_empty_string(self):
        """Test token estimation for empty string"""
        tokens = estimate_tokens_from_text("")
        assert tokens == 0

    def test_convert_legacy_request_gpt(self):
        """Test legacy request conversion for GPT"""
        provider, model, tokens = convert_legacy_request("gpt", "Hello world")
        
        assert provider == "openai"
        assert model == "gpt-3.5-turbo"
        assert tokens > 0

    def test_convert_legacy_request_image(self):
        """Test legacy request conversion for image"""
        provider, model, tokens = convert_legacy_request("image", "A cat")
        
        assert provider == "openai"
        assert model == "dall-e-2"
        assert tokens == 1  # Images use 1 token as unit

    def test_convert_legacy_request_audio(self):
        """Test legacy request conversion for audio"""
        provider, model, tokens = convert_legacy_request("audio", "Some text")
        
        assert provider == "elevenlabs"
        assert model == "eleven_turbo_v2"
        assert tokens == 1

    def test_convert_legacy_request_invalid(self):
        """Test error handling for invalid legacy type"""
        with pytest.raises(ValueError, match="Unknown legacy provider type"):
            convert_legacy_request("invalid_type", "content")

    def test_credit_rate_constant(self):
        """Test credit rate is set correctly"""
        assert CREDIT_RATE == 0.00001

    def test_pricing_consistency(self):
        """Test that all models have consistent pricing structure"""
        for provider, models in PROVIDER_PRICING.items():
            for model_name, pricing in models.items():
                # All prices should be non-negative
                assert pricing.input_price_per_token >= 0
                assert pricing.output_price_per_token >= 0
                
                # Context window should be positive
                assert pricing.context_window > 0
                
                # Boolean flags should be bool type
                assert isinstance(pricing.supports_vision, bool)
                assert isinstance(pricing.supports_function_calling, bool)

    def test_cost_calculation_precision(self):
        """Test that cost calculations maintain precision"""
        # Very small token counts should still calculate correctly
        cost = calculate_cost_in_credits("openai", "gpt-3.5-turbo", 1, 1)
        assert cost > 0
        assert isinstance(cost, float)

    def test_multiple_provider_comparison(self):
        """Test cost comparison across providers"""
        prompt_tokens = 1000
        output_tokens = 500
        
        # Calculate costs for different models
        gpt35_cost = calculate_cost_in_credits(
            "openai", "gpt-3.5-turbo", prompt_tokens, output_tokens
        )
        gpt4_cost = calculate_cost_in_credits(
            "openai", "gpt-4", prompt_tokens, output_tokens
        )
        claude_haiku_cost = calculate_cost_in_credits(
            "anthropic", "claude-3-haiku", prompt_tokens, output_tokens
        )
        
        # GPT-3.5 should be cheapest
        assert gpt35_cost < gpt4_cost
        
        # All should be positive
        assert gpt35_cost > 0
        assert gpt4_cost > 0
        assert claude_haiku_cost > 0


class TestModelFeatures:
    """Test model feature flags"""

    def test_gpt4_turbo_features(self):
        """Test GPT-4 Turbo feature flags"""
        model = PROVIDER_PRICING["openai"]["gpt-4-turbo"]
        assert model.supports_vision is True
        assert model.supports_function_calling is True

    def test_claude_vision_support(self):
        """Test Claude models vision support"""
        opus = PROVIDER_PRICING["anthropic"]["claude-3-opus"]
        sonnet = PROVIDER_PRICING["anthropic"]["claude-3-sonnet"]
        haiku = PROVIDER_PRICING["anthropic"]["claude-3-haiku"]
        
        assert opus.supports_vision is True
        assert sonnet.supports_vision is True
        assert haiku.supports_vision is True

    def test_image_models_no_output(self):
        """Test that image generation models have no output cost"""
        dalle3 = PROVIDER_PRICING["openai"]["dall-e-3"]
        dalle2 = PROVIDER_PRICING["openai"]["dall-e-2"]
        
        assert dalle3.output_price_per_token == 0
        assert dalle2.output_price_per_token == 0


class TestContextWindows:
    """Test context window specifications"""

    def test_gpt4_turbo_context(self):
        """Test GPT-4 Turbo has large context window"""
        model = PROVIDER_PRICING["openai"]["gpt-4-turbo"]
        assert model.context_window == 128000

    def test_claude_context(self):
        """Test Claude models have 200k context"""
        opus = PROVIDER_PRICING["anthropic"]["claude-3-opus"]
        assert opus.context_window == 200000

    def test_gpt35_context(self):
        """Test GPT-3.5 context window"""
        model = PROVIDER_PRICING["openai"]["gpt-3.5-turbo"]
        assert model.context_window == 16385
