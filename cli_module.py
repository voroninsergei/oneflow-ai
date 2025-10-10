"""
Command Line Interface for OneFlow.AI.
Интерфейс командной строки для OneFlow.AI.

This module provides a comprehensive CLI for interacting with OneFlow.AI,
including commands for requests, analytics, budget management, and configuration.

Этот модуль предоставляет полноценный CLI для взаимодействия с OneFlow.AI,
включая команды для запросов, аналитики, управления бюджетом и конфигурации.
"""

import argparse
import sys
from typing import Optional
from main import OneFlowAI
from config import Config, get_config
from budget import BudgetPeriod


class OneFlowCLI:
    """
    Command Line Interface for OneFlow.AI.
    Интерфейс командной строки для OneFlow.AI.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize CLI with optional configuration file.
        Инициализировать CLI с необязательным файлом конфигурации.
        
        Args:
            config_file: Path to configuration file.
        """
        self.config = Config(config_file) if config_file else Config()
        self.system = OneFlowAI(initial_balance=self.config.wallet_balance)
        self._apply_config()
    
    def _apply_config(self):
        """Apply configuration to the system."""
        # Apply budget limits
        for period_name, limit in self.config.budget_limits.items():
            if limit is not None:
                period = BudgetPeriod[period_name.upper()]
                self.system.budget.set_limit(period, limit)
        
        # Apply provider budgets
        for provider, limit in self.config.provider_budgets.items():
            if limit is not None:
                self.system.budget.set_provider_limit(provider, limit)
    
    def request(self, model: str, prompt: str, verbose: bool = False) -> int:
        """
        Process an AI request.
        Обработать запрос к AI.
        
        Args:
            model: Model type.
            prompt: User prompt.
            verbose: Show detailed output.
        
        Returns:
            int: Exit code (0 for success, 1 for error).
        """
        result = self.system.process_request(model, prompt)
        
        if result['status'] == 'success':
            if verbose:
                print(f"✓ Request successful")
                print(f"  Model: {model}")
                print(f"  Cost: {result['cost']:.2f} credits")
                print(f"  Balance: {result['balance']:.2f} credits")
                print(f"  Response: {result['response']}")
            else:
                print(result['response'])
            return 0
        else:
            print(f"✗ Error: {result['message']}", file=sys.stderr)
            if verbose:
                print(f"  Balance: {result['balance']:.2f} credits", file=sys.stderr)
            return 1
    
    def status(self):
        """
        Display system status.
        Показать статус системы.
        """
        print(self.system.get_status())
    
    def analytics(self, detailed: bool = False):
        """
        Display analytics report.
        Показать отчёт аналитики.
        
        Args:
            detailed: Show detailed report.
        """
        if detailed:
            print(self.system.analytics.get_summary_report())
            
            recent = self.system.analytics.get_recent_requests(limit=5)
            if recent:
                print("\nRecent Requests | Последние запросы:")
                print("-" * 60)
                for i, req in enumerate(recent, 1):
                    print(f"{i}. [{req['provider']}] {req['prompt'][:50]}...")
                    print(f"   Cost: {req['cost']:.2f} | Status: {req['status']}")
        else:
            print(self.system.analytics.get_summary_report())
    
    def budget(self):
        """
        Display budget information.
        Показать информацию о бюджете.
        """
        print(self.system.budget.get_budget_summary())
    
    def config_info(self):
        """
        Display configuration information.
        Показать информацию о конфигурации.
        """
        print(self.config.get_config_summary())
    
    def add_credits(self, amount: float):
        """
        Add credits to wallet.
        Добавить кредиты в кошелёк.
        
        Args:
            amount: Amount to add.
        """
        try:
            self.system.wallet.add_credits(amount)
            print(f"✓ Added {amount:.2f} credits")
            print(f"  New balance: {self.system.wallet.get_balance():.2f} credits")
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
        return 0
    
    def set_budget(self, period: str, amount: float):
        """
        Set budget limit for a period.
        Установить лимит бюджета на период.
        
        Args:
            period: Period name (daily, weekly, monthly, total).
            amount: Limit amount.
        """
        try:
            period_enum = BudgetPeriod[period.upper()]
            self.system.budget.set_limit(period_enum, amount)
            print(f"✓ Set {period} budget limit to {amount:.2f} credits")
        except KeyError:
            print(f"✗ Invalid period: {period}", file=sys.stderr)
            print(f"   Valid periods: daily, weekly, monthly, total", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"✗ Error: {e}", file=sys.stderr)
            return 1
        return 0
    
    def export_analytics(self, filepath: str):
        """
        Export analytics data to JSON file.
        Экспортировать данные аналитики в JSON файл.
        
        Args:
            filepath: Output file path.
        """
        import json
        
        try:
            data = self.system.analytics.export_to_dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Analytics exported to {filepath}")
        except Exception as e:
            print(f"✗ Error exporting analytics: {e}", file=sys.stderr)
            return 1
        return 0


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.
    Создать парсер аргументов для CLI.
    
    Returns:
        ArgumentParser: Configured parser.
    """
    parser = argparse.ArgumentParser(
        prog='oneflow',
        description='OneFlow.AI - AI Model Aggregator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  oneflow request gpt "Hello world"
  oneflow status
  oneflow analytics --detailed
  oneflow budget
  oneflow add-credits 50
  oneflow set-budget daily 100

For more information, visit: https://github.com/yourrepo/OneFlow.AI
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Request command
    request_parser = subparsers.add_parser('request', help='Make an AI request')
    request_parser.add_argument('model', type=str, help='Model type (gpt, image, audio, video)')
    request_parser.add_argument('prompt', type=str, help='Request prompt')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show analytics report')
    analytics_parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed report')
    analytics_parser.add_argument('--export', type=str, help='Export to JSON file')
    
    # Budget command
    subparsers.add_parser('budget', help='Show budget information')
    
    # Config command
    subparsers.add_parser('config', help='Show configuration')
    
    # Add credits command
    credits_parser = subparsers.add_parser('add-credits', help='Add credits to wallet')
    credits_parser.add_argument('amount', type=float, help='Amount to add')
    
    # Set budget command
    budget_parser = subparsers.add_parser('set-budget', help='Set budget limit')
    budget_parser.add_argument('period', type=str, choices=['daily', 'weekly', 'monthly', 'total'],
                              help='Budget period')
    budget_parser.add_argument('amount', type=float, help='Limit amount')
    
    return parser


def main():
    """
    Main entry point for CLI.
    Главная точка входа для CLI.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize CLI
    cli = OneFlowCLI(config_file=args.config)
    
    # Execute command
    try:
        if args.command == 'request':
            return cli.request(args.model, args.prompt, verbose=args.verbose)
        
        elif args.command == 'status':
            cli.status()
            return 0
        
        elif args.command == 'analytics':
            if hasattr(args, 'export') and args.export:
                return cli.export_analytics(args.export)
            else:
                cli.analytics(detailed=args.detailed)
                return 0
        
        elif args.command == 'budget':
            cli.budget()
            return 0
        
        elif args.command == 'config':
            cli.config_info()
            return 0
        
        elif args.command == 'add-credits':
            return cli.add_credits(args.amount)
        
        elif args.command == 'set-budget':
            return cli.set_budget(args.period, args.amount)
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
