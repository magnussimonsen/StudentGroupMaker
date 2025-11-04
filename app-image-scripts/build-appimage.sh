#!/bin/bash
# Build AppImage for GroupMaker
# This creates a portable single-file executable for Linux
# To run this script, first run ./build-wrapper.sh to build the executable
# Then run this script to create the AppImage. Command: ./app-image-scripts/build-appimage.sh
set -e

echo "========================================"
echo "GroupMaker AppImage Builder"
echo "========================================"

# Get to project root
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

# Check if executable exists
if [ ! -f "dist/GroupMaker" ]; then
    echo "ERROR: dist/GroupMaker not found!"
    echo "Please run ./build-wrapper.sh first to build the executable"
    exit 1
fi

# Create AppDir structure
echo "Creating AppDir structure..."
APPDIR="$PROJECT_DIR/AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copy executable
echo "Copying executable..."
cp dist/GroupMaker "$APPDIR/usr/bin/groupmaker"
chmod +x "$APPDIR/usr/bin/groupmaker"

# Create .desktop file
echo "Creating .desktop file..."
cat > "$APPDIR/usr/share/applications/groupmaker.desktop" << 'EOF'
[Desktop Entry]
Name=GroupMaker
Comment=Create random student groups with minimal pair repetition
Exec=groupmaker
Icon=groupmaker
Type=Application
Categories=Education;
Terminal=false
EOF

# Copy icon (if exists) or create placeholder
ICON_SOURCE="src/icons/icon.png"
if [ -f "$ICON_SOURCE" ]; then
    echo "Copying icon from $ICON_SOURCE..."
    cp "$ICON_SOURCE" "$APPDIR/usr/share/icons/hicolor/256x256/apps/groupmaker.png"
    cp "$ICON_SOURCE" "$APPDIR/groupmaker.png"
    cp "$ICON_SOURCE" "$APPDIR/.DirIcon"
else
    echo "WARNING: No icon found at $ICON_SOURCE"
    echo "Creating placeholder icon..."
    # Create a simple placeholder (requires imagemagick)
    if command -v convert &> /dev/null; then
        convert -size 256x256 xc:#4A90E2 -gravity center -pointsize 48 -fill white \
                -annotate +0+0 "GM" "$APPDIR/groupmaker.png"
        cp "$APPDIR/groupmaker.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/groupmaker.png"
        cp "$APPDIR/groupmaker.png" "$APPDIR/.DirIcon"
    else
        echo "Install imagemagick to auto-generate icon, or add app-image-scripts/icon.png"
    fi
fi

# Create AppRun script
echo "Creating AppRun script..."
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
exec "${HERE}/usr/bin/groupmaker" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# Copy .desktop file to root (required for AppImage)
cp "$APPDIR/usr/share/applications/groupmaker.desktop" "$APPDIR/groupmaker.desktop"

# Download appimagetool if not present
APPIMAGETOOL="$PROJECT_DIR/app-image-scripts/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    wget -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# Build AppImage
echo "Building AppImage..."

# Try running appimagetool normally first
if ARCH=x86_64 "$APPIMAGETOOL" "$APPDIR" "GroupMaker-x86_64.AppImage" 2>/dev/null; then
    echo "AppImage built successfully!"
else
    echo "Standard method failed, trying extraction method..."
    # If FUSE is not available, extract and run
    if ARCH=x86_64 "$APPIMAGETOOL" --appimage-extract-and-run "$APPDIR" "GroupMaker-x86_64.AppImage"; then
        echo "AppImage built successfully using extraction method!"
    else
        echo ""
        echo "ERROR: Failed to build AppImage"
        echo ""
        echo "If you see FUSE errors, install FUSE:"
        echo "  sudo apt install libfuse2"
        echo ""
        echo "Or use the extraction method (no FUSE needed):"
        echo "  cd app-image-scripts"
        echo "  ./appimagetool-x86_64.AppImage --appimage-extract"
        echo "  ./squashfs-root/AppRun ../AppDir GroupMaker-x86_64.AppImage"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "AppImage build complete!"
echo "========================================"
echo "Output: GroupMaker-x86_64.AppImage"
echo ""
echo "To run:"
echo "  chmod +x GroupMaker-x86_64.AppImage"
echo "  ./GroupMaker-x86_64.AppImage"
echo ""
echo "To distribute:"
echo "  Upload GroupMaker-x86_64.AppImage to GitHub releases"
echo "  Users can download and run without installation"
