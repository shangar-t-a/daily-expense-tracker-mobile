"""Data models for the Daily Expense Tracker application.

This module defines the core data structures used throughout the application,
including expense rows and complete expense entries.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExpenseRow:
    """Represents a single row in an expense entry.

    Args:
        item: Name or description of the expense item.
        balance: Balance or income amount as a string.
        expense: Expense amount as a string.
    """

    item: str = ""
    balance: str = ""
    expense: str = ""

    def is_empty(self) -> bool:
        """Check if this row contains any data.

        Returns:
            bool: True if all fields are empty, False otherwise.
        """
        return not (self.item.strip() or self.balance.strip() or self.expense.strip())

    def to_dict(self) -> dict[str, str]:
        """Convert row to dictionary format for JSON serialization.

        Returns:
            dict: Dictionary with keys 'item', 'balance', 'expense'.
        """
        return {
            "item": self.item,
            "balance": self.balance,
            "expense": self.expense,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "ExpenseRow":
        """Create ExpenseRow from dictionary.

        Args:
            data (dict): Dictionary containing 'item', 'balance', 'expense' keys.

        Returns:
            ExpenseRow: New ExpenseRow instance.
        """
        return cls(
            item=data.get("item", ""),
            balance=data.get("balance", ""),
            expense=data.get("expense", ""),
        )

    def get_balance_float(self) -> float:
        """Get balance as float, returning 0.0 if invalid.

        Returns:
            float: Balance as float, or 0.0 if conversion fails.
        """
        try:
            return float(self.balance) if self.balance.strip() else 0.0
        except ValueError:
            return 0.0

    def get_expense_float(self) -> float:
        """Get expense as float, returning 0.0 if invalid.

        Returns:
            float: Expense as float, or 0.0 if conversion fails.
        """
        try:
            return float(self.expense) if self.expense.strip() else 0.0
        except ValueError:
            return 0.0


@dataclass
class ExpenseEntry:
    """Represents a complete expense entry with metadata.

    Args:
        name: User-provided name for the entry.
        timestamp: When the entry was created/saved.
        rows: List of expense rows containing the data.
    """

    name: str
    timestamp: datetime
    rows: list[ExpenseRow] = field(default_factory=list)

    @property
    def save_key(self) -> str:
        """Generate the storage key for this entry.

        Returns:
            str: Key in format: '{name} @ {YYYY-MM-DD HH:MM:SS}'.
        """
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{self.name} @ {timestamp_str}"

    def calculate_totals(self) -> tuple[float, float, float]:
        """Calculate total balance, total expense, and remaining balance.

        Returns:
            tuple: Tuple of (total_balance, total_expense, remaining_balance).
        """
        total_balance = sum(row.get_balance_float() for row in self.rows)
        total_expense = sum(row.get_expense_float() for row in self.rows)
        remaining = total_balance - total_expense
        return total_balance, total_expense, remaining

    def to_dict(self) -> dict[str, list[dict[str, str]]]:
        """Convert entry to dictionary format for JSON storage.

        Returns:
            dict: Dictionary with 'entries' key containing list of row entries.
        """
        return {"entries": [row.to_dict() for row in self.rows if not row.is_empty()]}

    @classmethod
    def from_dict(cls, save_key: str, data: dict[str, list[dict[str, str]]]) -> "ExpenseEntry":
        """Create ExpenseEntry from storage dictionary.

        Args:
            save_key (str): The storage key in format '{name} @ {timestamp}'.
            data (dict): Dictionary containing 'entries' with list of row dicts.

        Returns:
            ExpenseEntry: New ExpenseEntry instance.

        Raises:
            ValueError: If save_key format is invalid or data is malformed.
        """
        # Parse save_key to extract name and timestamp
        if " @ " not in save_key:
            raise ValueError(f"Invalid save_key format: {save_key}")

        name, timestamp_str = save_key.split(" @ ", 1)

        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise ValueError(f"Invalid timestamp format in save_key: {timestamp_str}") from e

        # Parse rows
        rows_data = data.get("entries", [])
        rows = [ExpenseRow.from_dict(row_data) for row_data in rows_data]

        return cls(name=name, timestamp=timestamp, rows=rows)

    def __str__(self) -> str:
        """String representation of the entry.

        Returns:
            str: The save_key for this entry.
        """
        return self.save_key
