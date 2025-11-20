"""
Reusable Card Components - Common UI card patterns for the application
"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable, List
from utils.helpers import format_currency, format_date
from utils.config import COLORS, FONTS, SIZES, get_balance_color


class CardFactory:
    """Factory for creating reusable UI cards"""

    @staticmethod
    def create_entity_card(
        parent,
        name: str,
        balance: float,
        details: List[str] = None,
        on_click: Callable = None
    ) -> ctk.CTkFrame:
        """
        Create a standard entity card (company/user)

        Args:
            parent: Parent widget
            name: Entity name
            balance: Entity balance
            details: List of detail strings to display
            on_click: Callback when card is clicked

        Returns:
            CTkFrame card widget
        """
        card = ctk.CTkFrame(parent, corner_radius=SIZES['radius_medium'])
        card.pack(fill="x", pady=SIZES['card_margin'], padx=SIZES['card_margin'])

        if on_click:
            card.bind("<Button-1>", lambda e: on_click())

        # Content frame
        content = ctk.CTkFrame(card, fg_color=COLORS['bg_transparent'])
        content.pack(fill="x", padx=SIZES['card_padding'], pady=SIZES['card_padding'])
        if on_click:
            content.bind("<Button-1>", lambda e: on_click())

        # Name label
        name_label = ctk.CTkLabel(
            content,
            text=name,
            font=FONTS['card_title'],
            anchor="w"
        )
        name_label.pack(anchor="w")
        if on_click:
            name_label.bind("<Button-1>", lambda e: on_click())

        # Balance
        balance_text = format_currency(balance)
        balance_color = get_balance_color(balance)

        balance_label = ctk.CTkLabel(
            content,
            text=f"Balance: {balance_text}",
            font=FONTS['card_subtitle'],
            text_color=balance_color,
            anchor="w"
        )
        balance_label.pack(anchor="w")
        if on_click:
            balance_label.bind("<Button-1>", lambda e: on_click())

        # Details
        if details:
            detail_text = " | ".join([d for d in details if d])
            if detail_text:
                detail_label = ctk.CTkLabel(
                    content,
                    text=detail_text,
                    font=FONTS['card_detail'],
                    text_color=COLORS['text_secondary'],
                    anchor="w"
                )
                detail_label.pack(anchor="w")
                if on_click:
                    detail_label.bind("<Button-1>", lambda e: on_click())

        return card

    @staticmethod
    def create_transaction_card(
        parent,
        trans: Dict[str, Any],
        show_checkbox: bool = False,
        on_select: Callable = None,
        on_click: Callable = None
    ) -> ctk.CTkFrame:
        """
        Create a transaction display card

        Args:
            parent: Parent widget
            trans: Transaction dictionary
            show_checkbox: Whether to show selection checkbox
            on_select: Callback when checkbox is toggled
            on_click: Callback when card is clicked

        Returns:
            CTkFrame card widget
        """
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        # Top row: Date and ID
        top_frame = ctk.CTkFrame(content, fg_color="transparent")
        top_frame.pack(fill="x")

        # Checkbox if needed
        if show_checkbox:
            checkbox_var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                top_frame,
                text="",
                variable=checkbox_var,
                width=20,
                checkbox_width=18,
                checkbox_height=18,
                command=lambda: on_select(trans['id'], checkbox_var.get()) if on_select else None
            )
            checkbox.pack(side="left", padx=(0, 10))
            card.checkbox_var = checkbox_var

        # Date
        date_text = format_date(trans.get('transaction_date', ''), "%d-%m-%Y", "%d %b, %Y")
        ctk.CTkLabel(
            top_frame,
            text=date_text,
            font=("Roboto", 11),
            text_color="gray"
        ).pack(side="left")

        # ID
        ctk.CTkLabel(
            top_frame,
            text=f"ID: {trans['id']}",
            font=("Roboto", 10),
            text_color="gray"
        ).pack(side="right")

        # From -> To
        from_name = trans.get('from_name', 'Unknown')
        to_name = trans.get('to_name', 'Unknown')
        from_to_text = f"{from_name} → {to_name}"

        ctk.CTkLabel(
            content,
            text=from_to_text,
            font=("Roboto", 14, "bold"),
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Amount
        amount = trans.get('amount', 0)
        ctk.CTkLabel(
            content,
            text=format_currency(amount),
            font=("Roboto", 16, "bold"),
            text_color="green",
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))

        # Description if available
        description = trans.get('description', '')
        if description:
            ctk.CTkLabel(
                content,
                text=description,
                font=("Roboto", 11),
                text_color="gray",
                anchor="w",
                wraplength=400
            ).pack(anchor="w", pady=(3, 0))

        if on_click:
            card.bind("<Button-1>", lambda e: on_click())
            content.bind("<Button-1>", lambda e: on_click())

        return card

    @staticmethod
    def create_summary_card(
        parent,
        title: str,
        value: str,
        color: str = "gray"
    ) -> ctk.CTkLabel:
        """
        Create a summary statistics card

        Args:
            parent: Parent widget
            title: Card title
            value: Display value
            color: Value text color

        Returns:
            CTkLabel for the value (to allow updates)
        """
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

    @staticmethod
    def create_report_entity_card(
        parent,
        name: str,
        balance: float,
        detail: str
    ) -> ctk.CTkFrame:
        """
        Create an entity card for reports (simplified version)

        Args:
            parent: Parent widget
            name: Entity name
            balance: Entity balance
            detail: Detail text (email, company name, etc.)

        Returns:
            CTkFrame card widget
        """
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

        return card

    @staticmethod
    def create_ledger_entry_card(
        parent,
        entry: Dict[str, Any],
        show_running_balance: bool = True
    ) -> ctk.CTkFrame:
        """
        Create a ledger entry card

        Args:
            parent: Parent widget
            entry: Ledger entry dictionary
            show_running_balance: Whether to show running balance

        Returns:
            CTkFrame card widget
        """
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", pady=3, padx=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=8)

        # Top row: Date and party
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        date_text = format_date(entry.get('date', ''), "%d-%m-%Y", "%d %b, %Y")
        ctk.CTkLabel(
            top,
            text=date_text,
            font=("Roboto", 10),
            text_color="gray"
        ).pack(side="left")

        party = entry.get('party', 'Unknown')
        ctk.CTkLabel(
            top,
            text=party,
            font=("Roboto", 12, "bold")
        ).pack(side="right")

        # Bottom row: Amount and running balance
        bottom = ctk.CTkFrame(content, fg_color="transparent")
        bottom.pack(fill="x", pady=(5, 0))

        # Amount with direction indicator
        amount = entry.get('amount', 0)
        direction = entry.get('direction', '')

        if direction == 'credit':
            amount_text = f"+{format_currency(amount)}"
            amount_color = "green"
        else:
            amount_text = f"-{format_currency(amount)}"
            amount_color = "red"

        ctk.CTkLabel(
            bottom,
            text=amount_text,
            font=("Roboto", 14, "bold"),
            text_color=amount_color
        ).pack(side="left")

        # Running balance
        if show_running_balance and 'running_balance' in entry:
            running = entry['running_balance']
            balance_color = "green" if running >= 0 else "red"
            ctk.CTkLabel(
                bottom,
                text=f"Bal: {format_currency(running)}",
                font=("Roboto", 11),
                text_color=balance_color
            ).pack(side="right")

        return card
