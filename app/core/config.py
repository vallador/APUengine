import os

# ── Project Metadata ──────────────────────────────────────────
VERSION = "3.1"
AUTHOR  = "Ingeniería Integral FC"

# ── Theme & Branded Colors ────────────────────────────────────
# Corporate Green
C_ACCENT = "#008000"

# Main Palette - Light Mode
THEME_LIGHT = {
    'primary': '#212529',
    'secondary': '#343a40',
    'accent': C_ACCENT,
    'bg': '#f8f9fa',
    'text': '#212529',
    'tree_bg': '#ffffff',
    'tree_fg': '#000000',
    'header_bg': C_ACCENT,
    'header_fg': '#ffffff'
}

# Main Palette - Dark Mode
THEME_DARK = {
    'primary': '#121212',
    'secondary': '#333333',
    'accent': C_ACCENT,
    'bg': '#1e1e1e',
    'text': '#e0e0e0',
    'tree_bg': '#2d2d2d',
    'tree_fg': '#ffffff',
    'header_bg': C_ACCENT,
    'header_fg': '#ffffff'
}

# Excel Colors (Hex without #)
EXCEL_PALETTE = {
    'header': '008000',
    'total': '008000',
    'material': 'D5E8D4',
    'equipment': 'DAE8FC',
    'labor': 'FFF2CC',
    'aiu_row': 'E8E8E8'
}

# ── Database Configuration ─────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_ENGINE = os.path.join(BASE_DIR, "engine.db")
DB_DESTINO = os.path.join(BASE_DIR, "destino.db")

# ── Business Logic Constants ──────────────────────────────────
LABOR_FACTOR = 1.40  # 40% Prestaciones Sociales
AIU_DEFAULTS = {
    'admin': 0.10,
    'impr': 0.05,
    'util': 0.10
}
