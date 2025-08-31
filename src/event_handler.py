"""
Event Handler for the Image Labeling Tool.
Manages all event binding and handling for the application.
"""

import tkinter as tk


class EventHandler:
    """Handles all event binding and processing for the Image Labeling Tool."""
    
    def __init__(self, controller):
        self.controller = controller
        
    def bind_all_events(self):
        """Bind all events for the application."""
        self.bind_canvas_events()
        self.bind_keyboard_shortcuts()
        self.bind_listbox_events()
        
    def bind_canvas_events(self):
        """Bind canvas-related events."""
        canvas = self.controller.ui_manager.get_widget('canvas')
        if not canvas:
            return
            
        # Mouse events
        canvas.bind("<Button-1>", self.controller.on_canvas_click)
        canvas.bind("<B1-Motion>", self.controller.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.controller.on_canvas_release)
        canvas.bind("<Button-3>", self.controller.on_canvas_right_click)
        
        # Mouse wheel events for zooming
        canvas.bind("<MouseWheel>", self.controller.on_mouse_wheel)  # Windows
        canvas.bind("<Button-4>", self.controller.on_mouse_wheel)    # Linux scroll up
        canvas.bind("<Button-5>", self.controller.on_mouse_wheel)    # Linux scroll down
        
        # Focus for keyboard events
        canvas.focus_set()
        
    def bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts."""
        root = self.controller.root
        
        # File operations
        root.bind("<Control-i>", lambda e: self.controller.load_single_image())
        root.bind("<Control-o>", lambda e: self.controller.load_folder())
        root.bind("<Control-s>", lambda e: self.controller.save_annotations())
        root.bind("<Control-Shift-S>", lambda e: self.controller.save_master_dataset())
        root.bind("<Control-l>", lambda e: self.controller.load_individual_annotations())
        root.bind("<Control-Shift-L>", lambda e: self.controller.load_master_dataset())
        
        # Edit operations
        root.bind("<Control-n>", lambda e: self.controller.add_label())
        root.bind("<Control-z>", lambda e: self.controller.undo())
        root.bind("<Control-y>", lambda e: self.controller.redo())
        root.bind("<Control-Shift-Z>", lambda e: self.controller.redo())  # Alternative redo
        root.bind("<Delete>", lambda e: self.controller.delete_annotation())
        
        # Drawing operations
        root.bind("<Escape>", lambda e: self.controller.cancel_drawing())
        root.bind("<Return>", lambda e: self.controller.complete_polygon())
        
    def bind_listbox_events(self):
        """Bind listbox selection events."""
        # Image listbox
        image_listbox = self.controller.ui_manager.get_widget('image_listbox')
        if image_listbox:
            image_listbox.bind('<<ListboxSelect>>', self.controller.on_image_select)
            
        # Labels listbox
        labels_listbox = self.controller.ui_manager.get_widget('labels_listbox')
        if labels_listbox:
            labels_listbox.bind('<<ListboxSelect>>', self.controller.on_label_select)
            
        # Annotations listbox
        annotations_listbox = self.controller.ui_manager.get_widget('annotations_listbox')
        if annotations_listbox:
            annotations_listbox.bind('<<ListboxSelect>>', self.controller.on_annotation_select)