"""
Constants and configuration settings for the Image Labeling Tool.
"""

# UI Colors
COLORS = {
    'BACKGROUND': '#2C3E50',
    'PANEL': '#34495E',
    'PRIMARY': '#3498DB',
    'SUCCESS': '#27AE60',
    'WARNING': '#F39C12',
    'DANGER': '#E74C3C',
    'PURPLE': '#9B59B6',
    'HIGHLIGHT': '#FF0400',
    'SECONDARY': '#95A5A6',
    'INFO': '#E67E22',
    'WHITE': 'white',
    'CANVAS_BG': 'white'
}

# Default values
DEFAULTS = {
    'WINDOW_SIZE': '1400x800',
    'ANNOTATION_COLOR': '#FF0000',
    'ZOOM_FACTOR': 1.0,
    'MIN_ZOOM': 0.1,
    'MAX_ZOOM': 5.0,
    'MAX_UNDO_STEPS': 50,
    'VERTEX_THRESHOLD': 10,
    'EDGE_THRESHOLD': 5,
    'VERTEX_SIZE': 4,
    'VERTEX_SIZE_SELECTED': 6
}

# Supported image formats
SUPPORTED_FORMATS = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'
)

# File type filters for dialogs
FILE_TYPES = {
    'IMAGES': [
        ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("PNG files", "*.png"),
        ("All files", "*.*")
    ],
    'JSON': [
        ("JSON files", "*.json"),
        ("All files", "*.*")
    ]
}

# Tool types
TOOLS = ["None", "Point", "Rectangle", "Circle", "Polygon"]

# UI Configuration
UI_CONFIG = {
    'FONT_DEFAULT': ('Arial', 9),
    'FONT_BOLD': ('Arial', 10, 'bold'),
    'FONT_SMALL': ('Arial', 8),
    'LISTBOX_HEIGHT': 4,
    'PANEL_WIDTH': 300,
    'CONTROLS_HEIGHT': 50
}

# Annotation types for validation
ANNOTATION_TYPES = ['Point', 'Rectangle', 'Circle', 'Polygon']

# Menu accelerators
ACCELERATORS = {
    'LOAD_IMAGE': 'Ctrl+I',
    'LOAD_FOLDER': 'Ctrl+O',
    'SAVE': 'Ctrl+S',
    'SAVE_MASTER': 'Ctrl+Shift+S',
    'LOAD_ANNOTATIONS': 'Ctrl+L',
    'LOAD_MASTER': 'Ctrl+Shift+L',
    'ADD_LABEL': 'Ctrl+N',
    'UNDO': 'Ctrl+Z',
    'REDO': 'Ctrl+Y',
    'DELETE': 'Del'
}