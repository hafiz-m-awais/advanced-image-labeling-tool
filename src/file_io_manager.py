"""
File I/O Manager for the Image Labeling Tool.
Handles loading/saving annotations in various formats (JSON, COCO, Pascal VOC).
"""

import json
import os
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox
from PIL import Image
import tkinter as tk
from .utils import (
    find_image_files, get_current_date, ensure_directory_exists, 
    get_basename_without_ext, calculate_polygon_area
)
from .constants import FILE_TYPES


class FileIOManager:
    """Manages file I/O operations for annotations and datasets."""
    
    def __init__(self, controller):
        self.controller = controller
        
    def load_single_image(self):
        """Load a single image file."""
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=FILE_TYPES['IMAGES']
        )
        
        if file_path:
            if not self.controller.reset_workspace():
                return
            
            self.controller.images = [file_path]
            
            # Update image listbox
            image_listbox = self.controller.ui_manager.get_widget('image_listbox')
            if image_listbox:
                image_listbox.insert(0, os.path.basename(file_path))
                image_listbox.selection_set(0)
                self.controller.on_image_select(None)
            
            messagebox.showinfo("Success", f"Loaded image: {os.path.basename(file_path)}")
            
    def load_folder(self):
        """Load all images from a folder."""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
            
        if not self.controller.reset_workspace():
            return
            
        # Find all image files
        self.controller.images = find_image_files(folder_path)
        
        if self.controller.images:
            # Update image listbox
            image_listbox = self.controller.ui_manager.get_widget('image_listbox')
            if image_listbox:
                for img_path in self.controller.images:
                    image_listbox.insert(tk.END, os.path.basename(img_path))
                
                # Select first image
                image_listbox.selection_set(0)
                self.controller.on_image_select(None)
            
            messagebox.showinfo("Success", f"Loaded {len(self.controller.images)} images")
        else:
            messagebox.showwarning("Warning", "No supported image files found in the selected folder")
            
    def save_annotations(self):
        """Save annotations to individual JSON files."""
        if not self.controller.images:
            messagebox.showwarning("Warning", "No images loaded")
            return
        
        # Save current image annotations first
        if self.controller.current_image_index >= 0:
            self.controller.annotation_manager.save_image_annotations(self.controller.current_image_path)
        
        saved_count = 0
        annotations_dict = self.controller.annotation_manager.annotations
        
        for image_path, annotations in annotations_dict.items():
            if annotations:  # Only save if there are annotations
                base_name = get_basename_without_ext(image_path)
                json_path = os.path.join(os.path.dirname(image_path), base_name + "_annotations.json")
                
                try:
                    save_data = {
                        'image_path': image_path,
                        'image_name': os.path.basename(image_path),
                        'annotations': annotations,
                        'labels': self.controller.labels,
                        'label_colors': self.controller.label_colors,
                        'total_annotations': len(annotations),
                        'annotation_types': list(set([ann['type'] for ann in annotations])),
                        'creation_date': get_current_date()
                    }
                    
                    with open(json_path, 'w') as f:
                        json.dump(save_data, f, indent=2)
                    
                    saved_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save annotations for {os.path.basename(image_path)}: {str(e)}")
        
        if saved_count > 0:
            messagebox.showinfo("Save Complete", 
                              f"Successfully saved annotations for {saved_count} images\n" +
                              f"Files saved with '_annotations.json' suffix")
        else:
            messagebox.showinfo("Nothing to Save", 
                              "No annotations found to save.\n" +
                              "Create some annotations first, then save.")
                              
    def save_master_dataset(self):
        """Save all annotations into a single master JSON file."""
        if not self.controller.images:
            messagebox.showwarning("Warning", "No images loaded")
            return
        
        # Save current image annotations first
        if self.controller.current_image_index >= 0:
            self.controller.annotation_manager.save_image_annotations(self.controller.current_image_path)
        
        # Ask user for save location
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=FILE_TYPES['JSON'],
            title="Save Master Dataset As",
            initialfile="master_dataset.json"
        )
        
        if not save_path:
            return
        
        try:
            annotations_dict = self.controller.annotation_manager.annotations
            
            # Prepare master dataset
            dataset = {
                'dataset_info': {
                    'total_images': len(self.controller.images),
                    'total_annotations': sum(len(anns) for anns in annotations_dict.values()),
                    'labels': self.controller.labels,
                    'label_colors': self.controller.label_colors,
                    'creation_date': get_current_date(),
                    'annotation_types': list(set(
                        ann['type'] 
                        for img_anns in annotations_dict.values() 
                        for ann in img_anns
                    ))
                },
                'images': []
            }
            
            # Add data for each image
            for image_path in self.controller.images:
                image_annotations = annotations_dict.get(image_path, [])
                image_data = {
                    'image_path': image_path,
                    'image_name': os.path.basename(image_path),
                    'relative_path': os.path.relpath(image_path, os.path.dirname(save_path)),
                    'annotations': image_annotations,
                    'total_annotations': len(image_annotations),
                    'annotation_types': list(set(ann['type'] for ann in image_annotations)) if image_annotations else []
                }
                dataset['images'].append(image_data)
            
            # Save the master dataset
            with open(save_path, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            messagebox.showinfo("Success", 
                              f"Master dataset saved successfully!\n\n"
                              f"Total images: {len(dataset['images'])}\n"
                              f"Total annotations: {dataset['dataset_info']['total_annotations']}\n"
                              f"Saved to: {os.path.basename(save_path)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save master dataset: {str(e)}")
            
    def load_individual_annotations(self):
        """Load annotations from individual JSON files."""
        if not self.controller.images:
            messagebox.showwarning("Warning", "No images loaded")
            return
        
        loaded_count = 0
        annotations_dict = self.controller.annotation_manager.annotations
        
        for image_path in self.controller.images:
            base_name = get_basename_without_ext(image_path)
            json_path = os.path.join(os.path.dirname(image_path), base_name + "_annotations.json")
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    
                    # Load annotations
                    annotations_dict[image_path] = data.get('annotations', [])
                    
                    # Update labels and their colors if they exist in the file
                    file_labels = data.get('labels', [])
                    file_colors = data.get('label_colors', {})
                    
                    for label in file_labels:
                        if label not in self.controller.labels:
                            self.controller.labels.append(label)
                            if label in file_colors:
                                self.controller.label_colors[label] = file_colors[label]
                    
                    loaded_count += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load annotations for {os.path.basename(image_path)}: {str(e)}")
        
        # Update displays
        self.controller.update_labels_listbox()
        if self.controller.current_image_index >= 0:
            self.controller.annotation_manager.load_image_annotations(self.controller.current_image_path)
            self.controller.update_annotations_display()
        
        if loaded_count > 0:
            messagebox.showinfo("Success", f"Loaded annotations for {loaded_count} images")
        else:
            messagebox.showinfo("Info", "No annotation files found")
            
    def load_master_dataset(self):
        """Load annotations from a master dataset JSON file."""
        master_file = filedialog.askopenfilename(
            title="Select Master Dataset File",
            filetypes=FILE_TYPES['JSON'],
            initialfile="master_dataset.json"
        )
        
        if not master_file:
            return
            
        try:
            with open(master_file, 'r') as f:
                master_data = json.load(f)
            
            # Reset workspace before loading
            if not self.controller.reset_workspace():
                return
                
            # Load dataset info
            dataset_info = master_data.get('dataset_info', {})
            
            # Load labels and colors
            self.controller.labels = dataset_info.get('labels', [])
            self.controller.label_colors = dataset_info.get('label_colors', {})
            
            # Load annotations
            loaded_count = 0
            skipped_count = 0
            master_base_path = os.path.dirname(master_file)
            annotations_dict = self.controller.annotation_manager.annotations
            
            for image_data in master_data.get('images', []):
                image_path = image_data.get('image_path')
                relative_path = image_data.get('relative_path')
                
                # Try different path variations to find the image
                possible_paths = [
                    image_path,  # Absolute path as stored
                    os.path.join(master_base_path, relative_path),  # Relative to master file
                    os.path.join(os.path.dirname(master_file), os.path.basename(image_path))  # Same folder as master
                ]
                
                found_path = None
                for path in possible_paths:
                    if path and os.path.exists(path):
                        found_path = path
                        break
                
                if found_path:
                    # Add to images list if not already there
                    if found_path not in self.controller.images:
                        self.controller.images.append(found_path)
                        image_listbox = self.controller.ui_manager.get_widget('image_listbox')
                        if image_listbox:
                            image_listbox.insert(tk.END, os.path.basename(found_path))
                    
                    # Load annotations
                    annotations_dict[found_path] = image_data.get('annotations', [])
                    loaded_count += 1
                else:
                    skipped_count += 1
            
            # Update displays
            self.controller.update_labels_listbox()
            
            # If no image was selected, select the first one
            if self.controller.current_image_index == -1 and self.controller.images:
                image_listbox = self.controller.ui_manager.get_widget('image_listbox')
                if image_listbox:
                    image_listbox.selection_set(0)
                    self.controller.on_image_select(None)
            else:
                if self.controller.current_image_path:
                    self.controller.annotation_manager.load_image_annotations(self.controller.current_image_path)
                    self.controller.update_annotations_display()
            
            # Show results
            status = f"Loaded {loaded_count} image annotations"
            if skipped_count > 0:
                status += f"\nSkipped {skipped_count} images (not found)"
            messagebox.showinfo("Load Complete", status)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load master dataset: {str(e)}")
            
    def import_coco(self):
        """Import annotations from COCO format JSON file."""
        if not self.controller.images:
            if messagebox.askyesno("No Images Loaded", 
                                 "You need to load images before importing COCO annotations.\n\n"
                                 "Would you like to load images now?"):
                self.load_folder()
            return

        coco_file = filedialog.askopenfilename(
            title="Select COCO Annotation File",
            filetypes=FILE_TYPES['JSON']
        )
        
        if not coco_file:
            return

        try:
            with open(coco_file, 'r', encoding='utf-8') as f:
                coco_data = json.load(f)
            
            # Validate COCO format
            required_keys = ["images", "annotations", "categories"]
            if not all(key in coco_data for key in required_keys):
                raise ValueError("Invalid COCO format: Missing required keys")

            # Save current annotations if any
            if self.controller.current_image_index >= 0:
                self.controller.annotation_manager.save_image_annotations(self.controller.current_image_path)

            # Create mapping of category IDs to names
            category_map = {cat['id']: cat['name'] for cat in coco_data['categories']}
            
            # Create mapping of image IDs to image info
            image_map = {img['id']: {
                'file_name': img['file_name'],
                'width': img.get('width'),
                'height': img.get('height')
            } for img in coco_data['images']}

            # Add categories as labels if they don't exist
            for category in coco_data['categories']:
                label = category['name']
                if label not in self.controller.labels:
                    self.controller.labels.append(label)
                    if label not in self.controller.label_colors:
                        import random
                        color = f'#{random.randint(0, 0xFFFFFF):06x}'
                        self.controller.label_colors[label] = color

            self.controller.update_labels_listbox()

            # Create a mapping of filenames to full paths
            file_map = {os.path.basename(path): path for path in self.controller.images}
            
            # Process annotations
            imported_annotations = {}
            skipped_images = set()
            skipped_annotations = 0
            processed_annotations = 0

            # Group annotations by image_id
            annotations_by_image = {}
            for ann in coco_data['annotations']:
                img_id = ann.get('image_id')
                if img_id not in annotations_by_image:
                    annotations_by_image[img_id] = []
                annotations_by_image[img_id].append(ann)

            # Process each image
            for img_id, img_info in image_map.items():
                img_filename = img_info['file_name']
                if img_filename not in file_map:
                    skipped_images.add(img_filename)
                    continue

                img_path = file_map[img_filename]
                current_annotations = []

                # Process annotations for this image
                for ann in annotations_by_image.get(img_id, []):
                    try:
                        category_id = ann.get('category_id')
                        if category_id not in category_map:
                            continue

                        label = category_map[category_id]
                        bbox = ann.get('bbox', [])
                        segmentation = ann.get('segmentation', [])

                        if len(bbox) == 4:
                            # COCO bbox format: [x, y, width, height]
                            x, y, w, h = map(float, bbox)
                            annotation = {
                                'type': 'Rectangle',
                                'coordinates': [x, y, x + w, y + h],
                                'label': label,
                                'color': self.controller.label_colors.get(label, '#FF0000')
                            }
                            current_annotations.append(annotation)
                            processed_annotations += 1

                        elif segmentation and len(segmentation[0]) >= 6:
                            # Convert segmentation to polygon
                            coords = [float(c) for c in segmentation[0]]
                            annotation = {
                                'type': 'Polygon',
                                'coordinates': coords,
                                'label': label,
                                'color': self.controller.label_colors.get(label, '#FF0000')
                            }
                            current_annotations.append(annotation)
                            processed_annotations += 1
                        else:
                            skipped_annotations += 1

                    except Exception as e:
                        print(f"Warning: Failed to process annotation: {e}")
                        skipped_annotations += 1
                        continue

                if current_annotations:
                    imported_annotations[img_path] = current_annotations

            # Update annotations dictionary with imported annotations
            self.controller.annotation_manager.annotations.update(imported_annotations)

            # Refresh current image if it was in the imported set
            if self.controller.current_image_path in imported_annotations:
                self.controller.annotation_manager.load_image_annotations(self.controller.current_image_path)
                self.controller.update_annotations_display()

            # Show results
            status = (f"Successfully imported COCO annotations:\n"
                     f"Images with annotations: {len(imported_annotations)}\n"
                     f"Processed annotations: {processed_annotations}\n"
                     f"Skipped annotations: {skipped_annotations}\n")
            
            if skipped_images:
                status += f"\nWarning: Could not find these images:\n"
                status += "\n".join(sorted(list(skipped_images)[:5]))
                if len(skipped_images) > 5:
                    status += f"\n... and {len(skipped_images) - 5} more"

            messagebox.showinfo("Import Complete", status)

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file. Please make sure the file is in valid COCO JSON format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import COCO annotations:\n{str(e)}")
            
    def export_coco(self):
        """Export annotations in COCO format."""
        if not self.controller.images:
            messagebox.showwarning("Warning", "No images loaded")
            return
            
        # Save current image annotations first
        if self.controller.current_image_index >= 0:
            self.controller.annotation_manager.save_image_annotations(self.controller.current_image_path)
            
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=FILE_TYPES['JSON'],
            title="Export COCO Annotations",
            initialfile="annotations_coco.json"
        )
        
        if not save_path:
            return
            
        try:
            from datetime import datetime
            
            # Initialize COCO format structure
            coco_data = {
                "info": {
                    "year": datetime.now().year,
                    "version": "1.0",
                    "description": "Exported from Image Labeling Tool",
                    "contributor": "",
                    "date_created": get_current_date()
                },
                "licenses": [{"id": 1, "name": "Unknown", "url": ""}],
                "images": [],
                "annotations": [],
                "categories": []
            }
            
            # Create category mapping
            for i, label in enumerate(self.controller.labels, 1):
                coco_data["categories"].append({
                    "id": i,
                    "name": label,
                    "supercategory": "none"
                })
            category_map = {label: i for i, label in enumerate(self.controller.labels, 1)}
            
            annotation_id = 1
            annotations_dict = self.controller.annotation_manager.annotations
            
            # Process each image and its annotations
            for image_id, image_path in enumerate(self.controller.images, 1):
                # Get image dimensions
                try:
                    with Image.open(image_path) as img:
                        width, height = img.size
                except Exception as e:
                    print(f"Warning: Could not read image dimensions for {image_path}: {e}")
                    continue
                
                # Add image info
                coco_data["images"].append({
                    "id": image_id,
                    "file_name": os.path.basename(image_path),
                    "width": width,
                    "height": height,
                    "date_captured": get_current_date(),
                    "license": 1,
                    "coco_url": "",
                    "flickr_url": ""
                })
                
                # Process annotations for this image
                image_annotations = annotations_dict.get(image_path, [])
                for ann in image_annotations:
                    if ann['type'] not in ['Point', 'Rectangle', 'Circle', 'Polygon']:
                        continue
                        
                    coords = ann['coordinates']
                    label = ann.get('label')
                    if not label or label not in category_map:
                        continue
                        
                    try:
                        if ann['type'] == 'Point':
                            # Convert point to tiny rectangle for COCO format
                            x, y = coords
                            x, y = float(x), float(y)
                            bbox = [x-1, y-1, 2, 2]  # 2x2 pixel box
                            area = 4
                            segmentation = [[x-1, y-1, x+1, y-1, x+1, y+1, x-1, y+1]]
                            
                        elif ann['type'] in ['Rectangle', 'Circle']:
                            x1, y1, x2, y2 = map(float, coords)
                            # Ensure x1,y1 is top-left and x2,y2 is bottom-right
                            x1, x2 = min(x1, x2), max(x1, x2)
                            y1, y2 = min(y1, y2), max(y1, y2)
                            width = x2 - x1
                            height = y2 - y1
                            bbox = [x1, y1, width, height]
                            area = width * height
                            segmentation = [[x1, y1, x2, y1, x2, y2, x1, y2]]
                            
                        elif ann['type'] == 'Polygon':
                            polygon_coords = [float(c) for c in coords]
                            # Calculate bounding box
                            xs = polygon_coords[::2]
                            ys = polygon_coords[1::2]
                            x1, y1 = min(xs), min(ys)
                            x2, y2 = max(xs), max(ys)
                            width = x2 - x1
                            height = y2 - y1
                            bbox = [x1, y1, width, height]
                            area = calculate_polygon_area(polygon_coords)
                            segmentation = [polygon_coords]
                        
                        # Create COCO annotation
                        coco_ann = {
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": category_map[label],
                            "segmentation": segmentation,
                            "area": float(area),
                            "bbox": [float(x) for x in bbox],
                            "iscrowd": 0
                        }
                        
                        coco_data["annotations"].append(coco_ann)
                        annotation_id += 1
                        
                    except Exception as e:
                        print(f"Warning: Failed to process annotation: {e}")
                        continue
            
            # Save the COCO format data
            with open(save_path, 'w') as f:
                json.dump(coco_data, f, indent=2)
            
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported annotations in COCO format\n"
                              f"Total images: {len(coco_data['images'])}\n"
                              f"Total annotations: {len(coco_data['annotations'])}\n"
                              f"Total categories: {len(coco_data['categories'])}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export annotations: {str(e)}")
            
    def export_pascal_voc(self):
        """Export annotations in Pascal VOC format."""
        if not self.controller.images:
            messagebox.showwarning("Warning", "No images loaded")
            return
            
        # Save current image annotations first
        if self.controller.current_image_index >= 0:
            self.controller.annotation_manager.save_image_annotations(self.controller.current_image_path)
        
        export_dir = filedialog.askdirectory(
            title="Select Directory for Pascal VOC Annotations"
        )
        
        if not export_dir:
            return
            
        try:
            # Create Annotations subdirectory
            annotations_dir = os.path.join(export_dir, "Annotations")
            ensure_directory_exists(annotations_dir)
            
            processed_count = 0
            skipped_count = 0
            annotations_dict = self.controller.annotation_manager.annotations
            
            for image_path in self.controller.images:
                image_annotations = annotations_dict.get(image_path, [])
                if not image_annotations:
                    skipped_count += 1
                    continue
                
                try:
                    # Get image dimensions
                    with Image.open(image_path) as img:
                        width, height = img.size
                        channels = len(img.getbands())
                except Exception as e:
                    print(f"Warning: Could not read image {image_path}: {e}")
                    skipped_count += 1
                    continue
                
                # Create XML structure
                annotation = ET.Element("annotation")
                
                # Add basic image information
                ET.SubElement(annotation, "folder").text = os.path.basename(os.path.dirname(image_path))
                ET.SubElement(annotation, "filename").text = os.path.basename(image_path)
                ET.SubElement(annotation, "path").text = image_path
                
                source = ET.SubElement(annotation, "source")
                ET.SubElement(source, "database").text = "Unknown"
                
                size = ET.SubElement(annotation, "size")
                ET.SubElement(size, "width").text = str(width)
                ET.SubElement(size, "height").text = str(height)
                ET.SubElement(size, "depth").text = str(channels)
                
                ET.SubElement(annotation, "segmented").text = "0"
                
                # Process each annotation
                for ann in image_annotations:
                    if ann['type'] not in ['Point', 'Rectangle', 'Circle', 'Polygon']:
                        continue
                        
                    coords = ann['coordinates']
                    label = ann.get('label')
                    if not label:
                        continue
                    
                    obj = ET.SubElement(annotation, "object")
                    ET.SubElement(obj, "name").text = label
                    ET.SubElement(obj, "pose").text = "Unspecified"
                    ET.SubElement(obj, "truncated").text = "0"
                    ET.SubElement(obj, "difficult").text = "0"
                    
                    if ann['type'] == 'Point':
                        x, y = coords
                        bndbox = ET.SubElement(obj, "bndbox")
                        ET.SubElement(bndbox, "xmin").text = str(int(x - 1))
                        ET.SubElement(bndbox, "ymin").text = str(int(y - 1))
                        ET.SubElement(bndbox, "xmax").text = str(int(x + 1))
                        ET.SubElement(bndbox, "ymax").text = str(int(y + 1))
                        
                    elif ann['type'] in ['Rectangle', 'Circle']:
                        x1, y1, x2, y2 = coords
                        x1, x2 = min(x1, x2), max(x1, x2)
                        y1, y2 = min(y1, y2), max(y1, y2)
                        
                        bndbox = ET.SubElement(obj, "bndbox")
                        ET.SubElement(bndbox, "xmin").text = str(int(x1))
                        ET.SubElement(bndbox, "ymin").text = str(int(y1))
                        ET.SubElement(bndbox, "xmax").text = str(int(x2))
                        ET.SubElement(bndbox, "ymax").text = str(int(y2))
                        
                    elif ann['type'] == 'Polygon':
                        # For polygons, create bounding box from extremes
                        xs = coords[::2]
                        ys = coords[1::2]
                        x1, y1 = min(xs), min(ys)
                        x2, y2 = max(xs), max(ys)
                        
                        bndbox = ET.SubElement(obj, "bndbox")
                        ET.SubElement(bndbox, "xmin").text = str(int(x1))
                        ET.SubElement(bndbox, "ymin").text = str(int(y1))
                        ET.SubElement(bndbox, "xmax").text = str(int(x2))
                        ET.SubElement(bndbox, "ymax").text = str(int(y2))
                        
                        # Add polygon points as additional data
                        polygon = ET.SubElement(obj, "polygon")
                        for i in range(0, len(coords), 2):
                            point = ET.SubElement(polygon, "pt")
                            ET.SubElement(point, "x").text = str(int(coords[i]))
                            ET.SubElement(point, "y").text = str(int(coords[i + 1]))
                
                # Create XML file
                tree = ET.ElementTree(annotation)
                xml_filename = get_basename_without_ext(image_path) + ".xml"
                xml_path = os.path.join(annotations_dir, xml_filename)
                
                # Write pretty XML
                try:
                    import xml.dom.minidom as minidom
                    xml_str = ET.tostring(annotation, 'utf-8')
                    dom = minidom.parseString(xml_str)
                    with open(xml_path, 'w', encoding='utf-8') as f:
                        f.write(dom.toprettyxml(indent="    "))
                except:
                    # Fallback to basic XML writing
                    tree.write(xml_path, encoding='utf-8', xml_declaration=True)
                
                processed_count += 1
            
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported annotations in Pascal VOC format\n"
                              f"Processed images: {processed_count}\n"
                              f"Skipped images: {skipped_count}\n"
                              f"Annotations saved in: {annotations_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export annotations: {str(e)}")