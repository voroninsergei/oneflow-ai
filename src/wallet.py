"""
wallet.py - OneFlow.AI Wallet Module

This module defines a Wallet class for managing user credits and budgets. The wallet tracks available credits, allows adding credits, deducting cost for requests, and retrieving the current balance. It also provides a method to check if the wallet can afford a given cost.

wallet.py - Модуль кошелька OneFlow.AI

Этот модуль определяет класс Wallet для управления кредитами и бюджетами пользователя. Кошелек отслеживает доступные кредиты, позволяет пополнять баланс, списывать стоимость запросов и получать текущий баланс. Также предоставляет метод для проверки, может ли кошелек оплатить указанную стоимость.
"""

class Wallet:
    """
    Wallet manages user credits for API requests in OneFlow.AI.
    The wallet starts with an initial balance and supports adding and deducting credits.

    Класс Wallet управляет кредитами пользователя для запросов в OneFlow.AI.
    Кошелек начинается с первоначального баланса и поддерживает добавление и списание кредитов.
    """
    def __init__(self, initial_balance: float = 0.0):
        """
        Initialize the wallet with an initial balance.

        Инициализирует кошелек с начальным балансом.

        Args:
            initial_balance (float): The starting amount of credits. Начальное количество кредитов.
        """
        self.balance = float(initial_balance)

    def add_credits(self, amount: float):
        """
        Add credits to the wallet.

        Пополняет кошелек.

        Args:
            amount (float): The amount of credits to add. Количество добавляемых кредитов.
        """
        self.balance += float(amount)

    def deduct(self, cost: float) -> bool:
        """
        Deduct credits from the wallet if possible.

        Списывает кредиты из кошелка, если возможно.

        Args:
            cost (float): The cost to deduct. Стоимость, которая должна быть списана.

        Returns:
            bool: True if deduction succeeded, False otherwise. True, если списание удалось, иначе False.
        """
        if self.balance >= cost:
            self.balance -= float(cost)
            return True
        return False

    def get_balance(self) -> float:
        """
        Get the current balance of the wallet.

        Возвращает текущий баланс кошелька.

        Returns:
            float: The available credits. Доступные кредиты.
        """
        return self.balance

    def can_afford(self, cost: float) -> bool:
        """
        Check if the wallet can cover the cost.

        Проверяет, может ли кошелек покрыть стоимость.

        Args:
            cost (float): The cost to check. Стоимость для проверки.

        Returns:
            bool: True if the wallet has enough credits, False otherwise.
            True, если в кошелке достаточно кредитов, иначе False.
        """
        return self.balance >= cost
