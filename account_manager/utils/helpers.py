"""
Helper Functions - Utility functions for the application
"""

from datetime import datetime
from typing import Union, Callable, Optional, List
import customtkinter as ctk


def format_currency(amount: float) -> str:
    """
    Format a number as Indian currency with Indian number system formatting

    Args:
        amount: The amount to format

    Returns:
        Formatted currency string in Indian style (e.g., "₹1,50,000.00")
    """
    # Split into integer and decimal parts
    amount_str = f"{amount:.2f}"
    parts = amount_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"

    # Handle negative numbers
    is_negative = False
    if integer_part.startswith('-'):
        is_negative = True
        integer_part = integer_part[1:]

    # Format in Indian style (groups of 3, then 2)
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        # Reverse the string for easier grouping
        reversed_num = integer_part[::-1]

        # First group of 3 digits
        groups = [reversed_num[:3]]
        remaining = reversed_num[3:]

        # Then groups of 2
        while remaining:
            groups.append(remaining[:2])
            remaining = remaining[2:]

        # Join groups with comma and reverse back
        formatted = ','.join(groups)
        formatted = formatted[::-1]

    # Add negative sign if needed
    if is_negative:
        formatted = '-' + formatted

    # Return with rupee symbol
    return f"₹{formatted}.{decimal_part}"


def format_date(date_str: Union[str, datetime], input_format: str = "%d-%m-%Y",
                output_format: str = "%d %B, %Y") -> str:
    """
    Format a date string

    Args:
        date_str: Date string or datetime object
        input_format: Input date format (default: DD-MM-YYYY)
        output_format: Output date format (default: DD Month, YYYY)

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


def get_current_date(format_str: str = "%d-%m-%Y") -> str:
    """
    Get current date as formatted string

    Args:
        format_str: Date format (default: DD-MM-YYYY)

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


class DropdownButton:
    """
    Simple clickable button that acts as a dropdown selector
    Much more reliable than trying to make Entry widgets clickable
    """

    def __init__(self, parent, values: List[str], callback: Optional[Callable] = None,
                 height: int = 40, font: tuple = ("Roboto", 14), placeholder: str = "Select..."):
        """
        Initialize dropdown button

        Args:
            parent: Parent widget
            values: List of dropdown options
            callback: Function to call when option is selected
            height: Button height
            font: Button font
            placeholder: Placeholder text when no selection
        """
        self.values = values
        self.callback = callback
        self.dropdown_window = None
        self.current_value = placeholder
        self.placeholder = placeholder

        # Create button that looks like an entry field
        self.button = ctk.CTkButton(
            parent,
            text=placeholder,
            height=height,
            font=font,
            fg_color=("gray90", "gray20"),
            text_color=("gray10", "gray90"),
            hover_color=("gray85", "gray25"),
            anchor="w",
            command=self.show_dropdown,
            cursor="hand2"
        )

    def pack(self, **kwargs):
        """Pack the button"""
        self.button.pack(**kwargs)

    def get(self) -> str:
        """Get current value"""
        return self.current_value

    def set(self, value: str):
        """Set current value"""
        self.current_value = value
        self.button.configure(text=value)

    def show_dropdown(self):
        """Show dropdown menu"""
        # Close existing dropdown if open
        if self.dropdown_window:
            self.close_dropdown()
            return

        # Don't show if no values
        if not self.values or len(self.values) == 0:
            return

        # Create toplevel window for dropdown
        self.dropdown_window = ctk.CTkToplevel(self.button)
        self.dropdown_window.withdraw()

        # Remove window decorations
        self.dropdown_window.overrideredirect(True)

        # Calculate position
        self.button.update()
        x = self.button.winfo_rootx()
        y = self.button.winfo_rooty() + self.button.winfo_height()

        # Get screen dimensions
        screen_height = self.button.winfo_screenheight()

        # Calculate dropdown height
        item_height = 35
        max_height = 300
        dropdown_height = min(len(self.values) * item_height + 10, max_height)

        # Check if dropdown would go off bottom of screen
        if y + dropdown_height > screen_height - 50:
            y = self.button.winfo_rooty() - dropdown_height

        # Set window size and position
        width = self.button.winfo_width()
        self.dropdown_window.geometry(f"{width}x{dropdown_height}+{x}+{y}")

        # Create scrollable frame for options
        if len(self.values) * item_height > max_height:
            container = ctk.CTkScrollableFrame(
                self.dropdown_window,
                width=width-10,
                height=dropdown_height-10,
                fg_color=("gray95", "gray15"),
                corner_radius=8
            )
            container.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            container = ctk.CTkFrame(
                self.dropdown_window,
                fg_color=("gray95", "gray15"),
                corner_radius=8
            )
            container.pack(fill="both", expand=True, padx=5, pady=5)

        # Add options
        for value in self.values:
            if value == "Select..." or "No entities" in value:
                continue

            option_btn = ctk.CTkButton(
                container,
                text=value,
                height=item_height,
                font=("Roboto", 13),
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                anchor="w",
                command=lambda v=value: self.select_option(v)
            )
            option_btn.pack(fill="x", padx=5, pady=2)

        # Show window
        self.dropdown_window.deiconify()
        self.dropdown_window.lift()
        self.dropdown_window.focus_force()

        # Bind events to close dropdown
        self.dropdown_window.bind("<FocusOut>", lambda e: self.close_dropdown())
        self.dropdown_window.bind("<Escape>", lambda e: self.close_dropdown())

    def select_option(self, value: str):
        """Handle option selection"""
        self.current_value = value
        self.button.configure(text=value)

        # Call callback if provided
        if self.callback:
            try:
                self.callback(value)
            except Exception as e:
                print(f"Error in callback: {e}")

        # Close dropdown
        self.close_dropdown()

    def close_dropdown(self):
        """Close dropdown menu"""
        if self.dropdown_window:
            try:
                self.dropdown_window.destroy()
            except:
                pass
            self.dropdown_window = None

    def update_values(self, values: List[str]):
        """Update dropdown values"""
        self.values = values
