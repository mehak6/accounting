# Account Management Software - Project Report

## Project Overview
A window-based desktop application for managing financial transactions between multiple companies and users. The system tracks money transfers, maintains transaction history, and provides comprehensive financial records for all entities.

## Technology Stack Recommendation
- **Language**: Python 3.13.7 (already installed)
- **GUI Framework**: CustomTkinter (modern UI library with dark/light themes)
- **Database**: SQLite (built-in, lightweight file-based database)
- **Additional Libraries**:
  - `customtkinter` (modern Tkinter wrapper - install via: `pip install customtkinter`)
  - `sqlite3` (built-in for database operations)
  - `datetime` (built-in for timestamps)
  - `json` (built-in for configuration)

### Why CustomTkinter?
- **Modern Look**: Rounded corners, smooth animations, professional appearance
- **Small File Size**: ~10-15MB executable (very lightweight)
- **Easy Migration**: Built on Tkinter, minimal code changes needed
- **Built-in Themes**: Dark/Light mode support with blue, dark-blue, and green themes
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **HighDPI Support**: Crisp display on high-resolution screens

## Core Features to Implement

### 1. Company Management
- Add/Edit/Delete companies
- Company details: Name, Address, Contact Info, Account Balance
- Company financial overview

### 2. User Management
- Add/Edit/Delete users within companies
- User details: Name, Email, Role, Department, Account Balance
- User financial overview

### 3. Transaction Management (Core Feature)
- **Company-to-Company Transactions**: Money transfers between companies
- **Company-to-User Transactions**: Payments from companies to users
- **User-to-Company Transactions**: Payments from users to companies
- **User-to-User Transactions**: Money transfers between users
- Transaction details: Date, Amount, From/To entities, Description, Reference

### 4. Transaction Entry Interface
- Quick transaction entry with date and amount
- Dropdown selection for source and destination (companies/users)
- Transaction type auto-detection based on selected entities
- Transaction validation and confirmation

### 5. Financial Reporting
- Account balances for all companies and users
- Transaction history with filtering options
- Financial summaries and reports
- Export transaction data (CSV, PDF)

### 6. Data Management
- SQLite database for persistent storage
- Data backup and restore functionality
- Import/Export capabilities (CSV format)

## File Structure
```
account_manager/
├── main.py                 # Main application entry point
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── company_dialog.py   # Company management dialogs
│   ├── user_dialog.py      # User management dialogs
│   ├── transaction_dialog.py # Transaction entry dialog
│   └── reports_window.py   # Financial reports window
├── database/
│   ├── __init__.py
│   ├── db_manager.py       # Database operations
│   └── models.py           # Data models
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Utility functions
└── data/
    └── financial_data.db   # SQLite database file
```

## Implementation Steps

### Phase 1: Core Setup
1. Create project directory structure
2. Set up SQLite database with tables:
   - Companies (id, name, address, phone, email, balance, created_date)
   - Users (id, company_id, name, email, role, department, balance, created_date)
   - Transactions (id, transaction_date, amount, from_type, from_id, to_type, to_id, description, reference, created_date)
   - Transaction_Types (id, type_name, description)

### Phase 2: GUI Development
1. Create main window with transaction entry form
2. Implement company management interface
3. Implement user management interface
4. Implement transaction entry dialog
5. Create financial reports and balance overview

### Phase 3: Core Functionality
1. Transaction processing and balance updates
2. Database CRUD operations for all entities
3. Data validation and error handling
4. Search and filter capabilities for transactions
5. Balance calculation and tracking

### Phase 4: Advanced Features
1. Data backup/restore
2. Import/Export functionality
3. Reporting features
4. User preferences and settings

## User Interface Design

### Main Window Layout (CustomTkinter Modern Design)
- **Menu Bar**: File, Edit, View, Transactions, Reports, Help
- **Toolbar**: Modern rounded buttons (New Transaction, View Reports, Add Company/User)
- **Transaction Entry Panel**:
  - Date picker with modern styling
  - Amount field with rounded corners
  - From/To selection dropdowns (CTkComboBox)
  - Submit button with hover effects
- **Recent Transactions Panel**: Scrollable frame with transaction cards
- **Balance Overview Panel**: Modern cards showing balances with color indicators
- **Status Bar**: Minimalist status information with theme toggle
- **Theme Support**: Dark/Light mode toggle button

### Design Features
- **Color Scheme**: Professional blue theme (customizable)
- **Rounded Corners**: All widgets use corner_radius for modern look
- **Consistent Spacing**: 20px padding, 10px spacing between elements
- **Font Styling**: Roboto font family with size hierarchy
- **Hover Effects**: Smooth transitions on buttons and interactive elements

### Key Windows/Dialogs
1. **Transaction Entry**: Quick transaction input with validation
2. **Company Management**: Add/edit company information and view balances
3. **User Management**: Manage users within companies and view balances
4. **Transaction History**: View and filter all transactions
5. **Financial Reports**: Balance sheets, transaction summaries, profit/loss
6. **Search/Filter**: Advanced search across transactions and entities
7. **Settings**: Application preferences and backup options

## Database Schema

### Companies Table
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    phone TEXT,
    email TEXT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT,
    department TEXT,
    balance DECIMAL(15,2) DEFAULT 0.00,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id)
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    from_type TEXT NOT NULL CHECK (from_type IN ('company', 'user')),
    from_id INTEGER NOT NULL,
    to_type TEXT NOT NULL CHECK (to_type IN ('company', 'user')),
    to_id INTEGER NOT NULL,
    description TEXT,
    reference TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transaction Types Table
```sql
CREATE TABLE transaction_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE,
    description TEXT
);
```

## Security Considerations
- Input validation for all user inputs
- SQL injection prevention using parameterized queries
- Data backup recommendations
- User access logging

## Future Enhancements
- Multi-user support with authentication
- Network database support (PostgreSQL/MySQL)
- Advanced reporting with charts
- Email integration for notifications
- Export to multiple formats (PDF, Excel)

## Estimated Timeline
- **Phase 1**: 1-2 days
- **Phase 2**: 2-3 days
- **Phase 3**: 2-3 days
- **Phase 4**: 1-2 days
- **Total**: 6-10 days

## Next Steps
1. Confirm requirements and feature priorities
2. Create project directory structure
3. Begin with database setup and core models
4. Develop main GUI framework
5. Implement core CRUD operations
6. Add advanced features incrementally

## Dependencies
Minimal dependencies - mostly Python standard library:
- `customtkinter` for modern GUI (install: `pip install customtkinter`)
- `sqlite3` for database (built-in)
- `datetime` for timestamps (built-in)
- `json` for configuration (built-in)
- `csv` for import/export (built-in)

**Installation:**
```bash
pip install customtkinter
```