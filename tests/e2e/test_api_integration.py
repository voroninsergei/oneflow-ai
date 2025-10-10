"""
Integration tests for FastAPI endpoints
Интеграционные тесты для FastAPI эндпоинтов
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from fastapi import FastAPI
    from test_api_compatibility import (
        RequestSchemaV1,
        RequestSchemaV2,
        ResponseSchemaV1,
        ResponseSchemaV2,
        router_v1,
        router_v2,
        APIVersionRegistry
    )
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
@pytest.mark.e2e
@pytest.mark.api
class TestAPIVersioning:
    """Test API versioning system"""

    @pytest.fixture
    def app(self):
        """Create FastAPI app with versioned routers"""
        app = FastAPI(title="OneFlow.AI Test")
        app.include_router(router_v1)
        app.include_router(router_v2)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    def test_v1_info_endpoint(self, client):
        """Test V1 info endpoint"""
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.0.0"
        assert data["stability"] == "stable"

    def test_v2_info_endpoint(self, client):
        """Test V2 info endpoint"""
        response = client.get("/api/v2/info")
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert data["stability"] == "stable"

    def test_v1_request_schema_validation(self, client):
        """Test V1 request schema validation"""
        valid_request = {
            "provider": "gpt",
            "prompt": "Test prompt"
        }
        
        # Would need actual endpoint implementation
        # This tests schema validation
        try:
            validated = RequestSchemaV1(**valid_request)
            assert validated.provider == "gpt"
            assert validated.prompt == "Test prompt"
        except Exception as e:
            pytest.fail(f"Schema validation failed: {e}")

    def test_v2_extended_fields(self, client):
        """Test V2 extended request fields"""
        v2_request = {
            "provider": "gpt",
            "prompt": "Test",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 100,
            "stream": False,
            "metadata": {"key": "value"}
        }
        
        validated = RequestSchemaV2(**v2_request)
        assert validated.model == "gpt-4"
        assert validated.temperature == 0.7
        assert validated.metadata["key"] == "value"

    def test_v1_backward_compatibility(self, client):
        """Test that V1 requests still work"""
        v1_request = {
            "provider": "gpt",
            "prompt": "Legacy request"
        }
        
        # V1 should not require new V2 fields
        validated = RequestSchemaV1(**v1_request)
        assert validated.provider == "gpt"

    def test_v2_backward_compatible_with_v1(self, client):
        """Test that V2 accepts V1-style requests"""
        v1_style_request = {
            "provider": "gpt",
            "prompt": "Test"
        }
        
        # V2 should accept requests without new fields (optional)
        validated = RequestSchemaV2(**v1_style_request)
        assert validated.provider == "gpt"
        assert validated.model is None
        assert validated.temperature is None

    def test_response_schema_v1(self):
        """Test V1 response schema"""
        response_data = {
            "status": "success",
            "response": "Test response",
            "cost": 5.0,
            "provider": "gpt"
        }
        
        validated = ResponseSchemaV1(**response_data)
        assert validated.status == "success"
        assert validated.cost == 5.0

    def test_response_schema_v2_extended(self):
        """Test V2 extended response fields"""
        from datetime import datetime
        
        response_data = {
            "status": "success",
            "response": "Test response",
            "cost": 5.0,
            "provider": "gpt",
            "request_id": "req_123",
            "model_used": "gpt-4",
            "tokens_used": 150,
            "latency_ms": 234
        }
        
        validated = ResponseSchemaV2(**response_data)
        assert validated.request_id == "req_123"
        assert validated.tokens_used == 150
        assert validated.latency_ms == 234

    def test_api_version_registry(self):
        """Test API version registry"""
        from test_api_compatibility import APIVersion
        
        v1_info = APIVersionRegistry.get_version_info(APIVersion.V1)
        assert v1_info.version == "1.0.0"
        assert not v1_info.deprecated
        
        v2_info = APIVersionRegistry.get_version_info(APIVersion.V2)
        assert v2_info.version == "2.0.0"
        assert not v2_info.deprecated

    def test_all_versions_listed(self):
        """Test listing all API versions"""
        versions = APIVersionRegistry.get_all_versions()
        assert "v1" in versions
        assert "v2" in versions

    def test_deprecated_version_check(self):
        """Test checking if version is deprecated"""
        from test_api_compatibility import APIVersion
        
        assert not APIVersionRegistry.is_deprecated(APIVersion.V1)
        assert not APIVersionRegistry.is_deprecated(APIVersion.V2)


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
@pytest.mark.e2e
@pytest.mark.api
class TestAPIRequestFlow:
    """Test complete API request flow"""

    @pytest.fixture
    def app_with_endpoints(self, mock_all_providers):
        """Create app with mock request endpoints"""
        app = FastAPI()
        
        @app.post("/api/v1/request")
        async def process_request_v1(request: RequestSchemaV1):
            # Mock processing
            return ResponseSchemaV1(
                status="success",
                response=f"Processed: {request.prompt}",
                cost=5.0,
                provider=request.provider
            )
        
        @app.post("/api/v2/request")
        async def process_request_v2(request: RequestSchemaV2):
            # Mock processing with extended fields
            return ResponseSchemaV2(
                status="success",
                response=f"Processed: {request.prompt}",
                cost=5.0,
                provider=request.provider,
                request_id="req_test_123",
                model_used=request.model or "default",
                tokens_used=100,
                latency_ms=150
            )
        
        return app

    @pytest.fixture
    def client_with_endpoints(self, app_with_endpoints):
        """Create client with endpoints"""
        return TestClient(app_with_endpoints)

    def test_v1_request_flow(self, client_with_endpoints):
        """Test V1 request flow"""
        request_data = {
            "provider": "gpt",
            "prompt": "Test prompt"
        }
        
        response = client_with_endpoints.post("/api/v1/request", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "Processed" in data["response"]
        assert data["cost"] == 5.0

    def test_v2_request_flow(self, client_with_endpoints):
        """Test V2 request flow"""
        request_data = {
            "provider": "gpt",
            "prompt": "Test prompt",
            "model": "gpt-4",
            "temperature": 0.7
        }
        
        response = client_with_endpoints.post("/api/v2/request", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["request_id"] == "req_test_123"
        assert data["model_used"] == "gpt-4"
        assert data["tokens_used"] == 100

    def test_v1_validation_error(self, client_with_endpoints):
        """Test V1 validation error"""
        invalid_request = {
            "prompt": "Missing provider"
        }
        
        response = client_with_endpoints.post("/api/v1/request", json=invalid_request)
        assert response.status_code == 422  # Validation error

    def test_v2_validation_error(self, client_with_endpoints):
        """Test V2 validation error"""
        invalid_request = {
            "provider": "gpt"
            # Missing required prompt
        }
        
        response = client_with_endpoints.post("/api/v2/request", json=invalid_request)
        assert response.status_code == 422

    def test_v2_parameter_validation(self, client_with_endpoints):
        """Test V2 parameter validation"""
        invalid_request = {
            "provider": "gpt",
            "prompt": "Test",
            "temperature": 5.0  # Invalid: must be 0-2
        }
        
        response = client_with_endpoints.post("/api/v2/request", json=invalid_request)
        assert response.status_code == 422


@pytest.mark.e2e
@pytest.mark.integration
class TestDatabaseIntegration:
    """Test database integration with other components"""

    def test_database_request_logging(self, system_with_db):
        """Test logging requests to database"""
        system = system_with_db
        db = system['db']
        
        # Create user
        user = db.create_user('testuser', 'test@example.com', initial_balance=100.0)
        
        # Log request
        request = db.create_request(
            user_id=user.id,
            provider='gpt',
            model='gpt-3.5-turbo',
            prompt='Test prompt',
            response='Test response',
            cost=5.0,
            status='success'
        )
        
        assert request.id is not None
        assert request.cost == 5.0
        
        # Verify retrieval
        requests = db.get_requests(user_id=user.id)
        assert len(requests) == 1

    def test_database_transaction_tracking(self, system_with_db):
        """Test transaction tracking in database"""
        system = system_with_db
        db = system['db']
        
        user = db.create_user('testuser', 'test@example.com', initial_balance=100.0)
        
        # Create transaction
        transaction = db.create_transaction(
            user_id=user.id,
            trans_type='deduct',
            amount=10.0,
            balance_before=100.0,
            balance_after=90.0,
            description='Test request'
        )
        
        assert transaction.amount == 10.0
        
        # Update user balance
        db.update_user_balance(user.id, 90.0)
        
        updated_user = db.get_user(user.id)
        assert updated_user.balance == 90.0
