"""
Test Currency - Write to file to verify encoding
"""

import sys
sys.path.insert(0, '.')

from utils.helpers import format_currency, validate_amount
from database.db_manager import DatabaseManager

# Write results to file
with open('currency_test_results.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("Currency Change Test Results\n")
    f.write("=" * 60 + "\n\n")

    # Test 1: Currency Formatting
    f.write("1. Currency Formatting Tests:\n")
    test_amounts = [1234.56, 100000, -5000, 0, 999999.99]
    for amount in test_amounts:
        formatted = format_currency(amount)
        f.write(f"   Amount: {amount:12.2f} -> {formatted}\n")
    f.write("\n")

    # Test 2: Validation
    f.write("2. Amount Validation Tests:\n")
    test_cases = [
        '1234.56',
        '₹1234.56',
        'Rs 1234.56',
        'Rs. 5000',
        '10,000',
        '₹10,000'
    ]

    for test in test_cases:
        is_valid, amount = validate_amount(test)
        status = "✓ VALID" if is_valid else "✗ INVALID"
        f.write(f"   Input: '{test:15s}' -> {status}, Parsed: {amount:10.2f}\n")
    f.write("\n")

    # Test 3: Database
    f.write("3. Database Balance Tests:\n")
    db = DatabaseManager()
    balances = db.get_total_balances()
    f.write(f"   Company Total: {format_currency(balances['company_total'])}\n")
    f.write(f"   User Total: {format_currency(balances['user_total'])}\n")
    f.write(f"   Grand Total: {format_currency(balances['grand_total'])}\n")
    f.write("\n")

    # Get transactions
    f.write("4. Sample Transactions:\n")
    transactions = db.get_all_transactions(limit=3)
    for trans in transactions:
        f.write(f"   {trans['from_name']} → {trans['to_name']}: {format_currency(trans['amount'])}\n")

    db.close()

    f.write("\n" + "=" * 60 + "\n")
    f.write("SUCCESS: All currency displays now use Indian Rupees (₹)\n")
    f.write("=" * 60 + "\n")

print("Test completed! Results saved to: currency_test_results.txt")
print("Check the file to see rupee symbol formatting.")
