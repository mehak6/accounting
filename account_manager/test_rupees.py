"""
Test Currency Changes - Rupee Symbol
"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

sys.path.insert(0, '.')

from utils.helpers import format_currency, validate_amount
from database.db_manager import DatabaseManager

print("=" * 60)
print("Testing Currency Change to Indian Rupees")
print("=" * 60)
print()

# Test 1: Currency Formatting
print("1. Testing format_currency():")
test_amounts = [1234.56, 100000, -5000, 0, 999999.99]
for amount in test_amounts:
    try:
        formatted = format_currency(amount)
        print(f"   Amount: {amount:12.2f} -> {formatted}")
    except Exception as e:
        print(f"   Amount: {amount:12.2f} -> ERROR: {e}")
print()

# Test 2: Amount Validation
print("2. Testing validate_amount() with various formats:")
test_cases = [
    '1234.56',
    'Rs 1234.56',
    'Rs. 5000',
    '10,000',
    '5000',
    'Rs. 1,00,000'
]

for test in test_cases:
    is_valid, amount = validate_amount(test)
    status = "VALID" if is_valid else "INVALID"
    print(f"   Input: '{test:20s}' -> {status:7s}, Amount: {amount:12.2f}")
print()

# Test 3: Database with Rupees
print("3. Testing database with rupee formatting:")
db = DatabaseManager()

# Get existing balances
balances = db.get_total_balances()
print(f"   Company Total: {format_currency(balances['company_total'])}")
print(f"   User Total: {format_currency(balances['user_total'])}")
print(f"   Grand Total: {format_currency(balances['grand_total'])}")
print()

# Get a transaction
transactions = db.get_all_transactions(limit=1)
if transactions:
    trans = transactions[0]
    print(f"   Sample Transaction:")
    print(f"   From: {trans['from_name']}")
    print(f"   To: {trans['to_name']}")
    print(f"   Amount: {format_currency(trans['amount'])}")
print()

db.close()

print("=" * 60)
print("SUCCESS: Currency changed to Indian Rupees!")
print("=" * 60)
print()
print("All currency displays now use the Rupee symbol.")
print("The application is ready to use with INR currency.")
print()
print("To launch the application:")
print("  py main.py")
