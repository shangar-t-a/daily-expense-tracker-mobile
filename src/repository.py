"""Repository for managing expense entry persistence.

This module handles all JSON file operations for storing and retrieving expense entries.
"""

import json
from pathlib import Path
from typing import Any

from models import ExpenseEntry


class ExpenseRepository:
    """Repository for expense entry storage and retrieval.

    Manages JSON file operations for persisting expense data.

    Attributes:
        storage_path (str | Path): Path to the JSON storage file.
    """

    def __init__(self, storage_path: str | Path) -> None:
        """Initialize the repository.

        Args:
            storage_path (str | Path): Path to the JSON storage file.
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage file and parent directories if they don't exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_data({})

    def _read_data(self) -> dict[str, Any]:
        """Read all data from storage file.

        Returns:
            dict[str, Any]: Dictionary containing all saved entries.

        Raises:
            IOError: If file cannot be read.
            json.JSONDecodeError: If file contains invalid JSON.
        """
        try:
            with open(self.storage_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Backup corrupted file
            backup_path = self.storage_path.with_suffix(".json.bak")
            if self.storage_path.exists():
                self.storage_path.rename(backup_path)
            # Create fresh file
            self._write_data({})
            return {}

    def _write_data(self, data: dict[str, Any]) -> None:
        """Write data to storage file.

        Args:
            data (dict[str, Any]): Dictionary to write to storage.

        Raises:
            IOError: If file cannot be written.
        """
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_all(self) -> dict[str, ExpenseEntry]:
        """Load all expense entries from storage.

        Returns:
            dict[str, ExpenseEntry]: Dictionary mapping save_key to ExpenseEntry objects.

        Raises:
            IOError: If storage cannot be read.
        """
        data = self._read_data()
        entries: dict[str, ExpenseEntry] = {}

        for save_key, entry_data in data.items():
            try:
                entry = ExpenseEntry.from_dict(save_key, entry_data)
                entries[save_key] = entry
            except (ValueError, KeyError) as e:
                # Skip malformed entries but log the issue
                print(f"Warning: Skipping malformed entry '{save_key}': {e}")
                continue

        return entries

    def load_entry(self, save_key: str) -> ExpenseEntry | None:
        """Load a specific entry by its save key.

        Args:
            save_key (str): The key identifying the entry.

        Returns:
            ExpenseEntry | None: ExpenseEntry if found, None otherwise.

        Raises:
            IOError: If storage cannot be read.
        """
        data = self._read_data()

        if save_key not in data:
            return None

        try:
            return ExpenseEntry.from_dict(save_key, data[save_key])
        except (ValueError, KeyError) as e:
            print(f"Warning: Could not load entry '{save_key}': {e}")
            return None

    def save_entry(self, entry: ExpenseEntry) -> None:
        """Save an expense entry to storage.

        If an entry with the same save_key exists, it will be overwritten.

        Args:
            entry: The ExpenseEntry to save.

        Raises:
            IOError: If storage cannot be written.
        """
        data = self._read_data()
        data[entry.save_key] = entry.to_dict()
        self._write_data(data)

    def delete_entry(self, save_key: str) -> bool:
        """Delete an entry from storage.

        Args:
            save_key (str): The key identifying the entry to delete.

        Returns:
            bool: True if entry was deleted, False if not found.

        Raises:
            IOError: If storage cannot be written.
        """
        data = self._read_data()

        if save_key not in data:
            return False

        del data[save_key]
        self._write_data(data)
        return True

    def entry_exists(self, save_key: str) -> bool:
        """Check if an entry exists in storage.

        Args:
            save_key (str): The key identifying the entry.

        Returns:
            bool: True if entry exists, False otherwise.

        Raises:
            IOError: If storage cannot be read.
        """
        data = self._read_data()
        return save_key in data

    def get_all_keys(self) -> list[str]:
        """Get all save keys from storage.

        Returns:
            list[str]: List of all save keys, sorted reverse chronologically.

        Raises:
            IOError: If storage cannot be read.
        """
        data = self._read_data()
        # Sort by timestamp in reverse order (newest first)
        keys = sorted(
            data.keys(),
            key=lambda k: k.split(" @ ")[1] if " @ " in k else "",
            reverse=True,
        )
        return keys

    def clear_all(self) -> None:
        """Delete all entries from storage.

        Raises:
            IOError: If storage cannot be written.
        """
        self._write_data({})
