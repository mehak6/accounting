"""
Test: Multiple users without email addresses
This tests that users can be added without email (email is optional)
"""

import sys
sys.path.insert(0, '.')

from database.db_manager import DatabaseManager

print("=" * 70)
print("Testing User Email Fix - Multiple Users Without Email")
print("=" * 70)
print()

# Initialize database (this will run the migration)
print("Step 1: Initializing database and running migration...")
db = DatabaseManager()
print("Database initialized successfully")
print()

# Test 1: Add first user without email
print("Step 2: Adding first user without email...")
try:
    user1_id = db.add_user(
        name="Test User 1",
        email="",  # Empty email
        role="Manager",
        department="Sales"
    )
    print(f"SUCCESS: User 1 added with ID: {user1_id}")
except Exception as e:
    print(f"ERROR: Failed to add user 1: {e}")
    db.close()
    sys.exit(1)

# Test 2: Add second user without email (this should work now!)
print()
print("Step 3: Adding second user without email...")
try:
    user2_id = db.add_user(
        name="Test User 2",
        email="",  # Empty email - this was failing before
        role="Developer",
        department="Engineering"
    )
    print(f"SUCCESS: User 2 added with ID: {user2_id}")
except Exception as e:
    print(f"ERROR: Failed to add user 2: {e}")
    db.close()
    sys.exit(1)

# Test 3: Add third user with no email parameter
print()
print("Step 4: Adding third user with no email...")
try:
    user3_id = db.add_user(
        name="Test User 3",
        role="Designer",
        department="Creative"
    )
    print(f"SUCCESS: User 3 added with ID: {user3_id}")
except Exception as e:
    print(f"ERROR: Failed to add user 3: {e}")
    db.close()
    sys.exit(1)

# Test 4: Add users with same email (should also work now)
print()
print("Step 5: Adding users with duplicate emails...")
try:
    user4_id = db.add_user(
        name="Test User 4",
        email="test@example.com"
    )
    print(f"SUCCESS: User 4 added with ID: {user4_id}")

    user5_id = db.add_user(
        name="Test User 5",
        email="test@example.com"  # Same email - should work now!
    )
    print(f"SUCCESS: User 5 added with ID: {user5_id} (duplicate email allowed)")
except Exception as e:
    print(f"ERROR: Failed to add users with duplicate email: {e}")
    db.close()
    sys.exit(1)

# Verify all users
print()
print("Step 6: Verifying all users...")
all_users = db.get_all_users()
print(f"Total users in database: {len(all_users)}")
print()
print("Users list:")
for user in all_users:
    email_display = user['email'] if user['email'] else "(no email)"
    print(f"  - {user['name']:20s} | Email: {email_display:30s} | Role: {user.get('role', 'N/A')}")

db.close()

print()
print("=" * 70)
print("SUCCESS: All tests passed!")
print("=" * 70)
print()
print("Summary:")
print("  - Multiple users can now be added without email addresses")
print("  - Email field is optional (not required)")
print("  - Duplicate emails are allowed")
print("  - Only NAME is required when adding users")
print()
print("The issue has been fixed!")
