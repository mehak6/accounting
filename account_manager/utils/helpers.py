"""
Helper Functions - Utility functions for the application
"""

from datetime import datetime
from typing import Union, Callable, Optional, List
import customtkinter as ctk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AccountManager')


def handle_error(error: Exception, user_message: str = None, show_dialog: bool = True) -> str:
    """
    Handle errors with user-friendly messages and logging

    Args:
        error: The exception that occurred
        user_message: Custom message to show user (optional)
        show_dialog: Whether to show error dialog

    Returns:
        User-friendly error message
    """
    # Log the technical error
    logger.error(f"Error: {error}", exc_info=True)

    # Map common errors to user-friendly messages
    error_messages = {
        'UNIQUE constraint failed': "This item already exists. Please use a different name.",
        'FOREIGN KEY constraint failed': "Cannot delete this item because it is referenced by other records.",
        'NOT NULL constraint failed': "Please fill in all required fields.",
        'CHECK constraint failed': "Invalid value provided. Please check your input.",
        'no such table': "Database error. Please restart the application.",
        'database is locked': "Database is busy. Please try again in a moment.",
        'Insufficient balance': "Insufficient balance for this operation.",
        'not found': "The requested item was not found.",
    }

    error_str = str(error)

    # Find matching error message
    friendly_message = user_message
    if not friendly_message:
        for key, message in error_messages.items():
            if key.lower() in error_str.lower():
                friendly_message = message
                break

    # Default message if no match
    if not friendly_message:
        friendly_message = "An unexpected error occurred. Please try again."

    # Show dialog if requested
    if show_dialog:
        messagebox.showerror("Error", friendly_message)

    return friendly_message


def show_success(message: str, title: str = "Success"):
    """Show success message dialog"""
    messagebox.showinfo(title, message)


def show_warning(message: str, title: str = "Warning"):
    """Show warning message dialog"""
    messagebox.showwarning(title, message)


def confirm_action(message: str, title: str = "Confirm") -> bool:
    """
    Show confirmation dialog

    Returns:
        True if user confirms, False otherwise
    """
    return messagebox.askyesno(title, message)


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

    if not date_str:
        return date_str

    # Try the specified input format first
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        pass

    # Auto-detect format: try DD-MM-YYYY
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime(output_format)
    except ValueError:
        pass

    # Try YYYY-MM-DD
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime(output_format)
    except ValueError:
        pass

    # Return original if nothing works
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


def normalize_date_for_sort(date_str: str) -> str:
    """
    Convert any date format to YYYY-MM-DD for proper string sorting

    Args:
        date_str: Date string in any format

    Returns:
        Date string in YYYY-MM-DD format for sorting
    """
    if not date_str:
        return ''

    # Try DD-MM-YYYY format
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Try YYYY-MM-DD format (already sortable)
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        pass

    return date_str


def sanitize_string(text: str, max_length: int = 500) -> str:
    """
    Sanitize a string input by removing dangerous characters and limiting length

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not text:
        return ""

    # Convert to string if not already
    text = str(text).strip()

    # Remove null bytes and control characters (except newlines and tabs)
    import re
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def validate_name(name: str) -> tuple[bool, str]:
    """
    Validate and sanitize a name field (company name, user name)

    Args:
        name: Name to validate

    Returns:
        Tuple of (is_valid, sanitized_name or error_message)
    """
    if not name:
        return False, "Name cannot be empty"

    sanitized = sanitize_string(name, max_length=100)

    if len(sanitized) < 1:
        return False, "Name is too short"

    if len(sanitized) > 100:
        return False, "Name is too long (max 100 characters)"

    return True, sanitized


def validate_description(description: str) -> tuple[bool, str]:
    """
    Validate and sanitize a description field

    Args:
        description: Description to validate

    Returns:
        Tuple of (is_valid, sanitized_description)
    """
    sanitized = sanitize_string(description, max_length=500)
    return True, sanitized


def validate_date_input(date_str: str) -> tuple[bool, str]:
    """
    Validate a date string in DD-MM-YYYY format

    Args:
        date_str: Date string to validate

    Returns:
        Tuple of (is_valid, error_message or empty string)
    """
    if not date_str:
        return False, "Date is required"

    import re
    # Check format DD-MM-YYYY
    if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
        return False, "Date must be in DD-MM-YYYY format"

    try:
        day, month, year = map(int, date_str.split('-'))
        datetime(year, month, day)
        return True, ""
    except ValueError:
        return False, "Invalid date"


def validate_email(email: str) -> bool:
    """
    Simple email validation

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    if not email:
        return True  # Email is optional
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


# ==================== PDF Export Functions ====================

def export_to_pdf(data: List[Dict], filename: str, title: str, fieldnames: List[str] = None):
    """
    Export data to PDF file with professional formatting

    Args:
        data: List of dictionaries containing data to export
        filename: Path to save the PDF file
        title: Title of the report
        fieldnames: List of field names to include (if None, use all from first row)
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from datetime import datetime

    # Determine if this is a transaction report (needs landscape)
    is_transaction = fieldnames and 'transaction_date' in fieldnames

    # Create PDF document - use landscape for transactions
    if is_transaction:
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm)
    else:
        doc = SimpleDocTemplate(filename, pagesize=A4)

    elements = []

    # Styles
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Add title
    elements.append(Paragraph(title, title_style))

    # Add generation date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_RIGHT,
        spaceAfter=15
    )
    generation_date = f"Generated on: {datetime.now().strftime('%d %B, %Y at %H:%M')}"
    elements.append(Paragraph(generation_date, date_style))
    elements.append(Spacer(1, 0.1 * inch))

    if not data:
        # No data message
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("No data available", no_data_style))
    else:
        # Determine fieldnames
        if not fieldnames:
            fieldnames = list(data[0].keys())

        # Create table data
        table_data = []

        # Header row with better names
        header_names = {
            'id': 'ID',
            'transaction_date': 'Date',
            'amount': 'Amount',
            'from_name': 'From',
            'to_name': 'To',
            'description': 'Description',
            'name': 'Name',
            'address': 'Address',
            'phone': 'Phone',
            'email': 'Email',
            'balance': 'Balance',
            'role': 'Role',
            'department': 'Department'
        }
        header_row = [header_names.get(field, field.replace('_', ' ').title()) for field in fieldnames]
        table_data.append(header_row)

        # Data rows
        for row in data:
            table_row = []
            for field in fieldnames:
                value = row.get(field, '')

                # Format currency fields
                if field in ['balance', 'amount'] and value != '':
                    try:
                        value = format_currency(float(value))
                    except:
                        pass

                # Truncate long descriptions
                if field == 'description' and len(str(value)) > 30:
                    value = str(value)[:27] + '...'

                # Truncate long addresses
                if field == 'address' and len(str(value)) > 25:
                    value = str(value)[:22] + '...'

                table_row.append(str(value) if value else '-')
            table_data.append(table_row)

        # Define column widths based on report type
        if is_transaction:
            # Transaction report: ID, Date, Amount, From, To, Description
            col_widths = [0.8*cm, 2.2*cm, 2.5*cm, 5*cm, 5*cm, 6*cm]
        elif fieldnames and 'address' in fieldnames:
            # Company report: ID, Name, Address, Phone, Email, Balance
            col_widths = [1*cm, 4*cm, 4*cm, 2.5*cm, 4*cm, 2.5*cm]
        elif fieldnames and 'department' in fieldnames:
            # User report: ID, Name, Email, Role, Department, Balance
            col_widths = [1*cm, 3.5*cm, 4.5*cm, 2.5*cm, 3*cm, 2.5*cm]
        else:
            col_widths = None

        # Create table with fixed widths
        if col_widths:
            table = Table(table_data, colWidths=col_widths)
        else:
            table = Table(table_data)

        # Table styling
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Center align ID column
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),

            # Right align amount/balance columns
            ('ALIGN', (2, 1), (2, -1), 'RIGHT') if is_transaction else ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Word wrap for long text
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)

        # Add footer with count
        elements.append(Spacer(1, 0.2 * inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f"Total Records: {len(data)}", footer_style))

    # Build PDF
    doc.build(elements)

    return filename
