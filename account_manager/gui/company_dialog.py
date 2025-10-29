"""
Company Dialog - Manage companies (Add, Edit, Delete, View)
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, validate_email


class CompanyDialog:
    """Dialog for managing companies"""

    def __init__(self, parent, db: DatabaseManager):
        """
        Initialize company dialog

        Args:
            parent: Parent window
            db: Database manager instance
        """
        self.parent = parent
        self.db = db
        self.selected_company_id = None

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Company Management")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create UI
        self.create_ui()
        self.load_companies()

    def create_ui(self):
        """Create dialog UI"""
        # Main container with two columns
        main_container = ctk.CTkFrame(self.dialog)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Left: Company list
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right: Company details form
        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

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
        self.name_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Address field
        ctk.CTkLabel(form_frame, text="Address:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.address_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.address_entry.pack(fill="x", pady=(0, 10))

        # Phone field
        ctk.CTkLabel(form_frame, text="Phone:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.phone_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Email field
        ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Balance display (read-only)
        ctk.CTkLabel(form_frame, text="Current Balance:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.balance_label = ctk.CTkLabel(
            form_frame,
            text="₹0.00",
            font=("Roboto", 18, "bold"),
            text_color="green"
        )
        self.balance_label.pack(anchor="w", pady=(0, 15))

        # Buttons frame
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # Add button
        self.add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add Company",
            height=40,
            corner_radius=8,
            command=self.add_company
        )
        self.add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Update button
        self.update_btn = ctk.CTkButton(
            button_frame,
            text="💾 Update",
            height=40,
            corner_radius=8,
            command=self.update_company,
            state="disabled"
        )
        self.update_btn.pack(side="left", fill="x", expand=True, padx=5)

        # Delete button
        self.delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            height=40,
            corner_radius=8,
            fg_color="red",
            hover_color="darkred",
            command=self.delete_company,
            state="disabled"
        )
        self.delete_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Clear button
        clear_btn = ctk.CTkButton(
            form_frame,
            text="Clear Form",
            height=35,
            corner_radius=8,
            fg_color="gray",
            hover_color="darkgray",
            command=self.clear_form
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

    def create_company_card(self, company: Dict[str, Any]):
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

    def select_company(self, company: Dict[str, Any]):
        """Select a company to edit"""
        self.selected_company_id = company['id']

        # Populate form
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, company['name'])

        self.address_entry.delete(0, "end")
        self.address_entry.insert(0, company.get('address', ''))

        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, company.get('phone', ''))

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, company.get('email', ''))

        balance = company.get('balance', 0.0)
        self.balance_label.configure(text=format_currency(balance))

        # Enable update/delete buttons
        self.update_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")

    def add_company(self):
        """Add new company"""
        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

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
            self.clear_form()
            self.load_companies()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add company: {str(e)}")

    def update_company(self):
        """Update selected company"""
        if not self.selected_company_id:
            messagebox.showerror("Error", "No company selected")
            return

        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Company name is required")
            return

        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

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
            self.clear_form()
            self.load_companies()

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
            self.clear_form()
            self.load_companies()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete company: {str(e)}")

    def clear_form(self):
        """Clear form and reset selection"""
        self.selected_company_id = None

        self.name_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.balance_label.configure(text="₹0.00")

        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
