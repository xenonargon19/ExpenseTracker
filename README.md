# Expense Tracker (Flask + SQLite)

A personal expense tracker built with **Flask and SQLite**, focused on **correct state management**, **deterministic logic**, and **incremental feature development**.

This project intentionally avoids ORMs and authentication to keep the data flow explicit and auditable.

---

## Features (V1)

### Transactions
- Record savings (positive amounts) and spending (negative amounts)
- All balances are derived **only from transactions**
- No cached totals or duplicated state

### Targets (Wishlist)
- Create, edit, delete savings targets
- Each target has a **normalized weight**
- Weights always sum to **100** across active targets
- Supports:
  - Default equal-priority target addition
  - Manual weight editing with normalization on save
- Purchases:
  - Remove the target
  - Create a spending transaction
  - Persist purchase history

### Achievements
- Achievements are derived from existing data and persisted only on unlock
- Current achievements:
  - Save 5,000
  - Save 10,000
  - Buy first target
- Behavior:
  - Locked achievements are greyed out
  - Unlock once, persist in DB
  - Popup notification on unlock
  - Reset progress button (clears achievements only)

---

## Core Design Principles

### Single Source of Truth
- Money state comes from the `transactions` table
- Purchases come from the `purchases` table
- Achievements are computed from those sources and stored only when unlocked

No duplicated counters. No cached balances.

### Deterministic Weight System
- Target weights are **always normalized before persisting**
- Raw weights are not stored historically
- Edit mode allows any inputs and normalizes on save

### Explicit Data Flow
- No ORM (raw SQLite)
- DB operations are centralized in `db.py`
- Achievement logic is separated into `achievements.py`

---

## Tech Stack
- Python 3
- Flask (development server)
- SQLite
- Jinja2 templates
- WSL Ubuntu + VS Code

---

## Project Structure

```
expense-tracker/
├── app.py              # Flask routes
├── main.py             # App entry point
├── db.py               # SQLite helpers (single source of truth)
├── achievements.py     # Achievement rules & evaluation
├── services/
│   ├── allocation.py   # Fund allocation logic
│   └── weights.py      # Weight normalization logic
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── targets.html
│   ├── transactions.html
│   └── achievements.html
├── static/
├── data.db              # (ignored, created at runtime)
```
---

## Running the App

1) Create / activate your environment (if you use one)
2) Run:

python main.py

Then open:
http://localhost:5000

---

## What’s Intentionally Not Included (V1)
- Authentication / multi-user support
- UI polish and animations
- Performance optimizations
- API endpoints

These are deliberately excluded to keep the logic inspectable.

---

## Possible Next Steps
- Trigger achievement popups closer to save/purchase actions
- Add purchase history view
- Show achievement timestamps in UI
- Add confirmation dialogs
- Improve UI styling
