"""
Wallet module for credit management.
Модуль кошелька для управления кредитами.
"""

from typing import Final


class InsufficientFundsError(Exception):
    """Raised when wallet has insufficient funds."""
    pass


class Wallet:
    """
    Manages user credits for API requests.
    Управляет кредитами пользователя для API запросов.
    """

    def __init__(self, initial_balance: float = 0.0) -> None:
        """
        Initialize wallet with initial balance.

        Args:
            initial_balance: Starting amount of credits.

        Raises:
            ValueError: If initial_balance is negative.
        """
        if initial_balance < 0:
            raise ValueError(f"Initial balance cannot be negative: {initial_balance}")
        self._balance: float = float(initial_balance)

    def add_credits(self, amount: float) -> None:
        """
        Add credits to the wallet.

        Args:
            amount: Amount of credits to add.

        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError(f"Cannot add negative amount: {amount}")
        self._balance += float(amount)

    def deduct(self, cost: float) -> bool:
        """
        Deduct credits from wallet if sufficient balance exists.

        Args:
            cost: Cost to deduct.

        Returns:
            True if deduction succeeded, False otherwise.

        Raises:
            ValueError: If cost is negative.
        """
        if cost < 0:
            raise ValueError(f"Cost cannot be negative: {cost}")
        if self._balance >= cost:
            self._balance -= float(cost)
            return True
        return False

    def deduct_or_raise(self, cost: float) -> None:
        """
        Deduct credits or raise exception if insufficient.

        Args:
            cost: Cost to deduct.

        Raises:
            InsufficientFundsError: If balance is insufficient.
            ValueError: If cost is negative.
        """
        if cost < 0:
            raise ValueError(f"Cost cannot be negative: {cost}")
        if self._balance < cost:
            raise InsufficientFundsError(
                f"Insufficient funds: balance={self._balance:.2f}, required={cost:.2f}"
            )
        self._balance -= float(cost)

    def get_balance(self) -> float:
        """
        Get current balance.

        Returns:
            Available credits.
        """
        return self._balance

    def can_afford(self, cost: float) -> bool:
        """
        Check if wallet can cover the cost.

        Args:
            cost: Cost to check.

        Returns:
            True if balance is sufficient.

        Raises:
            ValueError: If cost is negative.
        """
        if cost < 0:
            raise ValueError(f"Cost cannot be negative: {cost}")
        return self._balance >= cost

    def __repr__(self) -> str:
        return f"Wallet(balance={self._balance:.2f})"


__all__ = [
    "Wallet",
    "InsufficientFundsError",
]
