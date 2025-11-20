"""
Application Configuration - Centralized settings for colors, fonts, and sizes
"""

# =============================================================================
# COLOR SCHEME
# =============================================================================

COLORS = {
    # Primary colors
    'primary': '#1f538d',
    'primary_hover': '#14375e',
    'secondary': '#2b2b2b',

    # Status colors
    'success': '#28a745',
    'success_dark': '#1e7b34',
    'danger': '#dc3545',
    'danger_dark': '#a71d2a',
    'warning': '#ffc107',
    'info': '#17a2b8',

    # Balance colors
    'positive_balance': 'green',
    'negative_balance': 'red',
    'neutral': 'gray',

    # Text colors
    'text_primary': 'white',
    'text_secondary': 'gray',
    'text_muted': '#6c757d',

    # Background colors
    'bg_card': '#2b2b2b',
    'bg_transparent': 'transparent',
    'bg_highlight': '#3d3d3d',

    # Button colors
    'btn_primary': '#1f538d',
    'btn_success': '#28a745',
    'btn_danger': '#dc3545',
    'btn_secondary': '#6c757d',
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================

FONTS = {
    # Font family
    'family': 'Roboto',

    # Headings
    'heading_large': ('Roboto', 24, 'bold'),
    'heading_medium': ('Roboto', 20, 'bold'),
    'heading_small': ('Roboto', 16, 'bold'),

    # Body text
    'body_large': ('Roboto', 15),
    'body_medium': ('Roboto', 13),
    'body_small': ('Roboto', 11),

    # Special
    'card_title': ('Roboto', 15, 'bold'),
    'card_subtitle': ('Roboto', 13),
    'card_detail': ('Roboto', 11),
    'button': ('Roboto', 13),
    'label': ('Roboto', 12),
    'input': ('Roboto', 13),

    # Currency/Numbers
    'amount_large': ('Roboto', 28, 'bold'),
    'amount_medium': ('Roboto', 18, 'bold'),
    'amount_small': ('Roboto', 16, 'bold'),
}

# =============================================================================
# SIZES AND DIMENSIONS
# =============================================================================

SIZES = {
    # Window dimensions
    'window_width': 1200,
    'window_height': 700,
    'dialog_width': 500,
    'dialog_height': 600,

    # Padding and margins
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 15,
    'padding_xl': 20,

    # Border radius
    'radius_small': 5,
    'radius_medium': 8,
    'radius_large': 10,

    # Button dimensions
    'btn_height': 35,
    'btn_height_small': 30,
    'btn_width': 120,
    'btn_width_small': 80,

    # Input dimensions
    'input_height': 35,
    'input_width': 200,

    # Card dimensions
    'card_padding': 10,
    'card_margin': 5,

    # Sidebar
    'sidebar_width': 200,

    # List items
    'list_item_height': 40,
}

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

APP_SETTINGS = {
    'app_name': 'Account Manager',
    'version': '1.2.0',

    # Pagination
    'items_per_page': 50,
    'max_search_results': 100,

    # Validation
    'max_name_length': 100,
    'max_description_length': 500,
    'max_email_length': 254,
    'max_phone_length': 15,

    # Date format
    'date_format_display': '%d %B, %Y',
    'date_format_input': '%d-%m-%Y',
    'date_format_db': '%d-%m-%Y',

    # Currency
    'currency_symbol': '₹',
    'decimal_places': 2,
}

# =============================================================================
# THEME CONFIGURATION
# =============================================================================

THEME = {
    'mode': 'dark',  # 'dark' or 'light'
    'color_theme': 'blue',  # customtkinter theme
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_balance_color(balance: float) -> str:
    """Get color based on balance value"""
    if balance > 0:
        return COLORS['positive_balance']
    elif balance < 0:
        return COLORS['negative_balance']
    return COLORS['neutral']


def get_font(font_key: str) -> tuple:
    """Get font tuple by key"""
    return FONTS.get(font_key, FONTS['body_medium'])


def get_color(color_key: str) -> str:
    """Get color by key"""
    return COLORS.get(color_key, COLORS['text_primary'])


def get_size(size_key: str) -> int:
    """Get size by key"""
    return SIZES.get(size_key, 10)
