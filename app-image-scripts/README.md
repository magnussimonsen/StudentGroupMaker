# AppImage Build Scripts

This directory contains scripts for building AppImage packages for Linux distribution.

## What is AppImage?

AppImage is a universal package format for Linux that creates a single executable file containing your app and all dependencies. Users can download and run it without installation.

## Prerequisites

- Built executable in `dist/GroupMaker` (run `./build-wrapper.sh` first)
- (Optional) Icon file at `app-image-scripts/icon.png` (256x256 PNG recommended)
- (Optional) ImageMagick for auto-generating placeholder icon

## Build AppImage

```bash
# Make script executable
chmod +x app-image-scripts/build-appimage.sh

# Run the build
./app-image-scripts/build-appimage.sh
```

This will:
1. Check that `dist/GroupMaker` exists
2. Create AppDir structure with proper layout
3. Download `appimagetool` (if needed)
4. Package everything into `GroupMaker-x86_64.AppImage`

## Output

**File:** `GroupMaker-x86_64.AppImage` (~90MB)

**Distribution:**
- Upload to GitHub Releases
- Users download, make executable, and run
- No installation or dependencies needed on user's system

## Usage for End Users

```bash
# Download the AppImage
wget https://github.com/magnussimonsen/StudentGroupMaker/releases/latest/download/GroupMaker-x86_64.AppImage

# Make it executable
chmod +x GroupMaker-x86_64.AppImage

# Run it
./GroupMaker-x86_64.AppImage
```

### FUSE Issues (Common on Modern Ubuntu)

If you see FUSE errors like `Cannot mount AppImage` or `error loading libfuse.so.2`, use the extract-and-run method:

```bash
# Run with extraction (no FUSE needed)
./GroupMaker-x86_64.AppImage --appimage-extract-and-run
```

This is the recommended method for Ubuntu 24.04+ and other modern Linux distributions where FUSE may have permission restrictions.

## Adding a Custom Icon

1. Create a 256x256 PNG icon
2. Save it as `app-image-scripts/icon.png`
3. Rebuild the AppImage

If no icon is provided, the script will attempt to create a placeholder using ImageMagick.

## Files Created

- `AppDir/` - Temporary build directory (auto-cleaned)
- `appimagetool-x86_64.AppImage` - AppImage packaging tool (auto-downloaded)
- `GroupMaker-x86_64.AppImage` - Final distributable package
