"""
Canvas Manager for the Image Labeling Tool.
Handles canvas operations, drawing, zooming, and display management.
"""

import tkinter as tk
from PIL import Image, ImageTk
from .constants import DEFAULTS, COLORS
from .utils import clamp_value, point_to_line_distance, calculate_distance


class CanvasManager:
    """Manages canvas operations and drawing functionality."""
    
    def __init__(self, controller):
        self.controller = controller
        self.canvas = None
        
        # Image variables
        self.original_image = None
        self.display_image = None
        self.tk_image = None
        self.canvas_image_id = None
        
        # Zoom and pan variables
        self.zoom_factor = DEFAULTS['ZOOM_FACTOR']
        self.min_zoom = DEFAULTS['MIN_ZOOM']
        self.max_zoom = DEFAULTS['MAX_ZOOM']
        
        # Pan variables
        self.is_panning = False
        self.pan_mode = False
        self.last_pan_x = 0
        self.last_pan_y = 0
        
        # Drawing variables
        self.is_drawing = False
        self.start_x = None
        self.start_y = None
        self.polygon_points = []
        
        # Edit mode variables
        self.edit_mode = False
        self.selected_vertex = None
        self.selected_edge = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.original_coordinates = None
        
    def set_canvas(self, canvas):
        """Set the canvas widget reference."""
        self.canvas = canvas
        
    def load_image(self, image_path):
        """Load and display an image."""
        try:
            self.original_image = Image.open(image_path)
            self.reset_zoom()
            self.update_display()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
            
    def update_display(self):
        """Update the canvas display."""
        if not self.original_image or not self.canvas:
            return
            
        # Calculate display size
        width = int(self.original_image.width * self.zoom_factor)
        height = int(self.original_image.height * self.zoom_factor)
        
        # Resize image for display
        self.display_image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update zoom label
        zoom_label = self.controller.ui_manager.get_widget('zoom_label')
        if zoom_label:
            zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
        
        # Redraw annotations
        self.redraw_annotations()
        
    def redraw_annotations(self):
        """Redraw all annotations on the canvas."""
        if not self.canvas:
            return
            
        # Clear existing annotation drawings
        for tag in self.canvas.find_all():
            if any(tag_name in str(self.canvas.gettags(tag)) 
                   for tag_name in ['annotation_', 'highlight_']):
                self.canvas.delete(tag)
        
        # Get current annotations from annotation manager
        annotations = self.controller.annotation_manager.get_all_annotations()
        
        # Draw each annotation
        for i, annotation in enumerate(annotations):
            self.draw_annotation(annotation, i)
            
            # Highlight if selected
            if i == self.controller.annotation_manager.selected_annotation_index:
                self.highlight_annotation(annotation, i)
                
    def draw_annotation(self, annotation, index):
        """Draw a single annotation on the canvas."""
        if not self.canvas:
            return
            
        coords = self.scale_coordinates(annotation['coordinates'])
        color = annotation.get('color', DEFAULTS['ANNOTATION_COLOR'])
        is_selected = (index == self.controller.annotation_manager.selected_annotation_index)
        
        def draw_vertex(x, y, size=DEFAULTS['VERTEX_SIZE']):
            """Draw a vertex handle."""
            self.canvas.create_oval(x-size, y-size, x+size, y+size, 
                                  fill=COLORS['WHITE'], outline=color,
                                  tags=f"annotation_{index}")
        
        if annotation['type'] == 'Point':
            x, y = coords
            size = DEFAULTS['VERTEX_SIZE_SELECTED'] if is_selected else DEFAULTS['VERTEX_SIZE']
            self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                  fill=color, outline=color,
                                  tags=f"annotation_{index}")
            if is_selected:
                draw_vertex(x, y)
        
        elif annotation['type'] == 'Rectangle':
            x1, y1, x2, y2 = coords
            width = 2 if is_selected else 1
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                       outline=color, width=width,
                                       tags=f"annotation_{index}")
            
            if is_selected:
                # Draw corner vertices
                draw_vertex(x1, y1)  # Top-left
                draw_vertex(x2, y1)  # Top-right
                draw_vertex(x2, y2)  # Bottom-right
                draw_vertex(x1, y2)  # Bottom-left
                
                # Draw edge midpoints
                draw_vertex((x1 + x2)/2, y1)  # Top
                draw_vertex(x2, (y1 + y2)/2)  # Right
                draw_vertex((x1 + x2)/2, y2)  # Bottom
                draw_vertex(x1, (y1 + y2)/2)  # Left
        
        elif annotation['type'] == 'Circle':
            x1, y1, x2, y2 = coords
            width = 2 if is_selected else 1
            self.canvas.create_oval(x1, y1, x2, y2,
                                  outline=color, width=width,
                                  tags=f"annotation_{index}")
            
            if is_selected:
                # Draw corner vertices of bounding box
                draw_vertex(x1, y1)  # Top-left
                draw_vertex(x2, y1)  # Top-right
                draw_vertex(x2, y2)  # Bottom-right
                draw_vertex(x1, y2)  # Bottom-left
                
                # Draw edge midpoints
                draw_vertex((x1 + x2)/2, y1)  # Top
                draw_vertex(x2, (y1 + y2)/2)  # Right
                draw_vertex((x1 + x2)/2, y2)  # Bottom
                draw_vertex(x1, (y1 + y2)/2)  # Left
        
        elif annotation['type'] == 'Polygon':
            if len(coords) >= 6:  # At least 3 points
                width = 2 if is_selected else 1
                self.canvas.create_polygon(coords,
                                        outline=color, fill='', width=width,
                                        tags=f"annotation_{index}")
                
                if is_selected:
                    # Draw vertex handles
                    for i in range(0, len(coords), 2):
                        x, y = coords[i], coords[i+1]
                        draw_vertex(x, y)
                        
                        # Draw edge midpoints
                        if i < len(coords) - 2:
                            next_x = coords[i+2]
                            next_y = coords[i+3]
                        else:  # Connect last point to first
                            next_x = coords[0]
                            next_y = coords[1]
                        
                        mid_x = (x + next_x) / 2
                        mid_y = (y + next_y) / 2
                        draw_vertex(mid_x, mid_y, size=3)
                        
    def highlight_annotation(self, annotation, index):
        """Highlight a selected annotation."""
        if not self.canvas:
            return
            
        coords = self.scale_coordinates(annotation['coordinates'])
        highlight_color = COLORS['HIGHLIGHT']
        
        if annotation['type'] == 'Point':
            x, y = coords
            # Draw larger point for highlight
            self.canvas.create_oval(x-6, y-6, x+6, y+6,
                                  outline=highlight_color, width=2,
                                  tags=f"highlight_{index}")
            self.canvas.create_oval(x-3, y-3, x+3, y+3,
                                  fill=annotation.get('color', DEFAULTS['ANNOTATION_COLOR']),
                                  outline=annotation.get('color', DEFAULTS['ANNOTATION_COLOR']),
                                  tags=f"highlight_{index}")
        
        elif annotation['type'] in ['Rectangle', 'Circle']:
            x1, y1, x2, y2 = coords
            if annotation['type'] == 'Rectangle':
                self.canvas.create_rectangle(x1-2, y1-2, x2+2, y2+2,
                                          outline=highlight_color, width=2,
                                          tags=f"highlight_{index}")
            else:  # Circle
                self.canvas.create_oval(x1-2, y1-2, x2+2, y2+2,
                                     outline=highlight_color, width=2,
                                     tags=f"highlight_{index}")
        
        elif annotation['type'] == 'Polygon':
            if len(coords) >= 6:  # At least 3 points
                self.canvas.create_polygon(coords,
                                        outline=highlight_color, fill='', width=3,
                                        tags=f"highlight_{index}")
                # Draw vertex highlights
                for i in range(0, len(coords), 2):
                    x, y = coords[i], coords[i+1]
                    self.canvas.create_oval(x-4, y-4, x+4, y+4,
                                         fill=highlight_color, outline=highlight_color,
                                         tags=f"highlight_{index}")
        
        # Raise highlight to top
        self.canvas.tag_raise(f"highlight_{index}")
        
    def scale_coordinates(self, coords):
        """Scale coordinates based on current zoom factor."""
        if len(coords) > 4:  # Polygon coordinates (flat list)
            return [coord * self.zoom_factor for coord in coords]
        elif isinstance(coords[0], (list, tuple)):  # List of coordinate pairs
            scaled_coords = []
            for point in coords:
                scaled_coords.extend([point[0] * self.zoom_factor, point[1] * self.zoom_factor])
            return scaled_coords
        else:  # Simple coordinates
            return [coord * self.zoom_factor for coord in coords]
            
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to image coordinates."""
        if not self.canvas:
            return canvas_x, canvas_y
            
        # Get canvas coordinates
        actual_x = self.canvas.canvasx(canvas_x)
        actual_y = self.canvas.canvasy(canvas_y)
        
        # Convert to image coordinates
        image_x = actual_x / self.zoom_factor
        image_y = actual_y / self.zoom_factor
        
        return image_x, image_y
        
    def find_nearest_vertex(self, x, y, annotation):
        """Find the nearest vertex of an annotation to the given coordinates."""
        coords = annotation['coordinates']
        min_dist = float('inf')
        vertex_index = None
        threshold = DEFAULTS['VERTEX_THRESHOLD'] / self.zoom_factor
        
        if annotation['type'] == 'Point':
            dist = calculate_distance(coords[0], coords[1], x, y)
            if dist < threshold:
                return 0
        
        elif annotation['type'] in ['Rectangle', 'Circle']:
            vertices = [
                (coords[0], coords[1]),  # Top-left
                (coords[2], coords[1]),  # Top-right
                (coords[2], coords[3]),  # Bottom-right
                (coords[0], coords[3])   # Bottom-left
            ]
            for i, (vx, vy) in enumerate(vertices):
                dist = calculate_distance(vx, vy, x, y)
                if dist < min_dist:
                    min_dist = dist
                    vertex_index = i
            
            if min_dist < threshold:
                return vertex_index
        
        elif annotation['type'] == 'Polygon':
            for i in range(0, len(coords), 2):
                vx, vy = coords[i], coords[i+1]
                dist = calculate_distance(vx, vy, x, y)
                if dist < min_dist:
                    min_dist = dist
                    vertex_index = i // 2
            
            if min_dist < threshold:
                return vertex_index
        
        return None
        
    def is_near_edge(self, x, y, annotation):
        """Check if the point (x, y) is near any edge of the annotation."""
        coords = annotation['coordinates']
        threshold = DEFAULTS['EDGE_THRESHOLD'] / self.zoom_factor
        
        if annotation['type'] in ['Rectangle', 'Circle']:
            # Check each edge
            edges = [
                ((coords[0], coords[1]), (coords[2], coords[1])),  # Top
                ((coords[2], coords[1]), (coords[2], coords[3])),  # Right
                ((coords[2], coords[3]), (coords[0], coords[3])),  # Bottom
                ((coords[0], coords[3]), (coords[0], coords[1]))   # Left
            ]
            
            for i, ((x1, y1), (x2, y2)) in enumerate(edges):
                if point_to_line_distance(x, y, x1, y1, x2, y2) < threshold:
                    return i
        
        elif annotation['type'] == 'Polygon':
            for i in range(0, len(coords)-2, 2):
                x1, y1 = coords[i], coords[i+1]
                x2, y2 = coords[i+2], coords[i+3]
                if point_to_line_distance(x, y, x1, y1, x2, y2) < threshold:
                    return i // 2
            
            # Check the closing edge
            x1, y1 = coords[-2], coords[-1]
            x2, y2 = coords[0], coords[1]
            if point_to_line_distance(x, y, x1, y1, x2, y2) < threshold:
                return len(coords) // 2 - 1
        
        return None
        
    # Zoom operations
    def zoom_in(self):
        """Zoom in the canvas."""
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor = clamp_value(self.zoom_factor * 1.2, self.min_zoom, self.max_zoom)
            self.update_display()
            
    def zoom_out(self):
        """Zoom out the canvas."""
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor = clamp_value(self.zoom_factor / 1.2, self.min_zoom, self.max_zoom)
            self.update_display()
            
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_factor = DEFAULTS['ZOOM_FACTOR']
        self.update_display()
        
    def fit_to_window(self):
        """Fit image to window size."""
        if not self.original_image or not self.canvas:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready, retry later
            self.canvas.after(100, self.fit_to_window)
            return
        
        # Calculate scale to fit image in canvas
        scale_x = canvas_width / self.original_image.width
        scale_y = canvas_height / self.original_image.height
        self.zoom_factor = min(scale_x, scale_y) * 0.9  # 90% of available space
        self.zoom_factor = clamp_value(self.zoom_factor, self.min_zoom, self.max_zoom)
        
        self.update_display()
        
    def handle_mouse_wheel(self, event):
        """Handle mouse wheel for zooming."""
        if not self.original_image:
            return
            
        # Determine zoom direction
        if event.delta > 0 or event.num == 4:  # Zoom in
            if self.zoom_factor < self.max_zoom:
                old_zoom = self.zoom_factor
                self.zoom_factor = clamp_value(self.zoom_factor * 1.1, self.min_zoom, self.max_zoom)
                
                # Calculate zoom center
                canvas_x = self.canvas.canvasx(event.x)
                canvas_y = self.canvas.canvasy(event.y)
                
                self.update_display()
                
                # Adjust scroll position to zoom around mouse cursor
                zoom_ratio = self.zoom_factor / old_zoom
                new_x = canvas_x * zoom_ratio - event.x
                new_y = canvas_y * zoom_ratio - event.y
                
                # Update scroll position
                self.canvas.xview_moveto(new_x / (self.original_image.width * self.zoom_factor))
                self.canvas.yview_moveto(new_y / (self.original_image.height * self.zoom_factor))
        
        elif event.delta < 0 or event.num == 5:  # Zoom out
            if self.zoom_factor > self.min_zoom:
                old_zoom = self.zoom_factor
                self.zoom_factor = clamp_value(self.zoom_factor / 1.1, self.min_zoom, self.max_zoom)
                
                # Calculate zoom center
                canvas_x = self.canvas.canvasx(event.x)
                canvas_y = self.canvas.canvasy(event.y)
                
                self.update_display()
                
                # Adjust scroll position to zoom around mouse cursor
                zoom_ratio = self.zoom_factor / old_zoom
                new_x = canvas_x * zoom_ratio - event.x
                new_y = canvas_y * zoom_ratio - event.y
                
                # Update scroll position
                self.canvas.xview_moveto(new_x / (self.original_image.width * self.zoom_factor))
                self.canvas.yview_moveto(new_y / (self.original_image.height * self.zoom_factor))
                
    # Pan operations
    def toggle_pan_mode(self):
        """Toggle pan mode on/off."""
        self.pan_mode = not self.pan_mode
        pan_button = self.controller.ui_manager.get_widget('pan_button')
        
        if self.pan_mode:
            pan_button.config(text="Pan Mode: ON", bg=COLORS['SUCCESS'])
            if self.canvas:
                self.canvas.config(cursor="fleur")
        else:
            pan_button.config(text="Pan Mode: OFF", bg=COLORS['SECONDARY'])
            if self.canvas:
                self.canvas.config(cursor="")
            self.is_panning = False
            
    def start_pan(self, event):
        """Start panning operation."""
        if not self.pan_mode:
            return
        self.is_panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        if self.canvas:
            self.canvas.config(cursor="fleur")
            
    def do_pan(self, event):
        """Perform panning operation."""
        if not self.is_panning or not self.pan_mode or not self.canvas:
            return
            
        # Calculate the difference in mouse position
        dx = event.x - self.last_pan_x
        dy = event.y - self.last_pan_y
        
        # Get current scroll position
        x_view = self.canvas.xview()
        y_view = self.canvas.yview()
        
        # Calculate the scroll region size
        if self.original_image:
            scroll_width = self.original_image.width * self.zoom_factor
            scroll_height = self.original_image.height * self.zoom_factor
            
            # Calculate new scroll position
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Convert pixel movement to scroll fraction
            if scroll_width > canvas_width:
                dx_fraction = -dx / scroll_width
                new_x = clamp_value(x_view[0] + dx_fraction, 0, 1)
                self.canvas.xview_moveto(new_x)
            
            if scroll_height > canvas_height:
                dy_fraction = -dy / scroll_height
                new_y = clamp_value(y_view[0] + dy_fraction, 0, 1)
                self.canvas.yview_moveto(new_y)
        
        # Update last position
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        
    def end_pan(self, event):
        """End panning operation."""
        self.is_panning = False
        if self.pan_mode and self.canvas:
            self.canvas.config(cursor="fleur")
        elif self.canvas:
            self.canvas.config(cursor="")
            
    # Drawing operations
    def start_drawing_temp_annotation(self, annotation_type, start_x, start_y):
        """Start drawing a temporary annotation."""
        self.is_drawing = True
        self.start_x = start_x
        self.start_y = start_y
        
    def update_temp_annotation(self, annotation_type, current_x, current_y, color):
        """Update temporary annotation during drawing."""
        if not self.canvas or not self.is_drawing:
            return
            
        # Remove previous temporary annotation
        self.canvas.delete("temp_annotation")
        
        # Draw new temporary annotation
        start_canvas = self.scale_coordinates([self.start_x, self.start_y])
        current_canvas = self.scale_coordinates([current_x, current_y])
        
        if annotation_type == "Rectangle":
            self.canvas.create_rectangle(start_canvas[0], start_canvas[1], 
                                       current_canvas[0], current_canvas[1], 
                                       outline=color, tags="temp_annotation")
        elif annotation_type == "Circle":
            self.canvas.create_oval(start_canvas[0], start_canvas[1], 
                                  current_canvas[0], current_canvas[1], 
                                  outline=color, tags="temp_annotation")
                                  
    def finish_drawing(self):
        """Finish current drawing operation."""
        self.is_drawing = False
        self.start_x = None
        self.start_y = None
        if self.canvas:
            self.canvas.delete("temp_annotation")
            
    def add_polygon_point(self, x, y, color):
        """Add a point to the current polygon."""
        self.polygon_points.append((x, y))
        
        if not self.canvas:
            return
            
        # Draw point for visual feedback
        canvas_point = self.scale_coordinates([x, y])
        self.canvas.create_oval(canvas_point[0]-3, canvas_point[1]-3, 
                              canvas_point[0]+3, canvas_point[1]+3, 
                              fill=color, outline=color, tags="temp_polygon")
        
        # Draw line if not the first point
        if len(self.polygon_points) > 1:
            prev_point = self.scale_coordinates(list(self.polygon_points[-2]))
            curr_point = self.scale_coordinates(list(self.polygon_points[-1]))
            self.canvas.create_line(prev_point[0], prev_point[1], 
                                  curr_point[0], curr_point[1], 
                                  fill=color, width=2, tags="temp_polygon")
                                  
    def complete_polygon(self):
        """Complete the current polygon."""
        if len(self.polygon_points) >= 3:
            # Connect last point to first
            if self.canvas:
                first_point = self.scale_coordinates(list(self.polygon_points[0]))
                last_point = self.scale_coordinates(list(self.polygon_points[-1]))
                self.canvas.create_line(last_point[0], last_point[1], 
                                      first_point[0], first_point[1], 
                                      fill=DEFAULTS['ANNOTATION_COLOR'], width=2, tags="temp_polygon")
            return True
        return False
        
    def cancel_polygon(self):
        """Cancel current polygon drawing."""
        self.polygon_points.clear()
        if self.canvas:
            self.canvas.delete("temp_polygon")
            
    def clear_temporary_drawings(self):
        """Clear all temporary drawings."""
        if self.canvas:
            self.canvas.delete("temp_annotation")
            self.canvas.delete("temp_polygon")