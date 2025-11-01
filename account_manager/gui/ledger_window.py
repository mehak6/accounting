"""
Ledger Window - Shows complete transaction history for an account with grouping
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any, List
from collections import defaultdict

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
        self.view_mode = "grouped"  # "grouped" or "chronological"
        self.expanded_groups = set()  # Track which groups are expanded

        # Window setup
        self.title(f"Ledger - {entity_name}")

        # Set window size based on screen size (max 90% of screen)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1000, int(screen_width * 0.9))
        window_height = min(700, int(screen_height * 0.85))
        self.geometry(f"{window_width}x{window_height}")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Create UI
        self.create_header()
        self.create_view_toggle()
        self.create_ledger_table()
        self.create_footer()
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

    def create_view_toggle(self):
        """Create view mode toggle"""
        toggle_frame = ctk.CTkFrame(self, corner_radius=10)
        toggle_frame.pack(fill="x", padx=20, pady=(0, 10))

        label = ctk.CTkLabel(
            toggle_frame,
            text="View Mode:",
            font=("Roboto", 14, "bold")
        )
        label.pack(side="left", padx=20, pady=15)

        # Grouped view button
        self.grouped_btn = ctk.CTkButton(
            toggle_frame,
            text="📊 Grouped by Party",
            command=lambda: self.switch_view("grouped"),
            width=180,
            height=40,
            font=("Roboto", 13, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.grouped_btn.pack(side="left", padx=5, pady=10)

        # Chronological view button
        self.chrono_btn = ctk.CTkButton(
            toggle_frame,
            text="📅 Chronological",
            command=lambda: self.switch_view("chronological"),
            width=180,
            height=40,
            font=("Roboto", 13, "bold"),
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.chrono_btn.pack(side="left", padx=5, pady=10)

    def switch_view(self, mode: str):
        """Switch between grouped and chronological view"""
        self.view_mode = mode

        # Update button styles
        if mode == "grouped":
            self.grouped_btn.configure(fg_color="#3498db", hover_color="#2980b9")
            self.chrono_btn.configure(fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"))
        else:
            self.chrono_btn.configure(fg_color="#3498db", hover_color="#2980b9")
            self.grouped_btn.configure(fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"))

        # Reload data
        self.load_ledger_data()

    def create_ledger_table(self):
        """Create scrollable ledger table"""
        # Container frame
        self.table_container = ctk.CTkFrame(self, corner_radius=10)
        self.table_container.pack(fill="both", expand=True, padx=20, pady=(10, 10))

        # Scrollable frame for transactions
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_footer(self):
        """Create footer with close button"""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Close button
        close_btn = ctk.CTkButton(
            footer_frame,
            text="✖ Close",
            command=self.destroy,
            width=120,
            height=40,
            font=("Roboto", 14, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        close_btn.pack(pady=10)

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

            # Display based on view mode
            if self.view_mode == "grouped":
                self.display_grouped_view(ledger_entries)
            else:
                self.display_chronological_view(ledger_entries)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ledger: {str(e)}")

    def display_grouped_view(self, entries: List[Dict[str, Any]]):
        """Display transactions grouped by other party"""
        # Group transactions by other party
        groups = defaultdict(list)

        for entry in entries:
            # Determine the other party
            if entry['other_party_type'] == 'cash':
                party_key = ('cash', 0, 'Cash')
            else:
                party_key = (entry['other_party_type'], entry['other_party_id'], entry['other_party'])

            groups[party_key].append(entry)

        # Sort groups by total transaction count (descending)
        sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

        # Display each group
        for (party_type, party_id, party_name), group_entries in sorted_groups:
            self.create_group_section(party_type, party_id, party_name, group_entries)

    def create_group_section(self, party_type: str, party_id: int, party_name: str, entries: List[Dict[str, Any]]):
        """Create a collapsible section for a group of transactions"""
        group_key = (party_type, party_id, party_name)

        # Calculate statistics
        total_transactions = len(entries)
        total_credit = sum(e['amount'] for e in entries if e['type'] == 'Credit')
        total_debit = sum(e['amount'] for e in entries if e['type'] == 'Debit')
        net_amount = total_credit - total_debit

        # Group header frame
        header_frame = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=10,
            fg_color=("gray85", "gray20"),
            cursor="hand2"
        )
        header_frame.pack(fill="x", pady=(10, 2))

        # Make header clickable to toggle
        header_frame.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Expand/collapse icon
        is_expanded = group_key in self.expanded_groups
        icon = "▼" if is_expanded else "▶"
        icon_label = ctk.CTkLabel(
            header_frame,
            text=icon,
            font=("Roboto", 16, "bold"),
            width=30
        )
        icon_label.pack(side="left", padx=10, pady=15)
        icon_label.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Party info section
        info_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_section.pack(side="left", fill="x", expand=True, padx=10)
        info_section.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Party name
        party_label = ctk.CTkLabel(
            info_section,
            text=f"{party_name}",
            font=("Roboto", 15, "bold"),
            anchor="w"
        )
        party_label.pack(anchor="w")
        party_label.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Party type
        type_text = party_type.capitalize() if party_type != 'cash' else 'Cash Transactions'
        type_label = ctk.CTkLabel(
            info_section,
            text=type_text,
            font=("Roboto", 11),
            text_color="gray",
            anchor="w"
        )
        type_label.pack(anchor="w")
        type_label.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Statistics section
        stats_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_section.pack(side="right", padx=10)
        stats_section.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Total transactions
        trans_label = ctk.CTkLabel(
            stats_section,
            text=f"📝 {total_transactions} transaction{'s' if total_transactions != 1 else ''}",
            font=("Roboto", 11),
            text_color="gray"
        )
        trans_label.pack(side="left", padx=15)
        trans_label.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Net amount
        net_color = "#2ecc71" if net_amount >= 0 else "#e74c3c"
        net_label = ctk.CTkLabel(
            stats_section,
            text=f"Net: {format_currency(abs(net_amount))} {'↑' if net_amount >= 0 else '↓'}",
            font=("Roboto", 12, "bold"),
            text_color=net_color
        )
        net_label.pack(side="left", padx=15)
        net_label.bind("<Button-1>", lambda e: self.toggle_group(group_key))

        # Details frame (shown/hidden based on expanded state)
        if is_expanded:
            details_frame = ctk.CTkFrame(
                self.scroll_frame,
                corner_radius=10,
                fg_color=("gray90", "gray25")
            )
            details_frame.pack(fill="x", pady=(0, 5))

            # Summary row
            summary_frame = ctk.CTkFrame(details_frame, fg_color=("gray85", "gray20"))
            summary_frame.pack(fill="x", padx=10, pady=10)

            summary_text = f"💰 Total Credit: {format_currency(total_credit)}  |  💸 Total Debit: {format_currency(total_debit)}"
            summary_label = ctk.CTkLabel(
                summary_frame,
                text=summary_text,
                font=("Roboto", 12, "bold")
            )
            summary_label.pack(pady=10)

            # Transaction rows
            for entry in entries:
                self.create_ledger_row(details_frame, entry)

    def toggle_group(self, group_key):
        """Toggle group expansion"""
        if group_key in self.expanded_groups:
            self.expanded_groups.remove(group_key)
        else:
            self.expanded_groups.add(group_key)

        # Reload to update display
        self.load_ledger_data()

    def display_chronological_view(self, entries: List[Dict[str, Any]]):
        """Display transactions in chronological order"""
        # Table header
        header_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray85", "gray20"))
        header_frame.pack(fill="x", pady=(0, 10))

        headers = [
            ("Date", 120),
            ("Type", 80),
            ("Description", 250),
            ("Other Party", 200),
            ("Amount", 140),
            ("Balance", 140)
        ]

        for header_text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=("Roboto", 13, "bold"),
                width=width
            )
            label.pack(side="left", padx=5, pady=10)

        # Display each entry
        for entry in entries:
            self.create_ledger_row(self.scroll_frame, entry)

    def create_ledger_row(self, parent, entry: Dict[str, Any]):
        """Create a single ledger row"""
        # Row frame
        row_frame = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=("gray90", "gray25"),
            cursor="hand2"
        )
        row_frame.pack(fill="x", pady=2, padx=10)

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
            width=200,
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
            width=140
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
            width=140
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
        detail_dialog.geometry("650x550")
        detail_dialog.transient(self)
        detail_dialog.grab_set()

        # Center dialog
        detail_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 325
        y = self.winfo_y() + (self.winfo_height() // 2) - 275
        detail_dialog.geometry(f"650x550+{x}+{y}")

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
            ("From Type", entry['from_type'].capitalize()),
            ("To", entry['to_name'] if entry['to_type'] != 'cash' else 'Cash Withdrawal'),
            ("To Type", entry['to_type'].capitalize()),
            ("Other Party", entry['other_party']),
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
