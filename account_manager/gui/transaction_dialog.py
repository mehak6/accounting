"""
Transaction Dialog - View and manage all transactions
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, format_date


class TransactionDialog:
    """Dialog for viewing and managing transactions"""

    def __init__(self, parent, db: DatabaseManager):
        """
        Initialize transaction dialog

        Args:
            parent: Parent window
            db: Database manager instance
        """
        self.parent = parent
        self.db = db
        self.selected_transaction_id = None

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Transaction Management")
        self.dialog.geometry("1000x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create UI
        self.create_ui()
        self.load_transactions()

    def create_ui(self):
        """Create dialog UI"""
        # Main container
        main_container = ctk.CTkFrame(self.dialog)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Top: Search and filter bar
        self.create_toolbar(main_container)

        # Action buttons row (UPDATE and DELETE) - Separate row for maximum visibility
        self.create_action_buttons(main_container)

        # Middle: Transaction list
        list_frame = ctk.CTkFrame(main_container, corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=(10, 10))

        self.create_transaction_list(list_frame)

        # Bottom: Transaction details
        details_frame = ctk.CTkFrame(main_container, corner_radius=10)
        details_frame.pack(fill="x", pady=(0, 0))

        self.create_transaction_details(details_frame)

    def create_toolbar(self, parent):
        """Create toolbar with search and actions"""
        toolbar = ctk.CTkFrame(parent, corner_radius=10, height=60)
        toolbar.pack(fill="x", pady=(0, 10))

        # Title
        title = ctk.CTkLabel(
            toolbar,
            text="All Transactions",
            font=("Roboto", 20, "bold")
        )
        title.pack(side="left", padx=15)

        # Search entry
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search transactions...",
            width=250,
            height=35
        )
        self.search_entry.pack(side="left", padx=10)

        # Search button
        search_btn = ctk.CTkButton(
            toolbar,
            text="🔍 Search",
            width=100,
            height=35,
            command=self.search_transactions
        )
        search_btn.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.load_transactions
        )
        refresh_btn.pack(side="left", padx=5)

    def create_action_buttons(self, parent):
        """Create action buttons row (UPDATE and DELETE) in a separate prominent row"""
        # Action buttons frame - separate row for maximum visibility
        action_frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#2b2b2b")
        action_frame.pack(fill="x", pady=(10, 0))

        # Configure grid columns
        action_frame.grid_columnconfigure(0, weight=1)  # Info label takes remaining space
        action_frame.grid_columnconfigure(1, weight=0)  # Update button fixed
        action_frame.grid_columnconfigure(2, weight=0)  # Delete button fixed

        # Info label
        info_label = ctk.CTkLabel(
            action_frame,
            text="📋 Select a transaction below to UPDATE or DELETE it:",
            font=("Roboto", 14, "bold"),
            text_color="#3498db"
        )
        info_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Update button - Very prominent (GRID column 1)
        self.update_btn = ctk.CTkButton(
            action_frame,
            text="✎ UPDATE",
            width=180,
            height=50,
            font=("Roboto", 16, "bold"),
            corner_radius=12,
            fg_color="#f39c12",
            hover_color="#d68910",
            border_width=3,
            border_color="#b87a0a",
            command=self.update_transaction,
            state="disabled"
        )
        self.update_btn.grid(row=0, column=1, padx=10, pady=15)

        # Delete button - Very prominent (GRID column 2)
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ DELETE",
            width=180,
            height=50,
            font=("Roboto", 16, "bold"),
            corner_radius=12,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            border_width=3,
            border_color="#922b21",
            command=self.delete_transaction,
            state="disabled"
        )
        self.delete_btn.grid(row=0, column=2, padx=10, pady=15)

    def create_transaction_list(self, parent):
        """Create scrollable transaction list"""
        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Transaction History",
            font=("Roboto", 18, "bold")
        ).pack(side="left")

        # Count label
        self.count_label = ctk.CTkLabel(
            header,
            text="0 transactions",
            font=("Roboto", 12),
            text_color="gray"
        )
        self.count_label.pack(side="right")

        # Scrollable list
        self.trans_list = ctk.CTkScrollableFrame(
            parent,
            corner_radius=8
        )
        self.trans_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_transaction_details(self, parent):
        """Create transaction details panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Transaction Details",
            font=("Roboto", 16, "bold")
        )
        title.pack(pady=(15, 10))

        # Details container
        details_container = ctk.CTkFrame(parent, fg_color="transparent")
        details_container.pack(fill="x", padx=15, pady=(0, 15))

        # Left column
        left_col = ctk.CTkFrame(details_container, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # ID
        self.detail_id = self.create_detail_row(left_col, "ID:")

        # Date
        self.detail_date = self.create_detail_row(left_col, "Date:")

        # Amount
        self.detail_amount = self.create_detail_row(left_col, "Amount:")

        # Right column
        right_col = ctk.CTkFrame(details_container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # From
        self.detail_from = self.create_detail_row(right_col, "From:")

        # To
        self.detail_to = self.create_detail_row(right_col, "To:")

        # Type
        self.detail_type = self.create_detail_row(right_col, "Type:")

        # Full width for description and reference
        self.detail_desc = self.create_detail_row(parent, "Description:", padx=15)
        self.detail_ref = self.create_detail_row(parent, "Reference:", padx=15)

    def create_detail_row(self, parent, label_text: str, padx: int = 0) -> ctk.CTkLabel:
        """Create a detail row with label and value"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5, padx=padx)

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Roboto", 12),
            width=100,
            anchor="w"
        ).pack(side="left")

        value_label = ctk.CTkLabel(
            frame,
            text="--",
            font=("Roboto", 12, "bold"),
            anchor="w"
        )
        value_label.pack(side="left", fill="x", expand=True)

        return value_label

    def load_transactions(self):
        """Load and display all transactions"""
        # Clear existing list
        for widget in self.trans_list.winfo_children():
            widget.destroy()

        # Get transactions
        transactions = self.db.get_all_transactions()

        # Update count
        self.count_label.configure(text=f"{len(transactions)} transactions")

        if not transactions:
            no_data = ctk.CTkLabel(
                self.trans_list,
                text="No transactions yet",
                font=("Roboto", 14),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display each transaction
        for trans in transactions:
            self.create_transaction_card(trans)

    def create_transaction_card(self, trans: Dict[str, Any]):
        """Create a transaction display card"""
        card = ctk.CTkFrame(self.trans_list, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        # Make card clickable
        card.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        # Card content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=12)
        content.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        # Top row: Date and ID
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")
        top_row.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        date_text = format_date(trans['transaction_date'], "%d-%m-%Y", "%d %b, %Y")
        date_label = ctk.CTkLabel(
            top_row,
            text=date_text,
            font=("Roboto", 11),
            text_color="gray",
            anchor="w"
        )
        date_label.pack(side="left")
        date_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        id_label = ctk.CTkLabel(
            top_row,
            text=f"ID: {trans['id']}",
            font=("Roboto", 10),
            text_color="gray",
            anchor="e"
        )
        id_label.pack(side="right")
        id_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        # Middle row: From -> To
        from_to_text = f"{trans['from_name']} → {trans['to_name']}"
        from_to_label = ctk.CTkLabel(
            content,
            text=from_to_text,
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        from_to_label.pack(anchor="w", pady=(5, 0))
        from_to_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        # Bottom row: Amount and description
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(5, 0))
        bottom_row.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        amount_label = ctk.CTkLabel(
            bottom_row,
            text=format_currency(trans['amount']),
            font=("Roboto", 16, "bold"),
            text_color="green",
            anchor="w"
        )
        amount_label.pack(side="left")
        amount_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

        if trans.get('description'):
            desc_label = ctk.CTkLabel(
                bottom_row,
                text=f"📝 {trans['description'][:40]}...",
                font=("Roboto", 11),
                text_color="gray",
                anchor="e"
            )
            desc_label.pack(side="right")
            desc_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

    def select_transaction(self, trans: Dict[str, Any]):
        """Select a transaction to view details"""
        self.selected_transaction_id = trans['id']

        # Populate details
        self.detail_id.configure(text=str(trans['id']))

        date_text = format_date(trans['transaction_date'], "%d-%m-%Y", "%d %B, %Y")
        self.detail_date.configure(text=date_text)

        self.detail_amount.configure(
            text=format_currency(trans['amount']),
            text_color="green"
        )

        from_text = f"{trans['from_name']} ({trans['from_type'].capitalize()})"
        self.detail_from.configure(text=from_text)

        to_text = f"{trans['to_name']} ({trans['to_type'].capitalize()})"
        self.detail_to.configure(text=to_text)

        type_text = f"{trans['from_type'].capitalize()} to {trans['to_type'].capitalize()}"
        self.detail_type.configure(text=type_text)

        self.detail_desc.configure(text=trans.get('description', '--'))
        self.detail_ref.configure(text=trans.get('reference', '--'))

        # Enable update and delete buttons
        self.update_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")

    def search_transactions(self):
        """Search transactions by keyword"""
        search_term = self.search_entry.get().strip()

        if not search_term:
            self.load_transactions()
            return

        # Clear existing list
        for widget in self.trans_list.winfo_children():
            widget.destroy()

        # Search
        transactions = self.db.search_transactions(search_term)

        # Update count
        self.count_label.configure(text=f"{len(transactions)} results")

        if not transactions:
            no_data = ctk.CTkLabel(
                self.trans_list,
                text=f"No results for '{search_term}'",
                font=("Roboto", 14),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display results
        for trans in transactions:
            self.create_transaction_card(trans)

    def delete_transaction(self):
        """Delete selected transaction"""
        if not self.selected_transaction_id:
            messagebox.showerror("Error", "No transaction selected")
            return

        trans = self.db.get_transaction(self.selected_transaction_id)
        if not trans:
            messagebox.showerror("Error", "Transaction not found")
            return

        # Confirm deletion
        confirm_msg = (
            f"Delete this transaction?\n\n"
            f"ID: {trans['id']}\n"
            f"From: {trans['from_name']}\n"
            f"To: {trans['to_name']}\n"
            f"Amount: {format_currency(trans['amount'])}\n\n"
            f"WARNING: This will reverse the balance changes!\n"
            f"This action cannot be undone!"
        )

        if not messagebox.askyesno("Confirm Deletion", confirm_msg):
            return

        # Delete from database
        try:
            self.db.delete_transaction(self.selected_transaction_id)
            messagebox.showinfo("Success", "Transaction deleted successfully!")

            # Clear selection
            self.selected_transaction_id = None
            self.update_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")

            # Refresh list
            self.load_transactions()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")

    def update_transaction(self):
        """Open dialog to update selected transaction"""
        if not self.selected_transaction_id:
            messagebox.showerror("Error", "No transaction selected")
            return

        trans = self.db.get_transaction(self.selected_transaction_id)
        if not trans:
            messagebox.showerror("Error", "Transaction not found")
            return

        # Create update dialog
        update_dialog = ctk.CTkToplevel(self.dialog)
        update_dialog.title("Update Transaction")
        update_dialog.geometry("600x700")
        update_dialog.transient(self.dialog)
        update_dialog.grab_set()

        # Main container
        main_frame = ctk.CTkScrollableFrame(update_dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="✎ Update Transaction",
            font=("Roboto", 24, "bold")
        )
        title.pack(pady=(0, 20))

        # Transaction ID (read-only)
        id_label = ctk.CTkLabel(main_frame, text=f"Transaction ID: {trans['id']}", font=("Roboto", 12), text_color="gray")
        id_label.pack(anchor="w", pady=(0, 15))

        # Date field
        date_label = ctk.CTkLabel(main_frame, text="Date:", font=("Roboto", 13))
        date_label.pack(anchor="w", pady=(5, 3))

        date_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="DD-MM-YYYY",
            height=38,
            font=("Roboto", 13)
        )
        date_entry.insert(0, trans['transaction_date'])
        date_entry.pack(fill="x", pady=(0, 8))

        # Amount field
        amount_label = ctk.CTkLabel(main_frame, text="Amount (₹):", font=("Roboto", 13))
        amount_label.pack(anchor="w", pady=(5, 3))

        amount_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Enter amount",
            height=38,
            font=("Roboto", 13)
        )
        amount_entry.insert(0, str(trans['amount']))
        amount_entry.pack(fill="x", pady=(0, 8))

        # From dropdown
        from_label = ctk.CTkLabel(main_frame, text="From:", font=("Roboto", 13))
        from_label.pack(anchor="w", pady=(5, 3))

        # Get all entities
        all_entities = []
        for account in self.db.get_all_accounts():
            all_entities.append(f"{account['name']} (Account)")
        for customer in self.db.get_all_customers():
            all_entities.append(f"{customer['name']} (Customer)")
        all_entities.append("Cash (Cash)")

        from_var = ctk.StringVar(value=f"{trans['from_name']} ({trans['from_type'].capitalize()})")
        from_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=from_var,
            values=all_entities,
            height=38,
            font=("Roboto", 13),
            dropdown_font=("Roboto", 12)
        )
        from_dropdown.pack(fill="x", pady=(0, 8))

        # To dropdown
        to_label = ctk.CTkLabel(main_frame, text="To:", font=("Roboto", 13))
        to_label.pack(anchor="w", pady=(5, 3))

        to_var = ctk.StringVar(value=f"{trans['to_name']} ({trans['to_type'].capitalize()})")
        to_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=to_var,
            values=all_entities,
            height=38,
            font=("Roboto", 13),
            dropdown_font=("Roboto", 12)
        )
        to_dropdown.pack(fill="x", pady=(0, 8))

        # Description field
        desc_label = ctk.CTkLabel(main_frame, text="Description (Optional):", font=("Roboto", 13))
        desc_label.pack(anchor="w", pady=(5, 3))

        desc_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Transaction description",
            height=38,
            font=("Roboto", 13)
        )
        if trans.get('description'):
            desc_entry.insert(0, trans['description'])
        desc_entry.pack(fill="x", pady=(0, 8))

        # Reference field
        ref_label = ctk.CTkLabel(main_frame, text="Reference (Optional):", font=("Roboto", 13))
        ref_label.pack(anchor="w", pady=(5, 3))

        ref_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Reference number",
            height=38,
            font=("Roboto", 13)
        )
        if trans.get('reference'):
            ref_entry.insert(0, trans['reference'])
        ref_entry.pack(fill="x", pady=(0, 10))

        def save_updates():
            """Save the transaction updates"""
            # Get values
            date = date_entry.get().strip()
            amount = amount_entry.get().strip()
            from_entity = from_var.get()
            to_entity = to_var.get()
            description = desc_entry.get().strip()
            reference = ref_entry.get().strip()

            # Validate
            if not all([date, amount, from_entity, to_entity]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return

            if from_entity == to_entity:
                messagebox.showerror("Error", "From and To entities must be different")
                return

            try:
                amount = float(amount.replace(',', ''))
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return

            # Parse entity names and types
            def parse_entity(entity_str):
                if " (Account)" in entity_str:
                    return entity_str.replace(" (Account)", ""), "account"
                elif " (Customer)" in entity_str:
                    return entity_str.replace(" (Customer)", ""), "customer"
                else:
                    return "Cash", "cash"

            from_name, from_type = parse_entity(from_entity)
            to_name, to_type = parse_entity(to_entity)

            # Delete old transaction (this reverses the balances)
            try:
                self.db.delete_transaction(self.selected_transaction_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")
                return

            # Add new transaction with updated values
            try:
                self.db.add_transaction(
                    from_entity=from_name,
                    from_type=from_type,
                    to_entity=to_name,
                    to_type=to_type,
                    amount=amount,
                    transaction_date=date,
                    description=description if description else None,
                    reference=reference if reference else None
                )

                messagebox.showinfo("Success", "Transaction updated successfully!")
                update_dialog.destroy()

                # Clear selection and refresh
                self.selected_transaction_id = None
                self.update_btn.configure(state="disabled")
                self.delete_btn.configure(state="disabled")
                self.load_transactions()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")

        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(20, 0))

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ SAVE CHANGES",
            height=50,
            font=("Roboto", 16, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=save_updates
        )
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="✕ CANCEL",
            height=50,
            font=("Roboto", 16, "bold"),
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            command=update_dialog.destroy
        )
        cancel_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
