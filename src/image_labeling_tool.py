"""
Main Controller Class for the Image Labeling Tool - FIXED VERSION
Coordinates all components and handles user interactions.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, colorchooser
from .ui_manager import UIManager
from .menu_manager import MenuManager
from .event_handler import EventHandler
from .annotation_manager import AnnotationManager
from .canvas_manager import CanvasManager
from .file_io_manager import FileIOManager
from .constants import DEFAULTS
from .utils import format_coordinates


class ImageLabelingTool:
    """Main controller for the Image Labeling Tool application."""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize managers
        self.ui_manager = UIManager(root, self)
        self.menu_manager = MenuManager(root, self)
        self.annotation_manager = AnnotationManager(self)
        self.canvas_manager = CanvasManager(self)
        self.file_io_manager = FileIOManager(self)
        self.event_handler = EventHandler(self)
        
        # Application state
        self.images = []
        self.current_image_index = -1
        self.current_image_path = None
        
        # Labels management
        self.labels = []
        self.label_colors = {}
        self.selected_label = None
        
        # Drawing and editing state
        self.current_tool = "None"
        self.annotation_color = DEFAULTS['ANNOTATION_COLOR']
        
        # FIXED: Add minimum drag distance for rectangles/circles
        self.min_drag_distance = 5  # pixels
        self.drag_start_pos = None
        
        # Initialize UI
        self.setup_application()
        
    def setup_application(self):
        """Initialize the complete application."""
        # Setup main window
        self.ui_manager.setup_main_window()
        
        # Create UI layout
        self.ui_manager.create_main_layout()
        
        # Create menu
        self.menu_manager.create_menu_bar()
        
        # Set canvas reference in canvas manager
        canvas = self.ui_manager.get_widget('canvas')
        self.canvas_manager.set_canvas(canvas)
        
        # Bind all events
        self.event_handler.bind_all_events()
        
        # Initialize status
        self.update_status_hint("Ready - Load images to start annotating")
        
    # Image Management
    def reset_workspace(self):
        """Reset workspace data with confirmation."""
        if any(self.annotation_manager.annotations.values()):
            if not messagebox.askyesno("Confirm Reset", 
                                     "Loading new images will clear current annotations and labels.\n\n"
                                     "Do you want to continue?"):
                return False
        
        # Clear all data
        self.images = []
        self.annotation_manager.annotations = {}
        self.annotation_manager.current_annotations = []
        self.current_image_index = -1
        self.current_image_path = None
        self.labels = []
        self.label_colors = {}
        self.selected_label = None
        
        # Clear UI
        image_listbox = self.ui_manager.get_widget('image_listbox')
        if image_listbox:
            image_listbox.delete(0, tk.END)
            
        self.update_labels_listbox()
        self.update_annotations_display()
        
        if self.canvas_manager.canvas:
            self.canvas_manager.canvas.delete("all")
        
        return True
        
    def on_image_select(self, event):
        """Handle image selection from listbox."""
        image_listbox = self.ui_manager.get_widget('image_listbox')
        if not image_listbox:
            return
            
        selection = image_listbox.curselection()
        if selection:
            # Save current annotations before switching
            if self.current_image_index >= 0:
                self.annotation_manager.save_image_annotations(self.current_image_path)
            
            self.current_image_index = selection[0]
            self.current_image_path = self.images[self.current_image_index]
            
            # Load and display new image
            if self.canvas_manager.load_image(self.current_image_path):
                self.annotation_manager.load_image_annotations(self.current_image_path)
                self.update_annotations_display()
                self.update_status_hint(f"Loaded: {self.current_image_path}")
            else:
                messagebox.showerror("Error", f"Failed to load image: {self.current_image_path}")
                
    # Tool Management
    def on_tool_change(self, event):
        """Handle tool selection change."""
        tool_var = self.ui_manager.get_widget('tool_var')
        if tool_var:
            self.current_tool = tool_var.get()
            
        # Reset drawing states
        self.canvas_manager.is_drawing = False
        self.canvas_manager.polygon_points = []
        self.canvas_manager.clear_temporary_drawings()
        self.drag_start_pos = None  # FIXED: Reset drag position
        
        # Update status hint based on selected tool
        if self.current_tool == "Point":
            self.update_status_hint("Click on image to place a point annotation")
        elif self.current_tool == "Rectangle":
            self.update_status_hint("Click and drag to draw a rectangle (minimum drag required)")
        elif self.current_tool == "Circle":
            self.update_status_hint("Click and drag to draw a circle (minimum drag required)")
        elif self.current_tool == "Polygon":
            self.update_status_hint("Click to add points. Right-click or press Enter to complete polygon. Press Esc to cancel.")
        else:
            self.update_status_hint("Select a tool and label to start annotating")
            
    # Canvas Event Handlers - FIXED
    def on_canvas_click(self, event):
        """Handle canvas click events - FIXED."""
        if not self.canvas_manager.original_image:
            return
        
        # Convert to image coordinates
        orig_x, orig_y = self.canvas_manager.canvas_to_image_coords(event.x, event.y)
        
        # Handle edit mode
        if self.canvas_manager.edit_mode and self.annotation_manager.selected_annotation_index is not None:
            self.handle_edit_mode_click(orig_x, orig_y)
            return
        
        # Handle panning mode
        if self.canvas_manager.pan_mode:
            self.canvas_manager.start_pan(event)
            return
            
        # Check if annotation tool is selected
        if self.current_tool == "None":
            return
        
        # Check if label is selected before annotation
        if not self.check_label_selected():
            return
        
        # FIXED: Handle different tools properly
        if self.current_tool == "Point":
            self.add_point_annotation(orig_x, orig_y)
        elif self.current_tool in ["Rectangle", "Circle"]:
            # FIXED: Only start drawing, don't create annotation yet
            self.drag_start_pos = (orig_x, orig_y)
            self.canvas_manager.start_drawing_temp_annotation(self.current_tool, orig_x, orig_y)
        elif self.current_tool == "Polygon":
            self.canvas_manager.add_polygon_point(orig_x, orig_y, self.annotation_color)
            self.update_polygon_status()
            
    def on_canvas_drag(self, event):
        """Handle canvas drag events - FIXED."""
        orig_x, orig_y = self.canvas_manager.canvas_to_image_coords(event.x, event.y)
        
        # Handle edit mode dragging
        if self.canvas_manager.edit_mode:
            self.handle_edit_mode_drag(orig_x, orig_y)
            return
        
        # Handle panning
        if self.canvas_manager.pan_mode and self.canvas_manager.is_panning:
            self.canvas_manager.do_pan(event)
            return
            
        # FIXED: Handle drawing with minimum drag requirement
        if self.canvas_manager.is_drawing and self.current_tool in ["Rectangle", "Circle"] and self.drag_start_pos:
            # Calculate drag distance
            start_canvas = self.canvas_manager.scale_coordinates([self.drag_start_pos[0], self.drag_start_pos[1]])
            current_canvas = self.canvas_manager.scale_coordinates([orig_x, orig_y])
            
            drag_distance = ((current_canvas[0] - start_canvas[0])**2 + (current_canvas[1] - start_canvas[1])**2)**0.5
            
            # Only show temporary annotation if dragged minimum distance
            if drag_distance >= self.min_drag_distance:
                self.canvas_manager.update_temp_annotation(self.current_tool, orig_x, orig_y, self.annotation_color)
            
    def on_canvas_release(self, event):
        """Handle canvas release events - FIXED."""
        orig_x, orig_y = self.canvas_manager.canvas_to_image_coords(event.x, event.y)
        
        # Handle edit mode release
        if self.canvas_manager.edit_mode:
            self.handle_edit_mode_release()
            return
            
        # Handle panning end
        if self.canvas_manager.pan_mode and self.canvas_manager.is_panning:
            self.canvas_manager.end_pan(event)
            return
            
        # FIXED: Handle drawing completion with minimum drag requirement
        if self.canvas_manager.is_drawing and self.current_tool in ["Rectangle", "Circle"] and self.drag_start_pos:
            # Calculate drag distance
            start_canvas = self.canvas_manager.scale_coordinates([self.drag_start_pos[0], self.drag_start_pos[1]])
            current_canvas = self.canvas_manager.scale_coordinates([orig_x, orig_y])
            
            drag_distance = ((current_canvas[0] - start_canvas[0])**2 + (current_canvas[1] - start_canvas[1])**2)**0.5
            
            # Only create annotation if dragged minimum distance
            if drag_distance >= self.min_drag_distance:
                if self.current_tool == "Rectangle":
                    self.add_rectangle_annotation(self.drag_start_pos[0], self.drag_start_pos[1], orig_x, orig_y)
                elif self.current_tool == "Circle":
                    self.add_circle_annotation(self.drag_start_pos[0], self.drag_start_pos[1], orig_x, orig_y)
            else:
                # Show message that minimum drag is required
                self.update_status_hint("Drag to create rectangle/circle - single click not allowed")
            
            # Reset drawing state
            self.canvas_manager.finish_drawing()
            self.drag_start_pos = None
            
    def on_canvas_right_click(self, event):
        """Handle canvas right-click events."""
        if self.current_tool == "Polygon":
            self.complete_polygon()
            
    def on_mouse_wheel(self, event):
        """Handle mouse wheel events for zooming."""
        self.canvas_manager.handle_mouse_wheel(event)
        
    # Edit Mode Handlers
    def handle_edit_mode_click(self, x, y):
        """Handle clicks in edit mode."""
        if self.annotation_manager.selected_annotation_index is None:
            return
            
        annotation = self.annotation_manager.get_annotation(self.annotation_manager.selected_annotation_index)
        if not annotation:
            return
            
        # Find if clicked on a vertex
        vertex = self.canvas_manager.find_nearest_vertex(x, y, annotation)
        if vertex is not None:
            self.canvas_manager.selected_vertex = vertex
            self.canvas_manager.drag_start_x = x
            self.canvas_manager.drag_start_y = y
            self.canvas_manager.original_coordinates = annotation['coordinates'].copy()
            return
            
        # Find if clicked on an edge
        edge = self.canvas_manager.is_near_edge(x, y, annotation)
        if edge is not None:
            self.canvas_manager.selected_edge = edge
            self.canvas_manager.drag_start_x = x
            self.canvas_manager.drag_start_y = y
            self.canvas_manager.original_coordinates = annotation['coordinates'].copy()
            return
            
        # If clicked outside, exit edit mode
        self.exit_edit_mode()
        
    def handle_edit_mode_drag(self, x, y):
        """Handle dragging in edit mode."""
        if (self.canvas_manager.selected_vertex is None and 
            self.canvas_manager.selected_edge is None):
            return
            
        if self.annotation_manager.selected_annotation_index is None:
            return
            
        annotation = self.annotation_manager.get_annotation(self.annotation_manager.selected_annotation_index)
        if not annotation:
            return
            
        dx = x - self.canvas_manager.drag_start_x
        dy = y - self.canvas_manager.drag_start_y
        
        new_coords = self.canvas_manager.original_coordinates.copy()
        
        # Handle vertex dragging
        if self.canvas_manager.selected_vertex is not None:
            self.update_annotation_vertex(annotation, new_coords, x, y)
        # Handle edge dragging (move entire shape)
        elif self.canvas_manager.selected_edge is not None:
            self.move_annotation(annotation, new_coords, dx, dy)
        
        # Update annotation and redraw
        self.annotation_manager.update_annotation(
            self.annotation_manager.selected_annotation_index, 
            {'coordinates': new_coords}
        )
        self.canvas_manager.redraw_annotations()
        
    def handle_edit_mode_release(self):
        """Handle release in edit mode."""
        if (self.canvas_manager.selected_vertex is not None or 
            self.canvas_manager.selected_edge is not None):
            # Save the state for undo
            self.annotation_manager.save_annotation_state()
            
            # Reset edit state
            self.canvas_manager.selected_vertex = None
            self.canvas_manager.selected_edge = None
            self.canvas_manager.drag_start_x = None
            self.canvas_manager.drag_start_y = None
            self.canvas_manager.original_coordinates = None
            
    def update_annotation_vertex(self, annotation, coords, x, y):
        """Update annotation vertex during editing."""
        if annotation['type'] == 'Point':
            coords[0] = x
            coords[1] = y
        elif annotation['type'] in ['Rectangle', 'Circle']:
            vertex_map = {
                0: (0, 1),  # Top-left
                1: (2, 1),  # Top-right
                2: (2, 3),  # Bottom-right
                3: (0, 3)   # Bottom-left
            }
            if self.canvas_manager.selected_vertex in vertex_map:
                x_idx, y_idx = vertex_map[self.canvas_manager.selected_vertex]
                coords[x_idx] = x
                coords[y_idx] = y
                
                # FIXED: Ensure proper rectangle bounds
                coords[0], coords[2] = min(coords[0], coords[2]), max(coords[0], coords[2])
                coords[1], coords[3] = min(coords[1], coords[3]), max(coords[1], coords[3])
                
        elif annotation['type'] == 'Polygon':
            vertex_idx = self.canvas_manager.selected_vertex
            coords[vertex_idx * 2] = x
            coords[vertex_idx * 2 + 1] = y
            
    def move_annotation(self, annotation, coords, dx, dy):
        """Move entire annotation during editing."""
        if annotation['type'] == 'Point':
            coords[0] = self.canvas_manager.original_coordinates[0] + dx
            coords[1] = self.canvas_manager.original_coordinates[1] + dy
        elif annotation['type'] in ['Rectangle', 'Circle']:
            coords[0] = self.canvas_manager.original_coordinates[0] + dx
            coords[1] = self.canvas_manager.original_coordinates[1] + dy
            coords[2] = self.canvas_manager.original_coordinates[2] + dx
            coords[3] = self.canvas_manager.original_coordinates[3] + dy
        elif annotation['type'] == 'Polygon':
            for i in range(0, len(coords), 2):
                coords[i] = self.canvas_manager.original_coordinates[i] + dx
                coords[i + 1] = self.canvas_manager.original_coordinates[i + 1] + dy
                
    # Annotation Creation Methods
    def add_point_annotation(self, x, y):
        """Add a point annotation."""
        if self.annotation_manager.add_annotation('Point', [x, y], self.selected_label, self.annotation_color):
            self.update_annotations_display()
            
    def add_rectangle_annotation(self, x1, y1, x2, y2):
        """Add a rectangle annotation - FIXED."""
        coords = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
        # Ensure minimum size
        if abs(coords[2] - coords[0]) < 1 or abs(coords[3] - coords[1]) < 1:
            self.update_status_hint("Rectangle too small - drag to create larger rectangle")
            return
            
        if self.annotation_manager.add_annotation('Rectangle', coords, self.selected_label, self.annotation_color):
            self.update_annotations_display()
            
    def add_circle_annotation(self, x1, y1, x2, y2):
        """Add a circle annotation - FIXED."""
        coords = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
        # Ensure minimum size
        if abs(coords[2] - coords[0]) < 1 or abs(coords[3] - coords[1]) < 1:
            self.update_status_hint("Circle too small - drag to create larger circle")
            return
            
        if self.annotation_manager.add_annotation('Circle', coords, self.selected_label, self.annotation_color):
            self.update_annotations_display()
            
    def add_polygon_annotation(self, points):
        """Add a polygon annotation."""
        # Convert list of tuples to flat list
        flat_coords = []
        for point in points:
            flat_coords.extend([point[0], point[1]])
            
        if self.annotation_manager.add_annotation('Polygon', flat_coords, self.selected_label, self.annotation_color):
            self.update_annotations_display()
            messagebox.showinfo("Success", f"Polygon annotation added with {len(points)} vertices")
            
    # Polygon Management
    def complete_polygon(self, event=None):
        """Complete the current polygon."""
        if self.current_tool == "Polygon" and len(self.canvas_manager.polygon_points) >= 3:
            if self.canvas_manager.complete_polygon():
                self.add_polygon_annotation(self.canvas_manager.polygon_points)
                self.canvas_manager.polygon_points = []
                self.canvas_manager.clear_temporary_drawings()
                self.update_status_hint("Polygon completed. Start new polygon or select another tool.")
                return True
        return False
        
    def cancel_drawing(self, event=None):
        """Cancel the current drawing operation."""
        if self.canvas_manager.edit_mode:
            self.exit_edit_mode()
            return
            
        if self.canvas_manager.is_drawing or self.canvas_manager.polygon_points:
            self.canvas_manager.clear_temporary_drawings()
            self.canvas_manager.finish_drawing()
            self.canvas_manager.cancel_polygon()
            self.drag_start_pos = None  # FIXED: Reset drag position
            self.update_status_hint("Drawing cancelled")
            
    def update_polygon_status(self):
        """Update status hint for polygon drawing."""
        num_points = len(self.canvas_manager.polygon_points)
        if num_points >= 3:
            self.update_status_hint(
                f"Polygon: {num_points} points added. Right-click or press Enter to complete, Esc to cancel")
        else:
            self.update_status_hint(
                f"Polygon: {num_points} points added. Add at least {3 - num_points} more points")
                
    # Annotation Management
    def on_annotation_select(self, event):
        """Handle annotation selection from listbox."""
        annotations_listbox = self.ui_manager.get_widget('annotations_listbox')
        if not annotations_listbox:
            return
            
        selection = annotations_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        self.annotation_manager.selected_annotation_index = index
        annotation = self.annotation_manager.get_annotation(index)
        
        if annotation:
            self.canvas_manager.redraw_annotations()
            self.show_annotation_details(annotation)
            
    def show_annotation_details(self, annotation):
        """Display detailed information about the selected annotation."""
        details = self.annotation_manager.get_annotation_details(annotation)
        
        # Build status message
        status_parts = [
            f"Type: {details['type']}",
            f"Label: {details['label']}",
            f"Color: {details['color']}"
        ]
        
        if details['type'] == 'Point':
            status_parts.append(f"Position: {details['position']}")
        elif details['type'] in ['Rectangle', 'Circle']:
            status_parts.extend([
                f"Size: {details['width']}x{details['height']}",
                f"Area: {details['area']}"
            ])
        elif details['type'] == 'Polygon':
            status_parts.append(f"Vertices: {details['num_vertices']}")
            
        self.update_status_hint(" | ".join(status_parts))
        
    def edit_annotation(self):
        """Enter edit mode for selected annotation."""
        annotations_listbox = self.ui_manager.get_widget('annotations_listbox')
        if not annotations_listbox:
            return
            
        selection = annotations_listbox.curselection()
        if selection and self.annotation_manager.current_annotations:
            self.annotation_manager.selected_annotation_index = selection[0]
            self.canvas_manager.edit_mode = True
            
            # Disable drawing tools while editing
            tool_var = self.ui_manager.get_widget('tool_var')
            if tool_var:
                tool_var.set("None")
            self.current_tool = "None"
            
            # Disable pan mode while editing
            self.canvas_manager.pan_mode = False
            pan_button = self.ui_manager.get_widget('pan_button')
            if pan_button:
                pan_button.config(text="Pan Mode: OFF", bg='#95A5A6')
                
            if self.canvas_manager.canvas:
                self.canvas_manager.canvas.config(cursor="crosshair")
                
            self.canvas_manager.redraw_annotations()
            
            annotation = self.annotation_manager.get_annotation(self.annotation_manager.selected_annotation_index)
            if annotation:
                self.update_status_hint(
                    f"Editing {annotation['type']}: Drag white handles to resize, drag edges to move. "
                    "Click outside or press Esc to finish.")
            
            # Show edit hint for first-time users
            if not hasattr(self, 'edit_hint_shown'):
                messagebox.showinfo("Edit Mode", 
                                  "Edit Mode activated:\n\n"
                                  "- Drag vertices (small circles) to resize\n"
                                  "- Drag edges to move the entire shape\n"
                                  "- Press Escape to cancel\n"
                                  "- Click outside shape to finish editing")
                self.edit_hint_shown = True
                
    def exit_edit_mode(self):
        """Exit edit mode and reset related variables."""
        self.canvas_manager.edit_mode = False
        self.annotation_manager.selected_annotation_index = None
        self.canvas_manager.selected_vertex = None
        self.canvas_manager.selected_edge = None
        self.canvas_manager.drag_start_x = None
        self.canvas_manager.drag_start_y = None
        self.canvas_manager.original_coordinates = None
        
        if self.canvas_manager.canvas:
            self.canvas_manager.canvas.config(cursor="")
            
        self.canvas_manager.redraw_annotations()
        
        # Reset status hint based on current tool
        if self.current_tool != "None":
            self.on_tool_change(None)
        else:
            self.update_status_hint("Ready")
            
    def delete_annotation(self):
        """Delete the selected annotation."""
        annotations_listbox = self.ui_manager.get_widget('annotations_listbox')
        if not annotations_listbox:
            return
            
        selection = annotations_listbox.curselection()
        if selection and self.annotation_manager.current_annotations:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this annotation?"):
                index = selection[0]
                deleted_annotation = self.annotation_manager.delete_annotation(index)
                if deleted_annotation:
                    self.update_annotations_display()
                    messagebox.showinfo("Success", f"Deleted {deleted_annotation['type']} annotation")
        else:
            messagebox.showwarning("No Selection", "Please select an annotation to delete")
            
    def update_annotations_display(self):
        """Update the annotations listbox and redraw on canvas."""
        annotations_listbox = self.ui_manager.get_widget('annotations_listbox')
        if not annotations_listbox:
            return
            
        # Clear listbox
        annotations_listbox.delete(0, tk.END)
        
        # Add current annotations
        for annotation in self.annotation_manager.current_annotations:
            summary = self.annotation_manager.get_annotation_summary(annotation)
            annotations_listbox.insert(tk.END, summary)
        
        # Redraw canvas
        self.canvas_manager.redraw_annotations()
        
    # Label Management - FIXED: Added edit functionality
    def on_label_select(self, event):
        """Handle label selection from listbox."""
        labels_listbox = self.ui_manager.get_widget('labels_listbox')
        if not labels_listbox:
            return
            
        selection = labels_listbox.curselection()
        if selection:
            self.selected_label = self.labels[selection[0]]
            
            # Set the annotation color to the label's color
            if self.selected_label in self.label_colors:
                self.annotation_color = self.label_colors[self.selected_label]
                
            # Visual feedback
            labels_listbox.config(selectbackground='#27AE60')
            
            # Update hint
            if self.current_tool != "None":
                self.on_tool_change(None)
            else:
                self.update_status_hint(f"Label '{self.selected_label}' selected. Choose a tool to start annotating.")
        else:
            self.selected_label = None
            self.update_status_hint("Select a label before annotating")
            
    def add_label(self):
        """Add a new label."""
        label = simpledialog.askstring("Add Label", "Enter new label name:")
        if label:
            label = label.strip()
            if label and label not in self.labels:
                # Ask for color
                color = colorchooser.askcolor(title=f"Choose color for label '{label}'")[1]
                if color:
                    self.labels.append(label)
                    self.label_colors[label] = color
                    self.update_labels_listbox()
                    
                    # Auto-select the newly added label
                    labels_listbox = self.ui_manager.get_widget('labels_listbox')
                    if labels_listbox:
                        labels_listbox.selection_set(len(self.labels) - 1)
                        self.selected_label = label
                        self.annotation_color = color
                        
                    messagebox.showinfo("Success", f"Added and selected label: '{label}'")
                else:
                    messagebox.showinfo("Cancelled", "Label creation cancelled - no color selected")
            elif label in self.labels:
                messagebox.showwarning("Duplicate Label", f"Label '{label}' already exists!")
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid label name")
        else:
            messagebox.showinfo("Cancelled", "Label creation cancelled")
    
    # FIXED: Added edit label functionality
    def edit_label(self):
        """Edit the selected label."""
        labels_listbox = self.ui_manager.get_widget('labels_listbox')
        if not labels_listbox:
            return
            
        selection = labels_listbox.curselection()
        if selection:
            index = selection[0]
            old_label = self.labels[index]
            
            # Ask for new label name
            new_label = simpledialog.askstring("Edit Label", f"Edit label name:", initialvalue=old_label)
            if new_label and new_label.strip():
                new_label = new_label.strip()
                
                # Check if new name already exists (and is different from current)
                if new_label != old_label and new_label in self.labels:
                    messagebox.showwarning("Duplicate Label", f"Label '{new_label}' already exists!")
                    return
                
                # Ask for new color
                current_color = self.label_colors.get(old_label, '#FF0000')
                new_color = colorchooser.askcolor(title=f"Choose color for label '{new_label}'", 
                                                color=current_color)[1]
                if new_color:
                    # Update label name and color
                    self.labels[index] = new_label
                    del self.label_colors[old_label]
                    self.label_colors[new_label] = new_color
                    
                    # Update annotations that use this label
                    for ann in self.annotation_manager.current_annotations:
                        if ann.get('label') == old_label:
                            ann['label'] = new_label
                            ann['color'] = new_color  # Update annotation color too
                    
                    # Update selected label if it was the edited one
                    if self.selected_label == old_label:
                        self.selected_label = new_label
                        self.annotation_color = new_color
                    
                    # Update displays
                    self.update_labels_listbox()
                    self.update_annotations_display()
                    
                    # Re-select the edited label
                    labels_listbox.selection_set(index)
                    
                    messagebox.showinfo("Success", f"Updated label to: '{new_label}'")
        else:
            messagebox.showwarning("No Selection", "Please select a label to edit")
            
    def delete_label(self):
        """Delete the selected label."""
        labels_listbox = self.ui_manager.get_widget('labels_listbox')
        if not labels_listbox:
            return
            
        selection = labels_listbox.curselection()
        if selection:
            index = selection[0]
            label_to_delete = self.labels[index]
            
            # Check if label is used in annotations
            label_in_use = any(ann.get('label') == label_to_delete 
                             for ann in self.annotation_manager.current_annotations)
            
            if label_in_use:
                if not messagebox.askyesno("Label in Use", 
                                         f"Label '{label_to_delete}' is used in current annotations.\n" +
                                         "Deleting it will remove the label from those annotations.\n\n" +
                                         "Do you want to continue?"):
                    return
            
            if messagebox.askyesno("Confirm Delete", f"Delete label '{label_to_delete}'?"):
                # Remove from labels list
                del self.labels[index]
                del self.label_colors[label_to_delete]
                
                # Clear selection if this was the selected label
                if self.selected_label == label_to_delete:
                    self.selected_label = None
                
                # Update annotations that use this label
                if label_in_use:
                    for ann in self.annotation_manager.current_annotations:
                        if ann.get('label') == label_to_delete:
                            ann['label'] = None
                    self.update_annotations_display()
                
                self.update_labels_listbox()
                messagebox.showinfo("Success", f"Deleted label: '{label_to_delete}'")
        else:
            messagebox.showwarning("No Selection", "Please select a label to delete")
            
    def update_labels_listbox(self):
        """Update the labels listbox."""
        labels_listbox = self.ui_manager.get_widget('labels_listbox')
        if not labels_listbox:
            return
            
        labels_listbox.delete(0, tk.END)
        for i, label in enumerate(self.labels):
            labels_listbox.insert(tk.END, label)
            # Set the background color for the label entry
            if label in self.label_colors:
                labels_listbox.itemconfig(i, {'bg': self.label_colors[label]})
                
    def choose_color(self):
        """Choose annotation color."""
        color = colorchooser.askcolor(title="Choose Annotation Color")[1]
        if color:
            self.annotation_color = color
            # If a label is selected, update its color
            if self.selected_label:
                self.label_colors[self.selected_label] = color
                self.update_labels_listbox()
                
    def check_label_selected(self):
        """Check if a label is selected before annotation."""
        if not self.selected_label:
            messagebox.showwarning("No Label Selected", 
                                 "Please select a label first before creating annotations.\n\n" + 
                                 "Steps:\n1. Add labels using 'Add' button or Ctrl+N\n" + 
                                 "2. Click on a label in the Labels list to select it\n" + 
                                 "3. Then start annotating")
            return False
        return True
        
    # Undo/Redo Operations
    def undo(self):
        """Undo last annotation action."""
        if self.annotation_manager.undo():
            self.update_annotations_display()
            # Update tool combobox to match restored state
            tool_var = self.ui_manager.get_widget('tool_var')
            if tool_var:
                tool_var.set(self.current_tool)
                
    def redo(self):
        """Redo last undone action."""
        if self.annotation_manager.redo():
            self.update_annotations_display()
            # Update tool combobox to match restored state
            tool_var = self.ui_manager.get_widget('tool_var')
            if tool_var:
                tool_var.set(self.current_tool)
                
    # Canvas Controls
    def toggle_pan_mode(self):
        """Toggle pan mode on/off."""
        self.canvas_manager.toggle_pan_mode()
        # Clear any temporary drawing state
        self.canvas_manager.polygon_points = []
        self.canvas_manager.is_drawing = False
        self.drag_start_pos = None  # FIXED: Reset drag position
        
    def zoom_in(self):
        """Zoom in the canvas."""
        self.canvas_manager.zoom_in()
        
    def zoom_out(self):
        """Zoom out the canvas."""
        self.canvas_manager.zoom_out()
        
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.canvas_manager.reset_zoom()
        
    def fit_to_window(self):
        """Fit image to window size."""
        self.canvas_manager.fit_to_window()
        
    # File Operations (delegate to FileIOManager)
    def load_single_image(self):
        """Load a single image."""
        self.file_io_manager.load_single_image()
        
    def load_folder(self):
        """Load images from folder."""
        self.file_io_manager.load_folder()
        
    def save_annotations(self):
        """Save annotations to individual files."""
        self.file_io_manager.save_annotations()
        
    def save_master_dataset(self):
        """Save master dataset."""
        self.file_io_manager.save_master_dataset()
        
    def load_individual_annotations(self):
        """Load individual annotation files."""
        self.file_io_manager.load_individual_annotations()
        
    def load_master_dataset(self):
        """Load master dataset."""
        self.file_io_manager.load_master_dataset()
        
    def load_annotations(self):
        """Alias for load_individual_annotations."""
        self.load_individual_annotations()
        
    def import_coco(self):
        """Import COCO format annotations."""
        self.file_io_manager.import_coco()
        
    def export_coco(self):
        """Export annotations in COCO format."""
        self.file_io_manager.export_coco()
        
    def export_pascal_voc(self):
        """Export annotations in Pascal VOC format."""
        self.file_io_manager.export_pascal_voc()
        
    # Utility Methods
    def update_status_hint(self, message="Ready"):
        """Update the status bar with a hint message."""
        self.ui_manager.update_status_hint(message)