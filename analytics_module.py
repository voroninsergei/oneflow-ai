"""
Analytics module for OneFlow.AI.
Модуль аналитики для OneFlow.AI.

This module provides comprehensive analytics and usage tracking for OneFlow.AI,
including request logging, cost analysis, and provider statistics.

Этот модуль предоставляет всестороннюю аналитику и отслеживание использования
OneFlow.AI, включая логирование запросов, анализ затрат и статистику провайдеров.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict


class Analytics:
    """
    Analytics system for tracking OneFlow.AI usage.
    Система аналитики для отслеживания использования OneFlow.AI.
    """
    
    def __init__(self):
        """
        Initialize analytics system.
        Инициализировать систему аналитики.
        """
        self.requests: List[Dict[str, Any]] = []
        self.provider_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_cost': 0.0,
            'success_count': 0,
            'error_count': 0
        })
    
    def log_request(self, provider: str, cost: float, prompt: str,
                   status: str = 'success', response: str = '') -> None:
        """
        Log an AI request.
        Записать запрос к AI.
        
        Args:
            provider: Provider name.
            cost: Request cost.
            prompt: User prompt.
            status: Request status (success, error, budget_exceeded, etc.).
            response: Response from provider.
        """
        request_log = {
            'timestamp': datetime.now().isoformat(),
            'provider': provider,
            'cost': cost,
            'prompt': prompt,
            'status': status,
            'response': response
        }
        
        self.requests.append(request_log)
        
        # Update provider statistics
        self.provider_stats[provider]['count'] += 1
        self.provider_stats[provider]['total_cost'] += cost
        
        if status == 'success':
            self.provider_stats[provider]['success_count'] += 1
        else:
            self.provider_stats[provider]['error_count'] += 1
    
    def get_total_cost(self) -> float:
        """
        Get total cost of all requests.
        Получить общую стоимость всех запросов.
        
        Returns:
            float: Total cost.
        """
        return sum(req['cost'] for req in self.requests)
    
    def get_request_count(self) -> int:
        """
        Get total number of requests.
        Получить общее количество запросов.
        
        Returns:
            int: Number of requests.
        """
        return len(self.requests)
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each provider.
        Получить статистику для каждого провайдера.
        
        Returns:
            dict: Provider statistics.
        """
        return dict(self.provider_stats)
    
    def get_most_used_provider(self) -> Optional[str]:
        """
        Get the most frequently used provider.
        Получить наиболее часто используемого провайдера.
        
        Returns:
            str or None: Provider name or None if no requests.
        """
        if not self.provider_stats:
            return None
        
        return max(self.provider_stats.items(),
                  key=lambda x: x[1]['count'])[0]
    
    def get_most_expensive_provider(self) -> Optional[str]:
        """
        Get the provider with highest total cost.
        Получить провайдера с наибольшей общей стоимостью.
        
        Returns:
            str or None: Provider name or None if no requests.
        """
        if not self.provider_stats:
            return None
        
        return max(self.provider_stats.items(),
                  key=lambda x: x[1]['total_cost'])[0]
    
    def get_average_cost_per_request(self) -> float:
        """
        Get average cost per request.
        Получить среднюю стоимость запроса.
        
        Returns:
            float: Average cost, or 0.0 if no requests.
        """
        if not self.requests:
            return 0.0
        
        return self.get_total_cost() / len(self.requests)
    
    def get_success_rate(self) -> float:
        """
        Get overall success rate percentage.
        Получить общий процент успешных запросов.
        
        Returns:
            float: Success rate (0-100).
        """
        if not self.requests:
            return 0.0
        
        success_count = sum(1 for req in self.requests if req['status'] == 'success')
        return (success_count / len(self.requests)) * 100
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent requests.
        Получить последние запросы.
        
        Args:
            limit: Maximum number of requests to return.
        
        Returns:
            list: Recent requests.
        """
        return self.requests[-limit:] if self.requests else []
    
    def get_requests_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get requests filtered by status.
        Получить запросы, отфильтрованные по статусу.
        
        Args:
            status: Status to filter by.
        
        Returns:
            list: Filtered requests.
        """
        return [req for req in self.requests if req['status'] == status]
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export analytics data to dictionary.
        Экспортировать данные аналитики в словарь.
        
        Returns:
            dict: Complete analytics data.
        """
        return {
            'total_requests': self.get_request_count(),
            'total_cost': self.get_total_cost(),
            'average_cost': self.get_average_cost_per_request(),
            'success_rate': self.get_success_rate(),
            'most_used_provider': self.get_most_used_provider(),
            'most_expensive_provider': self.get_most_expensive_provider(),
            'provider_stats': self.get_provider_stats(),
            'recent_requests': self.get_recent_requests(limit=20),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_summary_report(self) -> str:
        """
        Generate summary analytics report.
        Сгенерировать сводный отчёт аналитики.
        
        Returns:
            str: Formatted analytics report.
        """
        lines = []
        lines.append("=" * 60)
        lines.append("Analytics Summary | Сводка аналитики")
        lines.append("=" * 60)
        
        if not self.requests:
            lines.append("\nNo requests recorded yet | Запросов пока не записано")
            lines.append("=" * 60)
            return "\n".join(lines)
        
        # Overall statistics
        lines.append(f"\nTotal Requests | Всего запросов: {self.get_request_count()}")
        lines.append(f"Total Cost | Общая стоимость: {self.get_total_cost():.2f} credits")
        lines.append(f"Average Cost | Средняя стоимость: {self.get_average_cost_per_request():.2f} credits")
        lines.append(f"Success Rate | Успешность: {self.get_success_rate():.1f}%")
        
        # Provider statistics
        lines.append("\nProvider Statistics | Статистика провайдеров:")
        lines.append("-" * 60)
        
        for provider, stats in sorted(self.provider_stats.items()):
            lines.append(f"\n{provider.upper()}:")
            lines.append(f"  Requests | Запросов: {stats['count']}")
            lines.append(f"  Total Cost | Общая стоимость: {stats['total_cost']:.2f} credits")
            lines.append(f"  Success | Успешно: {stats['success_count']}")
            lines.append(f"  Errors | Ошибки: {stats['error_count']}")
            
            if stats['count'] > 0:
                avg_cost = stats['total_cost'] / stats['count']
                success_rate = (stats['success_count'] / stats['count']) * 100
                lines.append(f"  Avg Cost | Средняя: {avg_cost:.2f} credits")
                lines.append(f"  Success Rate | Успешность: {success_rate:.1f}%")
        
        # Most used and expensive
        lines.append("\nTop Providers | Топ провайдеры:")
        lines.append("-" * 60)
        lines.append(f"Most Used | Чаще всего: {self.get_most_used_provider()}")
        lines.append(f"Most Expensive | Дороже всего: {self.get_most_expensive_provider()}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
