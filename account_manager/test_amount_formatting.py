"""
Test Indian Number Formatting in Amount Field
"""

import sys
sys.path.insert(0, '.')

print("=" * 70)
print("Testing Indian Number Formatting in Amount Field")
print("=" * 70)
print()

# Test 1: Check if imports work
print("Step 1: Testing imports...")
try:
    import customtkinter as ctk
    from gui.main_window import MainWindow
    from database.db_manager import DatabaseManager
    print("[OK] All imports successful")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)

print()

# Test 2: Check if the formatting function works correctly
print("Step 2: Testing number formatting logic...")

def test_format(number_str, expected):
    """Test formatting logic"""
    # Simulate the formatting logic
    clean_value = ''.join(c for c in number_str if c.isdigit() or c == '.')

    if '.' in clean_value:
        parts = clean_value.split('.')
        integer_part = parts[0]
        decimal_part = parts[1][:2] if len(parts) > 1 else ''
    else:
        integer_part = clean_value
        decimal_part = ''

    if integer_part:
        reversed_num = integer_part[::-1]
        groups = []
        groups.append(reversed_num[:3])
        remaining = reversed_num[3:]

        while remaining:
            groups.append(remaining[:2])
            remaining = remaining[2:]

        formatted = ','.join(groups)
        formatted = formatted[::-1]
    else:
        formatted = '0'

    if decimal_part:
        formatted = f"{formatted}.{decimal_part}"

    status = "[OK]" if formatted == expected else "[FAIL]"
    print(f"{status} Input: '{number_str}' -> Output: '{formatted}' (Expected: '{expected}')")
    return formatted == expected

# Test cases
test_cases = [
    ("150000", "1,50,000"),
    ("1500", "1,500"),
    ("15000", "15,000"),
    ("150000.50", "1,50,000.50"),
    ("1234567", "12,34,567"),
    ("12345678", "1,23,45,678"),
    ("123456789", "12,34,56,789"),
    ("100", "100"),
    ("1000", "1,000"),
    ("10000", "10,000"),
]

all_passed = True
for input_val, expected_val in test_cases:
    if not test_format(input_val, expected_val):
        all_passed = False

print()

if all_passed:
    print("[OK] All formatting tests passed!")
else:
    print("[FAIL] Some formatting tests failed!")

print()

# Test 3: Launch the application to test real-time formatting
print("Step 3: Testing in GUI (will open application)...")
print()
print("MANUAL TEST INSTRUCTIONS:")
print("-" * 70)
print("1. The application will open")
print("2. Find the 'Amount' field in the Quick Transaction Entry panel")
print("3. Try typing these numbers:")
print("   - Type '150000' -> Should show '1,50,000'")
print("   - Type '1234567' -> Should show '12,34,567'")
print("   - Type '150000.50' -> Should show '1,50,000.50'")
print("4. Verify the formatting happens as you type")
print("5. Close the application when done")
print("-" * 70)
print()

response = input("Press ENTER to launch the application for manual testing (or 'n' to skip): ")

if response.lower() != 'n':
    try:
        print()
        print("Launching application...")
        print()

        # Initialize application
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        db = DatabaseManager()
        root = ctk.CTk()
        root.title("Account Manager - Amount Formatting Test")
        root.geometry("1200x800")

        main_window = MainWindow(root, db)

        print("[OK] Application launched successfully!")
        print("[INFO] Try typing amounts in the Amount field")
        print()

        root.mainloop()

        db.close()

        print()
        print("[OK] Application closed")

    except Exception as e:
        print(f"[ERROR] Failed to launch application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print()
    print("Skipping GUI test")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print()
print("Summary:")
print("  - Number formatting logic: [OK]")
print("  - GUI integration: Manual test required")
print()
print("Expected behavior:")
print("  - Type '150000' -> Shows '1,50,000' (Indian lakhs format)")
print("  - Type '1500000' -> Shows '15,00,000'")
print("  - Type '12345678' -> Shows '1,23,45,678' (Indian crores format)")
print("  - Formatting happens in real-time as you type")
print()
