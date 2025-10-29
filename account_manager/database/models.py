"""
Data Models - Represents entities in the database
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    """Company data model"""
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    balance: float = 0.0
    created_date: Optional[datetime] = None

    def __str__(self):
        return self.name

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'balance': self.balance,
            'created_date': self.created_date
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create Company from dictionary"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            balance=data.get('balance', 0.0),
            created_date=data.get('created_date')
        )


@dataclass
class User:
    """User data model"""
    id: Optional[int] = None
    company_id: Optional[int] = None
    name: str = ""
    email: str = ""
    role: str = ""
    department: str = ""
    balance: float = 0.0
    created_date: Optional[datetime] = None

    def __str__(self):
        return self.name

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department': self.department,
            'balance': self.balance,
            'created_date': self.created_date
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create User from dictionary"""
        return cls(
            id=data.get('id'),
            company_id=data.get('company_id'),
            name=data.get('name', ''),
            email=data.get('email', ''),
            role=data.get('role', ''),
            department=data.get('department', ''),
            balance=data.get('balance', 0.0),
            created_date=data.get('created_date')
        )


@dataclass
class Transaction:
    """Transaction data model"""
    id: Optional[int] = None
    transaction_date: str = ""
    amount: float = 0.0
    from_type: str = ""  # 'company' or 'user'
    from_id: int = 0
    from_name: str = ""  # Populated from joins
    to_type: str = ""  # 'company' or 'user'
    to_id: int = 0
    to_name: str = ""  # Populated from joins
    description: str = ""
    reference: str = ""
    created_date: Optional[datetime] = None

    def __str__(self):
        return f"{self.from_name} → {self.to_name}: ${self.amount:.2f}"

    def get_transaction_type(self):
        """Get human-readable transaction type"""
        type_map = {
            ('company', 'company'): 'Company to Company',
            ('company', 'user'): 'Company to User',
            ('user', 'company'): 'User to Company',
            ('user', 'user'): 'User to User'
        }
        return type_map.get((self.from_type, self.to_type), 'Unknown')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'transaction_date': self.transaction_date,
            'amount': self.amount,
            'from_type': self.from_type,
            'from_id': self.from_id,
            'from_name': self.from_name,
            'to_type': self.to_type,
            'to_id': self.to_id,
            'to_name': self.to_name,
            'description': self.description,
            'reference': self.reference,
            'created_date': self.created_date
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create Transaction from dictionary"""
        return cls(
            id=data.get('id'),
            transaction_date=data.get('transaction_date', ''),
            amount=data.get('amount', 0.0),
            from_type=data.get('from_type', ''),
            from_id=data.get('from_id', 0),
            from_name=data.get('from_name', ''),
            to_type=data.get('to_type', ''),
            to_id=data.get('to_id', 0),
            to_name=data.get('to_name', ''),
            description=data.get('description', ''),
            reference=data.get('reference', ''),
            created_date=data.get('created_date')
        )


@dataclass
class TransactionType:
    """Transaction Type data model"""
    id: Optional[int] = None
    type_name: str = ""
    description: str = ""

    def __str__(self):
        return self.type_name

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type_name': self.type_name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create TransactionType from dictionary"""
        return cls(
            id=data.get('id'),
            type_name=data.get('type_name', ''),
            description=data.get('description', '')
        )
