"""
Ledger Window - Shows complete transaction history for an account
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, format_date


class LedgerWindow(ctk.CTkToplevel):
    """Window displaying ledger (transaction history) for a specific account"""

    def __init__(self, parent, db: DatabaseManager, entity_type: str, entity_id: int, entity_name: str):
        """
        Initialize ledger window

        Args:
            parent: Parent window
            db: Database manager instance
            entity_type: 'company' or 'user'
            entity_id: ID of the entity
            entity_name: Name of the entity for display
        """
        super().__init__(parent)

        self.db = db
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name

        # Window setup
        self.title(f"Ledger - {entity_name}")
        self.geometry("1000x700")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Create UI
        self.create_header()
        self.create_ledger_table()
        self.load_ledger_data()

        # Center window
        self.center_window()

    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_header(self):
        """Create header section"""
        header_frame = ctk.CTkFrame(self, corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📒 Account Ledger",
            font=("Roboto", 24, "bold")
        )
        title_label.pack(pady=(20, 5))

        # Account name
        account_label = ctk.CTkLabel(
            header_frame,
            text=self.entity_name,
            font=("Roboto", 18)
        )
        account_label.pack(pady=(0, 5))

        # Account type
        type_label = ctk.CTkLabel(
            header_frame,
            text=f"Type: {self.entity_type.capitalize()}",
            font=("Roboto", 14),
            text_color="gray"
        )
        type_label.pack(pady=(0, 10))

        # Current balance
        if self.entity_type == 'company':
            entity = self.db.get_company(self.entity_id)
        else:
            entity = self.db.get_user(self.entity_id)

        balance_label = ctk.CTkLabel(
            header_frame,
            text=f"Current Balance: {format_currency(entity['balance'])}",
            font=("Roboto", 16, "bold"),
            text_color="#2ecc71" if entity['balance'] >= 0 else "#e74c3c"
        )
        balance_label.pack(pady=(5, 20))

    def create_ledger_table(self):
        """Create scrollable ledger table"""
        # Container frame
        table_container = ctk.CTkFrame(self, corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Table header
        header_frame = ctk.CTkFrame(table_container, fg_color=("gray85", "gray20"))
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        headers = [
            ("Date", 120),
            ("Type", 80),
            ("Description", 250),
            ("Other Party", 180),
            ("Amount", 130),
            ("Balance", 130)
        ]

        for header_text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=("Roboto", 13, "bold"),
                width=width
            )
            label.pack(side="left", padx=5, pady=10)

        # Scrollable frame for transactions
        self.scroll_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def load_ledger_data(self):
        """Load and display ledger entries"""
        # Clear existing entries
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Get ledger entries
        try:
            ledger_entries = self.db.get_account_ledger(self.entity_type, self.entity_id)

            if not ledger_entries:
                # No transactions
                no_data_label = ctk.CTkLabel(
                    self.scroll_frame,
                    text="No transactions found for this account",
                    font=("Roboto", 14),
                    text_color="gray"
                )
                no_data_label.pack(pady=50)
                return

            # Display each entry
            for entry in ledger_entries:
                self.create_ledger_row(entry)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ledger: {str(e)}")

    def create_ledger_row(self, entry: Dict[str, Any]):
        """Create a single ledger row"""
        # Row frame
        row_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=8,
            fg_color=("gray90", "gray25"),
            cursor="hand2"
        )
        row_frame.pack(fill="x", pady=2)

        # Make row clickable
        row_frame.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Date
        date_label = ctk.CTkLabel(
            row_frame,
            text=format_date(entry['date']),
            font=("Roboto", 12),
            width=120
        )
        date_label.pack(side="left", padx=5, pady=8)
        date_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Type (Credit/Debit)
        type_color = "#27ae60" if entry['type'] == 'Credit' else "#e74c3c"
        type_label = ctk.CTkLabel(
            row_frame,
            text=entry['type'],
            font=("Roboto", 12, "bold"),
            text_color=type_color,
            width=80
        )
        type_label.pack(side="left", padx=5, pady=8)
        type_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Description
        desc_text = entry['description'][:35] + "..." if len(entry['description']) > 35 else entry['description']
        desc_label = ctk.CTkLabel(
            row_frame,
            text=desc_text or "(No description)",
            font=("Roboto", 12),
            width=250,
            anchor="w"
        )
        desc_label.pack(side="left", padx=5, pady=8)
        desc_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Other party
        other_party_label = ctk.CTkLabel(
            row_frame,
            text=entry['other_party'],
            font=("Roboto", 12),
            width=180,
            anchor="w"
        )
        other_party_label.pack(side="left", padx=5, pady=8)
        other_party_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Amount
        amount_label = ctk.CTkLabel(
            row_frame,
            text=format_currency(entry['amount']),
            font=("Roboto", 12, "bold"),
            text_color=type_color,
            width=130
        )
        amount_label.pack(side="left", padx=5, pady=8)
        amount_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Running balance
        balance_color = "#2ecc71" if entry['running_balance'] >= 0 else "#e74c3c"
        balance_label = ctk.CTkLabel(
            row_frame,
            text=format_currency(entry['running_balance']),
            font=("Roboto", 12, "bold"),
            text_color=balance_color,
            width=130
        )
        balance_label.pack(side="left", padx=5, pady=8)
        balance_label.bind("<Button-1>", lambda e: self.show_transaction_details(entry))

        # Hover effect
        def on_enter(e):
            row_frame.configure(fg_color=("gray85", "gray30"))

        def on_leave(e):
            row_frame.configure(fg_color=("gray90", "gray25"))

        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)

    def show_transaction_details(self, entry: Dict[str, Any]):
        """Show detailed transaction information in a dialog"""
        # Create detail dialog
        detail_dialog = ctk.CTkToplevel(self)
        detail_dialog.title("Transaction Details")
        detail_dialog.geometry("600x500")
        detail_dialog.transient(self)
        detail_dialog.grab_set()

        # Center dialog
        detail_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 300
        y = self.winfo_y() + (self.winfo_height() // 2) - 250
        detail_dialog.geometry(f"600x500+{x}+{y}")

        # Content frame
        content_frame = ctk.CTkFrame(detail_dialog, corner_radius=10)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="📄 Transaction Details",
            font=("Roboto", 20, "bold")
        )
        title_label.pack(pady=(20, 30))

        # Details
        details = [
            ("Transaction ID", f"#{entry['id']}"),
            ("Date", format_date(entry['date'])),
            ("Type", entry['type']),
            ("From", entry['from_name'] if entry['from_type'] != 'cash' else 'Cash Deposit'),
            ("To", entry['to_name'] if entry['to_type'] != 'cash' else 'Cash Withdrawal'),
            ("Amount", format_currency(entry['amount'])),
            ("Balance After", format_currency(entry['running_balance'])),
            ("Description", entry['description'] or "(No description)"),
            ("Reference", entry['reference'] or "(None)"),
        ]

        for label_text, value_text in details:
            detail_row = ctk.CTkFrame(content_frame, fg_color="transparent")
            detail_row.pack(fill="x", padx=20, pady=5)

            label = ctk.CTkLabel(
                detail_row,
                text=f"{label_text}:",
                font=("Roboto", 13, "bold"),
                width=150,
                anchor="w"
            )
            label.pack(side="left")

            value = ctk.CTkLabel(
                detail_row,
                text=str(value_text),
                font=("Roboto", 13),
                anchor="w"
            )
            value.pack(side="left", padx=10)

        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="Close",
            command=detail_dialog.destroy,
            height=40,
            font=("Roboto", 14)
        )
        close_btn.pack(pady=(30, 20))
