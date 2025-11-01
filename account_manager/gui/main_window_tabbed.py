"""
Main Window - Tabbed Interface (Single Window Design)
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import Optional

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, format_date, validate_amount, get_current_date, validate_email
from gui.company_dialog import CompanyDialog
from gui.user_dialog import UserDialog
from gui.transaction_dialog import TransactionDialog
from gui.reports_window import ReportsWindow
from gui.ledger_window import LedgerWindow


class MainWindow:
    """Main application window with tabbed interface"""

    def __init__(self, root: ctk.CTk, db: DatabaseManager):
        """Initialize main window with tabs"""
        self.root = root
        self.db = db

        # Transaction editing state
        self.editing_transaction_id = None

        # Create tab navigation
        self.create_tabbed_interface()

        # Load initial data
        self.load_data()

    def create_tabbed_interface(self):
        """Create main tabbed interface"""
        # Create tabview (tab container)
        self.tabview = ctk.CTkTabview(self.root, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.tab_dashboard = self.tabview.add("🏠 Dashboard")
        self.tab_companies = self.tabview.add("🏢 Companies")
        self.tab_users = self.tabview.add("👤 Users")
        self.tab_transactions = self.tabview.add("💸 Transactions")
        self.tab_reports = self.tabview.add("📊 Reports")

        # Set default tab
        self.tabview.set("🏠 Dashboard")

        # Create content for each tab
        self.create_dashboard_tab()
        self.create_companies_tab()
        self.create_users_tab()
        self.create_transactions_tab()
        self.create_reports_tab()

    def create_dashboard_tab(self):
        """Create dashboard tab content"""
        # Main container
        main_container = ctk.CTkFrame(self.tab_dashboard, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Two-column layout
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Build left column: Transaction entry only
        self.create_transaction_entry_panel(left_frame)

        # Build right column: Balance overview
        self.create_balance_panel(right_frame)
        self.create_recent_transactions_panel(right_frame)

    def create_companies_tab(self):
        """Create companies management tab"""
        self.selected_company_id = None

        # Main container with two columns
        main_container = ctk.CTkFrame(self.tab_companies, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: Company list
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Right: Company details form
        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Build left panel
        self.create_company_list_panel(left_frame)

        # Build right panel
        self.create_company_form_panel(right_frame)

    def create_company_list_panel(self, parent):
        """Create company list panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Companies",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Scrollable list
        self.company_list = ctk.CTkScrollableFrame(
            parent,
            corner_radius=8
        )
        self.company_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Refresh button
        refresh_btn = ctk.CTkButton(
            parent,
            text="🔄 Refresh List",
            height=35,
            corner_radius=8,
            command=self.load_companies
        )
        refresh_btn.pack(fill="x", padx=15, pady=(0, 15))

    def create_company_form_panel(self, parent):
        """Create company form panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Company Details",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Form container
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Name field
        ctk.CTkLabel(form_frame, text="Company Name:*", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_name_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.company_name_entry.pack(fill="x", pady=(0, 10))

        # Address field
        ctk.CTkLabel(form_frame, text="Address:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_address_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.company_address_entry.pack(fill="x", pady=(0, 10))

        # Phone field
        ctk.CTkLabel(form_frame, text="Phone:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_phone_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.company_phone_entry.pack(fill="x", pady=(0, 10))

        # Email field
        ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_email_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.company_email_entry.pack(fill="x", pady=(0, 10))

        # Balance display (read-only)
        ctk.CTkLabel(form_frame, text="Current Balance:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_balance_label = ctk.CTkLabel(
            form_frame,
            text="₹0.00",
            font=("Roboto", 18, "bold"),
            text_color="green"
        )
        self.company_balance_label.pack(anchor="w", pady=(0, 15))

        # Buttons frame
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # Add button - Enhanced visibility
        self.company_add_btn = ctk.CTkButton(
            button_frame,
            text="➕ ADD COMPANY",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            border_width=2,
            border_color="#1e8449",
            command=self.add_company
        )
        self.company_add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Update button - Enhanced visibility
        self.company_update_btn = ctk.CTkButton(
            button_frame,
            text="✎ UPDATE",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#f39c12",
            hover_color="#d68910",
            border_width=2,
            border_color="#b87a0a",
            command=self.update_company,
            state="disabled"
        )
        self.company_update_btn.pack(side="left", fill="x", expand=True, padx=5)

        # Delete button - Enhanced visibility
        self.company_delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑 DELETE",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            border_width=2,
            border_color="#a93226",
            command=self.delete_company,
            state="disabled"
        )
        self.company_delete_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Clear button - Enhanced visibility
        clear_btn = ctk.CTkButton(
            form_frame,
            text="⟲ CLEAR",
            height=48,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            border_width=2,
            border_color="#5d6d7e",
            command=self.clear_company_form
        )
        clear_btn.pack(fill="x", pady=(10, 0))

    def load_companies(self):
        """Load and display all companies"""
        # Clear existing list
        for widget in self.company_list.winfo_children():
            widget.destroy()

        # Get companies
        companies = self.db.get_all_companies()

        if not companies:
            no_data = ctk.CTkLabel(
                self.company_list,
                text="No companies yet\nClick 'Add Company' to create one",
                font=("Roboto", 13),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display each company
        for company in companies:
            self.create_company_card(company)

    def create_company_card(self, company: dict):
        """Create a company display card"""
        card = ctk.CTkFrame(self.company_list, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        # Make card clickable
        card.bind("<Button-1>", lambda e, c=company: self.select_company(c))

        # Company info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=10)
        info_frame.bind("<Button-1>", lambda e, c=company: self.select_company(c))

        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=company['name'],
            font=("Roboto", 15, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e, c=company: self.select_company(c))

        # Balance
        balance = company.get('balance', 0.0)
        balance_text = format_currency(balance)
        balance_color = "green" if balance >= 0 else "red"

        balance_label = ctk.CTkLabel(
            info_frame,
            text=f"Balance: {balance_text}",
            font=("Roboto", 13),
            text_color=balance_color,
            anchor="w"
        )
        balance_label.pack(anchor="w")
        balance_label.bind("<Button-1>", lambda e, c=company: self.select_company(c))

        # Contact info if available
        contact_parts = []
        if company.get('email'):
            contact_parts.append(company['email'])
        if company.get('phone'):
            contact_parts.append(company['phone'])

        if contact_parts:
            contact_label = ctk.CTkLabel(
                info_frame,
                text=" | ".join(contact_parts),
                font=("Roboto", 11),
                text_color="gray",
                anchor="w"
            )
            contact_label.pack(anchor="w")
            contact_label.bind("<Button-1>", lambda e, c=company: self.select_company(c))

    def select_company(self, company: dict):
        """Select a company to edit"""
        self.selected_company_id = company['id']

        # Populate form
        self.company_name_entry.delete(0, "end")
        self.company_name_entry.insert(0, company['name'])

        self.company_address_entry.delete(0, "end")
        self.company_address_entry.insert(0, company.get('address', ''))

        self.company_phone_entry.delete(0, "end")
        self.company_phone_entry.insert(0, company.get('phone', ''))

        self.company_email_entry.delete(0, "end")
        self.company_email_entry.insert(0, company.get('email', ''))

        balance = company.get('balance', 0.0)
        self.company_balance_label.configure(text=format_currency(balance))

        # Enable update/delete buttons
        self.company_update_btn.configure(state="normal")
        self.company_delete_btn.configure(state="normal")

    def add_company(self):
        """Add new company"""
        # Validate inputs
        name = self.company_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        address = self.company_address_entry.get().strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Add to database
        try:
            company_id = self.db.add_company(
                name=name,
                address=address,
                phone=phone,
                email=email
            )

            messagebox.showinfo("Success", f"Company '{name}' added successfully!")
            self.clear_company_form()
            self.load_companies()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add company: {str(e)}")

    def update_company(self):
        """Update selected company"""
        if not self.selected_company_id:
            messagebox.showerror("Error", "No company selected")
            return

        # Validate inputs
        name = self.company_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        address = self.company_address_entry.get().strip()
        phone = self.company_phone_entry.get().strip()
        email = self.company_email_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Update in database
        try:
            self.db.update_company(
                company_id=self.selected_company_id,
                name=name,
                address=address,
                phone=phone,
                email=email
            )

            messagebox.showinfo("Success", f"Company '{name}' updated successfully!")
            self.clear_company_form()
            self.load_companies()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update company: {str(e)}")

    def delete_company(self):
        """Delete selected company"""
        if not self.selected_company_id:
            messagebox.showerror("Error", "No company selected")
            return

        company = self.db.get_company(self.selected_company_id)
        if not company:
            messagebox.showerror("Error", "Company not found")
            return

        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{company['name']}'?\n\n"
            f"WARNING: This action cannot be undone!"
        ):
            return

        # Delete from database
        try:
            self.db.delete_company(self.selected_company_id)
            messagebox.showinfo("Success", f"Company '{company['name']}' deleted successfully!")
            self.clear_company_form()
            self.load_companies()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete company: {str(e)}")

    def clear_company_form(self):
        """Clear form and reset selection"""
        self.selected_company_id = None

        self.company_name_entry.delete(0, "end")
        self.company_address_entry.delete(0, "end")
        self.company_phone_entry.delete(0, "end")
        self.company_email_entry.delete(0, "end")
        self.company_balance_label.configure(text="₹0.00")

        self.company_update_btn.configure(state="disabled")
        self.company_delete_btn.configure(state="disabled")

    def create_users_tab(self):
        """Create users management tab"""
        self.selected_user_id = None

        # Main container with two columns
        main_container = ctk.CTkFrame(self.tab_users, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: User list
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Right: User details form
        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Build left panel
        self.create_user_list_panel(left_frame)

        # Build right panel
        self.create_user_form_panel(right_frame)

    def create_user_list_panel(self, parent):
        """Create user list panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Users",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Scrollable list
        self.user_list = ctk.CTkScrollableFrame(
            parent,
            corner_radius=8
        )
        self.user_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Refresh button
        refresh_btn = ctk.CTkButton(
            parent,
            text="🔄 Refresh List",
            height=35,
            corner_radius=8,
            command=self.load_users
        )
        refresh_btn.pack(fill="x", padx=15, pady=(0, 15))

    def create_user_form_panel(self, parent):
        """Create user form panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="User Details",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Form container
        form_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Name field
        ctk.CTkLabel(form_frame, text="User Name:*", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_name_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.user_name_entry.pack(fill="x", pady=(0, 10))

        # Email field
        ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_email_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.user_email_entry.pack(fill="x", pady=(0, 10))

        # Role field
        ctk.CTkLabel(form_frame, text="Role:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_role_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.user_role_entry.pack(fill="x", pady=(0, 10))

        # Department field
        ctk.CTkLabel(form_frame, text="Department:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_department_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.user_department_entry.pack(fill="x", pady=(0, 10))

        # Company selection
        ctk.CTkLabel(form_frame, text="Company:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_company_combo = ctk.CTkComboBox(
            form_frame,
            height=35,
            font=("Roboto", 13),
            values=["None"],
            state="readonly"
        )
        self.user_company_combo.pack(fill="x", pady=(0, 10))
        self.load_user_companies()

        # Balance display (read-only)
        ctk.CTkLabel(form_frame, text="Current Balance:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.user_balance_label = ctk.CTkLabel(
            form_frame,
            text="₹0.00",
            font=("Roboto", 18, "bold"),
            text_color="green"
        )
        self.user_balance_label.pack(anchor="w", pady=(0, 15))

        # Buttons frame
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # Add button - Enhanced visibility
        self.user_add_btn = ctk.CTkButton(
            button_frame,
            text="➕ ADD USER",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            border_width=2,
            border_color="#1e8449",
            command=self.add_user
        )
        self.user_add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Update button - Enhanced visibility
        self.user_update_btn = ctk.CTkButton(
            button_frame,
            text="✎ UPDATE",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#f39c12",
            hover_color="#d68910",
            border_width=2,
            border_color="#b87a0a",
            command=self.update_user,
            state="disabled"
        )
        self.user_update_btn.pack(side="left", fill="x", expand=True, padx=5)

        # Delete button - Enhanced visibility
        self.user_delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑 DELETE",
            height=55,
            font=("Roboto", 16, "bold"),
            corner_radius=10,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            border_width=2,
            border_color="#a93226",
            command=self.delete_user,
            state="disabled"
        )
        self.user_delete_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Clear button - Enhanced visibility
        clear_btn = ctk.CTkButton(
            form_frame,
            text="⟲ CLEAR",
            height=48,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            border_width=2,
            border_color="#5d6d7e",
            command=self.clear_user_form
        )
        clear_btn.pack(fill="x", pady=(10, 0))

    def load_user_companies(self):
        """Load companies into dropdown"""
        companies = self.db.get_all_companies()
        company_names = ["None"] + [c['name'] for c in companies]
        self.user_company_combo.configure(values=company_names)
        self.user_company_combo.set("None")

    def load_users(self):
        """Load and display all users"""
        # Clear existing list
        for widget in self.user_list.winfo_children():
            widget.destroy()

        # Get users
        users = self.db.get_all_users()

        if not users:
            no_data = ctk.CTkLabel(
                self.user_list,
                text="No users yet\nClick 'Add User' to create one",
                font=("Roboto", 13),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display each user
        for user in users:
            self.create_user_card(user)

    def create_user_card(self, user: dict):
        """Create a user display card"""
        card = ctk.CTkFrame(self.user_list, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        # Make card clickable
        card.bind("<Button-1>", lambda e, u=user: self.select_user(u))

        # User info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=10)
        info_frame.bind("<Button-1>", lambda e, u=user: self.select_user(u))

        # Name
        name_label = ctk.CTkLabel(
            info_frame,
            text=user['name'],
            font=("Roboto", 15, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e, u=user: self.select_user(u))

        # Company name
        company_text = "No company"
        if user.get('company_id'):
            company = self.db.get_company(user['company_id'])
            if company:
                company_text = f"Company: {company['name']}"

        company_label = ctk.CTkLabel(
            info_frame,
            text=company_text,
            font=("Roboto", 12),
            text_color="gray",
            anchor="w"
        )
        company_label.pack(anchor="w")
        company_label.bind("<Button-1>", lambda e, u=user: self.select_user(u))

        # Balance
        balance = user.get('balance', 0.0)
        balance_text = format_currency(balance)
        balance_color = "green" if balance >= 0 else "red"

        balance_label = ctk.CTkLabel(
            info_frame,
            text=f"Balance: {balance_text}",
            font=("Roboto", 13),
            text_color=balance_color,
            anchor="w"
        )
        balance_label.pack(anchor="w")
        balance_label.bind("<Button-1>", lambda e, u=user: self.select_user(u))

        # Role/Department if available
        details = []
        if user.get('role'):
            details.append(user['role'])
        if user.get('department'):
            details.append(user['department'])

        if details:
            detail_label = ctk.CTkLabel(
                info_frame,
                text=" | ".join(details),
                font=("Roboto", 11),
                text_color="gray",
                anchor="w"
            )
            detail_label.pack(anchor="w")
            detail_label.bind("<Button-1>", lambda e, u=user: self.select_user(u))

    def select_user(self, user: dict):
        """Select a user to edit"""
        self.selected_user_id = user['id']

        # Populate form
        self.user_name_entry.delete(0, "end")
        self.user_name_entry.insert(0, user['name'])

        self.user_email_entry.delete(0, "end")
        self.user_email_entry.insert(0, user.get('email', ''))

        self.user_role_entry.delete(0, "end")
        self.user_role_entry.insert(0, user.get('role', ''))

        self.user_department_entry.delete(0, "end")
        self.user_department_entry.insert(0, user.get('department', ''))

        # Set company
        if user.get('company_id'):
            company = self.db.get_company(user['company_id'])
            if company:
                self.user_company_combo.set(company['name'])
        else:
            self.user_company_combo.set("None")

        balance = user.get('balance', 0.0)
        self.user_balance_label.configure(text=format_currency(balance))

        # Enable update/delete buttons
        self.user_update_btn.configure(state="normal")
        self.user_delete_btn.configure(state="normal")

    def add_user(self):
        """Add new user"""
        # Validate inputs
        name = self.user_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name is required")
            return

        email = self.user_email_entry.get().strip()
        role = self.user_role_entry.get().strip()
        department = self.user_department_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Get company ID
        company_id = None
        company_name = self.user_company_combo.get()
        if company_name and company_name != "None":
            companies = self.db.get_all_companies()
            for company in companies:
                if company['name'] == company_name:
                    company_id = company['id']
                    break

        # Add to database
        try:
            user_id = self.db.add_user(
                name=name,
                email=email,
                role=role,
                department=department,
                company_id=company_id
            )

            messagebox.showinfo("Success", f"User '{name}' added successfully!")
            self.clear_user_form()
            self.load_users()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")

    def update_user(self):
        """Update selected user"""
        if not self.selected_user_id:
            messagebox.showerror("Error", "No user selected")
            return

        # Validate inputs
        name = self.user_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name is required")
            return

        email = self.user_email_entry.get().strip()
        role = self.user_role_entry.get().strip()
        department = self.user_department_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Get company ID
        company_id = None
        company_name = self.user_company_combo.get()
        if company_name and company_name != "None":
            companies = self.db.get_all_companies()
            for company in companies:
                if company['name'] == company_name:
                    company_id = company['id']
                    break

        # Update in database
        try:
            self.db.update_user(
                user_id=self.selected_user_id,
                name=name,
                email=email,
                role=role,
                department=department,
                company_id=company_id
            )

            messagebox.showinfo("Success", f"User '{name}' updated successfully!")
            self.clear_user_form()
            self.load_users()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {str(e)}")

    def delete_user(self):
        """Delete selected user"""
        if not self.selected_user_id:
            messagebox.showerror("Error", "No user selected")
            return

        user = self.db.get_user(self.selected_user_id)
        if not user:
            messagebox.showerror("Error", "User not found")
            return

        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete '{user['name']}'?\n\n"
            f"WARNING: This action cannot be undone!"
        ):
            return

        # Delete from database
        try:
            self.db.delete_user(self.selected_user_id)
            messagebox.showinfo("Success", f"User '{user['name']}' deleted successfully!")
            self.clear_user_form()
            self.load_users()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {str(e)}")

    def clear_user_form(self):
        """Clear form and reset selection"""
        self.selected_user_id = None

        self.user_name_entry.delete(0, "end")
        self.user_email_entry.delete(0, "end")
        self.user_role_entry.delete(0, "end")
        self.user_department_entry.delete(0, "end")
        self.user_company_combo.set("None")
        self.user_balance_label.configure(text="₹0.00")

        self.user_update_btn.configure(state="disabled")
        self.user_delete_btn.configure(state="disabled")

    def create_transactions_tab(self):
        """Create transactions history tab"""
        self.selected_transaction_id = None

        # Main container
        main_container = ctk.CTkFrame(self.tab_transactions, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Top: Search and filter toolbar
        self.create_transaction_toolbar(main_container)

        # Middle: Transaction list
        list_frame = ctk.CTkFrame(main_container, corner_radius=10)
        list_frame.pack(fill="both", expand=True, pady=(10, 10))

        self.create_transaction_list_panel(list_frame)

        # Bottom: Transaction details
        details_frame = ctk.CTkFrame(main_container, corner_radius=10)
        details_frame.pack(fill="x", pady=(0, 0))

        self.create_transaction_details_panel(details_frame)

    def create_transaction_toolbar(self, parent):
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
        self.transaction_search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search transactions...",
            width=250,
            height=35
        )
        self.transaction_search_entry.pack(side="left", padx=10)

        # Search button
        search_btn = ctk.CTkButton(
            toolbar,
            text="🔍 Search",
            width=100,
            height=35,
            command=self.search_transactions_list
        )
        search_btn.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.load_transactions_list
        )
        refresh_btn.pack(side="left", padx=5)

        # Delete button - Enhanced (red, larger, bold)
        self.transaction_delete_btn = ctk.CTkButton(
            toolbar,
            text="🗑️ DELETE",
            width=130,
            height=45,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            border_width=2,
            border_color="#922b21",
            command=self.delete_transaction,
            state="disabled"
        )
        self.transaction_delete_btn.pack(side="right", padx=10)

        # Update button - Enhanced (orange, larger, bold)
        self.transaction_update_btn = ctk.CTkButton(
            toolbar,
            text="✎ UPDATE",
            width=130,
            height=45,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#f39c12",
            hover_color="#d68910",
            border_width=2,
            border_color="#b87a0a",
            command=self.update_transaction_tab,
            state="disabled"
        )
        self.transaction_update_btn.pack(side="right", padx=10)

    def create_transaction_list_panel(self, parent):
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
        self.transaction_count_label = ctk.CTkLabel(
            header,
            text="0 transactions",
            font=("Roboto", 12),
            text_color="gray"
        )
        self.transaction_count_label.pack(side="right")

        # Scrollable list
        self.transaction_list = ctk.CTkScrollableFrame(
            parent,
            corner_radius=8
        )
        self.transaction_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_transaction_details_panel(self, parent):
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
        self.trans_detail_id = self.create_transaction_detail_row(left_col, "ID:")

        # Date
        self.trans_detail_date = self.create_transaction_detail_row(left_col, "Date:")

        # Amount
        self.trans_detail_amount = self.create_transaction_detail_row(left_col, "Amount:")

        # Right column
        right_col = ctk.CTkFrame(details_container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # From
        self.trans_detail_from = self.create_transaction_detail_row(right_col, "From:")

        # To
        self.trans_detail_to = self.create_transaction_detail_row(right_col, "To:")

        # Type
        self.trans_detail_type = self.create_transaction_detail_row(right_col, "Type:")

        # Full width for description and reference
        self.trans_detail_desc = self.create_transaction_detail_row(parent, "Description:", padx=15)
        self.trans_detail_ref = self.create_transaction_detail_row(parent, "Reference:", padx=15)

    def create_transaction_detail_row(self, parent, label_text: str, padx: int = 0):
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

    def load_transactions_list(self):
        """Load and display all transactions"""
        # Clear existing list
        for widget in self.transaction_list.winfo_children():
            widget.destroy()

        # Get transactions
        transactions = self.db.get_all_transactions()

        # Update count
        self.transaction_count_label.configure(text=f"{len(transactions)} transactions")

        if not transactions:
            no_data = ctk.CTkLabel(
                self.transaction_list,
                text="No transactions yet",
                font=("Roboto", 14),
                text_color="gray"
            )
            no_data.pack(pady=20)
            return

        # Display each transaction
        for trans in transactions:
            self.create_transaction_card(trans)

    def create_transaction_card(self, trans: dict):
        """Create a transaction display card"""
        card = ctk.CTkFrame(self.transaction_list, corner_radius=8)
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
                text=f"📝 {trans['description'][:40]}..." if len(trans['description']) > 40 else f"📝 {trans['description']}",
                font=("Roboto", 11),
                text_color="gray",
                anchor="e"
            )
            desc_label.pack(side="right")
            desc_label.bind("<Button-1>", lambda e, t=trans: self.select_transaction(t))

    def select_transaction(self, trans: dict):
        """Select a transaction to view details"""
        self.selected_transaction_id = trans['id']

        # Populate details
        self.trans_detail_id.configure(text=str(trans['id']))

        date_text = format_date(trans['transaction_date'], "%d-%m-%Y", "%d %B, %Y")
        self.trans_detail_date.configure(text=date_text)

        self.trans_detail_amount.configure(
            text=format_currency(trans['amount']),
            text_color="green"
        )

        from_text = f"{trans['from_name']} ({trans['from_type'].capitalize()})"
        self.trans_detail_from.configure(text=from_text)

        to_text = f"{trans['to_name']} ({trans['to_type'].capitalize()})"
        self.trans_detail_to.configure(text=to_text)

        type_text = f"{trans['from_type'].capitalize()} to {trans['to_type'].capitalize()}"
        self.trans_detail_type.configure(text=type_text)

        self.trans_detail_desc.configure(text=trans.get('description', '--'))
        self.trans_detail_ref.configure(text=trans.get('reference', '--'))

        # Enable update and delete buttons
        self.transaction_update_btn.configure(state="normal")
        self.transaction_delete_btn.configure(state="normal")

    def search_transactions_list(self):
        """Search transactions by keyword"""
        search_term = self.transaction_search_entry.get().strip()

        if not search_term:
            self.load_transactions_list()
            return

        # Clear existing list
        for widget in self.transaction_list.winfo_children():
            widget.destroy()

        # Search
        transactions = self.db.search_transactions(search_term)

        # Update count
        self.transaction_count_label.configure(text=f"{len(transactions)} results")

        if not transactions:
            no_data = ctk.CTkLabel(
                self.transaction_list,
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
            self.transaction_update_btn.configure(state="disabled")
            self.transaction_delete_btn.configure(state="disabled")

            # Refresh list
            self.load_transactions_list()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")

    def update_transaction_tab(self):
        """Enable editing mode for selected transaction in the details panel"""
        if not self.selected_transaction_id:
            messagebox.showerror("Error", "No transaction selected")
            return

        trans = self.db.get_transaction(self.selected_transaction_id)
        if not trans:
            messagebox.showerror("Error", "Transaction not found")
            return

        # Store original transaction for cancel
        self.editing_transaction = trans

        # Get all entities for dropdowns (using same format as dashboard)
        all_entities = []
        # Add Cash option
        all_entities.append("[Cash] Cash")
        for company in self.db.get_all_companies():
            all_entities.append(f"[Company] {company['name']}")
        for user in self.db.get_all_users():
            company_name = ""
            if user.get('company_id'):
                company = self.db.get_company(user['company_id'])
                if company:
                    company_name = f" ({company['name']})"
            all_entities.append(f"[User] {user['name']}{company_name}")

        # Clear current details and create edit form
        # Clear the details labels and replace with entry fields
        # Date - replace label with entry
        self.trans_detail_date_entry = ctk.CTkEntry(
            self.trans_detail_date.master,
            font=("Roboto", 12, "bold"),
            height=30
        )
        self.trans_detail_date.pack_forget()
        self.trans_detail_date_entry.pack(side="left", fill="x", expand=True)
        self.trans_detail_date_entry.insert(0, trans['transaction_date'])

        # Amount - replace label with entry
        self.trans_detail_amount_entry = ctk.CTkEntry(
            self.trans_detail_amount.master,
            font=("Roboto", 12, "bold"),
            height=30
        )
        self.trans_detail_amount.pack_forget()
        self.trans_detail_amount_entry.pack(side="left", fill="x", expand=True)
        self.trans_detail_amount_entry.insert(0, str(trans['amount']))
        # Add Indian rupee formatting
        self.trans_detail_amount_entry.bind("<KeyRelease>", self.format_edit_amount_input)

        # From - replace label with dropdown
        # Format the initial value to match the dropdown format: [Company] Name or [User] Name or [Cash] Cash
        from_initial = ""
        if trans['from_type'] == 'cash':
            from_initial = "[Cash] Cash"
        elif trans['from_type'] == 'company':
            from_initial = f"[Company] {trans['from_name']}"
        elif trans['from_type'] == 'user':
            from_initial = f"[User] {trans['from_name']}"
            # Add company info if user has one
            from_user = next((u for u in self.db.get_all_users() if u['name'] == trans['from_name']), None)
            if from_user and from_user.get('company_id'):
                from_company = self.db.get_company(from_user['company_id'])
                if from_company:
                    from_initial += f" ({from_company['name']})"

        self.trans_detail_from_var = ctk.StringVar(value=from_initial)
        self.trans_detail_from_dropdown = ctk.CTkOptionMenu(
            self.trans_detail_from.master,
            variable=self.trans_detail_from_var,
            values=all_entities,
            font=("Roboto", 11),
            height=30
        )
        self.trans_detail_from.pack_forget()
        self.trans_detail_from_dropdown.pack(side="left", fill="x", expand=True)

        # To - replace label with dropdown
        # Format the initial value to match the dropdown format: [Company] Name or [User] Name or [Cash] Cash
        to_initial = ""
        if trans['to_type'] == 'cash':
            to_initial = "[Cash] Cash"
        elif trans['to_type'] == 'company':
            to_initial = f"[Company] {trans['to_name']}"
        elif trans['to_type'] == 'user':
            to_initial = f"[User] {trans['to_name']}"
            # Add company info if user has one
            to_user = next((u for u in self.db.get_all_users() if u['name'] == trans['to_name']), None)
            if to_user and to_user.get('company_id'):
                to_company = self.db.get_company(to_user['company_id'])
                if to_company:
                    to_initial += f" ({to_company['name']})"

        self.trans_detail_to_var = ctk.StringVar(value=to_initial)
        self.trans_detail_to_dropdown = ctk.CTkOptionMenu(
            self.trans_detail_to.master,
            variable=self.trans_detail_to_var,
            values=all_entities,
            font=("Roboto", 11),
            height=30
        )
        self.trans_detail_to.pack_forget()
        self.trans_detail_to_dropdown.pack(side="left", fill="x", expand=True)

        # Description - replace label with entry
        self.trans_detail_desc_entry = ctk.CTkEntry(
            self.trans_detail_desc.master,
            font=("Roboto", 12, "bold"),
            height=30
        )
        self.trans_detail_desc.pack_forget()
        self.trans_detail_desc_entry.pack(side="left", fill="x", expand=True)
        if trans.get('description'):
            self.trans_detail_desc_entry.insert(0, trans['description'])

        # Reference - replace label with entry
        self.trans_detail_ref_entry = ctk.CTkEntry(
            self.trans_detail_ref.master,
            font=("Roboto", 12, "bold"),
            height=30
        )
        self.trans_detail_ref.pack_forget()
        self.trans_detail_ref_entry.pack(side="left", fill="x", expand=True)
        if trans.get('reference'):
            self.trans_detail_ref_entry.insert(0, trans['reference'])

        # Hide UPDATE and DELETE buttons, show SUBMIT and CANCEL buttons
        self.transaction_update_btn.pack_forget()
        self.transaction_delete_btn.pack_forget()

        # Create SUBMIT button
        self.transaction_submit_btn = ctk.CTkButton(
            self.transaction_update_btn.master,
            text="✓ SUBMIT CHANGES",
            width=150,
            height=45,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            border_width=2,
            border_color="#1e8449",
            command=self.submit_transaction_update
        )
        self.transaction_submit_btn.pack(side="right", padx=10)

        # Create CANCEL button
        self.transaction_cancel_btn = ctk.CTkButton(
            self.transaction_update_btn.master,
            text="✕ CANCEL",
            width=150,
            height=45,
            font=("Roboto", 14, "bold"),
            corner_radius=10,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            border_width=2,
            border_color="#5d6d7e",
            command=self.cancel_transaction_update
        )
        self.transaction_cancel_btn.pack(side="right", padx=10)

    def submit_transaction_update(self):
        """Submit the updated transaction"""
        # Get values from entry fields
        date = self.trans_detail_date_entry.get().strip()
        amount = self.trans_detail_amount_entry.get().strip()
        from_entity = self.trans_detail_from_var.get()
        to_entity = self.trans_detail_to_var.get()
        description = self.trans_detail_desc_entry.get().strip()
        reference = self.trans_detail_ref_entry.get().strip()

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

        # Parse entities to get type, id, and name
        from_type, from_id, from_name = self.parse_entity_selection(from_entity)
        to_type, to_id, to_name = self.parse_entity_selection(to_entity)

        if not from_type or not to_type:
            messagebox.showerror("Error", "Please select valid sender and receiver")
            return

        if from_type == to_type and from_id == to_id:
            messagebox.showerror("Error", "Cannot transfer to the same account")
            return

        # Delete old transaction
        try:
            self.db.delete_transaction(self.selected_transaction_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")
            return

        # Add new transaction
        try:
            self.db.add_transaction(
                transaction_date=date,
                amount=amount,
                from_type=from_type,
                from_id=from_id,
                to_type=to_type,
                to_id=to_id,
                description=description if description else "",
                reference=reference if reference else ""
            )

            messagebox.showinfo("Success", "Transaction updated successfully!")

            # Reset edit mode
            self.cancel_transaction_update()

            # Refresh list
            self.load_transactions_list()
            self.refresh_dashboard()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {str(e)}")

    def cancel_transaction_update(self):
        """Cancel edit mode and restore display mode"""
        # Destroy entry fields
        if hasattr(self, 'trans_detail_date_entry'):
            self.trans_detail_date_entry.destroy()
        if hasattr(self, 'trans_detail_amount_entry'):
            self.trans_detail_amount_entry.destroy()
        if hasattr(self, 'trans_detail_from_dropdown'):
            self.trans_detail_from_dropdown.destroy()
        if hasattr(self, 'trans_detail_to_dropdown'):
            self.trans_detail_to_dropdown.destroy()
        if hasattr(self, 'trans_detail_desc_entry'):
            self.trans_detail_desc_entry.destroy()
        if hasattr(self, 'trans_detail_ref_entry'):
            self.trans_detail_ref_entry.destroy()

        # Restore labels
        self.trans_detail_date.pack(side="left", fill="x", expand=True)
        self.trans_detail_amount.pack(side="left", fill="x", expand=True)
        self.trans_detail_from.pack(side="left", fill="x", expand=True)
        self.trans_detail_to.pack(side="left", fill="x", expand=True)
        self.trans_detail_desc.pack(side="left", fill="x", expand=True)
        self.trans_detail_ref.pack(side="left", fill="x", expand=True)

        # Destroy SUBMIT and CANCEL buttons
        if hasattr(self, 'transaction_submit_btn'):
            self.transaction_submit_btn.destroy()
        if hasattr(self, 'transaction_cancel_btn'):
            self.transaction_cancel_btn.destroy()

        # Restore UPDATE and DELETE buttons
        self.transaction_update_btn.pack(side="right", padx=10)
        self.transaction_delete_btn.pack(side="right", padx=10)

        # Clear selection
        self.selected_transaction_id = None
        self.transaction_update_btn.configure(state="disabled")
        self.transaction_delete_btn.configure(state="disabled")

        # Reset detail labels
        self.trans_detail_id.configure(text="--")
        self.trans_detail_date.configure(text="--")
        self.trans_detail_amount.configure(text="--", text_color="white")
        self.trans_detail_from.configure(text="--")
        self.trans_detail_to.configure(text="--")
        self.trans_detail_type.configure(text="--")
        self.trans_detail_desc.configure(text="--")
        self.trans_detail_ref.configure(text="--")

    def create_reports_tab(self):
        """Create reports tab"""
        # Title
        title = ctk.CTkLabel(
            self.tab_reports,
            text="Financial Reports",
            font=("Roboto", 24, "bold")
        )
        title.pack(pady=(20, 10))

        # Description
        desc_label = ctk.CTkLabel(
            self.tab_reports,
            text="Generate comprehensive financial reports including:\n\n"
                 "• Account Ledgers\n"
                 "• Balance Sheets\n"
                 "• Transaction Summaries\n"
                 "• Date Range Reports",
            font=("Roboto", 14),
            justify="left"
        )
        desc_label.pack(pady=30)

        # Button to open reports window
        open_btn = ctk.CTkButton(
            self.tab_reports,
            text="📊 Open Reports Window",
            height=50,
            width=250,
            font=("Roboto", 16),
            command=self.open_reports_window
        )
        open_btn.pack(pady=20)

    def create_transaction_entry_panel(self, parent):
        """Create quick transaction entry panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Quick Transaction Entry",
            font=("Roboto", 20, "bold")
        )
        title.pack(pady=(15, 10))

        # Scrollable form container to ensure buttons are always visible
        form_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Date field
        date_label = ctk.CTkLabel(form_frame, text="Date:", font=("Roboto", 13))
        date_label.pack(anchor="w", pady=(5, 3))

        self.date_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="DD-MM-YYYY",
            height=38,
            font=("Roboto", 13)
        )
        self.date_entry.pack(fill="x", pady=(0, 8))
        self.date_entry.insert(0, get_current_date())

        # Amount field
        amount_label = ctk.CTkLabel(form_frame, text="Amount:", font=("Roboto", 13))
        amount_label.pack(anchor="w", pady=(5, 3))

        self.amount_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            height=38,
            font=("Roboto", 13)
        )
        self.amount_entry.pack(fill="x", pady=(0, 8))

        # Bind event to format amount as user types
        self.amount_entry.bind("<KeyRelease>", self.format_amount_input)

        # From selection
        from_label = ctk.CTkLabel(form_frame, text="From:", font=("Roboto", 13))
        from_label.pack(anchor="w", pady=(5, 3))

        self.from_var = ctk.StringVar(value="Select...")
        self.from_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.from_var,
            values=["Select..."],
            height=38,
            font=("Roboto", 13),
            dropdown_font=("Roboto", 12)
        )
        self.from_dropdown.pack(fill="x", pady=(0, 8))

        # To selection
        to_label = ctk.CTkLabel(form_frame, text="To:", font=("Roboto", 13))
        to_label.pack(anchor="w", pady=(5, 3))

        self.to_var = ctk.StringVar(value="Select...")
        self.to_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.to_var,
            values=["Select..."],
            height=38,
            font=("Roboto", 13),
            dropdown_font=("Roboto", 12)
        )
        self.to_dropdown.pack(fill="x", pady=(0, 8))

        # Description field
        desc_label = ctk.CTkLabel(form_frame, text="Description (Optional):", font=("Roboto", 13))
        desc_label.pack(anchor="w", pady=(5, 3))

        self.desc_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Transaction description",
            height=38,
            font=("Roboto", 13)
        )
        self.desc_entry.pack(fill="x", pady=(0, 8))

        # Reference field
        ref_label = ctk.CTkLabel(form_frame, text="Reference (Optional):", font=("Roboto", 13))
        ref_label.pack(anchor="w", pady=(5, 3))

        self.ref_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Reference number",
            height=38,
            font=("Roboto", 13)
        )
        self.ref_entry.pack(fill="x", pady=(0, 10))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Submit button - Enhanced visibility (full width)
        self.submit_btn = ctk.CTkButton(
            buttons_frame,
            text="✓ SUBMIT TRANSACTION",
            height=60,
            font=("Roboto", 18, "bold"),
            corner_radius=12,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            border_width=2,
            border_color="#1e8449",
            command=self.submit_transaction
        )
        self.submit_btn.pack(fill="x")

        # Clear button - Enhanced visibility
        clear_btn = ctk.CTkButton(
            form_frame,
            text="⟲ CLEAR FORM",
            height=50,
            font=("Roboto", 16, "bold"),
            corner_radius=12,
            fg_color="#95a5a6",
            hover_color="#7f8c8d",
            border_width=2,
            border_color="#5d6d7e",
            command=self.clear_transaction_form
        )
        clear_btn.pack(fill="x", pady=(10, 0))

    def create_deposit_withdraw_panel(self, parent):
        """Create deposit/withdraw panel"""
        # Main frame
        dw_frame = ctk.CTkFrame(parent, corner_radius=10)
        dw_frame.pack(fill="x", padx=20, pady=(20, 0))

        # Title
        title = ctk.CTkLabel(
            dw_frame,
            text="💰 Cash Deposit / Withdraw",
            font=("Roboto", 18, "bold")
        )
        title.pack(pady=(20, 10))

        # Description
        desc = ctk.CTkLabel(
            dw_frame,
            text="Add or remove cash from accounts",
            font=("Roboto", 12),
            text_color="gray"
        )
        desc.pack(pady=(0, 20))

        # Form frame
        form_frame = ctk.CTkFrame(dw_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Operation type
        op_label = ctk.CTkLabel(form_frame, text="Operation:", font=("Roboto", 14))
        op_label.pack(anchor="w", pady=(0, 5))

        self.operation_var = ctk.StringVar(value="deposit")

        op_radio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        op_radio_frame.pack(fill="x", pady=(0, 15))

        deposit_radio = ctk.CTkRadioButton(
            op_radio_frame,
            text="💵 Deposit (Add Money)",
            variable=self.operation_var,
            value="deposit",
            font=("Roboto", 13)
        )
        deposit_radio.pack(side="left", padx=(0, 20))

        withdraw_radio = ctk.CTkRadioButton(
            op_radio_frame,
            text="💸 Withdraw (Remove Money)",
            variable=self.operation_var,
            value="withdraw",
            font=("Roboto", 13)
        )
        withdraw_radio.pack(side="left")

        # Entity selection
        entity_label = ctk.CTkLabel(form_frame, text="Select Account:", font=("Roboto", 14))
        entity_label.pack(anchor="w", pady=(10, 5))

        self.dw_entity_var = ctk.StringVar(value="Select...")
        self.dw_entity_dropdown = ctk.CTkOptionMenu(
            form_frame,
            variable=self.dw_entity_var,
            values=["Select..."],
            height=40,
            font=("Roboto", 14),
            dropdown_font=("Roboto", 12)
        )
        self.dw_entity_dropdown.pack(fill="x", pady=(0, 15))

        # Amount field
        amount_label = ctk.CTkLabel(form_frame, text="Amount:", font=("Roboto", 14))
        amount_label.pack(anchor="w", pady=(10, 5))

        self.dw_amount_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            height=40,
            font=("Roboto", 14)
        )
        self.dw_amount_entry.pack(fill="x", pady=(0, 15))

        # Description
        desc_label = ctk.CTkLabel(form_frame, text="Description:", font=("Roboto", 14))
        desc_label.pack(anchor="w", pady=(10, 5))

        self.dw_desc_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Optional description",
            height=40,
            font=("Roboto", 14)
        )
        self.dw_desc_entry.pack(fill="x", pady=(0, 20))

        # Submit button - Enhanced visibility
        submit_btn = ctk.CTkButton(
            form_frame,
            text="✓ EXECUTE OPERATION",
            height=60,
            font=("Roboto", 18, "bold"),
            corner_radius=12,
            fg_color="#3498db",
            hover_color="#2980b9",
            border_width=2,
            border_color="#1f618d",
            command=self.execute_deposit_withdraw
        )
        submit_btn.pack(fill="x")

    def create_balance_panel(self, parent):
        """Create balance overview panel"""
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Balance Overview",
            font=("Roboto", 24, "bold")
        )
        title.pack(pady=(20, 10))

        # Balance cards frame
        balance_frame = ctk.CTkFrame(parent, fg_color="transparent")
        balance_frame.pack(fill="x", padx=20, pady=(10, 20))

        # Company balance card
        company_card = ctk.CTkFrame(balance_frame, corner_radius=10)
        company_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            company_card,
            text="🏢 Companies",
            font=("Roboto", 16, "bold")
        ).pack(pady=(15, 5))

        self.company_balance_label = ctk.CTkLabel(
            company_card,
            text="₹0.00",
            font=("Roboto", 28, "bold"),
            text_color="green"
        )
        self.company_balance_label.pack(pady=(5, 15))

        # User balance card
        user_card = ctk.CTkFrame(balance_frame, corner_radius=10)
        user_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(
            user_card,
            text="👤 Users",
            font=("Roboto", 16, "bold")
        ).pack(pady=(15, 5))

        self.user_balance_label = ctk.CTkLabel(
            user_card,
            text="₹0.00",
            font=("Roboto", 28, "bold"),
            text_color="blue"
        )
        self.user_balance_label.pack(pady=(5, 15))

        # Accounts list section
        accounts_title = ctk.CTkLabel(
            parent,
            text="Click on any account to view ledger",
            font=("Roboto", 14),
            text_color="gray"
        )
        accounts_title.pack(pady=(10, 5))

        # Scrollable accounts list
        self.accounts_frame = ctk.CTkScrollableFrame(
            parent,
            corner_radius=8,
            height=300
        )
        self.accounts_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

    def create_recent_transactions_panel(self, parent):
        """Create recent transactions panel (placeholder)"""
        pass  # Can be added later if needed

    # Helper methods from original code
    def format_amount_input(self, event=None):
        """Format amount input in Indian numbering style"""
        try:
            cursor_pos = self.amount_entry.index("insert")
            current_value = self.amount_entry.get()
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
                groups = [reversed_num[:3]]
                remaining = reversed_num[3:]

                while remaining:
                    groups.append(remaining[:2])
                    remaining = remaining[2:]

                formatted = ','.join(groups)[::-1]
            else:
                formatted = '0'

            if decimal_part or '.' in current_value:
                formatted = f"{formatted}.{decimal_part}"

            commas_before = current_value[:cursor_pos].count(',')
            clean_cursor_pos = cursor_pos - commas_before

            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, formatted)

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

                self.amount_entry.icursor(new_pos)
            except:
                pass

        except Exception as e:
            pass

        return "break"

    def format_edit_amount_input(self, event=None):
        """Format amount input in Indian numbering style for edit mode"""
        try:
            cursor_pos = self.trans_detail_amount_entry.index("insert")
            current_value = self.trans_detail_amount_entry.get()
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
                groups = [reversed_num[:3]]
                remaining = reversed_num[3:]

                while remaining:
                    groups.append(remaining[:2])
                    remaining = remaining[2:]

                formatted = ','.join(groups)[::-1]
            else:
                formatted = '0'

            if decimal_part or '.' in current_value:
                formatted = f"{formatted}.{decimal_part}"

            commas_before = current_value[:cursor_pos].count(',')
            clean_cursor_pos = cursor_pos - commas_before

            self.trans_detail_amount_entry.delete(0, "end")
            self.trans_detail_amount_entry.insert(0, formatted)

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

                self.trans_detail_amount_entry.icursor(new_pos)
            except:
                pass

        except Exception as e:
            pass

        return "break"

    def load_data(self):
        """Load all data"""
        # Load dashboard data
        self.load_entity_data()
        self.load_balance_data()
        self.load_accounts_list()

        # Load tab-specific data
        self.load_companies()
        self.load_user_companies()  # For the company dropdown in Users tab
        self.load_users()
        self.load_transactions_list()

    def refresh_dashboard(self):
        """Refresh dashboard data after changes"""
        self.load_entity_data()
        self.load_balance_data()
        self.load_accounts_list()

    def load_entity_data(self):
        """Load entities for dropdowns"""
        entities = []

        # Get all companies
        companies = self.db.get_all_companies()
        for company in companies:
            entities.append(f"[Company] {company['name']}")

        # Get all users
        users = self.db.get_all_users()
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

        if len(entities) > 0:
            self.from_var.set(entities[0])
            self.to_var.set(entities[0])

    def load_balance_data(self):
        """Load balance overview"""
        # Get company balances
        companies = self.db.get_all_companies()
        company_total = sum(c['balance'] for c in companies)

        # Get user balances
        users = self.db.get_all_users()
        user_total = sum(u['balance'] for u in users)

        # Update labels
        self.company_balance_label.configure(text=format_currency(company_total))
        self.user_balance_label.configure(text=format_currency(user_total))

    def load_accounts_list(self):
        """Load clickable accounts list"""
        # Clear existing
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()

        # Companies section
        companies = self.db.get_all_companies()
        if companies:
            company_header = ctk.CTkLabel(
                self.accounts_frame,
                text="🏢 Companies",
                font=("Roboto", 14, "bold")
            )
            company_header.pack(anchor="w", pady=(5, 5))

            for company in companies:
                self.create_account_card(
                    self.accounts_frame,
                    'company',
                    company['id'],
                    company['name'],
                    company['balance']
                )

        # Users section
        users = self.db.get_all_users()
        if users:
            user_header = ctk.CTkLabel(
                self.accounts_frame,
                text="👤 Users",
                font=("Roboto", 14, "bold")
            )
            user_header.pack(anchor="w", pady=(15, 5))

            for user in users:
                self.create_account_card(
                    self.accounts_frame,
                    'user',
                    user['id'],
                    user['name'],
                    user['balance']
                )

    def create_account_card(self, parent, entity_type, entity_id, name, balance):
        """Create clickable account card"""
        card = ctk.CTkFrame(parent, corner_radius=8, cursor="hand2")
        card.pack(fill="x", pady=2)

        # Bind click to open ledger
        card.bind("<Button-1>", lambda e: self.open_ledger(entity_type, entity_id, name))

        # Name label
        name_label = ctk.CTkLabel(
            card,
            text=name,
            font=("Roboto", 13),
            anchor="w"
        )
        name_label.pack(side="left", padx=10, pady=8)
        name_label.bind("<Button-1>", lambda e: self.open_ledger(entity_type, entity_id, name))

        # Balance label
        balance_color = "#2ecc71" if balance >= 0 else "#e74c3c"
        balance_label = ctk.CTkLabel(
            card,
            text=format_currency(balance),
            font=("Roboto", 13, "bold"),
            text_color=balance_color,
            anchor="e"
        )
        balance_label.pack(side="right", padx=10, pady=8)
        balance_label.bind("<Button-1>", lambda e: self.open_ledger(entity_type, entity_id, name))

        # Hover effect
        def on_enter(e):
            card.configure(fg_color=("gray85", "gray30"))

        def on_leave(e):
            card.configure(fg_color=("gray90", "gray25"))

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def open_ledger(self, entity_type, entity_id, entity_name):
        """Open ledger window"""
        LedgerWindow(self.root, self.db, entity_type, entity_id, entity_name)

    # Dialog opening methods (temporary - will be integrated into tabs)
    def open_company_dialog(self):
        """Open company management dialog"""
        CompanyDialog(self.root, self.db)

    def open_user_dialog(self):
        """Open user management dialog"""
        UserDialog(self.root, self.db)

    def open_transaction_dialog(self):
        """Open transaction management dialog"""
        TransactionDialog(self.root, self.db)

    def open_reports_window(self):
        """Open reports window"""
        ReportsWindow(self.root, self.db)

    # Transaction methods
    def parse_entity_selection(self, selection: str) -> tuple:
        """Parse entity selection from dropdown"""
        if not selection or "No entities" in selection:
            return None, None, None

        if selection.startswith("[Cash]"):
            # Cash transactions use entity_id = 0
            return "cash", 0, "Cash"
        elif selection.startswith("[Company]"):
            entity_type = "company"
            name_part = selection.replace("[Company]", "").strip()
        elif selection.startswith("[User]"):
            entity_type = "user"
            name_part = selection.replace("[User]", "").strip()
            if "(" in name_part:
                name_part = name_part[:name_part.index("(")].strip()
        else:
            return None, None, None

        # Find entity by name
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
        """Submit transaction"""
        # Get values
        trans_date = self.date_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()
        reference = self.ref_entry.get().strip()

        # Validate date
        if not trans_date:
            messagebox.showerror("Error", "Please enter a date")
            return

        # Validate and parse amount
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
            messagebox.showerror("Error", "Cannot transfer to the same account")
            return

        # Confirm transaction
        confirm_msg = (
            f"Confirm Transaction:\n\n"
            f"From: {from_name} ({from_type})\n"
            f"To: {to_name} ({to_type})\n"
            f"Amount: {format_currency(amount)}\n"
            f"Date: {trans_date}\n"
            f"Description: {description if description else '(None)'}"
        )

        if not messagebox.askyesno("Confirm Transaction", confirm_msg):
            return

        # Create transaction
        try:
            self.db.add_transaction(
                transaction_date=trans_date,
                amount=amount,
                from_type=from_type,
                from_id=from_id,
                to_type=to_type,
                to_id=to_id,
                description=description,
                reference=reference
            )

            messagebox.showinfo("Success", "Transaction completed successfully!")
            self.clear_transaction_form()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {str(e)}")

    def edit_transaction_from_dashboard(self, trans: dict):
        """Populate form with transaction data for editing"""
        self.editing_transaction_id = trans['id']

        # Populate form fields
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, trans['transaction_date'])

        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(trans['amount']))

        self.desc_entry.delete(0, "end")
        self.desc_entry.insert(0, trans.get('description', ''))

        self.ref_entry.delete(0, "end")
        self.ref_entry.insert(0, trans.get('reference', ''))

        # Set dropdowns
        from_selection = f"[{trans['from_type'].capitalize()}] {trans['from_name']}"
        to_selection = f"[{trans['to_type'].capitalize()}] {trans['to_name']}"

        self.from_var.set(from_selection)
        self.to_var.set(to_selection)

        # Disable submit, enable update
        self.submit_btn.configure(state="disabled")
        # self.update_transaction_btn.configure(state="normal")  # Button removed from dashboard

        # Switch to Dashboard tab
        self.tabview.set("🏠 Dashboard")

        messagebox.showinfo("Edit Mode", "Transaction loaded for editing. Click 'Update Transaction' when ready.")

    def update_dashboard_transaction(self):
        """Update existing transaction"""
        if not self.editing_transaction_id:
            messagebox.showerror("Error", "No transaction selected for editing")
            return

        # Get values
        trans_date = self.date_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()
        reference = self.ref_entry.get().strip()

        # Validate date
        if not trans_date:
            messagebox.showerror("Error", "Please enter a date")
            return

        # Validate and parse amount
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
            messagebox.showerror("Error", "Cannot transfer to the same account")
            return

        # Confirm update
        confirm_msg = (
            f"Confirm Transaction Update:\n\n"
            f"From: {from_name} ({from_type})\n"
            f"To: {to_name} ({to_type})\n"
            f"Amount: {format_currency(amount)}\n"
            f"Date: {trans_date}\n"
            f"Description: {description if description else '(None)'}\n\n"
            f"WARNING: This will update transaction ID {self.editing_transaction_id}"
        )

        if not messagebox.askyesno("Confirm Update", confirm_msg):
            return

        # Update transaction
        try:
            # Delete old transaction and create new one (to maintain balance integrity)
            self.db.delete_transaction(self.editing_transaction_id)

            self.db.add_transaction(
                transaction_date=trans_date,
                amount=amount,
                from_type=from_type,
                from_id=from_id,
                to_type=to_type,
                to_id=to_id,
                description=description,
                reference=reference
            )

            messagebox.showinfo("Success", "Transaction updated successfully!")
            self.clear_transaction_form()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"Transaction update failed: {str(e)}")

    def execute_deposit_withdraw(self):
        """Execute deposit or withdraw operation"""
        operation = self.operation_var.get()
        amount_str = self.dw_amount_entry.get().strip()
        description = self.dw_desc_entry.get().strip()

        # Validate amount
        is_valid, amount = validate_amount(amount_str)
        if not is_valid:
            messagebox.showerror("Error", "Please enter a valid positive amount")
            return

        # Parse entity selection
        entity_type, entity_id, entity_name = self.parse_entity_selection(self.dw_entity_var.get())

        if not entity_type:
            messagebox.showerror("Error", "Please select a valid account")
            return

        # Set default description
        if not description:
            description = f"Cash {'deposit' if operation == 'deposit' else 'withdrawal'}"

        # Confirm operation
        op_text = "Deposit" if operation == "deposit" else "Withdrawal"
        confirm_msg = (
            f"Confirm {op_text}:\n\n"
            f"Account: {entity_name} ({entity_type})\n"
            f"Amount: {format_currency(amount)}\n"
            f"Description: {description}"
        )

        if not messagebox.askyesno(f"Confirm {op_text}", confirm_msg):
            return

        # Execute operation
        try:
            trans_date = get_current_date()

            if operation == "deposit":
                # Cash -> Entity (deposit)
                self.db.add_transaction(
                    transaction_date=trans_date,
                    amount=amount,
                    from_type='cash',
                    from_id=0,
                    to_type=entity_type,
                    to_id=entity_id,
                    description=description,
                    reference='DEPOSIT'
                )
            else:
                # Entity -> Cash (withdrawal)
                self.db.add_transaction(
                    transaction_date=trans_date,
                    amount=amount,
                    from_type=entity_type,
                    from_id=entity_id,
                    to_type='cash',
                    to_id=0,
                    description=description,
                    reference='WITHDRAWAL'
                )

            messagebox.showinfo("Success", f"{op_text} completed successfully!")

            # Clear form
            self.dw_amount_entry.delete(0, "end")
            self.dw_desc_entry.delete(0, "end")

            # Reload data
            self.load_data()

        except Exception as e:
            messagebox.showerror("Error", f"{op_text} failed: {str(e)}")

    def clear_transaction_form(self):
        """Clear transaction form"""
        self.editing_transaction_id = None

        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.ref_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, get_current_date())

        self.from_var.set("Select...")
        self.to_var.set("Select...")

        # Enable submit, disable update
        self.submit_btn.configure(state="normal")
        # self.update_transaction_btn.configure(state="disabled")  # Button removed from dashboard
