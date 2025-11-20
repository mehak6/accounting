"""
Reports Window - Financial reports and analytics
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, Any, List

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, format_date, export_to_pdf, normalize_date_for_sort


class ReportsWindow:
    """Window for viewing financial reports and analytics"""

    def __init__(self, parent, db: DatabaseManager):
        """
        Initialize reports window

        Args:
            parent: Parent window
            db: Database manager instance
        """
        self.parent = parent
        self.db = db
        self.transaction_sort_order = "desc"  # Default: newest first

        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Financial Reports")
        self.window.geometry("1000x700")
        self.window.transient(parent)

        # Create UI
        self.create_ui()
        self.load_reports()

    def create_ui(self):
        """Create reports window UI"""
        # Main container
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title bar
        title_bar = ctk.CTkFrame(main_container, corner_radius=10)
        title_bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            title_bar,
            text="📊 Financial Reports",
            font=("Roboto", 24, "bold")
        ).pack(side="left", padx=20, pady=15)

        # Export button
        export_btn = ctk.CTkButton(
            title_bar,
            text="📄 Export to PDF",
            height=35,
            width=150,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=self.export_report
        )
        export_btn.pack(side="right", padx=20)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            title_bar,
            text="🔄 Refresh",
            height=35,
            width=100,
            command=self.load_reports
        )
        refresh_btn.pack(side="right", padx=5)

        # Content area with tabs
        self.create_tabs(main_container)

    def create_tabs(self, parent):
        """Create tabbed interface for different reports"""
        # Tab view
        self.tabview = ctk.CTkTabview(parent, corner_radius=10)
        self.tabview.pack(fill="both", expand=True)

        # Add tabs
        self.tabview.add("Summary")
        self.tabview.add("Companies")
        self.tabview.add("Users")
        self.tabview.add("Transactions")

        # Create content for each tab
        self.create_summary_tab()
        self.create_companies_tab()
        self.create_users_tab()
        self.create_transactions_tab()

    def create_summary_tab(self):
        """Create summary overview tab"""
        tab = self.tabview.tab("Summary")

        # Summary cards container
        cards_container = ctk.CTkFrame(tab, fg_color="transparent")
        cards_container.pack(fill="x", pady=20, padx=20)

        # Row 1: Balance cards
        balance_row = ctk.CTkFrame(cards_container, fg_color="transparent")
        balance_row.pack(fill="x", pady=(0, 15))

        self.summary_company_balance = self.create_summary_card(
            balance_row, "Company Balances", "₹0.00", "green"
        )
        self.summary_user_balance = self.create_summary_card(
            balance_row, "User Balances", "₹0.00", "green"
        )
        self.summary_total_balance = self.create_summary_card(
            balance_row, "Total Balance", "₹0.00", "blue"
        )

        # Row 2: Transaction stats
        trans_row = ctk.CTkFrame(cards_container, fg_color="transparent")
        trans_row.pack(fill="x", pady=(0, 15))

        self.summary_trans_count = self.create_summary_card(
            trans_row, "Total Transactions", "0", "gray"
        )
        self.summary_trans_total = self.create_summary_card(
            trans_row, "Total Amount", "₹0.00", "purple"
        )
        self.summary_trans_avg = self.create_summary_card(
            trans_row, "Average Amount", "₹0.00", "orange"
        )

        # Row 3: Entity counts
        entity_row = ctk.CTkFrame(cards_container, fg_color="transparent")
        entity_row.pack(fill="x")

        self.summary_company_count = self.create_summary_card(
            entity_row, "Companies", "0", "gray"
        )
        self.summary_user_count = self.create_summary_card(
            entity_row, "Users", "0", "gray"
        )

    def create_summary_card(self, parent, title: str, value: str, color: str) -> ctk.CTkLabel:
        """Create a summary statistics card"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(side="left", fill="both", expand=True, padx=10)

        ctk.CTkLabel(
            card,
            text=title,
            font=("Roboto", 14)
        ).pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Roboto", 28, "bold"),
            text_color=color
        )
        value_label.pack(pady=(0, 15))

        return value_label

    def create_companies_tab(self):
        """Create companies report tab"""
        tab = self.tabview.tab("Companies")

        # Title
        ctk.CTkLabel(
            tab,
            text="Company Balances",
            font=("Roboto", 18, "bold")
        ).pack(pady=(15, 10))

        # Scrollable list
        self.companies_list = ctk.CTkScrollableFrame(tab, corner_radius=8)
        self.companies_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_users_tab(self):
        """Create users report tab"""
        tab = self.tabview.tab("Users")

        # Title
        ctk.CTkLabel(
            tab,
            text="User Balances",
            font=("Roboto", 18, "bold")
        ).pack(pady=(15, 10))

        # Scrollable list
        self.users_list = ctk.CTkScrollableFrame(tab, corner_radius=8)
        self.users_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_transactions_tab(self):
        """Create transactions report tab"""
        tab = self.tabview.tab("Transactions")

        # Header with title and sort dropdown
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title
        ctk.CTkLabel(
            header_frame,
            text="Transaction History",
            font=("Roboto", 18, "bold")
        ).pack(side="left")

        # Sort dropdown
        sort_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        sort_frame.pack(side="right")

        ctk.CTkLabel(
            sort_frame,
            text="Sort:",
            font=("Roboto", 12)
        ).pack(side="left", padx=(0, 5))

        self.trans_sort_var = ctk.StringVar(value="Newest First ↓")
        self.trans_sort_dropdown = ctk.CTkOptionMenu(
            sort_frame,
            variable=self.trans_sort_var,
            values=["Newest First ↓", "Oldest First ↑"],
            width=140,
            height=30,
            command=self.change_transaction_sort
        )
        self.trans_sort_dropdown.pack(side="left")

        # Scrollable list
        self.transactions_list = ctk.CTkScrollableFrame(tab, corner_radius=8)
        self.transactions_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_reports(self):
        """Load all report data"""
        self.load_summary()
        self.load_companies_report()
        self.load_users_report()
        self.load_transactions_report()

    def load_summary(self):
        """Load summary statistics"""
        # Balance totals
        balances = self.db.get_total_balances()
        self.summary_company_balance.configure(text=format_currency(balances['company_total']))
        self.summary_user_balance.configure(text=format_currency(balances['user_total']))
        self.summary_total_balance.configure(text=format_currency(balances['grand_total']))

        # Transaction summary
        trans_summary = self.db.get_transaction_summary()
        self.summary_trans_count.configure(text=str(trans_summary['total_count']))
        self.summary_trans_total.configure(text=format_currency(trans_summary['total_amount']))
        self.summary_trans_avg.configure(text=format_currency(trans_summary['average_amount']))

        # Entity counts
        companies = self.db.get_all_companies()
        users = self.db.get_all_users()
        self.summary_company_count.configure(text=str(len(companies)))
        self.summary_user_count.configure(text=str(len(users)))

    def load_companies_report(self):
        """Load companies balance report"""
        # Clear existing
        for widget in self.companies_list.winfo_children():
            widget.destroy()

        companies = self.db.get_all_companies()

        if not companies:
            ctk.CTkLabel(
                self.companies_list,
                text="No companies",
                text_color="gray"
            ).pack(pady=20)
            return

        # Sort by balance (descending)
        companies.sort(key=lambda x: x.get('balance', 0), reverse=True)

        # Display each company
        for company in companies:
            self.create_entity_report_card(
                self.companies_list,
                company['name'],
                company.get('balance', 0),
                f"📧 {company.get('email', 'N/A')}"
            )

    def load_users_report(self):
        """Load users balance report"""
        # Clear existing
        for widget in self.users_list.winfo_children():
            widget.destroy()

        users = self.db.get_all_users()

        if not users:
            ctk.CTkLabel(
                self.users_list,
                text="No users",
                text_color="gray"
            ).pack(pady=20)
            return

        # Sort by balance (descending)
        users.sort(key=lambda x: x.get('balance', 0), reverse=True)

        # Display each user
        for user in users:
            # Get company name
            company_text = "No company"
            if user.get('company_id'):
                company = self.db.get_company(user['company_id'])
                if company:
                    company_text = f"🏢 {company['name']}"

            self.create_entity_report_card(
                self.users_list,
                user['name'],
                user.get('balance', 0),
                company_text
            )

    def create_entity_report_card(self, parent, name: str, balance: float, detail: str):
        """Create an entity report card"""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Left: Name and detail
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left,
            text=name,
            font=("Roboto", 15, "bold"),
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=detail,
            font=("Roboto", 11),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")

        # Right: Balance
        balance_color = "green" if balance >= 0 else "red"
        ctk.CTkLabel(
            content,
            text=format_currency(balance),
            font=("Roboto", 18, "bold"),
            text_color=balance_color
        ).pack(side="right", padx=10)

    def load_transactions_report(self):
        """Load transactions report with sorting"""
        # Clear existing
        for widget in self.transactions_list.winfo_children():
            widget.destroy()

        transactions = self.db.get_all_transactions()

        if not transactions:
            ctk.CTkLabel(
                self.transactions_list,
                text="No transactions",
                text_color="gray"
            ).pack(pady=20)
            return

        # Sort transactions based on current sort order
        if self.transaction_sort_order == "desc":
            transactions.sort(key=lambda t: (normalize_date_for_sort(t.get('transaction_date', '')), t.get('id', 0)), reverse=True)
        else:
            transactions.sort(key=lambda t: (normalize_date_for_sort(t.get('transaction_date', '')), t.get('id', 0)))

        # Display each transaction
        for trans in transactions:
            self.create_transaction_report_card(trans)

    def change_transaction_sort(self, choice: str):
        """Change transaction sort order"""
        if choice == "Newest First ↓":
            self.transaction_sort_order = "desc"
        else:
            self.transaction_sort_order = "asc"
        self.load_transactions_report()

    def create_transaction_report_card(self, trans: Dict[str, Any]):
        """Create a transaction report card"""
        card = ctk.CTkFrame(self.transactions_list, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        # Top: Date and ID
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        date_text = format_date(trans['transaction_date'], "%d-%m-%Y", "%d %b, %Y")
        ctk.CTkLabel(
            top,
            text=date_text,
            font=("Roboto", 11),
            text_color="gray"
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text=f"ID: {trans['id']}",
            font=("Roboto", 10),
            text_color="gray"
        ).pack(side="right")

        # Middle: From -> To
        from_to = f"{trans['from_name']} → {trans['to_name']}"
        ctk.CTkLabel(
            content,
            text=from_to,
            font=("Roboto", 14, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Bottom: Amount
        ctk.CTkLabel(
            content,
            text=format_currency(trans['amount']),
            font=("Roboto", 16, "bold"),
            text_color="green",
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

    def export_report(self):
        """Export current report to PDF"""
        # Get current tab
        current_tab = self.tabview.get()

        # Determine what to export
        if current_tab == "Summary":
            messagebox.showinfo("Info", "Please select a specific report tab to export (Companies, Users, or Transactions)")
            return

        # Ask for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Export Report to PDF"
        )

        if not filename:
            return

        try:
            if current_tab == "Companies":
                data = self.db.get_all_companies()
                fieldnames = ['id', 'name', 'address', 'phone', 'email', 'balance']
                title = "Company Balances Report"

            elif current_tab == "Users":
                data = self.db.get_all_users()
                fieldnames = ['id', 'name', 'email', 'role', 'department', 'balance']
                title = "User Balances Report"

            elif current_tab == "Transactions":
                data = self.db.get_all_transactions()
                # Sort by current sort order
                if self.transaction_sort_order == "desc":
                    data.sort(key=lambda t: (normalize_date_for_sort(t.get('transaction_date', '')), t.get('id', 0)), reverse=True)
                else:
                    data.sort(key=lambda t: (normalize_date_for_sort(t.get('transaction_date', '')), t.get('id', 0)))
                fieldnames = ['id', 'transaction_date', 'amount', 'from_name', 'to_name', 'description']
                title = "Transaction History Report"

            export_to_pdf(data, filename, title, fieldnames)
            messagebox.showinfo("Success", f"Report exported successfully to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
