"""
User Dialog - Manage users (Add, Edit, Delete, View)
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any

from database.db_manager import DatabaseManager
from utils.helpers import format_currency, validate_email


class UserDialog:
    """Dialog for managing users"""

    def __init__(self, parent, db: DatabaseManager):
        """
        Initialize user dialog

        Args:
            parent: Parent window
            db: Database manager instance
        """
        self.parent = parent
        self.db = db
        self.selected_user_id = None

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("User Management")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Create UI
        self.create_ui()
        self.load_users()

    def create_ui(self):
        """Create dialog UI"""
        # Main container with two columns
        main_container = ctk.CTkFrame(self.dialog)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Left: User list
        left_frame = ctk.CTkFrame(main_container, corner_radius=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right: User details form
        right_frame = ctk.CTkFrame(main_container, corner_radius=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

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
        self.name_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Email field
        ctk.CTkLabel(form_frame, text="Email:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Role field
        ctk.CTkLabel(form_frame, text="Role:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.role_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.role_entry.pack(fill="x", pady=(0, 10))

        # Department field
        ctk.CTkLabel(form_frame, text="Department:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.department_entry = ctk.CTkEntry(form_frame, height=35, font=("Roboto", 13))
        self.department_entry.pack(fill="x", pady=(0, 10))

        # Company selection
        ctk.CTkLabel(form_frame, text="Company:", font=("Roboto", 13)).pack(anchor="w", pady=(10, 5))
        self.company_combo = ctk.CTkComboBox(
            form_frame,
            height=35,
            font=("Roboto", 13),
            values=["None"],
            state="readonly"
        )
        self.company_combo.pack(fill="x", pady=(0, 10))
        self.load_companies()

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
            text="➕ Add User",
            height=40,
            corner_radius=8,
            command=self.add_user
        )
        self.add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Update button
        self.update_btn = ctk.CTkButton(
            button_frame,
            text="💾 Update",
            height=40,
            corner_radius=8,
            command=self.update_user,
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
            command=self.delete_user,
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
        """Load companies into dropdown"""
        companies = self.db.get_all_companies()
        company_names = ["None"] + [c['name'] for c in companies]
        self.company_combo.configure(values=company_names)
        self.company_combo.set("None")

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

    def create_user_card(self, user: Dict[str, Any]):
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

    def select_user(self, user: Dict[str, Any]):
        """Select a user to edit"""
        self.selected_user_id = user['id']

        # Populate form
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, user['name'])

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, user.get('email', ''))

        self.role_entry.delete(0, "end")
        self.role_entry.insert(0, user.get('role', ''))

        self.department_entry.delete(0, "end")
        self.department_entry.insert(0, user.get('department', ''))

        # Set company
        if user.get('company_id'):
            company = self.db.get_company(user['company_id'])
            if company:
                self.company_combo.set(company['name'])
        else:
            self.company_combo.set("None")

        balance = user.get('balance', 0.0)
        self.balance_label.configure(text=format_currency(balance))

        # Enable update/delete buttons
        self.update_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")

    def add_user(self):
        """Add new user"""
        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name is required")
            return

        email = self.email_entry.get().strip()
        role = self.role_entry.get().strip()
        department = self.department_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Get company ID
        company_id = None
        company_name = self.company_combo.get()
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
            self.clear_form()
            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")

    def update_user(self):
        """Update selected user"""
        if not self.selected_user_id:
            messagebox.showerror("Error", "No user selected")
            return

        # Validate inputs
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name is required")
            return

        email = self.email_entry.get().strip()
        role = self.role_entry.get().strip()
        department = self.department_entry.get().strip()

        # Validate email if provided
        if email and not validate_email(email):
            messagebox.showerror("Error", "Invalid email address")
            return

        # Get company ID
        company_id = None
        company_name = self.company_combo.get()
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
            self.clear_form()
            self.load_users()

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
            self.clear_form()
            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {str(e)}")

    def clear_form(self):
        """Clear form and reset selection"""
        self.selected_user_id = None

        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.role_entry.delete(0, "end")
        self.department_entry.delete(0, "end")
        self.company_combo.set("None")
        self.balance_label.configure(text="₹0.00")

        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
