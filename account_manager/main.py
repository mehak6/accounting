"""
Account Manager - Main Application Entry Point
A modern desktop application for managing financial transactions
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import customtkinter as ctk
except ImportError:
    print("ERROR: CustomTkinter is not installed!")
    print("Please install it using: pip install customtkinter")
    sys.exit(1)

from database.db_manager import DatabaseManager
from gui.main_window import MainWindow


class AccountManagerApp:
    """Main application class"""

    def __init__(self):
        """Initialize the application"""
        # Set CustomTkinter appearance and theme
        ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
        ctk.set_default_color_theme("blue")  # Options: "blue", "dark-blue", "green"

        # Initialize database
        try:
            self.db = DatabaseManager()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Account Manager")
        self.root.geometry("1200x800")

        # Set minimum window size
        self.root.minsize(1000, 600)

        # Create main window interface
        self.main_window = MainWindow(self.root, self.db)

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run(self):
        """Run the application"""
        print("Starting Account Manager...")
        print(f"Theme: {ctk.get_appearance_mode()}")
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        # Close database connection
        if hasattr(self, 'db') and self.db:
            self.db.close()
            print("Database connection closed")

        # Destroy window
        self.root.destroy()
        print("Application closed")


def main():
    """Main entry point"""
    print("=" * 50)
    print("Account Manager v1.0.0")
    print("Modern Financial Transaction Management")
    print("=" * 50)

    # Create and run application
    app = AccountManagerApp()
    app.run()


if __name__ == "__main__":
    main()
