# Material Design 3 Color Palette
# Primary colors
PRIMARY = "#6750A4"
PRIMARY_CONTAINER = "#EADDFF"
ON_PRIMARY = "#FFFFFF"
ON_PRIMARY_CONTAINER = "#21005D"

# Secondary colors
SECONDARY = "#625B71"
SECONDARY_CONTAINER = "#E8DEF8"
ON_SECONDARY = "#FFFFFF"
ON_SECONDARY_CONTAINER = "#1D192B"

# Surface colors
SURFACE = "#1C1B1F"
SURFACE_VARIANT = "#49454F"
SURFACE_CONTAINER = "#211F26"
SURFACE_CONTAINER_HIGH = "#2B2930"
SURFACE_CONTAINER_HIGHEST = "#36343B"
ON_SURFACE = "#E6E1E5"
ON_SURFACE_VARIANT = "#CAC4D0"

# Background
BACKGROUND = "rgba(28,27,31,0.85)"  # Material semi-transparent surface
ON_BACKGROUND = "#E6E1E5"

# Error colors
ERROR = "#F2B8B5"
ON_ERROR = "#601410"
ERROR_CONTAINER = "#8C1D18"

# Success colors
SUCCESS = "#A6D4A3"
ON_SUCCESS = "#0F2E0C"
SUCCESS_CONTAINER = "#2A5A26"

# Legacy color mappings for compatibility
BG_MAIN = BACKGROUND
BG_LEFT = SURFACE_CONTAINER
BG_RIGHT = SURFACE_CONTAINER_HIGH
COLOR_ACCENT = PRIMARY
BTN_RECORD = ERROR
BTN_PLAY = SUCCESS
BTN_STOP = SURFACE_VARIANT
BTN_TEXT = ON_PRIMARY
TAB_ACTIVE = PRIMARY_CONTAINER
TAB_INACTIVE = SURFACE_CONTAINER
TAB_ACTIVE_TEXT = ON_PRIMARY_CONTAINER
TAB_INACTIVE_TEXT = ON_SURFACE_VARIANT
LABEL_TEXT = ON_SURFACE
TRANSCRIPT_TEXT = ON_SURFACE_VARIANT
LINE = ON_SURFACE_VARIANT
CONSOLE_BG = SURFACE
CONSOLE_TEXT = ON_SURFACE
SETTINGS_BG = SURFACE_CONTAINER
SETTINGS_TEXT = ON_SURFACE_VARIANT

# Material Design 3 scrollbar
SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {SURFACE_VARIANT};
        border-radius: 4px;
        min-height: 40px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {PRIMARY};
    }}
    QScrollBar::handle:vertical:pressed {{
        background: {PRIMARY};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {SURFACE_VARIANT};
        border-radius: 4px;
        min-width: 40px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {PRIMARY};
    }}
    QScrollBar::handle:horizontal:pressed {{
        background: {PRIMARY};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
        width: 0px;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: none;
    }}
"""

# Material Design 3 button styles
BUTTON_FILLED = f"""
    QPushButton {{
        background: {PRIMARY};
        color: {ON_PRIMARY};
        border: none;
        border-radius: 20px;
        font-weight: 500;
        padding: 10px 24px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {PRIMARY};
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.3);
    }}
    QPushButton:pressed {{
        background: {PRIMARY};
        box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    QPushButton:disabled {{
        background: {SURFACE_VARIANT};
        color: {ON_SURFACE_VARIANT};
    }}
"""

BUTTON_OUTLINED = f"""
    QPushButton {{
        background: transparent;
        color: {PRIMARY};
        border: 1px solid {PRIMARY};
        border-radius: 20px;
        font-weight: 500;
        padding: 10px 24px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: rgba(103, 80, 164, 0.08);
    }}
    QPushButton:pressed {{
        background: rgba(103, 80, 164, 0.12);
    }}
    QPushButton:disabled {{
        border-color: {SURFACE_VARIANT};
        color: {ON_SURFACE_VARIANT};
    }}
"""

BUTTON_TEXT = f"""
    QPushButton {{
        background: transparent;
        color: {PRIMARY};
        border: none;
        border-radius: 20px;
        font-weight: 500;
        padding: 10px 12px;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: rgba(103, 80, 164, 0.08);
    }}
    QPushButton:pressed {{
        background: rgba(103, 80, 164, 0.12);
    }}
    QPushButton:disabled {{
        color: {ON_SURFACE_VARIANT};
    }}
"""

# Material Design 3 card style
CARD_STYLE = f"""
    QFrame {{
        background: {SURFACE_CONTAINER};
        border-radius: 12px;
        border: none;
    }}
"""

# Material Design 3 elevated card style
CARD_ELEVATED_STYLE = f"""
    QFrame {{
        background: {SURFACE_CONTAINER_HIGH};
        border-radius: 12px;
        border: none;
    }}
"""
