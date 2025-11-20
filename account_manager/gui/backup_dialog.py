"""
Backup Dialog - Database backup and restore functionality
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, Any, List
import os

from database.db_manager import DatabaseManager
from utils.helpers import handle_error, show_success, show_warning, confirm_action
from utils.config import COLORS, FONTS, SIZES


class BackupDialog:
    """Dialog for database backup and restore operations"""

    def __init__(self, parent, db: DatabaseManager):
        """
        Initialize backup dialog

        Args:
            parent: Parent window
            db: Database manager instance
        """
        self.parent = parent
        self.db = db

        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Database Backup & Restore")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 600) // 2
        y = (self.dialog.winfo_screenheight() - 500) // 2
        self.dialog.geometry(f"600x500+{x}+{y}")

        self.create_ui()
        self.load_backups()

    def create_ui(self):
        """Create the dialog UI"""
        # Title
        title_label = ctk.CTkLabel(
            self.dialog,
            text="Database Backup & Restore",
            font=FONTS['heading_medium']
        )
        title_label.pack(pady=(20, 10))

        # Info text
        info_label = ctk.CTkLabel(
            self.dialog,
            text="Create backups of your financial data to prevent data loss.\nRestore from a backup to recover previous data.",
            font=FONTS['body_small'],
            text_color=COLORS['text_secondary']
        )
        info_label.pack(pady=(0, 20))

        # Action buttons frame
        action_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)

        # Create Backup button
        self.backup_btn = ctk.CTkButton(
            action_frame,
            text="Create Backup",
            command=self.create_backup,
            fg_color=COLORS['btn_success'],
            hover_color=COLORS['success_dark'],
            height=40,
            font=FONTS['button']
        )
        self.backup_btn.pack(side="left", padx=(0, 10))

        # Import Backup button
        self.import_btn = ctk.CTkButton(
            action_frame,
            text="Import Backup",
            command=self.import_backup,
            fg_color=COLORS['btn_primary'],
            height=40,
            font=FONTS['button']
        )
        self.import_btn.pack(side="left", padx=(0, 10))

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            action_frame,
            text="Refresh",
            command=self.load_backups,
            fg_color=COLORS['btn_secondary'],
            width=80,
            height=40,
            font=FONTS['button']
        )
        self.refresh_btn.pack(side="right")

        # Backups list label
        list_label = ctk.CTkLabel(
            self.dialog,
            text="Available Backups:",
            font=FONTS['body_large'],
            anchor="w"
        )
        list_label.pack(fill="x", padx=20, pady=(20, 5))

        # Scrollable frame for backups
        self.backup_list_frame = ctk.CTkScrollableFrame(
            self.dialog,
            height=250
        )
        self.backup_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Close button
        close_btn = ctk.CTkButton(
            self.dialog,
            text="Close",
            command=self.dialog.destroy,
            fg_color=COLORS['btn_secondary'],
            width=100,
            height=35
        )
        close_btn.pack(pady=(0, 20))

    def load_backups(self):
        """Load and display available backups"""
        # Clear existing items
        for widget in self.backup_list_frame.winfo_children():
            widget.destroy()

        try:
            backups = self.db.get_backup_list()

            if not backups:
                no_backup_label = ctk.CTkLabel(
                    self.backup_list_frame,
                    text="No backups found. Create your first backup!",
                    font=FONTS['body_medium'],
                    text_color=COLORS['text_secondary']
                )
                no_backup_label.pack(pady=20)
                return

            for backup in backups:
                self.create_backup_card(backup)

        except Exception as e:
            handle_error(e, "Failed to load backups")

    def create_backup_card(self, backup: Dict[str, Any]):
        """Create a card for a backup entry"""
        card = ctk.CTkFrame(self.backup_list_frame, corner_radius=SIZES['radius_medium'])
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        # Left side - info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        # Filename
        ctk.CTkLabel(
            info_frame,
            text=backup['filename'],
            font=FONTS['card_title'],
            anchor="w"
        ).pack(anchor="w")

        # Details
        size_mb = backup['size'] / (1024 * 1024)
        detail_text = f"Created: {backup['created']} | Size: {size_mb:.2f} MB"
        ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=FONTS['card_detail'],
            text_color=COLORS['text_secondary'],
            anchor="w"
        ).pack(anchor="w")

        # Right side - buttons
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(side="right")

        # Restore button
        restore_btn = ctk.CTkButton(
            btn_frame,
            text="Restore",
            command=lambda p=backup['path']: self.restore_backup(p),
            fg_color=COLORS['btn_primary'],
            width=80,
            height=30,
            font=FONTS['body_small']
        )
        restore_btn.pack(side="left", padx=(0, 5))

        # Delete button
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            command=lambda p=backup['path']: self.delete_backup(p),
            fg_color=COLORS['btn_danger'],
            hover_color=COLORS['danger_dark'],
            width=70,
            height=30,
            font=FONTS['body_small']
        )
        delete_btn.pack(side="left")

    def create_backup(self):
        """Create a new backup"""
        try:
            backup_path = self.db.create_backup()
            show_success(f"Backup created successfully!\n\nSaved to:\n{backup_path}")
            self.load_backups()
        except Exception as e:
            handle_error(e, "Failed to create backup")

    def import_backup(self):
        """Import a backup from external location"""
        filepath = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )

        if not filepath:
            return

        try:
            # Copy to backup directory
            import shutil
            backup_dir = os.path.dirname(self.db.db_path)
            filename = os.path.basename(filepath)

            # Ensure unique name
            if not filename.startswith('backup_'):
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"backup_{timestamp}_imported.db"

            dest_path = os.path.join(backup_dir, filename)
            shutil.copy2(filepath, dest_path)

            show_success(f"Backup imported successfully!\n\nSaved as:\n{filename}")
            self.load_backups()

        except Exception as e:
            handle_error(e, "Failed to import backup")

    def restore_backup(self, backup_path: str):
        """Restore from a backup"""
        if not confirm_action(
            "Are you sure you want to restore from this backup?\n\n"
            "WARNING: This will replace ALL current data with the backup data.\n"
            "A safety backup of current data will be created first.",
            "Confirm Restore"
        ):
            return

        try:
            self.db.restore_from_backup(backup_path)
            show_success(
                "Database restored successfully!\n\n"
                "Please restart the application to see the restored data."
            )
            self.dialog.destroy()
        except Exception as e:
            handle_error(e, "Failed to restore from backup")

    def delete_backup(self, backup_path: str):
        """Delete a backup"""
        filename = os.path.basename(backup_path)

        if not confirm_action(
            f"Are you sure you want to delete this backup?\n\n{filename}\n\n"
            "This action cannot be undone.",
            "Confirm Delete"
        ):
            return

        try:
            self.db.delete_backup(backup_path)
            show_success("Backup deleted successfully!")
            self.load_backups()
        except Exception as e:
            handle_error(e, "Failed to delete backup")
