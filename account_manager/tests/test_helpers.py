"""
Helper Functions Tests
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    format_currency,
    format_date,
    validate_email,
    validate_phone,
    validate_amount,
    sanitize_string,
    validate_name,
    validate_description,
    validate_date_input,
    normalize_date_for_sort,
    truncate_string
)


class TestFormatCurrency(unittest.TestCase):
    """Test currency formatting"""

    def test_basic_format(self):
        """Test basic currency formatting"""
        self.assertEqual(format_currency(1000), "₹1,000.00")

    def test_indian_format(self):
        """Test Indian number system formatting"""
        self.assertEqual(format_currency(150000), "₹1,50,000.00")
        self.assertEqual(format_currency(12345678), "₹1,23,45,678.00")

    def test_negative_amount(self):
        """Test negative amount formatting"""
        result = format_currency(-1000)
        self.assertIn("-", result)

    def test_decimal_precision(self):
        """Test decimal precision"""
        self.assertEqual(format_currency(100.5), "₹100.50")
        self.assertEqual(format_currency(100.123), "₹100.12")

    def test_zero_amount(self):
        """Test zero amount"""
        self.assertEqual(format_currency(0), "₹0.00")


class TestFormatDate(unittest.TestCase):
    """Test date formatting"""

    def test_dd_mm_yyyy_format(self):
        """Test DD-MM-YYYY input format"""
        result = format_date("15-01-2024", "%d-%m-%Y", "%d %B, %Y")
        self.assertEqual(result, "15 January, 2024")

    def test_yyyy_mm_dd_format(self):
        """Test YYYY-MM-DD input format auto-detection"""
        result = format_date("2024-01-15")
        self.assertIn("January", result)

    def test_empty_date(self):
        """Test empty date returns empty"""
        self.assertEqual(format_date(""), "")
        self.assertEqual(format_date(None), None)

    def test_invalid_date(self):
        """Test invalid date returns original"""
        result = format_date("invalid")
        self.assertEqual(result, "invalid")


class TestValidateEmail(unittest.TestCase):
    """Test email validation"""

    def test_valid_email(self):
        """Test valid email addresses"""
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.org"))

    def test_invalid_email(self):
        """Test invalid email addresses"""
        self.assertFalse(validate_email("invalid"))
        self.assertFalse(validate_email("@domain.com"))
        self.assertFalse(validate_email("user@"))

    def test_empty_email(self):
        """Test empty email is valid (optional field)"""
        self.assertTrue(validate_email(""))


class TestValidatePhone(unittest.TestCase):
    """Test phone validation"""

    def test_valid_phone(self):
        """Test valid phone numbers"""
        self.assertTrue(validate_phone("1234567890"))
        self.assertTrue(validate_phone("123-456-7890"))
        self.assertTrue(validate_phone("(123) 456-7890"))

    def test_invalid_phone(self):
        """Test invalid phone numbers"""
        self.assertFalse(validate_phone("123"))
        self.assertFalse(validate_phone("abcdefghij"))


class TestValidateAmount(unittest.TestCase):
    """Test amount validation"""

    def test_valid_amount(self):
        """Test valid amounts"""
        is_valid, amount = validate_amount("100")
        self.assertTrue(is_valid)
        self.assertEqual(amount, 100.0)

    def test_amount_with_currency(self):
        """Test amount with currency symbols"""
        is_valid, amount = validate_amount("₹1,000")
        self.assertTrue(is_valid)
        self.assertEqual(amount, 1000.0)

    def test_negative_amount(self):
        """Test negative amount is invalid"""
        is_valid, _ = validate_amount("-100")
        self.assertFalse(is_valid)

    def test_zero_amount(self):
        """Test zero amount is invalid"""
        is_valid, _ = validate_amount("0")
        self.assertFalse(is_valid)

    def test_invalid_amount(self):
        """Test invalid amount string"""
        is_valid, _ = validate_amount("abc")
        self.assertFalse(is_valid)


class TestSanitizeString(unittest.TestCase):
    """Test string sanitization"""

    def test_basic_sanitize(self):
        """Test basic string sanitization"""
        result = sanitize_string("  Hello World  ")
        self.assertEqual(result, "Hello World")

    def test_remove_control_chars(self):
        """Test removal of control characters"""
        result = sanitize_string("Hello\x00World")
        self.assertEqual(result, "HelloWorld")

    def test_max_length(self):
        """Test max length enforcement"""
        long_string = "a" * 1000
        result = sanitize_string(long_string, max_length=100)
        self.assertEqual(len(result), 100)

    def test_empty_string(self):
        """Test empty string"""
        self.assertEqual(sanitize_string(""), "")
        self.assertEqual(sanitize_string(None), "")


class TestValidateName(unittest.TestCase):
    """Test name validation"""

    def test_valid_name(self):
        """Test valid names"""
        is_valid, result = validate_name("John Doe")
        self.assertTrue(is_valid)
        self.assertEqual(result, "John Doe")

    def test_empty_name(self):
        """Test empty name is invalid"""
        is_valid, _ = validate_name("")
        self.assertFalse(is_valid)

    def test_long_name(self):
        """Test name exceeding max length"""
        long_name = "a" * 150
        is_valid, result = validate_name(long_name)
        self.assertTrue(is_valid)
        self.assertEqual(len(result), 100)


class TestValidateDateInput(unittest.TestCase):
    """Test date input validation"""

    def test_valid_date(self):
        """Test valid date"""
        is_valid, error = validate_date_input("15-01-2024")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_invalid_format(self):
        """Test invalid date format"""
        is_valid, error = validate_date_input("2024-01-15")
        self.assertFalse(is_valid)
        self.assertIn("DD-MM-YYYY", error)

    def test_invalid_date(self):
        """Test invalid date values"""
        is_valid, _ = validate_date_input("32-01-2024")
        self.assertFalse(is_valid)

    def test_empty_date(self):
        """Test empty date"""
        is_valid, _ = validate_date_input("")
        self.assertFalse(is_valid)


class TestNormalizeDateForSort(unittest.TestCase):
    """Test date normalization for sorting"""

    def test_dd_mm_yyyy(self):
        """Test DD-MM-YYYY to YYYY-MM-DD conversion"""
        result = normalize_date_for_sort("15-01-2024")
        self.assertEqual(result, "2024-01-15")

    def test_already_sortable(self):
        """Test YYYY-MM-DD stays the same"""
        result = normalize_date_for_sort("2024-01-15")
        self.assertEqual(result, "2024-01-15")

    def test_empty_date(self):
        """Test empty date"""
        self.assertEqual(normalize_date_for_sort(""), "")


class TestTruncateString(unittest.TestCase):
    """Test string truncation"""

    def test_truncate(self):
        """Test string truncation"""
        result = truncate_string("Hello World", 8)
        self.assertEqual(result, "Hello...")

    def test_no_truncate_needed(self):
        """Test no truncation needed"""
        result = truncate_string("Hello", 10)
        self.assertEqual(result, "Hello")


if __name__ == '__main__':
    unittest.main()
