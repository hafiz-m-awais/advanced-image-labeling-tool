"""
UI Manager for the Image Labeling Tool - FIXED VERSION
Handles the creation and management of UI components.
"""

import tkinter as tk
from tkinter import ttk
from .constants import COLORS, UI_CONFIG, TOOLS


class UIManager:
    """Manages UI components and layout for the Image Labeling Tool."""
    
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.widgets = {}
        
    def setup_main_window(self):
        """Setup main window properties."""
        self.root.title("Advanced Image Labeling Tool")
        self.root.geometry("1400x800")
        self.root.configure(bg=COLORS['BACKGROUND'])
        
    def create_main_layout(self):
        """Create the main application layout."""
        # Main container
        main_container = tk.Frame(self.root, bg=COLORS['BACKGROUND'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel
        self.create_left_panel(main_container)
        
        # Right panel
        self.create_right_panel(main_container)
        
        # Center panel
        self.create_center_panel(main_container)
        
        # Status bar
        self.create_status_bar()
        
        return main_container
    
    def create_left_panel(self, parent):
        """Create left panel with file operations and image list."""
        left_panel = tk.Frame(parent, bg=COLORS['PANEL'], width=UI_CONFIG['PANEL_WIDTH'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # File operations frame
        self.create_file_operations_frame(left_panel)
        
        # Image list frame
        self.create_image_list_frame(left_panel)
        
        self.widgets['left_panel'] = left_panel
        
    def create_file_operations_frame(self, parent):
        """Create file operations frame."""
        file_frame = tk.LabelFrame(parent, text="File Operations", 
                                  bg=COLORS['PANEL'], fg=COLORS['WHITE'], 
                                  font=UI_CONFIG['FONT_BOLD'])
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File operation buttons
        buttons = [
            ("Load Single Image", self.controller.load_single_image, COLORS['PURPLE']),
            ("Load Folder", self.controller.load_folder, COLORS['PRIMARY']),
            ("Save Annotations", self.controller.save_annotations, COLORS['SUCCESS']),
            ("Load Annotations", self.controller.load_annotations, COLORS['WARNING'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(file_frame, text=text, command=command,
                           bg=color, fg=COLORS['WHITE'], 
                           font=UI_CONFIG['FONT_BOLD'])
            btn.pack(fill=tk.X, pady=2)
            
        self.widgets['file_frame'] = file_frame
    
    def create_image_list_frame(self, parent):
        """Create image list frame."""
        image_frame = tk.LabelFrame(parent, text="Image List", 
                                   bg=COLORS['PANEL'], fg=COLORS['WHITE'], 
                                   font=UI_CONFIG['FONT_BOLD'])
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image listbox with scrollbar
        listbox_frame = tk.Frame(image_frame, bg=COLORS['PANEL'])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        image_listbox = tk.Listbox(listbox_frame, bg=COLORS['BACKGROUND'], fg=COLORS['WHITE'],
                                  selectbackground=COLORS['PRIMARY'], 
                                  font=UI_CONFIG['FONT_DEFAULT'])
        scrollbar_images = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        image_listbox.config(yscrollcommand=scrollbar_images.set)
        scrollbar_images.config(command=image_listbox.yview)
        
        image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_images.pack(side=tk.RIGHT, fill=tk.Y)
        
        image_listbox.bind('<<ListboxSelect>>', self.controller.on_image_select)
        
        self.widgets['image_listbox'] = image_listbox
        
    def create_right_panel(self, parent):
        """Create right panel with tools and annotations."""
        right_panel = tk.Frame(parent, bg=COLORS['PANEL'], width=UI_CONFIG['PANEL_WIDTH'])
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Tools frame
        self.create_tools_frame(right_panel)
        
        # Labels frame
        self.create_labels_frame(right_panel)
        
        # Annotations frame
        self.create_annotations_frame(right_panel)
        
        self.widgets['right_panel'] = right_panel
    
    def create_tools_frame(self, parent):
        """Create annotation tools frame."""
        tools_frame = tk.LabelFrame(parent, text="Annotation Tools",
                                   bg=COLORS['PANEL'], fg=COLORS['WHITE'], 
                                   font=UI_CONFIG['FONT_BOLD'])
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Tool selection
        tk.Label(tools_frame, text="Tool:", bg=COLORS['PANEL'], fg=COLORS['WHITE']).pack(anchor=tk.W, padx=5)
        
        tool_var = tk.StringVar(value="None")
        tool_combo = ttk.Combobox(tools_frame, textvariable=tool_var, 
                                 values=TOOLS, state="readonly", width=15)
        tool_combo.pack(fill=tk.X, padx=5, pady=2)
        tool_combo.bind('<<ComboboxSelected>>', self.controller.on_tool_change)
        
        # Color selection
        color_frame = tk.Frame(tools_frame, bg=COLORS['PANEL'])
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(color_frame, text="Color:", bg=COLORS['PANEL'], fg=COLORS['WHITE']).pack(side=tk.LEFT)
        tk.Button(color_frame, text="Choose", command=self.controller.choose_color,
                 bg=COLORS['DANGER'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.RIGHT)
        
        self.widgets['tool_var'] = tool_var
        self.widgets['tools_frame'] = tools_frame
    
    def create_labels_frame(self, parent):
        """Create labels management frame - FIXED with Edit button."""
        labels_frame = tk.LabelFrame(parent, text="Labels",
                                    bg=COLORS['PANEL'], fg=COLORS['WHITE'], 
                                    font=UI_CONFIG['FONT_BOLD'])
        labels_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label operations - FIXED: Added Edit button
        label_ops_frame = tk.Frame(labels_frame, bg=COLORS['PANEL'])
        label_ops_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(label_ops_frame, text="Add", command=self.controller.add_label,
                 bg=COLORS['SUCCESS'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.LEFT, padx=2)
        tk.Button(label_ops_frame, text="Edit", command=self.controller.edit_label,
                 bg=COLORS['WARNING'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.LEFT, padx=2)
        tk.Button(label_ops_frame, text="Delete", command=self.controller.delete_label,
                 bg=COLORS['DANGER'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.LEFT, padx=2)
        
        # Labels listbox
        labels_listbox_frame = tk.Frame(labels_frame, bg=COLORS['PANEL'])
        labels_listbox_frame.pack(fill=tk.X, padx=5, pady=5)
        
        labels_listbox = tk.Listbox(labels_listbox_frame, bg=COLORS['BACKGROUND'], fg=COLORS['WHITE'],
                                   selectbackground=COLORS['PRIMARY'], 
                                   height=UI_CONFIG['LISTBOX_HEIGHT'], 
                                   font=UI_CONFIG['FONT_DEFAULT'])
        scrollbar_labels = tk.Scrollbar(labels_listbox_frame, orient=tk.VERTICAL)
        labels_listbox.config(yscrollcommand=scrollbar_labels.set)
        scrollbar_labels.config(command=labels_listbox.yview)
        
        labels_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_labels.pack(side=tk.RIGHT, fill=tk.Y)
        
        labels_listbox.bind('<<ListboxSelect>>', self.controller.on_label_select)
        
        self.widgets['labels_listbox'] = labels_listbox
    
    def create_annotations_frame(self, parent):
        """Create annotations management frame."""
        annotations_frame = tk.LabelFrame(parent, text="Current Annotations",
                                         bg=COLORS['PANEL'], fg=COLORS['WHITE'], 
                                         font=UI_CONFIG['FONT_BOLD'])
        annotations_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Annotation operations
        ann_ops_frame = tk.Frame(annotations_frame, bg=COLORS['PANEL'])
        ann_ops_frame.pack(fill=tk.X, padx=5, pady=2)
        
        buttons = [
            ("Edit", self.controller.edit_annotation, COLORS['WARNING']),
            ("Delete", self.controller.delete_annotation, COLORS['DANGER']),
            ("Undo", self.controller.undo, COLORS['SECONDARY'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(ann_ops_frame, text=text, command=command,
                           bg=color, fg=COLORS['WHITE'], 
                           font=UI_CONFIG['FONT_SMALL'])
            btn.pack(side=tk.LEFT, padx=2)
        
        # Annotations listbox
        ann_listbox_frame = tk.Frame(annotations_frame, bg=COLORS['PANEL'])
        ann_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        annotations_listbox = tk.Listbox(ann_listbox_frame, bg=COLORS['BACKGROUND'], fg=COLORS['WHITE'],
                                        selectbackground=COLORS['PRIMARY'], 
                                        font=UI_CONFIG['FONT_DEFAULT'])
        scrollbar_ann = tk.Scrollbar(ann_listbox_frame, orient=tk.VERTICAL)
        annotations_listbox.config(yscrollcommand=scrollbar_ann.set)
        scrollbar_ann.config(command=annotations_listbox.yview)
        
        annotations_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_ann.pack(side=tk.RIGHT, fill=tk.Y)
        
        annotations_listbox.bind('<<ListboxSelect>>', self.controller.on_annotation_select)
        
        self.widgets['annotations_listbox'] = annotations_listbox
        
    def create_center_panel(self, parent):
        """Create center panel with canvas and controls."""
        center_panel = tk.Frame(parent, bg=COLORS['BACKGROUND'])
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas frame
        self.create_canvas_frame(center_panel)
        
        # Controls frame
        self.create_controls_frame(center_panel)
        
        self.widgets['center_panel'] = center_panel
    
    def create_canvas_frame(self, parent):
        """Create canvas frame with scrollbars."""
        canvas_frame = tk.Frame(parent, bg=COLORS['BACKGROUND'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        canvas = tk.Canvas(canvas_frame, bg=COLORS['CANVAS_BG'], highlightthickness=0)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Grid layout for canvas and scrollbars
        canvas.grid(row=0, column=0, sticky='nsew')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        self.widgets['canvas'] = canvas
    
    def create_controls_frame(self, parent):
        """Create controls frame."""
        controls_frame = tk.Frame(parent, bg=COLORS['PANEL'], height=UI_CONFIG['CONTROLS_HEIGHT'])
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        controls_frame.pack_propagate(False)
        
        # Pan mode toggle
        pan_button = tk.Button(controls_frame, text="Pan Mode: OFF", 
                              command=self.controller.toggle_pan_mode,
                              bg=COLORS['SECONDARY'], fg=COLORS['WHITE'], 
                              font=UI_CONFIG['FONT_SMALL'])
        pan_button.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        tk.Label(controls_frame, text="Zoom:", bg=COLORS['PANEL'], fg=COLORS['WHITE']).pack(side=tk.LEFT, padx=5)
        
        zoom_buttons = [
            ("Zoom In", self.controller.zoom_in),
            ("Zoom Out", self.controller.zoom_out),
            ("Fit to Window", self.controller.fit_to_window),
            ("Reset Zoom", self.controller.reset_zoom)
        ]
        
        for text, command in zoom_buttons:
            btn = tk.Button(controls_frame, text=text, command=command,
                           bg=COLORS['PRIMARY'], fg=COLORS['WHITE'], 
                           font=UI_CONFIG['FONT_SMALL'])
            btn.pack(side=tk.LEFT, padx=2)
        
        # Undo/Redo controls
        tk.Button(controls_frame, text="Undo", command=self.controller.undo,
                 bg=COLORS['INFO'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Redo", command=self.controller.redo,
                 bg=COLORS['INFO'], fg=COLORS['WHITE'], 
                 font=UI_CONFIG['FONT_SMALL']).pack(side=tk.LEFT, padx=2)
        
        # Zoom level display
        zoom_label = tk.Label(controls_frame, text="100%", bg=COLORS['PANEL'], fg=COLORS['WHITE'])
        zoom_label.pack(side=tk.RIGHT, padx=10)
        
        self.widgets['pan_button'] = pan_button
        self.widgets['zoom_label'] = zoom_label
        
    def create_status_bar(self):
        """Create status bar."""
        status_bar = tk.Label(self.root, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                             bg=COLORS['BACKGROUND'], fg=COLORS['WHITE'], 
                             font=UI_CONFIG['FONT_DEFAULT'])
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.widgets['status_bar'] = status_bar
    
    def get_widget(self, name):
        """Get a widget by name."""
        return self.widgets.get(name)
    
    def update_status_hint(self, message="Ready"):
        """Update the status bar with a hint message."""
        status_bar = self.widgets.get('status_bar')
        if status_bar:
            status_bar.config(text=f" {message}")