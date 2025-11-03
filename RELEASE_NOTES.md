# Release Notes

## Version 0.2.0 - November 2025

### New Features
- **Co-occurrence Matrix Visualization**: Visual heatmap showing how often students are paired together across rounds
- **Dark/Light Mode**: Toggle between themes via View menu for comfortable viewing in any lighting
- **Adjustable Font Size**: Menu options from 8pt to 24pt for better accessibility

### Improvements
- **Modular Architecture**: Complete codebase refactor into organized packages (core, models, ui, utils, constants)
- **Cross-platform Build System**: Automated build scripts work on both Windows and Linux
- **Enhanced UI Layout**: Streamlined controls in top bar, student actions in bottom bar
- **Better Export**: File dialog for choosing save location when exporting group plans

### Technical Changes
- Migrated to modular `src/` package structure
- Added matplotlib for data visualization
- Improved PyInstaller build configuration with automatic dependency detection
- Cross-platform development scripts (setup, run, build)

### Bug Fixes
- Fixed export functionality to use actual schedule data instead of formatted text
- Corrected matrix visualization to use proper heatmap instead of text table

### For Developers
- Virtual environment setup automation
- Unified cross-platform build scripts
- Development launcher scripts for both Windows (`.bat`) and Linux (`.sh`)
- Clean separation of concerns following Unix philosophy
