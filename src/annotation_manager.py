"""
Annotation Manager for the Image Labeling Tool.
Handles annotation data management, validation, and operations.
"""

import copy
from .utils import calculate_polygon_area, format_coordinates
from .constants import ANNOTATION_TYPES, DEFAULTS


class AnnotationManager:
    """Manages annotation data and operations."""
    
    def __init__(self, controller):
        self.controller = controller
        self.annotations = {}  # Dictionary to store annotations for each image
        self.current_annotations = []  # Current image annotations
        self.selected_annotation_index = None
        
        # Undo/Redo functionality
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = DEFAULTS['MAX_UNDO_STEPS']
        
    def add_annotation(self, annotation_type, coordinates, label, color):
        """Add a new annotation."""
        if not self.validate_annotation_data(annotation_type, coordinates, label):
            return False
            
        annotation = {
            'type': annotation_type,
            'coordinates': coordinates,
            'label': label,
            'color': color
        }
        
        self.save_annotation_state()
        self.current_annotations.append(annotation)
        return True
        
    def delete_annotation(self, index):
        """Delete annotation at the specified index."""
        if 0 <= index < len(self.current_annotations):
            self.save_annotation_state()
            deleted_annotation = self.current_annotations.pop(index)
            return deleted_annotation
        return None
        
    def update_annotation(self, index, annotation_data):
        """Update annotation at the specified index."""
        if 0 <= index < len(self.current_annotations):
            self.save_annotation_state()
            self.current_annotations[index].update(annotation_data)
            return True
        return False
        
    def get_annotation(self, index):
        """Get annotation at the specified index."""
        if 0 <= index < len(self.current_annotations):
            return self.current_annotations[index]
        return None
        
    def get_all_annotations(self):
        """Get all current annotations."""
        return self.current_annotations.copy()
        
    def clear_annotations(self):
        """Clear all current annotations."""
        self.save_annotation_state()
        self.current_annotations.clear()
        
    def validate_annotation_data(self, annotation_type, coordinates, label):
        """Validate annotation data."""
        if annotation_type not in ANNOTATION_TYPES:
            return False
            
        if not coordinates:
            return False
            
        if annotation_type == 'Point' and len(coordinates) != 2:
            return False
        elif annotation_type in ['Rectangle', 'Circle'] and len(coordinates) != 4:
            return False
        elif annotation_type == 'Polygon' and len(coordinates) < 6:  # At least 3 points
            return False
            
        if not label:
            return False
            
        return True
        
    def get_annotation_summary(self, annotation):
        """Get a formatted summary of an annotation."""
        ann_type = annotation['type']
        label = annotation.get('label', 'No Label')
        coords = annotation['coordinates']
        
        summary = f"{ann_type}: {label}"
        
        if ann_type == 'Point':
            summary += f" at {format_coordinates(coords[:2])}"
        elif ann_type in ['Rectangle', 'Circle']:
            summary += f" {format_coordinates(coords)}"
        elif ann_type == 'Polygon':
            num_points = len(coords) // 2
            summary += f" with {num_points} vertices"
            
        return summary
        
    def get_annotation_details(self, annotation):
        """Get detailed information about an annotation."""
        ann_type = annotation['type']
        label = annotation.get('label', 'No Label')
        coords = annotation['coordinates']
        color = annotation.get('color', DEFAULTS['ANNOTATION_COLOR'])
        
        details = {
            'type': ann_type,
            'label': label,
            'color': color,
            'coordinates': coords
        }
        
        if ann_type == 'Point':
            details['position'] = f"({coords[0]:.1f}, {coords[1]:.1f})"
            
        elif ann_type in ['Rectangle', 'Circle']:
            width = abs(coords[2] - coords[0])
            height = abs(coords[3] - coords[1])
            area = width * height
            
            details.update({
                'top_left': f"({coords[0]:.1f}, {coords[1]:.1f})",
                'bottom_right': f"({coords[2]:.1f}, {coords[3]:.1f})",
                'width': f"{width:.1f}",
                'height': f"{height:.1f}",
                'area': f"{area:.1f}"
            })
            
        elif ann_type == 'Polygon':
            num_points = len(coords) // 2
            area = calculate_polygon_area(coords)
            
            details.update({
                'num_vertices': num_points,
                'area': f"{area:.1f}",
                'vertices': []
            })
            
            for i in range(0, len(coords), 2):
                details['vertices'].append(f"({coords[i]:.1f}, {coords[i+1]:.1f})")
                
        return details
        
    def save_annotation_state(self):
        """Save current state for undo functionality."""
        current_state = {
            'annotations': copy.deepcopy(self.current_annotations)
        }
        
        self.undo_stack.append(current_state)
        self.redo_stack.clear()  # Clear redo stack when new action is performed
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
            
    def undo(self):
        """Undo last annotation action."""
        if self.undo_stack:
            # Save current state to redo stack
            current_state = {
                'annotations': copy.deepcopy(self.current_annotations)
            }
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.undo_stack.pop()
            self.current_annotations = previous_state['annotations']
            return True
        return False
        
    def redo(self):
        """Redo last undone action."""
        if self.redo_stack:
            # Save current state to undo stack
            current_state = {
                'annotations': copy.deepcopy(self.current_annotations)
            }
            self.undo_stack.append(current_state)
            
            # Restore next state
            next_state = self.redo_stack.pop()
            self.current_annotations = next_state['annotations']
            return True
        return False
        
    def save_image_annotations(self, image_path):
        """Save current annotations to the specified image path."""
        if image_path:
            self.annotations[image_path] = copy.deepcopy(self.current_annotations)
            
    def load_image_annotations(self, image_path):
        """Load annotations for the specified image path."""
        if image_path in self.annotations:
            self.current_annotations = copy.deepcopy(self.annotations[image_path])
        else:
            self.current_annotations = []
            
        # Clear undo/redo stacks when switching images
        self.undo_stack.clear()
        self.redo_stack.clear()
        
    def get_annotation_statistics(self):
        """Get statistics about current annotations."""
        if not self.current_annotations:
            return {}
            
        stats = {
            'total': len(self.current_annotations),
            'by_type': {},
            'by_label': {}
        }
        
        for annotation in self.current_annotations:
            ann_type = annotation['type']
            label = annotation.get('label', 'No Label')
            
            # Count by type
            stats['by_type'][ann_type] = stats['by_type'].get(ann_type, 0) + 1
            
            # Count by label
            stats['by_label'][label] = stats['by_label'].get(label, 0) + 1
            
        return stats
        
    def find_annotations_by_label(self, label):
        """Find all annotations with the specified label."""
        return [
            (i, ann) for i, ann in enumerate(self.current_annotations) 
            if ann.get('label') == label
        ]
        
    def find_annotations_by_type(self, annotation_type):
        """Find all annotations of the specified type."""
        return [
            (i, ann) for i, ann in enumerate(self.current_annotations) 
            if ann['type'] == annotation_type
        ]