"""
Database Manager - Handles all SQLite database operations
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# Import helper for date normalization
try:
    from utils.helpers import normalize_date_for_sort
except ImportError:
    # Fallback if import fails
    def normalize_date_for_sort(date_str):
        if not date_str:
            return ''
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 3 and len(parts[0]) <= 2:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str


class DatabaseManager:
    """Manages SQLite database connections and operations"""

    def __init__(self, db_path: str = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file. If None, uses default path.
        """
        if db_path is None:
            # Determine the correct base directory
            # When running as PyInstaller executable, use the .exe directory
            # When running as Python script, use the project root
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as Python script
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            db_path = os.path.join(base_dir, 'data', 'financial_data.db')
            print(f"Database will be stored at: {db_path}")

        self.db_path = db_path
        self.connection = None

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.connect()
        self.create_tables()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            return self.connection
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_tables(self):
        """Create all required database tables"""
        cursor = self.connection.cursor()

        try:
            # Companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    balance REAL DEFAULT 0.00,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    name TEXT NOT NULL,
                    email TEXT,
                    role TEXT,
                    department TEXT,
                    balance REAL DEFAULT 0.00,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE SET NULL
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_date DATE NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0),
                    from_type TEXT NOT NULL CHECK (from_type IN ('company', 'user')),
                    from_id INTEGER NOT NULL,
                    to_type TEXT NOT NULL CHECK (to_type IN ('company', 'user')),
                    to_id INTEGER NOT NULL,
                    description TEXT,
                    reference TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Transaction types table (for future categorization)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            """)

            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date
                ON transactions(transaction_date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_from
                ON transactions(from_type, from_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_to
                ON transactions(to_type, to_id)
            """)

            self.connection.commit()

            # Insert default transaction types if table is empty
            cursor.execute("SELECT COUNT(*) FROM transaction_types")
            if cursor.fetchone()[0] == 0:
                default_types = [
                    ('Company to Company', 'Money transfer between companies'),
                    ('Company to User', 'Payment from company to user'),
                    ('User to Company', 'Payment from user to company'),
                    ('User to User', 'Money transfer between users')
                ]
                cursor.executemany(
                    "INSERT INTO transaction_types (type_name, description) VALUES (?, ?)",
                    default_types
                )
                self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            raise

        # Run migrations
        self.migrate_remove_email_unique_constraint()
        self.migrate_add_cash_transaction_support()

    def migrate_remove_email_unique_constraint(self):
        """
        Migration: Remove UNIQUE constraint from users.email field
        This allows multiple users with empty or duplicate emails
        """
        cursor = self.connection.cursor()

        try:
            # Check if the users table has the UNIQUE constraint on email
            # by attempting to get the table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()

            if result and 'UNIQUE' in result[0] and 'email TEXT UNIQUE' in result[0]:
                print("Migrating database: Removing UNIQUE constraint from users.email...")

                # Step 1: Create new users table without UNIQUE constraint
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER,
                        name TEXT NOT NULL,
                        email TEXT,
                        role TEXT,
                        department TEXT,
                        balance REAL DEFAULT 0.00,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE SET NULL
                    )
                """)

                # Step 2: Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO users_new (id, company_id, name, email, role, department, balance, created_date)
                    SELECT id, company_id, name, email, role, department, balance, created_date
                    FROM users
                """)

                # Step 3: Drop old table
                cursor.execute("DROP TABLE users")

                # Step 4: Rename new table to users
                cursor.execute("ALTER TABLE users_new RENAME TO users")

                self.connection.commit()
                print("Migration completed: Email field is now optional and non-unique")

        except sqlite3.Error as e:
            print(f"Migration info: {e}")
            # If migration fails, it's probably already migrated or a new database
            self.connection.rollback()

    def migrate_add_cash_transaction_support(self):
        """
        Migration: Update transactions table to support 'cash' type for deposits/withdrawals
        This allows from_type and to_type to be 'cash' in addition to 'company' and 'user'
        """
        cursor = self.connection.cursor()

        try:
            # Check if the transactions table has the old CHECK constraint
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='transactions'")
            result = cursor.fetchone()

            if result and "CHECK (from_type IN ('company', 'user'))" in result[0]:
                print("Migrating database: Adding 'cash' support to transactions table...")

                # Step 1: Create new transactions table with updated constraints
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_date DATE NOT NULL,
                        amount REAL NOT NULL CHECK (amount > 0),
                        from_type TEXT NOT NULL CHECK (from_type IN ('company', 'user', 'cash')),
                        from_id INTEGER NOT NULL,
                        to_type TEXT NOT NULL CHECK (to_type IN ('company', 'user', 'cash')),
                        to_id INTEGER NOT NULL,
                        description TEXT,
                        reference TEXT,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Step 2: Copy data from old table to new table
                cursor.execute("""
                    INSERT INTO transactions_new (id, transaction_date, amount, from_type, from_id, 
                                                   to_type, to_id, description, reference, created_date)
                    SELECT id, transaction_date, amount, from_type, from_id, 
                           to_type, to_id, description, reference, created_date
                    FROM transactions
                """)

                # Step 3: Drop old table
                cursor.execute("DROP TABLE transactions")

                # Step 4: Rename new table to transactions
                cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")

                self.connection.commit()
                print("Migration completed: Transactions table now supports cash deposits/withdrawals")

        except sqlite3.Error as e:
            print(f"Migration info: {e}")
            # If migration fails, it's probably already migrated or a new database
            self.connection.rollback()

    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SELECT query and return results

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of result rows
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def execute_update(self, query: str, params: Tuple = (), auto_commit: bool = True) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query

        Args:
            query: SQL query string
            params: Query parameters tuple
            auto_commit: Whether to commit after execution (default True)

        Returns:
            Number of affected rows or last row ID for INSERT
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        if auto_commit:
            self.connection.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute multiple queries with different parameters

        Args:
            query: SQL query string
            params_list: List of parameter tuples

        Returns:
            Number of affected rows
        """
        cursor = self.connection.cursor()
        cursor.executemany(query, params_list)
        self.connection.commit()
        return cursor.rowcount

    # ==================== Company Operations ====================

    def add_company(self, name: str, address: str = "", phone: str = "",
                    email: str = "") -> int:
        """Add a new company"""
        query = """
            INSERT INTO companies (name, address, phone, email)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (name, address, phone, email))

    def get_company(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get company by ID"""
        query = "SELECT * FROM companies WHERE id = ?"
        results = self.execute_query(query, (company_id,))
        return dict(results[0]) if results else None

    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies"""
        query = "SELECT * FROM companies ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def update_company(self, company_id: int, name: str = None, address: str = None,
                       phone: str = None, email: str = None) -> int:
        """Update company information"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if address is not None:
            updates.append("address = ?")
            params.append(address)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if email is not None:
            updates.append("email = ?")
            params.append(email)

        if not updates:
            return 0

        params.append(company_id)
        query = f"UPDATE companies SET {', '.join(updates)} WHERE id = ?"
        return self.execute_update(query, tuple(params))

    def delete_company(self, company_id: int) -> int:
        """Delete a company"""
        query = "DELETE FROM companies WHERE id = ?"
        return self.execute_update(query, (company_id,))

    def update_company_balance(self, company_id: int, amount: float, auto_commit: bool = True) -> int:
        """Update company balance by adding the specified amount"""
        query = "UPDATE companies SET balance = balance + ? WHERE id = ?"
        return self.execute_update(query, (amount, company_id), auto_commit)

    # ==================== User Operations ====================

    def add_user(self, name: str, email: str = "", role: str = "",
                 department: str = "", company_id: int = None) -> int:
        """Add a new user"""
        query = """
            INSERT INTO users (name, email, role, department, company_id)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (name, email, role, department, company_id))

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        return dict(results[0]) if results else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        query = "SELECT * FROM users ORDER BY name"
        results = self.execute_query(query)
        return [dict(row) for row in results]

    def get_users_by_company(self, company_id: int) -> List[Dict[str, Any]]:
        """Get all users for a specific company"""
        query = "SELECT * FROM users WHERE company_id = ? ORDER BY name"
        results = self.execute_query(query, (company_id,))
        return [dict(row) for row in results]

    def update_user(self, user_id: int, name: str = None, email: str = None,
                    role: str = None, department: str = None,
                    company_id: int = None) -> int:
        """Update user information"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        if department is not None:
            updates.append("department = ?")
            params.append(department)
        if company_id is not None:
            updates.append("company_id = ?")
            params.append(company_id)

        if not updates:
            return 0

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        return self.execute_update(query, tuple(params))

    def delete_user(self, user_id: int) -> int:
        """Delete a user"""
        query = "DELETE FROM users WHERE id = ?"
        return self.execute_update(query, (user_id,))

    def update_user_balance(self, user_id: int, amount: float, auto_commit: bool = True) -> int:
        """Update user balance by adding the specified amount"""
        query = "UPDATE users SET balance = balance + ? WHERE id = ?"
        return self.execute_update(query, (amount, user_id), auto_commit)

    # ==================== Transaction Operations ====================

    def add_transaction(self, transaction_date: str, amount: float,
                       from_type: str, from_id: int, to_type: str, to_id: int,
                       description: str = "", reference: str = "") -> int:
        """
        Add a new transaction and update balances

        Args:
            transaction_date: Date in DD-MM-YYYY format
            amount: Transaction amount (must be positive)
            from_type: 'company' or 'user'
            from_id: ID of the sender
            to_type: 'company' or 'user'
            to_id: ID of the receiver
            description: Transaction description
            reference: Reference number or code

        Returns:
            Transaction ID
        """
        # Validate inputs
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")

        if from_type not in ['company', 'user'] or to_type not in ['company', 'user']:
            raise ValueError("Transaction type must be 'company' or 'user'")

        try:
            # Insert transaction (don't auto-commit)
            query = """
                INSERT INTO transactions
                (transaction_date, amount, from_type, from_id, to_type, to_id,
                 description, reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            transaction_id = self.execute_update(
                query,
                (transaction_date, amount, from_type, from_id, to_type, to_id,
                 description, reference),
                auto_commit=False
            )

            # Update sender balance (subtract) - don't auto-commit
            if from_type == 'company':
                self.update_company_balance(from_id, -amount, auto_commit=False)
            else:
                self.update_user_balance(from_id, -amount, auto_commit=False)

            # Update receiver balance (add) - don't auto-commit
            if to_type == 'company':
                self.update_company_balance(to_id, amount, auto_commit=False)
            else:
                self.update_user_balance(to_id, amount, auto_commit=False)

            # Commit all changes atomically
            self.connection.commit()
            return transaction_id

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to add transaction: {e}")

    def deposit(self, entity_type: str, entity_id: int, amount: float, description: str = "Cash Deposit") -> int:
        """
        Deposit money to an account (add balance)
        
        Args:
            entity_type: 'company' or 'user'
            entity_id: ID of the entity
            amount: Amount to deposit (must be positive)
            description: Description of the deposit
            
        Returns:
            Transaction ID
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if entity_type not in ['company', 'user']:
            raise ValueError("Entity type must be 'company' or 'user'")
        
        try:
            # Create a transaction record for audit trail (don't auto-commit)
            query = """
                INSERT INTO transactions
                (transaction_date, amount, from_type, from_id, to_type, to_id,
                 description, reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            transaction_id = self.execute_update(
                query,
                (datetime.now().strftime('%d-%m-%Y'), amount, 'cash', 0, entity_type, entity_id,
                 description, 'DEPOSIT'),
                auto_commit=False
            )

            # Update balance (don't auto-commit)
            if entity_type == 'company':
                self.update_company_balance(entity_id, amount, auto_commit=False)
            else:
                self.update_user_balance(entity_id, amount, auto_commit=False)

            # Commit all changes atomically
            self.connection.commit()
            return transaction_id

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to deposit: {e}")

    def withdraw(self, entity_type: str, entity_id: int, amount: float, description: str = "Cash Withdrawal") -> int:
        """
        Withdraw money from an account (subtract balance)
        
        Args:
            entity_type: 'company' or 'user'
            entity_id: ID of the entity
            amount: Amount to withdraw (must be positive)
            description: Description of the withdrawal
            
        Returns:
            Transaction ID
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if entity_type not in ['company', 'user']:
            raise ValueError("Entity type must be 'company' or 'user'")
        
        # Check balance
        if entity_type == 'company':
            entity = self.get_company(entity_id)
        else:
            entity = self.get_user(entity_id)
        
        if not entity:
            raise Exception(f"Entity not found: {entity_type} id {entity_id}")
        
        if entity['balance'] < amount:
            raise Exception(f"Insufficient balance: {entity['balance']} < {amount}")
        
        try:
            # Create a transaction record for audit trail (don't auto-commit)
            query = """
                INSERT INTO transactions
                (transaction_date, amount, from_type, from_id, to_type, to_id,
                 description, reference)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            transaction_id = self.execute_update(
                query,
                (datetime.now().strftime('%d-%m-%Y'), amount, entity_type, entity_id, 'cash', 0,
                 description, 'WITHDRAW'),
                auto_commit=False
            )

            # Update balance (don't auto-commit)
            if entity_type == 'company':
                self.update_company_balance(entity_id, -amount, auto_commit=False)
            else:
                self.update_user_balance(entity_id, -amount, auto_commit=False)

            # Commit all changes atomically
            self.connection.commit()
            return transaction_id

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to withdraw: {e}")

    def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID with sender and receiver names"""
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            WHERE t.id = ?
        """
        results = self.execute_query(query, (transaction_id,))
        return dict(results[0]) if results else None

    def get_all_transactions(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get all transactions with names"""
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            ORDER BY t.transaction_date DESC, t.created_date DESC
        """
        if limit:
            # Use parameterized query to prevent SQL injection
            query += " LIMIT ?"
            results = self.execute_query(query, (int(limit),))
        else:
            results = self.execute_query(query)
        return [dict(row) for row in results]

    def get_transactions_paginated(self, page: int = 1, per_page: int = 50) -> tuple[List[Dict[str, Any]], int]:
        """
        Get paginated transactions with total count

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page

        Returns:
            Tuple of (transactions list, total count)
        """
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM transactions"
        count_result = self.execute_query(count_query)
        total_count = count_result[0]['count'] if count_result else 0

        # Get paginated results
        offset = (page - 1) * per_page
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            ORDER BY t.transaction_date DESC, t.created_date DESC
            LIMIT ? OFFSET ?
        """
        results = self.execute_query(query, (per_page, offset))
        return [dict(row) for row in results], total_count

    def get_transaction_count(self) -> int:
        """Get total number of transactions"""
        query = "SELECT COUNT(*) as count FROM transactions"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0

    def search_transactions(self, search_term: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search transactions by description, from/to names

        Args:
            search_term: Search string
            limit: Maximum results to return

        Returns:
            List of matching transactions
        """
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            WHERE t.description LIKE ?
               OR c1.name LIKE ?
               OR u1.name LIKE ?
               OR c2.name LIKE ?
               OR u2.name LIKE ?
            ORDER BY t.transaction_date DESC, t.created_date DESC
            LIMIT ?
        """
        search_pattern = f"%{search_term}%"
        results = self.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, limit))
        return [dict(row) for row in results]

    def search_companies(self, search_term: str) -> List[Dict[str, Any]]:
        """Search companies by name, email, or phone"""
        query = """
            SELECT * FROM companies
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        results = self.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in results]

    def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by name, email, or department"""
        query = """
            SELECT * FROM users
            WHERE name LIKE ? OR email LIKE ? OR department LIKE ?
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        results = self.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in results]

    def get_transactions_by_entity(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """Get all transactions for a specific company or user"""
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            WHERE (t.from_type = ? AND t.from_id = ?)
               OR (t.to_type = ? AND t.to_id = ?)
            ORDER BY t.transaction_date DESC
        """
        results = self.execute_query(query, (entity_type, entity_id, entity_type, entity_id))
        return [dict(row) for row in results]

    def get_account_ledger(self, entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
        """
        Get ledger entries for an account with running balance
        
        Args:
            entity_type: 'company' or 'user'
            entity_id: ID of the entity
            
        Returns:
            List of transactions with type (Debit/Credit) and running balance
        """
        # Get all transactions for this entity
        transactions = self.get_transactions_by_entity(entity_type, entity_id)

        # Sort by date (oldest first) to calculate running balance
        transactions.sort(key=lambda x: (normalize_date_for_sort(x.get('transaction_date', '')), x.get('created_date', '')))
        
        # Get starting balance (should be 0 for new accounts)
        if entity_type == 'company':
            entity = self.get_company(entity_id)
        else:
            entity = self.get_user(entity_id)
        
        # Calculate running balance
        running_balance = 0.0
        ledger_entries = []
        
        for trans in transactions:
            # Determine if this is a debit or credit for this account
            is_credit = (trans['to_type'] == entity_type and trans['to_id'] == entity_id)
            is_debit = (trans['from_type'] == entity_type and trans['from_id'] == entity_id)
            
            if is_credit:
                # Money coming in (credit)
                running_balance += trans['amount']
                trans_type = 'Credit'
                other_party = trans['from_name'] if trans['from_type'] != 'cash' else 'Cash Deposit'
                other_party_type = trans['from_type']
                other_party_id = trans['from_id']
            else:
                # Money going out (debit)
                running_balance -= trans['amount']
                trans_type = 'Debit'
                other_party = trans['to_name'] if trans['to_type'] != 'cash' else 'Cash Withdrawal'
                other_party_type = trans['to_type']
                other_party_id = trans['to_id']

            # Add ledger entry
            ledger_entry = {
                'id': trans['id'],
                'date': trans['transaction_date'],
                'type': trans_type,
                'description': trans['description'] or '',
                'reference': trans['reference'] or '',
                'other_party': other_party,
                'other_party_type': other_party_type,
                'other_party_id': other_party_id,
                'amount': trans['amount'],
                'running_balance': running_balance,
                'from_name': trans['from_name'],
                'to_name': trans['to_name'],
                'from_type': trans['from_type'],
                'to_type': trans['to_type'],
                'created_date': trans['created_date']
            }
            ledger_entries.append(ledger_entry)
        
        # Reverse to show newest first
        ledger_entries.reverse()
        
        return ledger_entries

    def delete_transaction(self, transaction_id: int) -> int:
        """
        Delete a transaction and reverse balance changes
        WARNING: This will affect account balances
        """
        # Get transaction details first
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return 0

        try:
            # Reverse balance changes
            amount = transaction['amount']
            from_type = transaction['from_type']
            from_id = transaction['from_id']
            to_type = transaction['to_type']
            to_id = transaction['to_id']

            # Reverse sender balance (add back) - don't auto-commit
            if from_type == 'company':
                self.update_company_balance(from_id, amount, auto_commit=False)
            elif from_type == 'user':
                self.update_user_balance(from_id, amount, auto_commit=False)

            # Reverse receiver balance (subtract) - don't auto-commit
            if to_type == 'company':
                self.update_company_balance(to_id, -amount, auto_commit=False)
            elif to_type == 'user':
                self.update_user_balance(to_id, -amount, auto_commit=False)

            # Delete transaction (don't auto-commit)
            query = "DELETE FROM transactions WHERE id = ?"
            result = self.execute_update(query, (transaction_id,), auto_commit=False)

            # Commit all changes atomically
            self.connection.commit()
            return result

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to delete transaction: {e}")

    def delete_all_transactions(self) -> int:
        """
        Delete ALL transactions and reset all balances to zero
        WARNING: This will delete all transaction history and reset all account balances!
        """
        try:
            # Reset all company balances to 0
            self.connection.execute("UPDATE companies SET balance = 0.00")

            # Reset all user balances to 0
            self.connection.execute("UPDATE users SET balance = 0.00")

            # Delete all transactions
            result = self.connection.execute("DELETE FROM transactions")
            deleted_count = result.rowcount

            self.connection.commit()
            return deleted_count

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to delete all transactions: {e}")

    def delete_multiple_transactions(self, transaction_ids: list) -> int:
        """
        Delete multiple transactions and reverse balance changes for each
        WARNING: This will affect account balances
        """
        if not transaction_ids:
            return 0

        deleted_count = 0
        try:
            for transaction_id in transaction_ids:
                # Get transaction details first
                transaction = self.get_transaction(transaction_id)
                if not transaction:
                    continue

                # Reverse balance changes
                amount = transaction['amount']
                from_type = transaction['from_type']
                from_id = transaction['from_id']
                to_type = transaction['to_type']
                to_id = transaction['to_id']

                # Reverse sender balance (add back)
                if from_type == 'company':
                    self.update_company_balance(from_id, amount)
                elif from_type == 'user':
                    self.update_user_balance(from_id, amount)

                # Reverse receiver balance (subtract)
                if to_type == 'company':
                    self.update_company_balance(to_id, -amount)
                elif to_type == 'user':
                    self.update_user_balance(to_id, -amount)

                # Delete transaction
                query = "DELETE FROM transactions WHERE id = ?"
                self.execute_update(query, (transaction_id,))
                deleted_count += 1

            self.connection.commit()
            return deleted_count

        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Failed to delete transactions: {e}")

    # ==================== Reporting Operations ====================

    def get_total_balances(self) -> Dict[str, float]:
        """Get total balances for companies and users"""
        cursor = self.connection.cursor()

        cursor.execute("SELECT SUM(balance) FROM companies")
        company_total = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(balance) FROM users")
        user_total = cursor.fetchone()[0] or 0.0

        return {
            'company_total': company_total,
            'user_total': user_total,
            'grand_total': company_total + user_total
        }

    def get_transaction_summary(self) -> Dict[str, Any]:
        """Get transaction summary statistics"""
        cursor = self.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_count = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM transactions")
        total_amount = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(amount) FROM transactions")
        avg_amount = cursor.fetchone()[0] or 0.0

        return {
            'total_count': total_count,
            'total_amount': total_amount,
            'average_amount': avg_amount
        }

    def search_transactions(self, search_term: str) -> List[Dict[str, Any]]:
        """Search transactions by description, reference, or entity names"""
        query = """
            SELECT
                t.*,
                CASE
                    WHEN t.from_type = 'company' THEN c1.name
                    ELSE u1.name
                END as from_name,
                CASE
                    WHEN t.to_type = 'company' THEN c2.name
                    ELSE u2.name
                END as to_name
            FROM transactions t
            LEFT JOIN companies c1 ON t.from_type = 'company' AND t.from_id = c1.id
            LEFT JOIN users u1 ON t.from_type = 'user' AND t.from_id = u1.id
            LEFT JOIN companies c2 ON t.to_type = 'company' AND t.to_id = c2.id
            LEFT JOIN users u2 ON t.to_type = 'user' AND t.to_id = u2.id
            WHERE t.description LIKE ?
               OR t.reference LIKE ?
               OR c1.name LIKE ?
               OR u1.name LIKE ?
               OR c2.name LIKE ?
               OR u2.name LIKE ?
            ORDER BY t.transaction_date DESC
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern,) * 6
        results = self.execute_query(query, params)
        return [dict(row) for row in results]

    # ==================== Backup and Restore Operations ====================

    def create_backup(self, backup_path: str = None) -> str:
        """
        Create a backup of the database

        Args:
            backup_path: Optional custom backup path. If None, creates in same directory.

        Returns:
            Path to the backup file
        """
        if backup_path is None:
            # Create backup in same directory with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.dirname(self.db_path)
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')

        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Close connection temporarily for safe copy
        self.connection.commit()

        try:
            # Use SQLite backup API for consistency
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()

            return backup_path

        except Exception as e:
            raise Exception(f"Failed to create backup: {e}")

    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Restore database from a backup file

        Args:
            backup_path: Path to the backup file

        Returns:
            True if restore successful
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Verify it's a valid SQLite database
        try:
            test_conn = sqlite3.connect(backup_path)
            test_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
        except sqlite3.Error as e:
            raise Exception(f"Invalid backup file: {e}")

        try:
            # Close current connection
            self.close()

            # Create backup of current database before restore
            current_backup = self.db_path + '.pre_restore'
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, current_backup)

            # Copy backup to database location
            shutil.copy2(backup_path, self.db_path)

            # Reconnect
            self.connect()

            # Remove pre-restore backup on success
            if os.path.exists(current_backup):
                os.remove(current_backup)

            return True

        except Exception as e:
            # Attempt to restore from pre-restore backup
            if os.path.exists(current_backup):
                shutil.copy2(current_backup, self.db_path)
                self.connect()
            raise Exception(f"Failed to restore from backup: {e}")

    def get_backup_list(self, backup_dir: str = None) -> List[Dict[str, Any]]:
        """
        Get list of available backups

        Args:
            backup_dir: Directory to search for backups. Defaults to database directory.

        Returns:
            List of backup info dictionaries
        """
        if backup_dir is None:
            backup_dir = os.path.dirname(self.db_path)

        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('backup_') and filename.endswith('.db'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime).strftime('%d-%m-%Y %H:%M:%S')
                })

        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a backup file

        Args:
            backup_path: Path to the backup file

        Returns:
            True if deletion successful
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Safety check - don't delete the active database
        if os.path.abspath(backup_path) == os.path.abspath(self.db_path):
            raise Exception("Cannot delete the active database")

        os.remove(backup_path)
        return True
