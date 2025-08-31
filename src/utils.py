"""
Utility functions for the Image Labeling Tool.
"""

import os
import json
from datetime import datetime
from .constants import SUPPORTED_FORMATS


def get_current_date():
    """Get current date in ISO format."""
    return datetime.now().isoformat()


def is_image_file(filepath):
    """Check if a file is a supported image format."""
    return filepath.lower().endswith(SUPPORTED_FORMATS)


def find_image_files(directory):
    """Find all supported image files in a directory."""
    image_files = []
    try:
        for filename in sorted(os.listdir(directory)):
            filepath = os.path.join(directory, filename)
            if is_image_file(filepath):
                image_files.append(filepath)
    except (OSError, PermissionError):
        pass
    return image_files


def validate_json_file(filepath):
    """Validate if a file is a valid JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return False


def safe_float_conversion(value, default=0.0):
    """Safely convert a value to float with a default fallback."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int_conversion(value, default=0):
    """Safely convert a value to int with a default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def point_to_line_distance(x, y, x1, y1, x2, y2):
    """Calculate the distance from point (x,y) to line segment (x1,y1)-(x2,y2)."""
    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1
    
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    if len_sq == 0:
        return calculate_distance(x, y, x1, y1)
        
    param = dot / len_sq
    
    if param < 0:
        return calculate_distance(x, y, x1, y1)
    elif param > 1:
        return calculate_distance(x, y, x2, y2)
    
    x_proj = x1 + param * C
    y_proj = y1 + param * D
    
    return calculate_distance(x, y, x_proj, y_proj)


def calculate_polygon_area(coords):
    """Calculate the area of a polygon using the shoelace formula."""
    n = len(coords) // 2
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i*2] * coords[j*2+1]
        area -= coords[i*2+1] * coords[j*2]
    return abs(area) / 2


def clamp_value(value, min_val, max_val):
    """Clamp a value between min and max bounds."""
    return max(min_val, min(value, max_val))


def get_basename_without_ext(filepath):
    """Get filename without extension from a filepath."""
    return os.path.splitext(os.path.basename(filepath))[0]


def ensure_directory_exists(directory):
    """Ensure a directory exists, create it if it doesn't."""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def format_coordinates(coords, precision=1):
    """Format coordinates for display with specified precision."""
    if not coords:
        return ""
    
    if len(coords) == 2:  # Point
        return f"({coords[0]:.{precision}f}, {coords[1]:.{precision}f})"
    elif len(coords) == 4:  # Rectangle/Circle
        return f"({coords[0]:.{precision}f}, {coords[1]:.{precision}f}) to ({coords[2]:.{precision}f}, {coords[3]:.{precision}f})"
    else:  # Polygon
        num_points = len(coords) // 2
        return f"{num_points} vertices"


def normalize_coordinates(coords):
    """Normalize coordinates to ensure consistency."""
    if len(coords) == 4:  # Rectangle/Circle
        x1, y1, x2, y2 = coords
        return [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
    return coords