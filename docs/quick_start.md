# Daily Expense Tracker - Quick Start Guide

## 🚀 Running the App

1. Navigate to src directory

   ```powershell
   cd src
   ```

2. Run the application

   ```powershell
   python main.py
   ```

## 📂 Project Structure

```txt
src/
├── models.py           # Data classes (ExpenseRow, ExpenseEntry)
├── repository.py       # JSON storage operations
├── manager.py          # Business logic & validation
├── main.py             # UI screens & controllers
└── expenseapp.kv       # Declarative UI layout
```

## 🔄 Architecture Flow

```txt
User Action (UI)
    ↓
main.py (Controller)
    ↓
manager.py (Business Logic)
    ↓
repository.py (Data Access)
    ↓
models.py (Data Structure)
    ↓
data.json (Storage)
```

## 📊 Data Format

### JSON Structure

```json
{
    "Groceries @ 2025-12-22 14:30:15": {
        "entries": [
            {"item": "Milk", "balance": "50", "expense": "5"},
            {"item": "Bread", "balance": "50", "expense": "3"}
        ]
    }
}
```

### Key Format

```txt
{name} @ {YYYY-MM-DD HH:MM:SS}
```

## 🔧 Configuration

### Change Number of Rows

In `main.py`, `EditorScreen.on_pre_enter()`:

```python
for _ in range(15):  # Change 15 to desired number
    # ...
```

Also update in `expenseapp.kv` grid if needed.

### Change Input Filters

In `main.py`, change `input_filter`:

```python
bal = TextInput(input_filter="number")  # float, int, or None
```

### Change Storage Location

In `main.py`, modify:

```python
STORE_PATH = ASSETS_DIR / "data.json"  # Change filename
```
