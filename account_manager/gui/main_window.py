"""
Main Window - Primary application interface
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, format_date, validate_amount, get_current_date


class MainWindow:
    """Main application window with modern CustomTkinter design"""

    def __init__(self, root: ctk.CTk, db: DatabaseManager):
        """
        Initialize main window

        Args:
            root: CTk root window
            db: Database manager instance
        """
        self.root = root
        self.db = db

        # Create main layout
        self.create_menu_bar()
        self.create_main_layout()
        self.load_data()

    def format_amount_input(self, event=None):
        """
        Format amount input in Indian numbering style (1,50,000) as user types
        """
        try:
            # Get current cursor position
            cursor_pos = self.amount_entry.index("insert")

            # Get current value
            current_value = self.amount_entry.get()

            # Remove all non-numeric characters except decimal point
            clean_value = ''.join(c for c in current_value if c.isdigit() or c == '.')

            if not clean_value or clean_value == '.':
                return

            # Split into integer and decimal parts
            if '.' in clean_value:
                parts = clean_value.split('.')
                integer_part = parts[0]
                decimal_part = parts[1] if len(parts) > 1 else ''
                # Limit decimal to 2 places
                decimal_part = decimal_part[:2]
            else:
                integer_part = clean_value
                decimal_part = ''

            # Format integer part in Indian style
            if integer_part:
                # Reverse the string for easier grouping
                reversed_num = integer_part[::-1]

                # First group of 3, then groups of 2
                groups = []
                groups.append(reversed_num[:3])  # First 3 digits
                remaining = reversed_num[3:]

                # Add groups of 2
                while remaining:
                    groups.append(remaining[:2])
                    remaining = remaining[2:]

                # Join groups with comma and reverse back
                formatted = ','.join(groups)
                formatted = formatted[::-1]
            else:
                formatted = '0'

            # Add decimal part if exists
            if decimal_part or '.' in current_value:
                formatted = f"{formatted}.{decimal_part}"

            # Calculate new cursor position
            # Count commas before old cursor position
            commas_before = current_value[:cursor_pos].count(',')
            # Count commas before same logical position in new string
            clean_cursor_pos = cursor_pos - commas_before

            # Update the entry
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, formatted)

            # Try to restore cursor position
            try:
                # Find the new position accounting for commas
                new_pos = 0
                char_count = 0
                for i, char in enumerate(formatted):
                    if char != ',':
                        char_count += 1
                    if char_count >= clean_cursor_pos:
                        new_pos = i + 1
                        break
                else:
                    new_pos = len(formatted)

                self.amount_entry.icursor(new_pos)
            except:
                pass

        except Exception as e:
            # If anything goes wrong, just continue without formatting
            pass

        return "break"  # Prevent default behavior

    def create_menu_bar(self):
        """Create menu bar"""
        # Create menu frame at top
        menu_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        menu_frame.pack(fill="x", padx=0, pady=0)

        # Menu buttons
        menu_items = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🏢 Companies", self.open_company_dialog),
            ("👤 Users", self.open_user_dialog),
            ("💸 Transactions", self.open_transaction_dialog),
            ("📊 Reports", self.open_reports_window),
            ("⚙️ Settings", self.show_settings),
        ]

        for text, command in menu_items:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                width=120,
                height=35,
                corner_radius=8,
                command=command,
                fg_color="transparent",
                hover_color=("gray75", "gray25")
            )
            btn.pack(side="left", padx=5, pady=2)

        # Theme toggle button on the right
        self.theme_btn = ctk.CTkButton(
            menu_frame,
            text="🌙 Dark",
            width=100,
            height=35,
            corner_radius=8,
            command=self.toggle_theme,
            fg_color="transparent",
            hover_color=("gray75", "gray25")
        )
        self.theme_btn.pack(side="right", padx=5, pady=2)

    def create_main_layout(self):
        """Create main application layout"""
        # Main container
        main_container = ctk.CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create three-column layout
        # Left column: Quick transaction entry (40%)
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Right column: Balance overview and recent transactions (60%)
        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Build left column: Transaction entry and Deposit/Withdraw
        self.create_transaction_entry_panel(left_frame)
        self.create_deposit_withdraw_panel(left_frame)

        # Build right column: Split into top (balances) and bottom (recent transactions)
        self.create_balance_panel(right_frame)
        self.create_recent_transactions_panel(right_frame)

    def create_transaction_entry_panel(self, parent):
        """Create quick transaction entry panel"""
        # Title - Made more compact
        title = ctk.CTkLabel(
            parent,
            text="Quick Transaction Entry",
            font=("Roboto", 18, "bold")
        )
        title.pack(pady=(10, 5))

        # Form container
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=5)

        # Date field
        date_label = ctk.CTkLabel(form_frame, text="Date:", font=("Roboto", 12))
        date_label.pack(anchor="w", pady=(5, 2))

        self.date_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="YYYY-MM-DD",
            height=35,
            font=("Roboto", 12)
        )
        self.date_entry.pack(fill="x", pady=(0, 8))
        self.date_entry.insert(0, get_current_date())

        # Amount field
        amount_label = ctk.CTkLabel(form_frame, text="Amount:", font=("Roboto", 12))
        amount_label.pack(anchor="w", pady=(5, 2))

        self.amount_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            height=35,
            font=("Roboto", 12)
        )
        self.amount_entry.pack(fill="x", pady=(0, 8))
        
        # Bind event to format amount as user types (Indian numbering: 1,50,000)
        self.amount_entry.bind("<KeyRelease>", self.format_amount_input)

        # From selection
        from_label = ctk.CTkLabel(form_frame, text="From:", font=("Roboto", 12))
        from_label.pack(anchor="w", pady=(5, 2))

        # Create native dropdown for From selection
        self.from_var = ctk.StringVar(value="Select...")
        self.from_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.from_var,
            values=["Select..."],
            height=35,
            font=("Roboto", 12),
            dropdown_font=("Roboto", 11),
            corner_radius=8
        )
        self.from_dropdown.pack(fill="x", pady=(0, 8))

        # To selection
        to_label = ctk.CTkLabel(form_frame, text="To:", font=("Roboto", 12))
        to_label.pack(anchor="w", pady=(5, 2))

        # Create native dropdown for To selection
        self.to_var = ctk.StringVar(value="Select...")
        self.to_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.to_var,
            values=["Select..."],
            height=35,
            font=("Roboto", 12),
            dropdown_font=("Roboto", 11),
            corner_radius=8
        )
        self.to_dropdown.pack(fill="x", pady=(0, 8))

        # Description field
        desc_label = ctk.CTkLabel(form_frame, text="Description (Optional):", font=("Roboto", 12))
        desc_label.pack(anchor="w", pady=(5, 2))

        self.desc_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Transaction description",
            height=35,
            font=("Roboto", 12)
        )
        self.desc_entry.pack(fill="x", pady=(0, 8))

        # Reference field
        ref_label = ctk.CTkLabel(form_frame, text="Reference (Optional):", font=("Roboto", 12))
        ref_label.pack(anchor="w", pady=(5, 2))

        self.ref_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Reference number",
            height=35,
            font=("Roboto", 12)
        )
        self.ref_entry.pack(fill="x", pady=(0, 10))

        # Submit button - Made more prominent and compact
        submit_btn = ctk.CTkButton(
            form_frame,
            text="✓ Submit Transaction",
            height=42,
            font=("Roboto", 14, "bold"),
            corner_radius=8,
            command=self.submit_transaction,
            fg_color="#1f77b4",
            hover_color="#1557a0"
        )
        submit_btn.pack(fill="x", pady=(10, 5))

        # Clear button - Improved styling and compact
        clear_btn = ctk.CTkButton(
            form_frame,
            text="⟲ Clear Form",
            height=36,
            font=("Roboto", 12, "bold"),
            corner_radius=8,
            fg_color="#666666",
            hover_color="#555555",
            command=self.clear_form
        )
        clear_btn.pack(fill="x", pady=(0, 10))

    def create_deposit_withdraw_panel(self, parent):
        """Create deposit/withdraw panel for cash in/out operations"""
        # Main frame - More compact
        dw_frame = ctk.CTkFrame(parent, corner_radius=10)
        dw_frame.pack(fill="x", padx=15, pady=(10, 10))

        # Title - More compact
        title = ctk.CTkLabel(
            dw_frame,
            text="💰 Cash Deposit / Withdraw",
            font=("Roboto", 14, "bold")
        )
        title.pack(pady=(10, 5))

        # Form frame
        form_frame = ctk.CTkFrame(dw_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=15, pady=(0, 10))

        # Operation type (Deposit or Withdraw) - More compact
        op_label = ctk.CTkLabel(form_frame, text="Operation:", font=("Roboto", 12))
        op_label.pack(anchor="w", pady=(0, 3))

        self.operation_var = ctk.StringVar(value="deposit")

        op_radio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        op_radio_frame.pack(fill="x", pady=(0, 8))

        deposit_radio = ctk.CTkRadioButton(
            op_radio_frame,
            text="💵 Deposit",
            variable=self.operation_var,
            value="deposit",
            font=("Roboto", 11)
        )
        deposit_radio.pack(side="left", padx=(0, 15))

        withdraw_radio = ctk.CTkRadioButton(
            op_radio_frame,
            text="💸 Withdraw",
            variable=self.operation_var,
            value="withdraw",
            font=("Roboto", 11)
        )
        withdraw_radio.pack(side="left")

        # Entity selection - More compact
        entity_label = ctk.CTkLabel(form_frame, text="Account:", font=("Roboto", 12))
        entity_label.pack(anchor="w", pady=(5, 2))

        # Create native dropdown for entity selection
        self.dw_entity_var = ctk.StringVar(value="Select...")
        self.dw_entity_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.dw_entity_var,
            values=["Select..."],
            height=35,
            font=("Roboto", 12),
            dropdown_font=("Roboto", 11),
            corner_radius=8
        )
        self.dw_entity_dropdown.pack(fill="x", pady=(0, 8))

        # Amount field - More compact
        amount_label = ctk.CTkLabel(form_frame, text="Amount:", font=("Roboto", 12))
        amount_label.pack(anchor="w", pady=(5, 2))

        self.dw_amount_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            height=35,
            font=("Roboto", 12)
        )
        self.dw_amount_entry.pack(fill="x", pady=(0, 8))

        # Bind formatting event
        self.dw_amount_entry.bind("<KeyRelease>", self.format_dw_amount_input)

        # Description field - More compact
        desc_label = ctk.CTkLabel(form_frame, text="Description (Optional):", font=("Roboto", 12))
        desc_label.pack(anchor="w", pady=(5, 2))

        self.dw_desc_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Purpose of deposit/withdrawal",
            height=35,
            font=("Roboto", 12)
        )
        self.dw_desc_entry.pack(fill="x", pady=(0, 8))

        # Submit button - Compact and prominent
        submit_btn = ctk.CTkButton(
            form_frame,
            text="✓ Submit",
            height=42,
            font=("Roboto", 14, "bold"),
            corner_radius=8,
            command=self.submit_deposit_withdraw,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        submit_btn.pack(fill="x", pady=(10, 10))

    def format_dw_amount_input(self, event=None):
        """Format deposit/withdraw amount input in Indian numbering style"""
        try:
            cursor_pos = self.dw_amount_entry.index("insert")
            current_value = self.dw_amount_entry.get()
            
            clean_value = ''.join(c for c in current_value if c.isdigit() or c == '.')
            
            if not clean_value or clean_value == '.':
                return
            
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
            
            if decimal_part or '.' in current_value:
                formatted = f"{formatted}.{decimal_part}"
            
            commas_before = current_value[:cursor_pos].count(',')
            clean_cursor_pos = cursor_pos - commas_before
            
            self.dw_amount_entry.delete(0, "end")
            self.dw_amount_entry.insert(0, formatted)
            
            try:
                new_pos = 0
                char_count = 0
                for i, char in enumerate(formatted):
                    if char != ',':
                        char_count += 1
                    if char_count >= clean_cursor_pos:
                        new_pos = i + 1
                        break
                else:
                    new_pos = len(formatted)
                
                self.dw_amount_entry.icursor(new_pos)
            except:
                pass
        
        except Exception as e:
            pass
        
        return "break"

    def create_balance_panel(self, parent):
        """Create balance overview panel"""
        balance_frame = ctk.CTkFrame(parent, corner_radius=10)
        balance_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Title
        title = ctk.CTkLabel(
            balance_frame,
            text="Balance Overview",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Balance cards container
        cards_container = ctk.CTkFrame(balance_frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=10, pady=(0, 15))

        # Company balance card
        company_card = ctk.CTkFrame(cards_container, corner_radius=8)
        company_card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            company_card,
            text="Companies",
            font=("Roboto", 14)
        ).pack(pady=(10, 5))

        self.company_balance_label = ctk.CTkLabel(
            company_card,
            text="₹0.00",
            font=("Roboto", 24, "bold"),
            text_color="green"
        )
        self.company_balance_label.pack(pady=(0, 10))

        # User balance card
        user_card = ctk.CTkFrame(cards_container, corner_radius=8)
        user_card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            user_card,
            text="Users",
            font=("Roboto", 14)
        ).pack(pady=(10, 5))

        self.user_balance_label = ctk.CTkLabel(
            user_card,
            text="₹0.00",
            font=("Roboto", 24, "bold"),
            text_color="green"
        )
        self.user_balance_label.pack(pady=(0, 10))

        # Total balance card
        total_card = ctk.CTkFrame(cards_container, corner_radius=8, fg_color=("lightblue", "darkblue"))
        total_card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(
            total_card,
            text="Total",
            font=("Roboto", 14, "bold")
        ).pack(pady=(10, 5))

        self.total_balance_label = ctk.CTkLabel(
            total_card,
            text="₹0.00",
            font=("Roboto", 24, "bold")
        )
        self.total_balance_label.pack(pady=(0, 10))

        # Accounts list section
        accounts_title = ctk.CTkLabel(
            balance_frame,
            text="Click on any account to view ledger",
            font=("Roboto", 14),
            text_color="gray"
        )
        accounts_title.pack(pady=(10, 5))

        # Scrollable accounts list
        self.accounts_scroll = ctk.CTkScrollableFrame(
            balance_frame,
            fg_color="transparent",
            height=200
        )
        self.accounts_scroll.pack(fill="x", padx=10, pady=(0, 15))

        # Will be populated in load_accounts_list()

    def load_accounts_list(self):
        """Load and display clickable list of all accounts"""
        # Clear existing
        for widget in self.accounts_scroll.winfo_children():
            widget.destroy()

        # Get all companies and users
        companies = self.db.get_all_companies()
        users = self.db.get_all_users()

        if not companies and not users:
            no_data = ctk.CTkLabel(
                self.accounts_scroll,
                text="No accounts yet. Add companies or users first.",
                font=("Roboto", 12),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display companies
        if companies:
            companies_header = ctk.CTkLabel(
                self.accounts_scroll,
                text="🏢 Companies",
                font=("Roboto", 13, "bold"),
                anchor="w"
            )
            companies_header.pack(fill="x", pady=(5, 5), padx=5)

            for company in companies:
                self.create_account_card(company, 'company')

        # Display users
        if users:
            users_header = ctk.CTkLabel(
                self.accounts_scroll,
                text="👤 Users",
                font=("Roboto", 13, "bold"),
                anchor="w"
            )
            users_header.pack(fill="x", pady=(15, 5), padx=5)

            for user in users:
                self.create_account_card(user, 'user')

    def create_account_card(self, account: dict, account_type: str):
        """Create a clickable account card"""
        from utils.helpers import format_currency

        card = ctk.CTkFrame(
            self.accounts_scroll,
            corner_radius=8,
            fg_color=("gray90", "gray25"),
            cursor="hand2"
        )
        card.pack(fill="x", pady=2, padx=5)

        # Account info frame
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=8)

        # Account name
        name_label = ctk.CTkLabel(
            info_frame,
            text=account['name'],
            font=("Roboto", 13, "bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        # Balance
        balance = account['balance']
        balance_color = "#2ecc71" if balance >= 0 else "#e74c3c"
        balance_label = ctk.CTkLabel(
            info_frame,
            text=format_currency(balance),
            font=("Roboto", 13, "bold"),
            text_color=balance_color
        )
        balance_label.pack(side="right")

        # Click handler
        def on_click(e=None):
            self.open_ledger(account_type, account['id'], account['name'])

        card.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        balance_label.bind("<Button-1>", on_click)

        # Hover effect
        def on_enter(e):
            card.configure(fg_color=("gray85", "gray30"))

        def on_leave(e):
            card.configure(fg_color=("gray90", "gray25"))

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def open_ledger(self, entity_type: str, entity_id: int, entity_name: str):
        """Open ledger window for an account"""
        from gui.ledger_window import LedgerWindow
        
        try:
            ledger_win = LedgerWindow(self.root, self.db, entity_type, entity_id, entity_name)
            ledger_win.focus()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to open ledger: {str(e)}")

    def create_recent_transactions_panel(self, parent):
        """Create recent transactions panel"""
        trans_frame = ctk.CTkFrame(parent, corner_radius=10)
        trans_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Header with title and refresh button
        header = ctk.CTkFrame(trans_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="Recent Transactions",
            font=("Roboto", 20, "bold")
        )
        title.pack(side="left")

        refresh_btn = ctk.CTkButton(
            header,
            text="🔄 Refresh",
            width=100,
            height=30,
            corner_radius=8,
            command=self.refresh_data
        )
        refresh_btn.pack(side="right")

        # Scrollable frame for transactions
        self.trans_scroll = ctk.CTkScrollableFrame(
            trans_frame,
            corner_radius=8,
            fg_color="transparent"
        )
        self.trans_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_entity_lists(self):
        """Load companies and users into dropdown lists"""
        # Get all companies and users
        companies = self.db.get_all_companies()
        users = self.db.get_all_users()

        # Build entity list with type prefix
        entities = []
        for company in companies:
            entities.append(f"[Company] {company['name']}")

        for user in users:
            company_name = ""
            if user['company_id']:
                company = self.db.get_company(user['company_id'])
                if company:
                    company_name = f" ({company['name']})"
            entities.append(f"[User] {user['name']}{company_name}")

        if not entities:
            entities = ["No entities available - Add companies/users first"]

        # Update dropdown values
        self.from_dropdown.configure(values=entities)
        self.to_dropdown.configure(values=entities)
        self.dw_entity_dropdown.configure(values=entities)

        if len(entities) > 0:
            # Set default value in dropdowns
            self.from_var.set(entities[0])
            self.to_var.set(entities[0])
            self.dw_entity_var.set(entities[0])

    def parse_entity_selection(self, selection: str) -> tuple:
        """
        Parse entity selection from dropdown

        Returns:
            Tuple of (entity_type, entity_id, entity_name)
        """
        if not selection or "No entities" in selection:
            return None, None, None

        # Extract type
        if selection.startswith("[Company]"):
            entity_type = "company"
            name_part = selection.replace("[Company]", "").strip()
        elif selection.startswith("[User]"):
            entity_type = "user"
            name_part = selection.replace("[User]", "").strip()
            # Remove company name in parentheses
            if "(" in name_part:
                name_part = name_part[:name_part.index("(")].strip()
        else:
            return None, None, None

        # Find entity ID by name
        if entity_type == "company":
            companies = self.db.get_all_companies()
            for company in companies:
                if company['name'] == name_part:
                    return entity_type, company['id'], company['name']
        else:
            users = self.db.get_all_users()
            for user in users:
                if user['name'] == name_part:
                    return entity_type, user['id'], user['name']

        return None, None, None

    def submit_transaction(self):
        """Submit new transaction"""
        # Validate inputs
        date = self.date_entry.get().strip()
        if not date:
            messagebox.showerror("Error", "Please enter a transaction date")
            return

        amount_str = self.amount_entry.get().strip()
        is_valid, amount = validate_amount(amount_str)
        if not is_valid:
            messagebox.showerror("Error", "Please enter a valid positive amount")
            return

        # Parse entities
        from_type, from_id, from_name = self.parse_entity_selection(self.from_var.get())
        to_type, to_id, to_name = self.parse_entity_selection(self.to_var.get())

        if not from_type or not to_type:
            messagebox.showerror("Error", "Please select valid sender and receiver")
            return

        if from_type == to_type and from_id == to_id:
            messagebox.showerror("Error", "Sender and receiver cannot be the same")
            return

        # Get optional fields
        description = self.desc_entry.get().strip()
        reference = self.ref_entry.get().strip()

        # Confirm transaction
        confirm_msg = (
            f"Submit transaction?\n\n"
            f"From: {from_name}\n"
            f"To: {to_name}\n"
            f"Amount: {format_currency(amount)}\n"
            f"Date: {date}"
        )

        if not messagebox.askyesno("Confirm Transaction", confirm_msg):
            return

        # Add transaction
        try:
            self.db.add_transaction(
                transaction_date=date,
                amount=amount,
                from_type=from_type,
                from_id=from_id,
                to_type=to_type,
                to_id=to_id,
                description=description,
                reference=reference
            )

            messagebox.showinfo("Success", "Transaction added successfully!")
            self.clear_form()
            self.refresh_data()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

    def clear_form(self):
        """Clear transaction entry form"""
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, get_current_date())
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.ref_entry.delete(0, "end")

    def submit_deposit_withdraw(self):
        """Submit deposit or withdraw operation"""
        # Get operation type
        operation = self.operation_var.get()
        
        # Validate amount
        amount_str = self.dw_amount_entry.get().strip()
        is_valid, amount = validate_amount(amount_str)
        if not is_valid:
            messagebox.showerror("Error", "Please enter a valid positive amount")
            return
        
        # Parse entity selection
        entity_type, entity_id, entity_name = self.parse_entity_selection(self.dw_entity_var.get())
        
        if not entity_type:
            messagebox.showerror("Error", "Please select a valid account")
            return
        
        # Get description
        description = self.dw_desc_entry.get().strip()
        if not description:
            description = f"Cash {operation.capitalize()}"
        
        # Confirm operation
        op_text = "Deposit to" if operation == "deposit" else "Withdraw from"
        confirm_msg = (
            f"Confirm {operation}?\n\n"
            f"{op_text}: {entity_name}\n"
            f"Amount: {format_currency(amount)}\n"
            f"Description: {description}"
        )
        
        if not messagebox.askyesno(f"Confirm {operation.capitalize()}", confirm_msg):
            return
        
        # Perform operation
        try:
            if operation == "deposit":
                self.db.deposit(entity_type, entity_id, amount, description)
                messagebox.showinfo("Success", f"Deposited {format_currency(amount)} successfully!")
            else:  # withdraw
                # Check if sufficient balance
                if entity_type == "company":
                    entity = self.db.get_company(entity_id)
                else:
                    entity = self.db.get_user(entity_id)
                
                if entity and entity['balance'] < amount:
                    messagebox.showerror("Error", 
                        f"Insufficient balance!\n\n"
                        f"Current balance: {format_currency(entity['balance'])}\n"
                        f"Withdraw amount: {format_currency(amount)}")
                    return
                
                self.db.withdraw(entity_type, entity_id, amount, description)
                messagebox.showinfo("Success", f"Withdrawn {format_currency(amount)} successfully!")
            
            # Clear form and refresh
            self.dw_amount_entry.delete(0, "end")
            self.dw_desc_entry.delete(0, "end")
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to {operation}: {str(e)}")

    def load_data(self):
        """Load all data"""
        self.load_entity_lists()
        self.load_balances()
        self.load_accounts_list()
        self.load_recent_transactions()

    def load_balances(self):
        """Load and display balance information"""
        balances = self.db.get_total_balances()

        company_total = balances['company_total']
        user_total = balances['user_total']
        grand_total = balances['grand_total']

        self.company_balance_label.configure(text=format_currency(company_total))
        self.user_balance_label.configure(text=format_currency(user_total))
        self.total_balance_label.configure(text=format_currency(grand_total))

    def load_recent_transactions(self, limit: int = 10):
        """Load and display recent transactions"""
        # Clear existing transactions
        for widget in self.trans_scroll.winfo_children():
            widget.destroy()

        # Get recent transactions
        transactions = self.db.get_all_transactions(limit=limit)

        if not transactions:
            no_data_label = ctk.CTkLabel(
                self.trans_scroll,
                text="No transactions yet",
                font=("Roboto", 14),
                text_color="gray"
            )
            no_data_label.pack(pady=20)
            return

        # Display each transaction
        for trans in transactions:
            trans_card = self.create_transaction_card(self.trans_scroll, trans)
            trans_card.pack(fill="x", pady=5)

    def create_transaction_card(self, parent, trans: dict) -> ctk.CTkFrame:
        """Create a transaction display card"""
        card = ctk.CTkFrame(parent, corner_radius=8)

        # Main info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)

        # Left: From -> To
        left_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        from_to_text = f"{trans['from_name']} → {trans['to_name']}"
        ctk.CTkLabel(
            left_frame,
            text=from_to_text,
            font=("Roboto", 14, "bold"),
            anchor="w"
        ).pack(anchor="w")

        date_text = format_date(trans['transaction_date'], "%d-%m-%Y", "%d %b, %Y")
        ctk.CTkLabel(
            left_frame,
            text=date_text,
            font=("Roboto", 11),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")

        # Right: Amount
        amount_label = ctk.CTkLabel(
            info_frame,
            text=format_currency(trans['amount']),
            font=("Roboto", 18, "bold"),
            text_color="green"
        )
        amount_label.pack(side="right", padx=10)

        # Description if available
        if trans['description']:
            desc_label = ctk.CTkLabel(
                card,
                text=f"📝 {trans['description']}",
                font=("Roboto", 11),
                text_color="gray",
                anchor="w"
            )
            desc_label.pack(anchor="w", padx=15, pady=(0, 10))

        return card

    def refresh_data(self):
        """Refresh all data displays"""
        self.load_data()

    def toggle_theme(self):
        """Toggle between dark and light themes"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "Dark" else "dark"

        ctk.set_appearance_mode(new_mode)

        # Update button text
        if new_mode == "dark":
            self.theme_btn.configure(text="🌙 Dark")
        else:
            self.theme_btn.configure(text="☀️ Light")

    # Placeholder methods for menu buttons
    def show_dashboard(self):
        """Show dashboard (current view)"""
        self.refresh_data()

    def open_company_dialog(self):
        """Open company management dialog"""
        from gui.company_dialog import CompanyDialog
        dialog = CompanyDialog(self.root, self.db)
        self.root.wait_window(dialog.dialog)
        self.refresh_data()

    def open_user_dialog(self):
        """Open user management dialog"""
        from gui.user_dialog import UserDialog
        dialog = UserDialog(self.root, self.db)
        self.root.wait_window(dialog.dialog)
        self.refresh_data()

    def open_transaction_dialog(self):
        """Open transaction management dialog"""
        from gui.transaction_dialog import TransactionDialog
        dialog = TransactionDialog(self.root, self.db)
        self.root.wait_window(dialog.dialog)
        self.refresh_data()

    def open_reports_window(self):
        """Open reports window"""
        from gui.reports_window import ReportsWindow
        ReportsWindow(self.root, self.db)

    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings feature coming soon!")
