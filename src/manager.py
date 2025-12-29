"""Business logic manager for the Daily Expense Tracker.

This module contains the core business logic for managing expense entries,
including validation, calculations, and coordination with the repository.
"""

from datetime import datetime

from models import ExpenseEntry, ExpenseRow
from repository import ExpenseRepository

# Constants
MAX_SAVE_NAME_LENGTH = 50


class ExpenseManager:
    """Manager for expense business logic.

    Handles validation, calculations, and coordinates data operations
    with the repository.

    Attributes:
        repository (ExpenseRepository): Repository instance for data persistence.
    """

    def __init__(self, repository: ExpenseRepository) -> None:
        """Initialize the manager.

        Args:
            repository (ExpenseRepository): Repository instance for data operations.
        """
        self.repository = repository

    def validate_save_name(self, name: str) -> tuple[bool, str]:
        """Validate a save name.

        Args:
            name (str): The save name to validate.

        Returns:
            tuple[bool, str]: Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        name = name.strip()

        if not name:
            return False, "Save name cannot be empty"

        if len(name) > MAX_SAVE_NAME_LENGTH:
            return False, f"Save name is too long (max {MAX_SAVE_NAME_LENGTH} characters)"

        if "@" in name:
            return False, "Save name cannot contain '@' character"

        return True, ""

    def validate_rows(self, rows: list[ExpenseRow]) -> tuple[bool, str]:
        """Validate a list of expense rows.

        Args:
            rows (list[ExpenseRow]): List of ExpenseRow objects to validate.

        Returns:
            tuple[bool, str]: Tuple of (is_valid, error_message). If valid, error_message is empty.
        """
        # Check if at least one row has data
        has_data = any(not row.is_empty() for row in rows)

        if not has_data:
            return False, "At least one row must contain data"

        # Validate numeric fields
        for i, row in enumerate(rows, start=1):
            if row.is_empty():
                continue

            # Try to convert balance and expense to floats
            if row.balance.strip():
                try:
                    float(row.balance)
                except ValueError:
                    return False, f"Row {i}: Balance must be a valid number"

            if row.expense.strip():
                try:
                    float(row.expense)
                except ValueError:
                    return False, f"Row {i}: Expense must be a valid number"

        return True, ""

    def calculate_totals(self, rows: list[ExpenseRow]) -> tuple[float, float, float]:
        """Calculate totals from expense rows.

        Args:
            rows (list[ExpenseRow]): List of ExpenseRow objects.

        Returns:
            tuple[float, float, float]: Tuple of (total_balance, total_expense, remaining_balance).
        """
        total_balance = sum(row.get_balance_float() for row in rows)
        total_expense = sum(row.get_expense_float() for row in rows)
        remaining = total_balance - total_expense
        return total_balance, total_expense, remaining

    def create_entry(self, name: str, rows: list[ExpenseRow]) -> tuple[ExpenseEntry | None, str]:
        """Create a new expense entry.

        Args:
            name (str): Name for the entry.
            rows (list[ExpenseRow]): List of ExpenseRow objects.

        Returns:
            tuple[ExpenseEntry | None, str]: Tuple of (ExpenseEntry if successful, error_message).
            If successful, error_message is empty.
        """
        # Validate name
        is_valid, error = self.validate_save_name(name)
        if not is_valid:
            return None, error

        # Validate rows
        is_valid, error = self.validate_rows(rows)
        if not is_valid:
            return None, error

        # Filter out empty rows
        non_empty_rows = [row for row in rows if not row.is_empty()]

        # Create entry with current timestamp
        entry = ExpenseEntry(
            name=name.strip(),
            timestamp=datetime.now(),
            rows=non_empty_rows,
        )

        return entry, ""

    def save_entry(self, name: str, rows: list[ExpenseRow]) -> tuple[bool, str]:
        """Create and save an expense entry.

        Args:
            name (str): Name for the entry.
            rows (list[ExpenseRow]): List of ExpenseRow objects.

        Returns:
            tuple[bool, str]: Tuple of (success, message). Message contains error or success info.
        """
        # Create entry
        entry, error = self.create_entry(name, rows)
        if entry is None:
            return False, error

        # Check if entry with same name exists (warn but allow)
        existing_keys = self.repository.get_all_keys()
        name_exists = any(key.startswith(f"{entry.name} @") for key in existing_keys)

        try:
            # Save to repository
            self.repository.save_entry(entry)

            if name_exists:
                message = f"Entry saved (previous entry with name '{entry.name}' still exists)"
            else:
                message = "Entry saved successfully"

            return True, message

        except OSError as e:
            return False, f"Failed to save entry: {e}"

    def load_entry(self, save_key: str) -> tuple[ExpenseEntry | None, str]:
        """Load an expense entry by save key.

        Args:
            save_key (str): The key identifying the entry.

        Returns:
            tuple[ExpenseEntry | None, str]: Tuple of (ExpenseEntry if found, error_message).
            If successful, error_message is empty.
        """
        try:
            entry = self.repository.load_entry(save_key)

            if entry is None:
                return None, f"Entry not found: {save_key}"

            return entry, ""

        except OSError as e:
            return None, f"Failed to load entry: {e}"

    def load_all_entries(self) -> tuple[dict[str, ExpenseEntry], str]:
        """Load all expense entries.

        Returns:
            tuple[dict[str, ExpenseEntry], str]: Tuple of (dictionary of entries, error_message).
            If successful, error_message is empty.
        """
        try:
            entries = self.repository.load_all()
            return entries, ""

        except OSError as e:
            return {}, f"Failed to load entries: {e}"

    def delete_entry(self, save_key: str) -> tuple[bool, str]:
        """Delete an expense entry.

        Args:
            save_key (str): The key identifying the entry to delete.

        Returns:
            tuple[bool, str]: Tuple of (success, message).
        """
        try:
            deleted = self.repository.delete_entry(save_key)

            if not deleted:
                return False, f"Entry not found: {save_key}"

            return True, "Entry deleted successfully"

        except OSError as e:
            return False, f"Failed to delete entry: {e}"

    def get_all_save_keys(self) -> list[str]:
        """Get all save keys sorted reverse chronologically.

        Returns:
            list[str]: List of save keys (newest first).
        """
        try:
            return self.repository.get_all_keys()
        except OSError:
            return []

    def entry_exists(self, save_key: str) -> bool:
        """Check if an entry exists.

        Args:
            save_key (str): The key identifying the entry.

        Returns:
            True if entry exists, False otherwise.
        """
        try:
            return self.repository.entry_exists(save_key)
        except OSError:
            return False
