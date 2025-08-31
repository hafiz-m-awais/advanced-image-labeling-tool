"""
Menu Manager for the Image Labeling Tool.
Handles the creation and management of menu system.
"""

import tkinter as tk
from .constants import ACCELERATORS


class MenuManager:
    """Manages menu system for the Image Labeling Tool."""
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
    def create_menu_bar(self):
        """Create the main menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Create individual menus
        self.create_file_menu(menubar)
        self.create_edit_menu(menubar)
        
        return menubar
    
    def create_file_menu(self, menubar):
        """Create the File menu."""
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Basic file operations
        file_menu.add_command(
            label="Load Single Image", 
            command=self.controller.load_single_image, 
            accelerator=ACCELERATORS['LOAD_IMAGE']
        )
        file_menu.add_command(
            label="Load Folder", 
            command=self.controller.load_folder, 
            accelerator=ACCELERATORS['LOAD_FOLDER']
        )
        
        file_menu.add_separator()
        
        # Save operations
        file_menu.add_command(
            label="Save Annotations", 
            command=self.controller.save_annotations, 
            accelerator=ACCELERATORS['SAVE']
        )
        file_menu.add_command(
            label="Save as Master Dataset", 
            command=self.controller.save_master_dataset, 
            accelerator=ACCELERATORS['SAVE_MASTER']
        )
        
        # Load submenu
        load_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Load Annotations", menu=load_menu)
        load_menu.add_command(
            label="Load Individual Annotations", 
            command=self.controller.load_individual_annotations, 
            accelerator=ACCELERATORS['LOAD_ANNOTATIONS']
        )
        load_menu.add_command(
            label="Load Master Dataset", 
            command=self.controller.load_master_dataset, 
            accelerator=ACCELERATORS['LOAD_MASTER']
        )
        load_menu.add_command(
            label="Import COCO Annotations", 
            command=self.controller.import_coco
        )
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export Annotations", menu=export_menu)
        export_menu.add_command(
            label="Export as COCO", 
            command=self.controller.export_coco
        )
        export_menu.add_command(
            label="Export as Pascal VOC", 
            command=self.controller.export_pascal_voc
        )
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
    
    def create_edit_menu(self, menubar):
        """Create the Edit menu."""
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Label operations
        edit_menu.add_command(
            label="Add Label", 
            command=self.controller.add_label, 
            accelerator=ACCELERATORS['ADD_LABEL']
        )
        edit_menu.add_command(
            label="Delete Label", 
            command=self.controller.delete_label
        )
        
        edit_menu.add_separator()
        
        # Undo/Redo operations
        edit_menu.add_command(
            label="Undo", 
            command=self.controller.undo, 
            accelerator=ACCELERATORS['UNDO']
        )
        edit_menu.add_command(
            label="Redo", 
            command=self.controller.redo, 
            accelerator=ACCELERATORS['REDO']
        )
        edit_menu.add_command(
            label="Delete Annotation", 
            command=self.controller.delete_annotation, 
            accelerator=ACCELERATORS['DELETE']
        )