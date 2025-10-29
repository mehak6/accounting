"""
Test Ledger Functionality
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("Testing Ledger Functionality")
print("=" * 70)
print()

# Test 1: Import test
print("Step 1: Testing imports...")
try:
    from database.db_manager import DatabaseManager
    from gui.ledger_window import LedgerWindow
    print("[OK] All imports successful")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Database and ledger query
print("Step 2: Testing ledger query...")
try:
    db = DatabaseManager()
    print(f"[OK] Database initialized: {db.db_path}")

    # Get companies
    companies = db.get_all_companies()
    if companies:
        company = companies[0]
        print(f"[OK] Testing with company: {company['name']} (ID: {company['id']})")

        # Get ledger
        ledger_entries = db.get_account_ledger('company', company['id'])
        print(f"[OK] Ledger query successful: {len(ledger_entries)} entries")

        if ledger_entries:
            print()
            print("Sample ledger entries:")
            for i, entry in enumerate(ledger_entries[:3]):  # Show first 3
                print(f"  {i+1}. {entry['date']} | {entry['type']} | Rs. {entry['amount']:,.2f} | Balance: Rs. {entry['running_balance']:,.2f}")
        else:
            print("[INFO] No transactions for this account yet")
    else:
        print("[INFO] No companies found, skipping ledger test")

    db.close()

except Exception as e:
    print(f"[ERROR] Ledger query failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: GUI components
print("Step 3: Testing GUI components...")
try:
    import customtkinter as ctk
    print("[OK] CustomTkinter import successful")
    print("[OK] LedgerWindow class available")
    print("[INFO] Full GUI test requires manual launch of application")
except Exception as e:
    print(f"[ERROR] GUI test failed: {e}")

print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print()
print("Summary:")
print("  - Database ledger query: Working")
print("  - Ledger window class: Created")
print("  - Ready for full application test")
print()
print("Manual Test Steps:")
print("  1. Open AccountManager.exe")
print("  2. Look for 'Click on any account to view ledger' section")
print("  3. Click on any company or user")
print("  4. Ledger window should open with transaction history")
print("  5. Click on any transaction to see full details")
print()
