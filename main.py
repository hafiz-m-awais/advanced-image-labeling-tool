#!/usr/bin/env python3
"""
Advanced Image Labeling Tool - Main Entry Point
A comprehensive tool for image annotation with support for various shapes and formats.
"""

import tkinter as tk
from src.image_labeling_tool import ImageLabelingTool


def main():
    """Main entry point for the Image Labeling Tool application."""
    root = tk.Tk()
    app = ImageLabelingTool(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()