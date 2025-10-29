# Account Manager

A modern desktop application for managing financial transactions between companies and users.

![Python Version](https://img.shields.io/badge/python-3.13.7-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Modern UI**: Built with CustomTkinter for a sleek, professional appearance
- **Company Management**: Add, edit, and track companies with their balances
- **User Management**: Manage users and associate them with companies
- **Transaction Processing**: Record money transfers between any entities
- **Financial Reports**: View balance overviews and transaction history
- **Export to CSV**: Export reports for external analysis
- **Dark/Light Themes**: Toggle between dark and light modes
- **SQLite Database**: Lightweight, file-based database with no setup required

## Screenshots

The application features:
- Quick transaction entry panel on the main dashboard
- Balance overview cards showing real-time financial data
- Recent transactions display with modern card design
- Company and user management dialogs
- Comprehensive financial reports with export functionality

## Installation

### Prerequisites

- Python 3.13.7 (or Python 3.8+)
- pip (Python package installer)

### Setup

1. **Install CustomTkinter** (only required dependency):
   ```bash
   pip install customtkinter
   ```

2. **Navigate to the application directory**:
   ```bash
   cd F:/accounting/account_manager
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

That's it! The application will automatically create the database on first run.

## Usage

### First Time Setup

1. **Add Companies**:
   - Click "🏢 Companies" in the menu bar
   - Click "➕ Add Company"
   - Fill in company details
   - Click "Add Company"

2. **Add Users**:
   - Click "👤 Users" in the menu bar
   - Click "➕ Add User"
   - Fill in user details and optionally assign to a company
   - Click "Add User"

3. **Create Transactions**:
   - Use the Quick Transaction Entry panel on the main dashboard
   - Or click "💸 Transactions" for the full transaction manager

### Daily Operations

**Quick Transaction Entry (Main Dashboard)**:
1. Enter the date (defaults to today)
2. Enter the amount
3. Select the sender (From)
4. Select the receiver (To)
5. Optionally add description and reference
6. Click "Submit Transaction"

**View Reports**:
- Click "📊 Reports" to view:
  - Summary statistics
  - Company balances
  - User balances
  - Recent transactions
- Export any report to CSV

**Manage Entities**:
- Use the menu bar buttons to manage companies and users
- Click on any entity in the list to edit or delete

### Theme Toggle

Click the theme button (🌙 Dark / ☀️ Light) in the top-right corner to switch themes.

## Project Structure

```
account_manager/
├── main.py                 # Application entry point
├── README.md               # This file
├── gui/                    # User interface components
│   ├── __init__.py
│   ├── main_window.py      # Main dashboard
│   ├── company_dialog.py   # Company management
│   ├── user_dialog.py      # User management
│   ├── transaction_dialog.py # Transaction manager
│   └── reports_window.py   # Financial reports
├── database/               # Database layer
│   ├── __init__.py
│   ├── db_manager.py       # Database operations
│   └── models.py           # Data models
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── helpers.py          # Helper functions
└── data/                   # Database storage
    └── financial_data.db   # SQLite database (auto-created)
```

## Database Schema

### Companies Table
- `id`: Unique identifier
- `name`: Company name
- `address`: Company address
- `phone`: Phone number
- `email`: Email address
- `balance`: Current balance
- `created_date`: Creation timestamp

### Users Table
- `id`: Unique identifier
- `company_id`: Associated company (optional)
- `name`: User name
- `email`: Email address
- `role`: Job role
- `department`: Department
- `balance`: Current balance
- `created_date`: Creation timestamp

### Transactions Table
- `id`: Unique identifier
- `transaction_date`: Transaction date
- `amount`: Transaction amount
- `from_type`: Sender type (company/user)
- `from_id`: Sender ID
- `to_type`: Receiver type (company/user)
- `to_id`: Receiver ID
- `description`: Transaction description
- `reference`: Reference number
- `created_date`: Creation timestamp

## Features in Detail

### Transaction Types

The application supports four types of transactions:
1. **Company to Company**: Money transfers between companies
2. **Company to User**: Payments from companies to users (e.g., salaries)
3. **User to Company**: Payments from users to companies (e.g., expenses)
4. **User to User**: Money transfers between users

### Balance Tracking

- Balances are automatically updated when transactions are created
- Deleting a transaction reverses the balance changes
- Real-time balance display on all screens

### Data Export

Export reports to CSV format for:
- Companies and their balances
- Users and their balances
- Complete transaction history

## Troubleshooting

**Issue**: Application won't start
- **Solution**: Make sure CustomTkinter is installed: `pip install customtkinter`

**Issue**: Database errors
- **Solution**: Delete `data/financial_data.db` and restart (will recreate a fresh database)

**Issue**: Display issues on high-DPI screens
- **Solution**: CustomTkinter automatically handles high-DPI displays. Restart the application if issues persist.

**Issue**: Transaction balance errors
- **Solution**: Ensure sender and receiver are different entities

## Development

### Adding New Features

The application is modular and easy to extend:

- **New GUI components**: Add to `gui/` folder
- **New database operations**: Add to `database/db_manager.py`
- **New utilities**: Add to `utils/helpers.py`

### Running in Development Mode

```bash
python main.py
```

Console output will show:
- Database initialization status
- Current theme
- Application events

## Technical Details

- **GUI Framework**: CustomTkinter (modern Tkinter wrapper)
- **Database**: SQLite3 (Python built-in)
- **File Size**: ~10-15MB when packaged as executable
- **Performance**: Handles thousands of transactions efficiently
- **Cross-Platform**: Works on Windows, macOS, and Linux

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the project report: `../account_manager_project_report.md`
3. Check CustomTkinter documentation: https://customtkinter.tomschimansky.com

## Version History

- **v1.0.0** (2025): Initial release
  - Company and user management
  - Transaction processing
  - Financial reports
  - CSV export
  - Dark/Light themes

---

**Built with ❤️ using Python and CustomTkinter**
