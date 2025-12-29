"""Daily Expense Tracker mobile application.

Main application module defining screens and UI logic.
"""

from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField

from manager import ExpenseManager
from models import ExpenseRow
from repository import ExpenseRepository

# ----------------------------------------------------- Helpers --------------------------------------------------------


def format_indian_currency(amount: float, show_symbol: bool = True) -> str:
    """Format amount in Indian numbering system with commas.

    Args:
        amount (float): The amount to format
        show_symbol (bool): Whether to include ₹ symbol

    Returns:
        Formatted string like ₹1,00,000.00 or 1,00,000.00
    """
    # Constants
    rupee_to_paise = 100
    indian_numbering_last_group = 3
    indian_numbering_other_group = 2

    if amount == 0:
        return "₹0.00" if show_symbol else "0.00"

    # Handle negative numbers
    is_negative = amount < 0
    amount = abs(amount)

    # Split into integer and decimal parts
    rupees = int(amount)
    paise = int(round((amount - rupees) * rupee_to_paise))

    # Handle rounding edge case where paise becomes 100
    if paise >= rupee_to_paise:
        rupees += 1
        paise = 0

    # Convert to string and reverse for easier processing
    s = str(rupees)

    # Indian numbering: last 3 digits, then groups of 2
    if len(s) <= indian_numbering_last_group:
        result = s
    else:
        result = s[-indian_numbering_last_group:]  # Last 3 digits
        s = s[:-indian_numbering_last_group]
        while s:
            if len(s) <= indian_numbering_other_group:
                result = s + "," + result
                break
            else:
                result = s[-indian_numbering_other_group:] + "," + result
                s = s[:-indian_numbering_other_group]

    # Add decimal part
    formatted = f"{result}.{paise:02d}"

    if show_symbol:
        formatted = f"₹{formatted}"

    return f"-{formatted}" if is_negative else formatted


def parse_indian_currency(text: str) -> float:
    """Parse Indian formatted currency string to float.

    Args:
        text: String like ₹1,00,000.00 or 100000

    Returns:
        Float value
    """
    if not text or not text.strip():
        return 0.0

    # Remove currency symbol and commas
    cleaned = text.replace("₹", "").replace(",", "").strip()

    try:
        return float(cleaned)
    except ValueError:
        return 0.0


# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------ Custom Widgets ------------------------------------------------------


class CurrencyInput(MDTextField):
    """Custom MDTextField that formats currency on blur and shows plain number on focus."""

    def __init__(self, **kwargs):
        """Initialize currency input."""
        super().__init__(**kwargs)
        self._raw_value = ""
        self._is_focused = False
        # Bind to the focus event
        self.bind(focus=self.on_focus_change)

    def on_focus_change(self, instance, value):
        """Handle focus changes."""
        if value:
            # On focus - show raw editable value
            self._is_focused = True
            parsed = parse_indian_currency(self.text)
            if parsed == 0:
                self.text = ""
            else:
                # Show number without formatting for easier editing
                self.text = str(int(parsed)) if parsed == int(parsed) else f"{parsed:.2f}"
        else:
            # On blur - format the value
            self._is_focused = False
            parsed = parse_indian_currency(self.text)
            if parsed != 0:
                self.text = format_indian_currency(parsed, show_symbol=False)
            else:
                self.text = ""

    def get_value(self) -> float:
        """Get the numeric value."""
        return parse_indian_currency(self.text)


# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------ Screens -------------------------------------------------------


class TappableCard(ButtonBehavior, MDBoxLayout):
    """Tappable card widget combining button behavior with box layout."""

    pass


class ScreenManagement(ScreenManager):
    """Screen manager for navigation."""

    pass


class MainScreen(Screen):
    """Main entry screen with navigation buttons."""

    pass


class EditorScreen(Screen):
    """Expense editor screen for data entry and calculations."""

    def __init__(self, **kwargs):
        """Initialize the editor screen."""
        super().__init__(**kwargs)
        self.row_widgets: list[tuple[MDTextField, CurrencyInput, CurrencyInput]] = []

    def on_pre_enter(self) -> None:
        """Create row widgets when entering screen."""
        # Build rows only once
        if self.row_widgets:
            return

        grid = self.ids.grid
        for _ in range(15):
            # Item column (50% width) - MDTextField for item description
            item = MDTextField(
                mode="outlined",
                size_hint_x=0.5,
                font_size="15sp",
            )

            # Balance column (25% width) - with currency formatting
            bal = CurrencyInput(
                mode="outlined",
                input_type="number",
                size_hint_x=0.25,
                font_size="15sp",
                halign="right",
            )

            # Expense column (25% width) - with currency formatting
            exp = CurrencyInput(
                mode="outlined",
                input_type="number",
                size_hint_x=0.25,
                font_size="15sp",
                halign="right",
            )

            grid.add_widget(item)
            grid.add_widget(bal)
            grid.add_widget(exp)

            self.row_widgets.append((item, bal, exp))

    def get_rows_data(self) -> list[ExpenseRow]:
        """Extract data from UI widgets.

        Returns:
            list[ExpenseRow]: List of ExpenseRow objects from the editor.
        """
        rows = []
        for item, bal, exp in self.row_widgets:
            # Get raw numeric values for saving
            bal_value = bal.get_value()
            exp_value = exp.get_value()

            row = ExpenseRow(
                item=item.text,
                balance=str(bal_value) if bal_value != 0 else "",
                expense=str(exp_value) if exp_value != 0 else "",
            )
            rows.append(row)
        return rows

    def load_rows_data(self, rows: list[ExpenseRow]) -> None:
        """Load data into UI widgets.

        Args:
            rows (list[ExpenseRow]): List of ExpenseRow objects to display.
        """
        # Ensure widgets are created first
        if not self.row_widgets:
            self.on_pre_enter()

        # First clear all widgets
        self.clear_all()

        # Load data up to available slots
        for i, row in enumerate(rows[:15]):
            self.row_widgets[i][0].text = row.item

            # Format balance
            if row.balance.strip():
                bal_val = parse_indian_currency(row.balance)
                self.row_widgets[i][1].text = format_indian_currency(bal_val, show_symbol=False)

            # Format expense
            if row.expense.strip():
                exp_val = parse_indian_currency(row.expense)
                self.row_widgets[i][2].text = format_indian_currency(exp_val, show_symbol=False)

    def clear_all(self) -> None:
        """Clear all input fields and totals."""
        for item, bal, exp in self.row_widgets:
            item.text = ""
            bal.text = ""
            exp.text = ""

        self.ids.total_exp.text = ""
        self.ids.total_bal.text = ""
        self.ids.save_name.text = ""


class LoadScreen(Screen):
    """Load screen for displaying and managing saved entries."""

    def on_pre_enter(self) -> None:
        """Refresh the entry list when entering screen."""
        self.refresh_list()

    def refresh_list(self) -> None:
        """Refresh the list of saved entries."""
        box = self.ids.load_box
        box.clear_widgets()

        app = App.get_running_app()

        # Get all save keys
        keys = app.manager.get_all_save_keys()

        if not keys:
            # Empty state with Material styling
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height="120dp",
                padding="24dp",
                spacing="8dp",
                elevation=1,
                radius=[12, 12, 12, 12],
            )
            empty_label = MDLabel(
                text="No saved entries yet",
                font_size="20sp",
                bold=True,
                halign="center",
            )
            empty_sublabel = MDLabel(
                text="Create your first entry!",
                font_size="14sp",
                halign="center",
            )
            empty_card.add_widget(empty_label)
            empty_card.add_widget(empty_sublabel)
            box.add_widget(empty_card)
            return

        # Create Material card for each entry
        for key in keys:
            # Main entry card with elevation
            card = MDCard(
                orientation="horizontal",
                size_hint_y=None,
                height="72dp",
                padding="16dp",
                spacing="12dp",
                elevation=2,
                radius=[12, 12, 12, 12],
            )

            tappable_content = TappableCard(
                orientation="vertical",
                spacing="4dp",
            )
            tappable_content.bind(on_release=lambda b, k=key: self.load_entry(k))

            entry_label = MDLabel(
                text=key,
                font_size="14sp",
                bold=True,
                size_hint_y=None,
                height="24dp",
            )

            tappable_content.add_widget(entry_label)
            card.add_widget(tappable_content)

            # Delete icon button
            delete_btn = MDIconButton(
                style="standard",
                size_hint=(None, None),
                size=("48dp", "48dp"),
                pos_hint={"center_y": 0.5},
            )
            delete_btn.icon = "delete"
            delete_btn.bind(on_release=lambda b, k=key: self.confirm_delete(k))
            card.add_widget(delete_btn)

            box.add_widget(card)

    def load_entry(self, key: str) -> None:
        """Load a saved entry into the editor.

        Args:
            key (str): The save key of the entry to load.
        """
        app = App.get_running_app()

        entry, error = app.manager.load_entry(key)

        if entry is None:
            app.show_error("Load Error", error)
            return

        # Get editor screen and load data
        editor = self.manager.get_screen("editor")
        editor.load_rows_data(entry.rows)
        # Extract just the name part (before @) for the save name field
        editor.ids.save_name.text = entry.name
        # Update balance and expense totals
        app.calculate()

        self.manager.current = "editor"

    def confirm_delete(self, key: str) -> None:
        """Show confirmation dialog before deleting.

        Args:
            key: The save key of the entry to delete.
        """

        def on_delete(*args):
            dialog.dismiss()
            self.delete_entry(key)

        def on_cancel(*args):
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text="Confirm Delete"),
            MDLabel(text=f"Delete entry: {key}?", padding="16dp"),
            MDBoxLayout(
                MDButton(MDButtonText(text="CANCEL"), on_release=on_cancel),
                MDButton(MDButtonText(text="DELETE"), on_release=on_delete),
                adaptive_height=True,
                spacing="8dp",
                padding="16dp",
            ),
        )
        dialog.open()

    def delete_entry(self, key: str) -> None:
        """Delete an entry after confirmation.

        Args:
            key (str): The save key of the entry to delete.
        """
        app = App.get_running_app()

        success, message = app.manager.delete_entry(key)

        if success:
            app.show_info("Success", message)
            self.refresh_list()
        else:
            app.show_error("Delete Error", message)


# ----------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------- App ---------------------------------------------------------


class ExpenseApp(MDApp):
    """Main application class."""

    def __init__(self, **kwargs):
        """Initialize the application."""
        super().__init__(**kwargs)
        # Use Android-safe storage path
        storage_dir = Path(self.user_data_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        storage_path = storage_dir / "data.json"
        repository = ExpenseRepository(str(storage_path))
        self.manager = ExpenseManager(repository)

        # Configure theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

    def build(self) -> ScreenManager:
        """Build and return the application UI.

        Returns:
            Root widget (ScreenManager).
        """
        kv_path = Path(__file__).parent / "expenseapp.kv"
        return Builder.load_file(str(kv_path))

    def calculate(self) -> None:
        """Calculate totals from editor data."""
        editor = self.root.get_screen("editor")

        rows = editor.get_rows_data()
        total_bal, total_exp, remaining = self.manager.calculate_totals(rows)

        # Format with Indian currency style
        editor.ids.total_exp.text = format_indian_currency(total_exp)
        editor.ids.total_bal.text = format_indian_currency(remaining)

    def clear(self) -> None:
        """Clear all fields in the editor."""
        editor = self.root.get_screen("editor")
        editor.clear_all()

    def save(self, name: str) -> None:
        """Save the current expense entry.

        Args:
            name (str): Name for the entry.
        """
        editor = self.root.get_screen("editor")

        rows = editor.get_rows_data()
        success, message = self.manager.save_entry(name, rows)

        if success:
            self.show_info("Success", message)
            self.root.current = "main"
        else:
            self.show_error("Save Error", message)

    def show_info(self, title: str, message: str) -> None:
        """Show an information popup.

        Args:
            title (str): Popup title.
            message (str): Message to display.
        """

        def on_ok(*args):
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDLabel(text=message, padding="16dp"),
            MDBoxLayout(
                MDButton(MDButtonText(text="OK"), on_release=on_ok),
                adaptive_height=True,
                spacing="8dp",
                padding="16dp",
            ),
        )
        dialog.open()

    def show_error(self, title: str, message: str) -> None:
        """Show an error popup.

        Args:
            title (str): Popup title.
            message (str): Error message to display.
        """

        def on_ok(*args):
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDLabel(text=message, padding="16dp"),
            MDBoxLayout(
                MDButton(MDButtonText(text="OK"), on_release=on_ok),
                adaptive_height=True,
                spacing="8dp",
                padding="16dp",
            ),
        )
        dialog.open()


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    ExpenseApp().run()
