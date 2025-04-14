# Offline eNaira Prototype Report

## Project Overview
- **Objective**: Build an offline eNaira USSD system for secure transactions using SQLite, Flask, and encryption.
- **Features**:
  - USSD menu for sending money, checking balance, viewing transactions, and syncing transactions.
  - PIN verification for transactions.
  - Offline transaction storage with encrypted JSON files.
  - Sync functionality to update balances and clear pending transactions.

## Implementation Details
- **Tech Stack**:
  - Flask for the USSD server.
  - SQLite for persistent storage.
  - Custom encryption (`crypto.py`) for transaction data.
- **Files**:
  - `app.py`: Main USSD server logic.
  - `database.py`: Database management (users and transactions).
  - `crypto.py`: Encryption/decryption of transaction data.
  - `run_post.py`: Script to simulate USSD flow.
  - `tests/test_app.py`: Automated tests for core functionality.
- **Challenges Overcome**:
  - Fixed SQLite `database is locked` errors by using Flask’s `g` for thread-safe connections and adding retry logic.
  - Resolved test failures by clearing transaction files and database state between tests.

## Testing Results
- **Manual Testing** (`run_post.py`):
  - Successfully initiated a transaction of 100 Naira from user1 to user2.
  - Verified PIN validation (correct PIN proceeds, incorrect PIN fails).
  - Confirmed sync updates balances (user1: 5000 → 4900, user2: 3000 → 3100).
  - Transaction file (`data/tx_12345.json`) created and deleted as expected.
- **Automated Testing** (`test_app.py`):
  - All tests passed:
    - `test_ussd_main_menu`: USSD menu loads correctly.
    - `test_transaction_with_correct_pin`: Transaction with correct PIN creates file.
    - `test_transaction_with_incorrect_pin`: Transaction with incorrect PIN fails and creates no file.
    - `test_sync_transactions`: Sync completes, updates balances, and deletes file.

## Future Improvements
- Add retry logic for failed sync attempts.
- Implement peer-to-peer testing for offline transactions.
- Enhance security with more robust encryption and user authentication.

## Conclusion
The offline eNaira prototype successfully demonstrates a secure, offline-capable USSD system with PIN verification and transaction syncing.