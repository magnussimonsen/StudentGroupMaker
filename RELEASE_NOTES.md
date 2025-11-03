# Release Notes

## Version 0.2.0 - November 2025

### 🎉 New Features
- **Co-occurrence Matrix Heatmap**: Visual color-coded matrix showing pairing frequency across rounds
- **Dark/Light Mode Toggle**: Switch themes via View menu for comfortable viewing
- **Adjustable Font Size**: 8pt-24pt options in Font Size menu for better accessibility
- **AppImage Distribution**: Portable single-file Linux executable (no installation required)

### 🚀 Improvements
- **Modular Architecture**: Complete codebase refactor into organized packages (core, models, ui, utils, constants)
- **Cross-platform Build System**: Automated build scripts for Windows and Linux
- **Enhanced UI Layout**: Streamlined top toolbar with controls, bottom bar for student actions
- **Better Export**: File dialog for choosing save location when exporting group plans
- **Professional Visualization**: Matplotlib-powered heatmaps with color scales and annotations

### 🔧 Technical Changes
- Migrated to modular `src/` package structure (16+ organized modules)
- Added matplotlib for data visualization
- Improved PyInstaller build with automatic dependency detection and hidden imports
- AppImage packaging with desktop integration
- Cross-platform development scripts (Python + shell wrappers)
- Virtual environment automation with `setup_group_maker_env.py`

### 🐛 Bug Fixes
- Fixed export functionality to use schedule data instead of formatted text
- Corrected matrix visualization to use proper matplotlib heatmap
- Added QDialog and QPushButton imports to main window
- Fixed export parameter mismatch (filename, class_name, rounds)

### 📦 Distribution
- **Linux**: `GroupMaker-x86_64.AppImage` (~98MB) - works on all distros
- **Windows**: `GroupMaker.exe` (build from Windows machine)
- **FUSE workaround**: `--appimage-extract-and-run` flag for modern Ubuntu systems

### 👨‍💻 For Developers
- Virtual environment setup automation (`setup_group_maker_env.py`)
- Unified cross-platform build scripts
- Launcher scripts for Windows (`.bat`) and Linux (`.sh`)
- AppImage build system in `app-image-scripts/`
- Clean separation of concerns following Unix philosophy
- Comprehensive README with setup instructions

### 📚 Documentation
- Updated README with AppImage download instructions
- Added FUSE troubleshooting guide
- Build instructions for both platforms
- AppImage packaging documentation
