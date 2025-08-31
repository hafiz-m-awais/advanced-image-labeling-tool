# Advanced Image Labeling Tool

A professional, modular image annotation application built with Python and Tkinter. Features a modern interface, multiple annotation types, and comprehensive export capabilities for computer vision and machine learning workflows.

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## Screenshots

*Add your application screenshots here*

## Features

### Core Functionality
- **Multiple Annotation Types**: Point, Rectangle, Circle, and Polygon annotations
- **Professional UI**: Modern dark theme with hover effects and smooth interactions
- **Advanced Editing**: Vertex-level editing with drag-and-drop precision
- **Batch Processing**: Load entire folders and manage multiple images
- **Project Management**: Save/load annotation projects with complete state preservation

### User Experience
- **Keyboard Shortcuts**: Full keyboard navigation (P/R/C/G for tools, Ctrl+Z/Y for undo/redo)
- **Context Menus**: Smart right-click menus for annotations and labels
- **Visual Feedback**: Tooltips, status messages, and smooth animations
- **Pan & Zoom**: Mouse wheel zoom, pan mode, fit-to-window functionality
- **Auto-save**: Periodic automatic saving to prevent data loss

### Export & Import
- **Multiple Formats**: JSON, COCO, Pascal VOC export formats
- **Industry Standard**: Compatible with popular ML/CV frameworks
- **Flexible Import**: Support for existing COCO datasets
- **Batch Operations**: Export entire projects or individual images

## Installation

### Option 1: Download Executable (Recommended)
1. Download the latest release from the [Releases](https://github.com/hafiz-m-awais/advanced-image-labeling-tool/releases) page
2. Run `Image Labeling Tool_by_Awais_Setup.exe`
3. Follow the installation wizard
4. Launch from Start Menu or desktop shortcut

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/hafiz-m-awais/advanced-image-labeling-tool.git
cd advanced-image-labeling-tool

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Quick Start

1. **Load Images**: Use "File → Load Folder" or "Load Single Image"
2. **Create Labels**: Click "Add" in the Labels section and choose colors
3. **Select Tools**: Choose from Point, Rectangle, Circle, or Polygon tools
4. **Start Annotating**: Click and drag to create annotations
5. **Save Work**: Use "File → Save Annotations" to save your progress

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Load Images | `Ctrl+O` |
| Save Annotations | `Ctrl+S` |
| Add Label | `Ctrl+N` |
| Undo | `Ctrl+Z` |
| Redo | `Ctrl+Y` |
| Point Tool | `P` |
| Rectangle Tool | `R` |
| Circle Tool | `C` |
| Polygon Tool | `G` |
| Pan Mode | `Space` |
| Zoom In/Out | `Ctrl +/-` |
| Fit to Window | `Ctrl+0` |

## Project Structure

```
image_labeling_tool/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── build.spec                # PyInstaller configuration
├── installer_awais.iss       # Inno Setup installer script
├── assets/                   # Icons and resources
│   └── icon.ico
└── src/                      # Source code modules
    ├── __init__.py
    ├── image_labeling_tool.py      # Main controller
    ├── constants.py               # Application constants
    ├── utils.py                   # Utility functions
    ├── ui_manager.py             # UI components manager
    ├── menu_manager.py           # Menu system
    ├── event_handler.py          # Event handling
    ├── annotation_manager.py     # Annotation data management
    ├── canvas_manager.py         # Canvas operations
    └── file_io_manager.py        # File I/O operations
```

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **Controller Pattern**: `ImageLabelingTool` coordinates all components
- **UI Management**: `UIManager` handles all interface creation and styling
- **Data Management**: `AnnotationManager` manages annotation data and validation
- **Canvas Operations**: `CanvasManager` handles drawing, zoom, and display
- **File Operations**: `FileIOManager` handles multiple format I/O
- **Event Handling**: `EventHandler` manages user interactions and shortcuts

## Building from Source

### Create Executable
```bash
# Install build dependencies
pip install pyinstaller

# Build executable
pyinstaller build.spec
```

### Create Windows Installer
```bash
# Install Inno Setup from https://jrsoftware.org/isdl.php
# Then run:
iscc installer_awais.iss
```

## Export Formats

### JSON Format
```json
{
  "image_path": "path/to/image.jpg",
  "annotations": [
    {
      "type": "Rectangle",
      "coordinates": [10, 10, 100, 100],
      "label": "object",
      "color": "#FF0000"
    }
  ],
  "labels": ["object", "background"],
  "label_colors": {"object": "#FF0000", "background": "#00FF00"}
}
```

### COCO Format
Standard COCO JSON format with images, annotations, and categories sections.

### Pascal VOC Format
XML format compatible with Pascal VOC datasets.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/hafiz-m-awais/advanced-image-labeling-tool.git
cd advanced-image-labeling-tool

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install development dependencies
pip install -r requirements.txt
```

## System Requirements

- **OS**: Windows 7/8/10/11 (64-bit)
- **Python**: 3.6+ (for source installation)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB for installation

## Roadmap

- [ ] **Phase 2**: Auto-save functionality and session persistence
- [ ] **Phase 3**: Plugin system for custom annotation types
- [ ] **Phase 4**: Collaboration features and cloud sync
- [ ] **Phase 5**: AI-assisted annotation suggestions
- [ ] **Phase 6**: Video annotation support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## Changelog

### v1.0.0 (Current)
- Initial release with full annotation suite
- Modern UI with dark theme
- Multiple export formats
- Professional Windows installer
- Comprehensive keyboard shortcuts
- Context menu system

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/hafiz-m-awais/advanced-image-labeling-tool/issues)
- 📚 **Documentation**: [Project Wiki](https://github.com/hafiz-m-awais/advanced-image-labeling-tool/wiki)

---

**⭐ If you found this project helpful, please consider giving it a star!**
