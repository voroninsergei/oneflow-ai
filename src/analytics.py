"""
Analytics module for OneFlow.AI.
Модуль аналитики для OneFlow.AI.

This module provides comprehensive request tracking, cost analysis, and reporting.
Этот модуль предоставляет полное отслеживание запросов, анализ затрат и отчётность.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class Analytics:
    """
    Track and analyze API usage.
    Отслеживание и анализ использования API.
    """
    
    def __init__(self):
        """Initialize analytics tracker."""
        self.requests: List[Dict[str, Any]] = []
    
    def log_request(
        self,
        provider: str,
        cost: float,
        prompt: str,
        status: str = 'success',
        response: Optional[str] = None
    ) -> None:
        """
        Log an API request.
        Записать API запрос.
        
        Args:
            provider: Provider name.
            cost: Request cost.
            prompt: Input prompt.
            status: Request status ('success' or 'error').
            response: Response from provider (optional).
        """
        self.requests.append({
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'cost': cost,
            'prompt': prompt,
            'status': status,
            'response': response
        })
    
    def get_request_count(self) -> int:
        """Get total number of requests."""
        return len(self.requests)
    
    def get_total_cost(self) -> float:
        """Get total cost of all requests."""
        return sum(req['cost'] for req in self.requests)
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics by provider.
        Получить статистику по провайдерам.
        """
        stats = {}
        for req in self.requests:
            provider = req['provider']
            if provider not in stats:
                stats[provider] = {
                    'count': 0,
                    'total_cost': 0.0,
                    'success_count': 0,
                    'error_count': 0
                }
            
            stats[provider]['count'] += 1
            stats[provider]['total_cost'] += req['cost']
            
            if req['status'] == 'success':
                stats[provider]['success_count'] += 1
            else:
                stats[provider]['error_count'] += 1
        
        return stats
    
    def get_most_used_provider(self) -> Optional[str]:
        """Get the most frequently used provider."""
        if not self.requests:
            return None
        
        stats = self.get_provider_stats()
        return max(stats.items(), key=lambda x: x[1]['count'])[0]
    
    def get_most_expensive_provider(self) -> Optional[str]:
        """Get the provider with highest total cost."""
        if not self.requests:
            return None
        
        stats = self.get_provider_stats()
        return max(stats.items(), key=lambda x: x[1]['total_cost'])[0]
    
    def get_average_cost_per_request(self) -> float:
        """Get average cost per request."""
        if not self.requests:
            return 0.0
        return self.get_total_cost() / len(self.requests)
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent requests."""
        return self.requests[-limit:]
    
    def get_summary_report(self) -> str:
        """
        Generate summary report.
        Сгенерировать сводный отчёт.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Analytics Summary | Сводка аналитики")
        lines.append("=" * 60)
        
        total_requests = self.get_request_count()
        total_cost = self.get_total_cost()
        
        lines.append(f"\nTotal Requests | Всего запросов: {total_requests}")
        lines.append(f"Total Cost | Общая стоимость: {total_cost:.2f} credits")
        
        if total_requests > 0:
            avg_cost = self.get_average_cost_per_request()
            lines.append(f"Average Cost | Средняя стоимость: {avg_cost:.2f} credits")
            
            most_used = self.get_most_used_provider()
            most_expensive = self.get_most_expensive_provider()
            
            lines.append(f"\nMost Used Provider | Самый используемый: {most_used}")
            lines.append(f"Most Expensive | Самый дорогой: {most_expensive}")
            
            lines.append("\nProvider Statistics | Статистика провайдеров:")
            lines.append("-" * 60)
            
            stats = self.get_provider_stats()
            for provider, data in sorted(stats.items()):
                lines.append(f"\n  {provider}:")
                lines.append(f"    Requests | Запросов: {data['count']}")
                lines.append(f"    Cost | Стоимость: {data['total_cost']:.2f} credits")
                lines.append(f"    Success | Успешных: {data['success_count']}")
                lines.append(f"    Errors | Ошибок: {data['error_count']}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export analytics data to dictionary."""
        return {
            'total_requests': self.get_request_count(),
            'total_cost': self.get_total_cost(),
            'average_cost': self.get_average_cost_per_request(),
            'most_used_provider': self.get_most_used_provider(),
            'most_expensive_provider': self.get_most_expensive_provider(),
            'provider_stats': self.get_provider_stats(),
            'requests': self.requests
        }


def track(event: str, **kwargs):
    """Simple tracking function for compatibility."""
    print(f"Track: {event} - {kwargs}")
