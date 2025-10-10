"""
OneFlow.AI - FastAPI Web Server
Веб-сервер OneFlow.AI на FastAPI

This module provides a complete REST API for OneFlow.AI with FastAPI.
Provides endpoints for requests, analytics, budget management, and configuration.

Этот модуль предоставляет полный REST API для OneFlow.AI на FastAPI.
Предоставляет endpoints для запросов, аналитики, управления бюджетом и конфигурации.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uvicorn

# Import OneFlow.AI modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import OneFlowAI
from budget import BudgetPeriod
from config import Config

# Initialize FastAPI app
app = FastAPI(
    title="OneFlow.AI API",
    description="AI Model Aggregator with pricing, routing, and analytics",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global OneFlow.AI system instance
system = OneFlowAI(initial_balance=1000, use_real_api=False)

# Pydantic models for request/response validation
class AIRequest(BaseModel):
    """Request model for AI generation."""
    model: str = Field(..., description="Model type: gpt, image, audio, video")
    prompt: str = Field(..., description="Input prompt for generation")
    
    class Config:
        schema_extra = {
            "example": {
                "model": "gpt",
                "prompt": "Write a short poem about AI"
            }
        }


class AIResponse(BaseModel):
    """Response model for AI generation."""
    status: str
    response: Optional[Any] = None
    cost: float
    balance: float
    message: Optional[str] = None


class BudgetLimit(BaseModel):
    """Budget limit configuration."""
    period: str = Field(..., description="Period: daily, weekly, monthly, total")
    amount: Optional[float] = Field(None, description="Limit amount (null for no limit)")


class ProviderBudget(BaseModel):
    """Provider budget configuration."""
    provider: str
    amount: Optional[float]


class CreditsUpdate(BaseModel):
    """Credits update request."""
    amount: float = Field(..., gt=0, description="Amount of credits to add")


class StatusResponse(BaseModel):
    """System status response."""
    api_mode: str
    balance: float
    total_requests: int
    total_cost: float
    average_cost: Optional[float] = None
    most_used_provider: Optional[str] = None


# API Endpoints

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint - returns web dashboard.
    Корневой endpoint - возвращает веб-дашборд.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OneFlow.AI Dashboard</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                border-radius: 12px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 16px;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .card h2 {
                color: #333;
                margin-bottom: 15px;
                font-size: 18px;
            }
            .stat {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .stat-label {
                color: #666;
            }
            .stat-value {
                color: #333;
                font-weight: 600;
            }
            .btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.3s;
                margin-right: 10px;
                margin-top: 10px;
            }
            .btn:hover {
                background: #5568d3;
            }
            .btn-secondary {
                background: #48bb78;
            }
            .btn-secondary:hover {
                background: #38a169;
            }
            .input-group {
                margin-bottom: 15px;
            }
            .input-group label {
                display: block;
                margin-bottom: 5px;
                color: #333;
                font-weight: 600;
            }
            .input-group input, .input-group select {
                width: 100%;
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            .input-group input:focus, .input-group select:focus {
                outline: none;
                border-color: #667eea;
            }
            .response {
                background: #f7fafc;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin-top: 15px;
                border-radius: 4px;
                display: none;
            }
            .response.show {
                display: block;
            }
            .response.error {
                border-left-color: #f56565;
                background: #fff5f5;
            }
            .response.success {
                border-left-color: #48bb78;
                background: #f0fff4;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 OneFlow.AI Dashboard</h1>
                <p class="subtitle">AI Model Aggregator with pricing, routing, and analytics</p>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h2>📊 System Status</h2>
                    <div class="stat">
                        <span class="stat-label">Balance</span>
                        <span class="stat-value" id="balance">Loading...</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Requests</span>
                        <span class="stat-value" id="requests">Loading...</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Total Cost</span>
                        <span class="stat-value" id="cost">Loading...</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Most Used</span>
                        <span class="stat-value" id="most-used">Loading...</span>
                    </div>
                    <button class="btn" onclick="refreshStatus()">🔄 Refresh</button>
                </div>
                
                <div class="card">
                    <h2>🤖 Make AI Request</h2>
                    <div class="input-group">
                        <label>Model Type</label>
                        <select id="model">
                            <option value="gpt">GPT (Text)</option>
                            <option value="image">Image</option>
                            <option value="audio">Audio</option>
                            <option value="video">Video</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Prompt</label>
                        <input type="text" id="prompt" placeholder="Enter your prompt...">
                    </div>
                    <button class="btn" onclick="makeRequest()">✨ Generate</button>
                    <div class="response" id="request-response"></div>
                </div>
                
                <div class="card">
                    <h2>💰 Manage Credits</h2>
                    <div class="input-group">
                        <label>Amount to Add</label>
                        <input type="number" id="credits" placeholder="Enter amount..." value="50">
                    </div>
                    <button class="btn btn-secondary" onclick="addCredits()">➕ Add Credits</button>
                    <div class="response" id="credits-response"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Analytics</h2>
                <div id="analytics">Loading analytics...</div>
                <button class="btn" onclick="loadAnalytics()">📊 Refresh Analytics</button>
            </div>
            
            <div class="card">
                <h2>📖 API Documentation</h2>
                <p style="margin-bottom: 15px; color: #666;">
                    Full API documentation available at:
                </p>
                <button class="btn" onclick="window.open('/api/docs', '_blank')">📚 View Swagger Docs</button>
                <button class="btn btn-secondary" onclick="window.open('/api/redoc', '_blank')">📖 View ReDoc</button>
            </div>
        </div>
        
        <script>
            // Load status on page load
            window.addEventListener('load', () => {
                refreshStatus();
                loadAnalytics();
            });
            
            async function refreshStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    document.getElementById('balance').textContent = data.balance.toFixed(2) + ' credits';
                    document.getElementById('requests').textContent = data.total_requests;
                    document.getElementById('cost').textContent = data.total_cost.toFixed(2) + ' credits';
                    document.getElementById('most-used').textContent = data.most_used_provider || 'N/A';
                } catch (error) {
                    console.error('Error loading status:', error);
                }
            }
            
            async function makeRequest() {
                const model = document.getElementById('model').value;
                const prompt = document.getElementById('prompt').value;
                const responseDiv = document.getElementById('request-response');
                
                if (!prompt) {
                    showResponse(responseDiv, 'Please enter a prompt', 'error');
                    return;
                }
                
                responseDiv.innerHTML = '<div class="loading"></div> Processing...';
                responseDiv.className = 'response show';
                
                try {
                    const response = await fetch('/api/request', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ model, prompt })
                    });
                    
                    const data = await response.json();
                    
                    if (data.status === 'success') {
                        showResponse(responseDiv, 
                            `✅ Success! Cost: ${data.cost} credits | Balance: ${data.balance} credits<br><br>Response: ${JSON.stringify(data.response)}`,
                            'success'
                        );
                        refreshStatus();
                    } else {
                        showResponse(responseDiv, `❌ Error: ${data.message}`, 'error');
                    }
                } catch (error) {
                    showResponse(responseDiv, `❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function addCredits() {
                const amount = parseFloat(document.getElementById('credits').value);
                const responseDiv = document.getElementById('credits-response');
                
                if (!amount || amount <= 0) {
                    showResponse(responseDiv, 'Please enter a valid amount', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/credits/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ amount })
                    });
                    
                    const data = await response.json();
                    showResponse(responseDiv, 
                        `✅ Added ${amount} credits! New balance: ${data.balance} credits`,
                        'success'
                    );
                    refreshStatus();
                } catch (error) {
                    showResponse(responseDiv, `❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function loadAnalytics() {
                const analyticsDiv = document.getElementById('analytics');
                analyticsDiv.innerHTML = '<div class="loading"></div> Loading...';
                
                try {
                    const response = await fetch('/api/analytics');
                    const data = await response.json();
                    
                    let html = '<div style="white-space: pre-wrap; font-family: monospace; font-size: 12px;">';
                    html += data.summary.replace(/\n/g, '<br>');
                    html += '</div>';
                    
                    analyticsDiv.innerHTML = html;
                } catch (error) {
                    analyticsDiv.innerHTML = `❌ Error loading analytics: ${error.message}`;
                }
            }
            
            function showResponse(element, message, type) {
                element.innerHTML = message;
                element.className = `response show ${type}`;
            }
        </script>
    </body>
    </html>
    """


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """
    Get current system status.
    Получить текущий статус системы.
    """
    return {
        "api_mode": "Real" if system.use_real_api else "Mock (Demo)",
        "balance": system.wallet.get_balance(),
        "total_requests": system.analytics.get_request_count(),
        "total_cost": system.analytics.get_total_cost(),
        "average_cost": system.analytics.get_average_cost_per_request() if system.analytics.get_request_count() > 0 else None,
        "most_used_provider": system.analytics.get_most_used_provider()
    }


@app.post("/api/request", response_model=AIResponse)
async def process_request(request: AIRequest):
    """
    Process an AI request.
    Обработать запрос к AI.
    """
    result = system.process_request(request.model, request.prompt)
    return result


@app.get("/api/analytics")
async def get_analytics():
    """
    Get analytics summary.
    Получить сводку аналитики.
    """
    return {
        "summary": system.analytics.get_summary_report(),
        "data": system.analytics.export_to_dict()
    }


@app.get("/api/analytics/export")
async def export_analytics():
    """
    Export analytics data.
    Экспортировать данные аналитики.
    """
    return JSONResponse(
        content=system.analytics.export_to_dict(),
        headers={
            "Content-Disposition": f"attachment; filename=analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )


@app.get("/api/budget")
async def get_budget():
    """
    Get budget information.
    Получить информацию о бюджете.
    """
    return {
        "summary": system.budget.get_budget_summary(),
        "limits": system.budget.limits,
        "provider_budgets": system.budget.provider_limits
    }


@app.post("/api/budget/limit")
async def set_budget_limit(limit: BudgetLimit):
    """
    Set budget limit for a period.
    Установить лимит бюджета на период.
    """
    try:
        period = BudgetPeriod[limit.period.upper()]
        system.budget.set_limit(period, limit.amount)
        return {"message": f"Budget limit set: {limit.period} = {limit.amount}"}
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid period: {limit.period}. Valid: daily, weekly, monthly, total"
        )


@app.post("/api/budget/provider")
async def set_provider_budget(budget: ProviderBudget):
    """
    Set budget limit for a provider.
    Установить лимит бюджета для провайдера.
    """
    system.budget.set_provider_limit(budget.provider, budget.amount)
    return {"message": f"Provider budget set: {budget.provider} = {budget.amount}"}


@app.post("/api/credits/add")
async def add_credits(update: CreditsUpdate):
    """
    Add credits to wallet.
    Добавить кредиты в кошелёк.
    """
    system.wallet.add_credits(update.amount)
    return {
        "message": f"Added {update.amount} credits",
        "balance": system.wallet.get_balance()
    }


@app.get("/api/providers")
async def get_providers():
    """
    Get list of available providers.
    Получить список доступных провайдеров.
    """
    return {
        "providers": [
            {"name": "gpt", "type": "text", "rate": system.pricing.get_rate("gpt")},
            {"name": "image", "type": "image", "rate": system.pricing.get_rate("image")},
            {"name": "audio", "type": "audio", "rate": system.pricing.get_rate("audio")},
            {"name": "video", "type": "video", "rate": system.pricing.get_rate("video")}
        ]
    }


@app.get("/api/config")
async def get_config():
    """
    Get current configuration.
    Получить текущую конфигурацию.
    """
    return system.config.to_dict()


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Endpoint проверки здоровья.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting OneFlow.AI Web Server")
    print("=" * 60)
    print("\n📍 Server will be available at:")
    print("   • Main Dashboard: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/api/docs")
    print("   • ReDoc: http://localhost:8000/api/redoc")
    print("\n⚡ Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
