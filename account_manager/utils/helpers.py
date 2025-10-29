"""
Helper Functions - Utility functions for the application
"""

from datetime import datetime
from typing import Union


def format_currency(amount: float) -> str:
    """
    Format a number as currency with 2 decimal places

    Args:
        amount: The amount to format

    Returns:
        Formatted currency string (e.g., "₹1,234.56")
    """
    return f"₹{amount:,.2f}"


def format_date(date_str: Union[str, datetime], input_format: str = "%Y-%m-%d",
                output_format: str = "%B %d, %Y") -> str:
    """
    Format a date string

    Args:
        date_str: Date string or datetime object
        input_format: Input date format (default: YYYY-MM-DD)
        output_format: Output date format (default: Month DD, YYYY)

    Returns:
        Formatted date string
    """
    if isinstance(date_str, datetime):
        return date_str.strftime(output_format)

    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str


def get_current_date(format_str: str = "%Y-%m-%d") -> str:
    """
    Get current date as formatted string

    Args:
        format_str: Date format (default: YYYY-MM-DD)

    Returns:
        Current date string
    """
    return datetime.now().strftime(format_str)


def validate_email(email: str) -> bool:
    """
    Simple email validation

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Simple phone number validation (allows various formats)

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    # Remove common separators
    clean_phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it's 10-15 digits
    return bool(re.match(r'^\d{10,15}$', clean_phone))


def validate_amount(amount_str: str) -> tuple[bool, float]:
    """
    Validate and parse an amount string

    Args:
        amount_str: Amount string to validate

    Returns:
        Tuple of (is_valid, parsed_amount)
    """
    try:
        # Remove currency symbols (₹, Rs., Rs, $, INR) and commas
        clean_amount = amount_str.replace('₹', '').replace('Rs.', '').replace('Rs', '').replace('$', '').replace('INR', '').replace(',', '').strip()
        amount = float(clean_amount)

        if amount <= 0:
            return False, 0.0

        return True, amount
    except (ValueError, AttributeError):
        return False, 0.0


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def get_balance_color(balance: float) -> str:
    """
    Get color indicator for balance amount

    Args:
        balance: Balance amount

    Returns:
        Color name for CustomTkinter
    """
    if balance > 0:
        return "green"
    elif balance < 0:
        return "red"
    else:
        return "gray"


def export_to_csv(data: list[dict], filename: str, fieldnames: list[str] = None):
    """
    Export data to CSV file

    Args:
        data: List of dictionaries to export
        filename: Output filename
        fieldnames: List of field names (if None, uses keys from first row)
    """
    import csv

    if not data:
        raise ValueError("No data to export")

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def import_from_csv(filename: str) -> list[dict]:
    """
    Import data from CSV file

    Args:
        filename: Input filename

    Returns:
        List of dictionaries
    """
    import csv

    with open(filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def show_error_message(title: str, message: str):
    """
    Display error message (placeholder for GUI integration)

    Args:
        title: Error title
        message: Error message
    """
    print(f"ERROR - {title}: {message}")


def show_success_message(title: str, message: str):
    """
    Display success message (placeholder for GUI integration)

    Args:
        title: Success title
        message: Success message
    """
    print(f"SUCCESS - {title}: {message}")


def confirm_action(title: str, message: str) -> bool:
    """
    Confirm an action (placeholder for GUI integration)

    Args:
        title: Confirmation title
        message: Confirmation message

    Returns:
        True if confirmed, False otherwise
    """
    response = input(f"{title}: {message} (y/n): ")
    return response.lower() == 'y'
