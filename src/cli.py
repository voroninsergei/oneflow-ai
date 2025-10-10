"""
OneFlow.AI CLI - Fixed Version
CLI OneFlow.AI - Исправленная версия

Working command-line interface with all documented commands.
Рабочий интерфейс командной строки со всеми задокументированными командами.
"""

import argparse
import sys
import json
from typing import Optional

# Try to import main components
try:
    from main import OneFlowAI
    HAS_MAIN = True
except ImportError:
    HAS_MAIN = False
    print("Warning: Could not import OneFlowAI. Some features may be limited.")

try:
    from budget import BudgetPeriod
    HAS_BUDGET = True
except ImportError:
    HAS_BUDGET = False


def handle_request(args):
    """Handle request command."""
    if not HAS_MAIN:
        print("Error: OneFlowAI module not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    result = system.process_request(args.model, args.prompt)
    
    if result['status'] == 'success':
        if args.verbose:
            print(f"✓ Success")
            print(f"  Provider: {result.get('provider', 'unknown')}")
            print(f"  Cost: {result['cost']:.2f} credits")
            print(f"  Balance: {result['balance']:.2f} credits")
            print(f"  Response: {result['response']}")
        else:
            print(result['response'])
        return 0
    else:
        print(f"✗ Error: {result['message']}", file=sys.stderr)
        return 1


def handle_status(args):
    """Handle status command."""
    if not HAS_MAIN:
        print("Error: OneFlowAI module not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    print(system.get_status())
    return 0


def handle_analytics(args):
    """Handle analytics command."""
    if not HAS_MAIN:
        print("Error: OneFlowAI module not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    
    if args.export:
        try:
            from analytics import Analytics
            analytics = Analytics()
            data = analytics.export_to_dict()
            
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Analytics exported to {args.export}")
            return 0
        except Exception as e:
            print(f"✗ Export failed: {e}", file=sys.stderr)
            return 1
    else:
        summary = system.get_analytics_summary()
        if summary:
            print(summary)
        else:
            print("Analytics not available")
        return 0


def handle_budget(args):
    """Handle budget command."""
    if not HAS_MAIN:
        print("Error: OneFlowAI module not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    summary = system.get_budget_summary()
    
    if summary:
        print(summary)
    else:
        print("Budget module not available")
    
    return 0


def handle_config(args):
    """Handle config command."""
    try:
        from config import Config
        config = Config()
        print(config.get_config_summary())
        return 0
    except ImportError:
        print("Config module not available")
        return 1


def handle_add_credits(args):
    """Handle add-credits command."""
    if not HAS_MAIN:
        print("Error: OneFlowAI module not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    
    try:
        system.add_credits(args.amount)
        print(f"✓ Added {args.amount:.2f} credits")
        print(f"  New balance: {system.wallet.get_balance():.2f} credits")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def handle_set_budget(args):
    """Handle set-budget command."""
    if not HAS_MAIN or not HAS_BUDGET:
        print("Error: Required modules not available")
        return 1
    
    system = OneFlowAI(initial_balance=100)
    
    try:
        system.setup_budget(**{args.period: args.amount})
        print(f"✓ Budget limit set: {args.period} = {args.amount:.2f} credits")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='oneflow',
        description='OneFlow.AI - AI Model Aggregator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  oneflow request gpt "Hello world"
  oneflow status
  oneflow analytics --export data.json
  oneflow add-credits 50
  oneflow set-budget daily 100

For more information: https://github.com/voroninsergei/oneflow-ai
        """
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # request command
    request_parser = subparsers.add_parser('request', help='Make an AI request')
    request_parser.add_argument('model', help='Model type (gpt, image, audio, video)')
    request_parser.add_argument('prompt', help='Request prompt')
    request_parser.set_defaults(func=handle_request)
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.set_defaults(func=handle_status)
    
    # analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show analytics')
    analytics_parser.add_argument('--export', help='Export to JSON file')
    analytics_parser.set_defaults(func=handle_analytics)
    
    # budget command
    budget_parser = subparsers.add_parser('budget', help='Show budget information')
    budget_parser.set_defaults(func=handle_budget)
    
    # config command
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.set_defaults(func=handle_config)
    
    # add-credits command
    credits_parser = subparsers.add_parser('add-credits', help='Add credits to wallet')
    credits_parser.add_argument('amount', type=float, help='Amount to add')
    credits_parser.set_defaults(func=handle_add_credits)
    
    # set-budget command
    budget_set_parser = subparsers.add_parser('set-budget', help='Set budget limit')
    budget_set_parser.add_argument('period', choices=['daily', 'weekly', 'monthly', 'total'])
    budget_set_parser.add_argument('amount', type=float, help='Limit amount')
    budget_set_parser.set_defaults(func=handle_set_budget)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Execute command
    try:
        return args.func(args)
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
