# Daily Expense Tracker Mobile App

**Version:** 2.0 <br>
**Date:** December 28, 2025 <br>
**Framework:** Kivy 2.3.1, KivyMD 2.0.1.dev0 <br>
**Python:** 3.13+

---

## Table of Contents

- [Daily Expense Tracker Mobile App](#daily-expense-tracker-mobile-app)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Key Characteristics](#key-characteristics)
  - [Core Features](#core-features)
    - [1. New Entry Creation](#1-new-entry-creation)
    - [2. Expense Tracking](#2-expense-tracking)
    - [3. Calculate Totals](#3-calculate-totals)
    - [4. Clear Functionality](#4-clear-functionality)
    - [5. Save System](#5-save-system)
    - [6. Load System](#6-load-system)
    - [7. Data Management](#7-data-management)
  - [User Workflows](#user-workflows)
    - [Workflow 1: Create New Entry](#workflow-1-create-new-entry)
    - [Workflow 2: Load Existing Entry](#workflow-2-load-existing-entry)
    - [Workflow 3: Delete Entry](#workflow-3-delete-entry)
    - [Module Structure](#module-structure)
    - [Key Design Principles](#key-design-principles)
  - [Storage System](#storage-system)
    - [Storage Backend: JSON File](#storage-backend-json-file)

---

## Overview

The Daily Expense Tracker is a mobile-first application built with the Kivy framework that allows users to track their daily expenses. Users can create multiple expense sheets, track items with their associated balances and expenses, calculate totals automatically, and save/load their entries for future reference.

### Key Characteristics

- **Mobile-First Design**: Optimized for mobile devices using Kivy
- **Offline-First**: All data stored locally in JSON format
- **Simple UX**: Three-screen navigation flow
- **Persistent Storage**: Save and load unlimited expense entries
- **Calculations**: Real-time expense totals and remaining balance

---

## Core Features

### 1. New Entry Creation

Users can create a new expense tracking sheet with:

- 15 rows for expense items
- Three columns per row: Item Description, Balance, Expense
- Ability to fill any number of rows (1-15)
- Empty rows are ignored during save

### 2. Expense Tracking

Each expense entry tracks:

- **Item Description**: Description of the expense (e.g., "Groceries", "Rent")
- **Balance**: Amount of money allocated or income received
- **Expense**: Amount spent on the item

### 3. Calculate Totals

The app provides a calculation feature that computes:

- **Total Expense**: Sum of all expense amounts
- **Remaining**: Total Balance - Total Expense

### 4. Clear Functionality

Users can clear all input fields in the current entry to start fresh.

### 5. Save System

Users can save their expense sheets with:

- Custom name for the entry
- Automatic timestamp in format: `YYYY-MM-DD HH:MM:SS`
- Full save format: `{SaveName} @ {Timestamp}`
- Persistent JSON storage

### 6. Load System

Users can:

- View all previously saved entries in reverse chronological order (newest first)
- Load any saved entry back into the editor for viewing/editing
- Delete unwanted entries
- Navigate back to create new entries

### 7. Data Management

- **Clear Function**: Reset all fields in the editor
- **Delete Function**: Remove saved entries from storage
- **Update Function**: Load, modify, and save existing entries as new entries

---

## User Workflows

### Workflow 1: Create New Entry

```txt
Main Screen
    ↓ [Tap "New Entry"]
Editor Screen
    ↓ [Enter items, balances, expenses]
    ↓ [Tap "Calculate"]
    ↓ [View totals]
    ↓ [Enter save name]
    ↓ [Tap "Save"]
    ↓ [Validates the sheet]
    ↓ [Show error if invalid / Success feedback]
Main Screen
```

### Workflow 2: Load Existing Entry

```txt
Main Screen
    ↓ [Tap "Load Saved"]
Load Screen
    ↓ [View list of saved entries]
    ↓ [Tap entry name]
Editor Screen (populated with data)
    ↓ [Modify as needed]
    ↓ [Save with same or new name]
Main Screen
```

### Workflow 3: Delete Entry

```txt
Main Screen
    ↓ [Tap "Load Saved"]
Load Screen
    ↓ [View list of saved entries]
    ↓ [Tap "Delete" button for entry]
    ↓ [Confirmation dialog]
    ↓ [Entry removed]
Load Screen (refreshed)
```

---

### Module Structure

```txt
src/
├── __init__.py
├── main.py                # Main app & screen definitions
├── models.py              # Data classes (ExpenseRow, ExpenseEntry)
├── repository.py          # JSON storage operations
├── manager.py             # Business logic (calculations, validations)
├── expenseapp.kv          # UI definitions
└── assets/
    └── data.json          # Persistent storage
```

### Key Design Principles

1. **Separation of Concerns**: View, Controller, Model are distinct
2. **Single Responsibility**: Each class has one clear purpose
3. **Dependency Injection**: Repository injected into Manager
4. **Type Safety**: Full type hints throughout
5. **Error Handling**: Comprehensive try/except with user feedback
6. **Testability**: Pure functions, mockable dependencies

---

## Storage System

### Storage Backend: JSON File

**Location**: `src/assets/data.json`

**Format**: Plain JSON dictionary

**Operations:**

1. Load All Entries
2. Save Entry
3. Delete Entry

---

**Document Version**: 1.0 <br>
**Last Updated**: December 26, 2025 <br>
**Author**: Shangar Arivazhagan
