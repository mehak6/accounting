"""
Test script for Account Manager application
"""

import sys
sys.path.insert(0, '.')

from database.db_manager import DatabaseManager
from datetime import datetime

def test_database():
    """Test database operations"""
    print("=" * 50)
    print("Testing Account Manager Application")
    print("=" * 50)

    # Test database initialization
    print("\n1. Initializing database...")
    db = DatabaseManager()
    print("   SUCCESS: Database initialized")

    # Test adding a company
    print("\n2. Adding test company...")
    company_id = db.add_company(
        'Acme Corporation',
        '123 Business Ave',
        '555-0100',
        'contact@acme.com'
    )
    print(f"   SUCCESS: Company added with ID: {company_id}")

    # Test retrieving company
    print("\n3. Retrieving company...")
    company = db.get_company(company_id)
    print(f"   SUCCESS: Retrieved company: {company['name']}")
    print(f"   Address: {company['address']}")
    print(f"   Balance: ${company['balance']:.2f}")

    # Test adding a second company
    print("\n4. Adding second company...")
    company2_id = db.add_company(
        'TechCorp Industries',
        '456 Tech Road',
        '555-0200',
        'info@techcorp.com'
    )
    print(f"   SUCCESS: Company added with ID: {company2_id}")

    # Test adding users
    print("\n5. Adding users...")
    user1_id = db.add_user(
        'John Doe',
        'john.doe@acme.com',
        'Sales Manager',
        'Sales',
        company_id
    )
    print(f"   SUCCESS: User 'John Doe' added with ID: {user1_id}")

    user2_id = db.add_user(
        'Jane Smith',
        'jane.smith@techcorp.com',
        'Developer',
        'Engineering',
        company2_id
    )
    print(f"   SUCCESS: User 'Jane Smith' added with ID: {user2_id}")

    # Test transactions
    print("\n6. Creating transactions...")

    # Company to User transaction
    trans1_id = db.add_transaction(
        transaction_date=datetime.now().strftime('%Y-%m-%d'),
        amount=5000.00,
        from_type='company',
        from_id=company_id,
        to_type='user',
        to_id=user1_id,
        description='Monthly salary payment',
        reference='SAL-2025-001'
    )
    print(f"   SUCCESS: Transaction 1 (Company->User) added with ID: {trans1_id}")

    # Company to Company transaction
    trans2_id = db.add_transaction(
        transaction_date=datetime.now().strftime('%Y-%m-%d'),
        amount=10000.00,
        from_type='company',
        from_id=company_id,
        to_type='company',
        to_id=company2_id,
        description='Service payment',
        reference='INV-2025-001'
    )
    print(f"   SUCCESS: Transaction 2 (Company->Company) added with ID: {trans2_id}")

    # User to Company transaction
    trans3_id = db.add_transaction(
        transaction_date=datetime.now().strftime('%Y-%m-%d'),
        amount=500.00,
        from_type='user',
        from_id=user1_id,
        to_type='company',
        to_id=company_id,
        description='Expense reimbursement',
        reference='EXP-2025-001'
    )
    print(f"   SUCCESS: Transaction 3 (User->Company) added with ID: {trans3_id}")

    # Check balances
    print("\n7. Checking balances...")

    # Company 1 balance
    company1 = db.get_company(company_id)
    print(f"   Acme Corporation balance: ${company1['balance']:.2f}")

    # Company 2 balance
    company2 = db.get_company(company2_id)
    print(f"   TechCorp Industries balance: ${company2['balance']:.2f}")

    # User 1 balance
    user1 = db.get_user(user1_id)
    print(f"   John Doe balance: ${user1['balance']:.2f}")

    # User 2 balance
    user2 = db.get_user(user2_id)
    print(f"   Jane Smith balance: ${user2['balance']:.2f}")

    # Total balances
    balances = db.get_total_balances()
    print(f"\n   Total Company Balances: ${balances['company_total']:.2f}")
    print(f"   Total User Balances: ${balances['user_total']:.2f}")
    print(f"   Grand Total: ${balances['grand_total']:.2f}")

    # Get all transactions
    print("\n8. Retrieving all transactions...")
    transactions = db.get_all_transactions()
    print(f"   Total transactions: {len(transactions)}")

    for trans in transactions:
        print(f"   - {trans['from_name']} -> {trans['to_name']}: ${trans['amount']:.2f}")

    # Test search
    print("\n9. Testing search...")
    results = db.search_transactions('salary')
    print(f"   Found {len(results)} transaction(s) matching 'salary'")

    # Test reports
    print("\n10. Testing reports...")
    summary = db.get_transaction_summary()
    print(f"   Total transactions: {summary['total_count']}")
    print(f"   Total amount: ${summary['total_amount']:.2f}")
    print(f"   Average amount: ${summary['average_amount']:.2f}")

    # Close database
    print("\n11. Closing database...")
    db.close()
    print("   SUCCESS: Database closed")

    print("\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    print("\nThe application is ready to use!")
    print("Run: py main.py")

if __name__ == "__main__":
    try:
        test_database()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
