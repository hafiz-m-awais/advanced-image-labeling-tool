# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build specification for Image Labeling Tool
This file defines how to build the executable from the Python application
"""

block_cipher = None

# Define the main script and dependencies
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('requirements.txt', '.'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        'json',
        'xml.etree.ElementTree',
        'xml.dom.minidom',
        'os',
        'copy',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary modules to reduce size
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageLabelingTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress the executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Windows specific options
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,  # Application icon
    version='version_info.txt',  # Version information
)

# Optional: Create a directory distribution instead of single file
# Uncomment the following lines if you prefer a directory distribution
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='ImageLabelingTool'
# )