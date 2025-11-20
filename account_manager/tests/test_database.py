"""
Database Manager Tests
"""

import unittest
import tempfile
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager"""

    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    # Company Tests
    def test_add_company(self):
        """Test adding a company"""
        company_id = self.db.add_company("Test Company", "123 Test St", "1234567890", "test@test.com")
        self.assertIsNotNone(company_id)
        self.assertGreater(company_id, 0)

    def test_get_company(self):
        """Test retrieving a company"""
        company_id = self.db.add_company("Test Company")
        company = self.db.get_company(company_id)
        self.assertIsNotNone(company)
        self.assertEqual(company['name'], "Test Company")

    def test_update_company(self):
        """Test updating a company"""
        company_id = self.db.add_company("Test Company")
        self.db.update_company(company_id, name="Updated Company")
        company = self.db.get_company(company_id)
        self.assertEqual(company['name'], "Updated Company")

    def test_delete_company(self):
        """Test deleting a company"""
        company_id = self.db.add_company("Test Company")
        self.db.delete_company(company_id)
        company = self.db.get_company(company_id)
        self.assertIsNone(company)

    def test_company_balance_update(self):
        """Test company balance updates"""
        company_id = self.db.add_company("Test Company")
        self.db.update_company_balance(company_id, 100.0)
        company = self.db.get_company(company_id)
        self.assertEqual(company['balance'], 100.0)

    # User Tests
    def test_add_user(self):
        """Test adding a user"""
        user_id = self.db.add_user("Test User", "user@test.com", "Admin", "IT")
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)

    def test_get_user(self):
        """Test retrieving a user"""
        user_id = self.db.add_user("Test User")
        user = self.db.get_user(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "Test User")

    def test_user_with_company(self):
        """Test user with company association"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User", company_id=company_id)
        user = self.db.get_user(user_id)
        self.assertEqual(user['company_id'], company_id)

    # Transaction Tests
    def test_add_transaction(self):
        """Test adding a transaction"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User")

        # Add initial balance
        self.db.update_company_balance(company_id, 1000.0)

        trans_id = self.db.add_transaction(
            "01-01-2024", 100.0,
            "company", company_id,
            "user", user_id,
            "Test transaction"
        )
        self.assertIsNotNone(trans_id)
        self.assertGreater(trans_id, 0)

    def test_transaction_balance_update(self):
        """Test that transaction updates balances correctly"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User")

        # Add initial balance
        self.db.update_company_balance(company_id, 1000.0)

        self.db.add_transaction(
            "01-01-2024", 100.0,
            "company", company_id,
            "user", user_id
        )

        company = self.db.get_company(company_id)
        user = self.db.get_user(user_id)

        self.assertEqual(company['balance'], 900.0)  # 1000 - 100
        self.assertEqual(user['balance'], 100.0)

    def test_deposit(self):
        """Test deposit functionality"""
        company_id = self.db.add_company("Test Company")
        self.db.deposit("company", company_id, 500.0, "Test deposit")

        company = self.db.get_company(company_id)
        self.assertEqual(company['balance'], 500.0)

    def test_withdraw(self):
        """Test withdraw functionality"""
        company_id = self.db.add_company("Test Company")
        self.db.update_company_balance(company_id, 1000.0)
        self.db.withdraw("company", company_id, 300.0, "Test withdraw")

        company = self.db.get_company(company_id)
        self.assertEqual(company['balance'], 700.0)

    def test_withdraw_insufficient_balance(self):
        """Test withdraw with insufficient balance"""
        company_id = self.db.add_company("Test Company")
        self.db.update_company_balance(company_id, 100.0)

        with self.assertRaises(Exception) as context:
            self.db.withdraw("company", company_id, 500.0)

        self.assertIn("Insufficient balance", str(context.exception))

    def test_delete_transaction(self):
        """Test deleting a transaction reverses balances"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User")

        self.db.update_company_balance(company_id, 1000.0)

        trans_id = self.db.add_transaction(
            "01-01-2024", 100.0,
            "company", company_id,
            "user", user_id
        )

        # Verify balances after transaction
        self.assertEqual(self.db.get_company(company_id)['balance'], 900.0)
        self.assertEqual(self.db.get_user(user_id)['balance'], 100.0)

        # Delete transaction
        self.db.delete_transaction(trans_id)

        # Verify balances are reversed
        self.assertEqual(self.db.get_company(company_id)['balance'], 1000.0)
        self.assertEqual(self.db.get_user(user_id)['balance'], 0.0)

    # Pagination Tests
    def test_get_transactions_paginated(self):
        """Test paginated transaction retrieval"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User")
        self.db.update_company_balance(company_id, 10000.0)

        # Add multiple transactions
        for i in range(25):
            self.db.add_transaction(
                f"0{(i % 28) + 1}-01-2024", 10.0,
                "company", company_id,
                "user", user_id
            )

        # Test pagination
        transactions, total = self.db.get_transactions_paginated(page=1, per_page=10)
        self.assertEqual(len(transactions), 10)
        self.assertEqual(total, 25)

        transactions, total = self.db.get_transactions_paginated(page=3, per_page=10)
        self.assertEqual(len(transactions), 5)

    # Search Tests
    def test_search_transactions(self):
        """Test transaction search"""
        company_id = self.db.add_company("Alpha Company")
        user_id = self.db.add_user("Test User")
        self.db.update_company_balance(company_id, 1000.0)

        self.db.add_transaction(
            "01-01-2024", 100.0,
            "company", company_id,
            "user", user_id,
            "Payment for services"
        )

        results = self.db.search_transactions("services")
        self.assertEqual(len(results), 1)

        results = self.db.search_transactions("Alpha")
        self.assertEqual(len(results), 1)

    def test_search_companies(self):
        """Test company search"""
        self.db.add_company("Alpha Corp", email="alpha@test.com")
        self.db.add_company("Beta Inc", email="beta@test.com")

        results = self.db.search_companies("Alpha")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Alpha Corp")

    def test_search_users(self):
        """Test user search"""
        self.db.add_user("John Smith", department="Sales")
        self.db.add_user("Jane Doe", department="Marketing")

        results = self.db.search_users("John")
        self.assertEqual(len(results), 1)

        results = self.db.search_users("Sales")
        self.assertEqual(len(results), 1)

    # Validation Tests
    def test_invalid_transaction_amount(self):
        """Test that negative amounts are rejected"""
        company_id = self.db.add_company("Test Company")
        user_id = self.db.add_user("Test User")

        with self.assertRaises(ValueError):
            self.db.add_transaction(
                "01-01-2024", -100.0,
                "company", company_id,
                "user", user_id
            )

    def test_invalid_entity_type(self):
        """Test that invalid entity types are rejected"""
        with self.assertRaises(ValueError):
            self.db.add_transaction(
                "01-01-2024", 100.0,
                "invalid", 1,
                "user", 1
            )


class TestDatabaseBalances(unittest.TestCase):
    """Test balance calculations"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_total_balances(self):
        """Test total balance calculations"""
        # Add companies with balances
        c1 = self.db.add_company("Company 1")
        c2 = self.db.add_company("Company 2")
        self.db.update_company_balance(c1, 1000.0)
        self.db.update_company_balance(c2, 2000.0)

        # Add users with balances
        u1 = self.db.add_user("User 1")
        u2 = self.db.add_user("User 2")
        self.db.update_user_balance(u1, 500.0)
        self.db.update_user_balance(u2, 300.0)

        balances = self.db.get_total_balances()

        self.assertEqual(balances['company_total'], 3000.0)
        self.assertEqual(balances['user_total'], 800.0)
        self.assertEqual(balances['grand_total'], 3800.0)


if __name__ == '__main__':
    unittest.main()
