"""
Tests for Analytics module.
Тесты для модуля аналитики.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from analytics import Analytics


def test_analytics_initialization():
    """Test analytics initialization."""
    analytics = Analytics()
    assert analytics.get_request_count() == 0
    assert analytics.get_total_cost() == 0.0


def test_log_request():
    """Test logging a request."""
    analytics = Analytics()
    analytics.log_request('gpt', 5.0, 'test prompt', status='success')
    
    assert analytics.get_request_count() == 1
    assert analytics.get_total_cost() == 5.0


def test_multiple_requests():
    """Test logging multiple requests."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 2.0, 'prompt 1')
    analytics.log_request('image', 10.0, 'prompt 2')
    analytics.log_request('gpt', 3.0, 'prompt 3')
    
    assert analytics.get_request_count() == 3
    assert analytics.get_total_cost() == 15.0


def test_provider_stats():
    """Test provider statistics."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 2.0, 'p1', status='success')
    analytics.log_request('gpt', 3.0, 'p2', status='success')
    analytics.log_request('image', 10.0, 'p3', status='success')
    analytics.log_request('gpt', 1.0, 'p4', status='error')
    
    stats = analytics.get_provider_stats()
    
    assert 'gpt' in stats
    assert 'image' in stats
    assert stats['gpt']['count'] == 3
    assert stats['gpt']['total_cost'] == 6.0
    assert stats['gpt']['success_count'] == 2
    assert stats['gpt']['error_count'] == 1
    assert stats['image']['count'] == 1


def test_most_used_provider():
    """Test getting most used provider."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 1.0, 'p1')
    analytics.log_request('gpt', 1.0, 'p2')
    analytics.log_request('gpt', 1.0, 'p3')
    analytics.log_request('image', 10.0, 'p4')
    
    assert analytics.get_most_used_provider() == 'gpt'


def test_most_expensive_provider():
    """Test getting most expensive provider."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 2.0, 'p1')
    analytics.log_request('image', 15.0, 'p2')
    analytics.log_request('audio', 3.0, 'p3')
    
    assert analytics.get_most_expensive_provider() == 'image'


def test_average_cost():
    """Test average cost calculation."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 2.0, 'p1')
    analytics.log_request('image', 10.0, 'p2')
    analytics.log_request('audio', 6.0, 'p3')
    
    # Total: 18.0, Count: 3, Average: 6.0
    assert analytics.get_average_cost_per_request() == pytest.approx(6.0)


def test_recent_requests():
    """Test getting recent requests."""
    analytics = Analytics()
    
    for i in range(20):
        analytics.log_request('gpt', 1.0, f'prompt {i}')
    
    recent = analytics.get_recent_requests(limit=5)
    assert len(recent) == 5
    # Should get the last 5 (15-19)
    assert 'prompt 19' in recent[-1]['prompt']


def test_summary_report():
    """Test summary report generation."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 5.0, 'test')
    analytics.log_request('image', 10.0, 'test2')
    
    report = analytics.get_summary_report()
    
    assert 'Analytics Summary' in report
    assert 'Total Requests' in report
    assert 'Total Cost' in report
    assert 'gpt' in report
    assert 'image' in report


def test_export_to_dict():
    """Test exporting to dictionary."""
    analytics = Analytics()
    
    analytics.log_request('gpt', 5.0, 'test prompt')
    
    data = analytics.export_to_dict()
    
    assert 'total_requests' in data
    assert 'total_cost' in data
    assert 'provider_stats' in data
    assert 'requests' in data
    assert data['total_requests'] == 1
    assert data['total_cost'] == 5.0


def test_empty_analytics():
    """Test analytics with no data."""
    analytics = Analytics()
    
    assert analytics.get_most_used_provider() is None
    assert analytics.get_most_expensive_provider() is None
    assert analytics.get_average_cost_per_request() == 0.0
    assert analytics.get_recent_requests() == []


def test_import():
    """Test that analytics module can be imported."""
    import analytics
    assert analytics is not None
