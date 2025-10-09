"""
Unit tests for the Wallet class in OneFlow.AI

English:
This test module verifies the basic functionality of the Wallet class,
including adding credits, deducting credits, checking balances and affordability.

Русская версия:
Данный модуль тестирует функциональность класса Wallet,
включая добавление кредитов, списание, проверку баланса и достаточности средств.
"""

import os
import sys
import pytest

# Adjust the path so that src modules can be imported when running tests from repository root
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from wallet import Wallet

def test_wallet_add_and_deduct():
    wallet = Wallet(initial_balance=10)
    assert wallet.get_balance() == 10
    wallet.add_credits(5)
    assert wallet.get_balance() == 15
    wallet.deduct(7)
    assert wallet.get_balance() == 8


def test_wallet_can_afford():
    wallet = Wallet(initial_balance=3)
    assert wallet.can_afford(2) is True
    assert wallet.can_afford(4) is False
