"""
Test Database Persistence - Verify data is saved correctly
"""

import sys
sys.path.insert(0, '.')

import os
from database.db_manager import DatabaseManager

print("=" * 70)
print("Testing Database Persistence")
print("=" * 70)
print()

# Test 1: Initialize database and check path
print("Step 1: Initializing database...")
db = DatabaseManager()
print(f"Database path: {db.db_path}")
print(f"Database file exists: {os.path.exists(db.db_path)}")
print()

# Test 2: Add test data
print("Step 2: Adding test data...")
try:
    # Add a company
    company_id = db.add_company(
        name="Persistence Test Company",
        address="123 Test Street",
        phone="555-9999",
        email="test@persistence.com"
    )
    print(f"Added company with ID: {company_id}")

    # Add a user
    user_id = db.add_user(
        name="Persistence Test User",
        email="user@persistence.com",
        role="Tester",
        department="QA",
        company_id=company_id
    )
    print(f"Added user with ID: {user_id}")

    # Add a transaction
    from datetime import datetime
    trans_id = db.add_transaction(
        transaction_date=datetime.now().strftime('%Y-%m-%d'),
        amount=1000.00,
        from_type='company',
        from_id=company_id,
        to_type='user',
        to_id=user_id,
        description='Test persistence transaction',
        reference='PERSIST-001'
    )
    print(f"Added transaction with ID: {trans_id}")
    print()

except Exception as e:
    print(f"ERROR adding data: {e}")
    db.close()
    sys.exit(1)

# Test 3: Verify data was saved
print("Step 3: Verifying data in current session...")
companies = db.get_all_companies()
users = db.get_all_users()
transactions = db.get_all_transactions()

print(f"Total companies: {len(companies)}")
print(f"Total users: {len(users)}")
print(f"Total transactions: {len(transactions)}")
print()

# Test 4: Close database properly
print("Step 4: Closing database connection...")
db.close()
print("Database closed")
print()

# Test 5: Verify database file still exists
print("Step 5: Verifying database file exists after close...")
db_file = db.db_path
if os.path.exists(db_file):
    file_size = os.path.getsize(db_file)
    print(f"SUCCESS: Database file exists at: {db_file}")
    print(f"File size: {file_size:,} bytes")
else:
    print(f"ERROR: Database file NOT found at: {db_file}")
    sys.exit(1)
print()

# Test 6: Open database again and verify data persisted
print("Step 6: Reopening database to verify persistence...")
db2 = DatabaseManager()
companies2 = db2.get_all_companies()
users2 = db2.get_all_users()
transactions2 = db2.get_all_transactions()

print(f"After reopen - Companies: {len(companies2)}")
print(f"After reopen - Users: {len(users2)}")
print(f"After reopen - Transactions: {len(transactions2)}")
print()

# Verify specific test data exists
print("Step 7: Verifying test data persisted...")
test_company_found = False
test_user_found = False
test_trans_found = False

for company in companies2:
    if company['name'] == "Persistence Test Company":
        test_company_found = True
        print(f"✓ Test company found: {company['name']}")

for user in users2:
    if user['name'] == "Persistence Test User":
        test_user_found = True
        print(f"✓ Test user found: {user['name']}")

for trans in transactions2:
    if trans['reference'] == 'PERSIST-001':
        test_trans_found = True
        print(f"✓ Test transaction found: {trans['reference']}")

db2.close()
print()

# Final results
print("=" * 70)
if test_company_found and test_user_found and test_trans_found:
    print("SUCCESS: All data persisted correctly!")
    print("=" * 70)
    print()
    print("Database is working correctly:")
    print("  ✓ Data is saved to disk")
    print("  ✓ Data persists after closing")
    print("  ✓ Data is available after reopening")
    print()
    print(f"Database location: {db_file}")
    print("All data will be preserved when you close the application.")
else:
    print("ERROR: Some data did not persist!")
    print("=" * 70)
    if not test_company_found:
        print("  ✗ Test company NOT found")
    if not test_user_found:
        print("  ✗ Test user NOT found")
    if not test_trans_found:
        print("  ✗ Test transaction NOT found")
    sys.exit(1)
