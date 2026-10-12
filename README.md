# GroupMaker

Create random student groups with minimal pair repetition. Built with Python + PySide6.

## Screenshot
![GroupMaker App](dev-screenshots/GroupMaker-2025-11-04-1.png)
![GroupMaker App](dev-screenshots/GroupMaker-2025-11-04-2.png)
![GroupMaker App](dev-screenshots/GroupMaker-2025-11-04-3.png)


## Download
- Latest releases (Windows + Linux):
	- https://github.com/magnussimonsen/StudentGroupMaker/releases/latest

## Features
- Manage multiple classes and student rosters; mark attendance and keep student identities stable when names change
- Export selected classes to one JSON file on the Desktop and import them later, including all saved seating charts
- Switch between Student Groups and Class Seating modes
- Create, rename, and delete multiple saved seating charts for each class
- Arrange and move students between seats and the unseated list using drag and drop
- Adjust classroom rows and columns, view spreadsheet-style seat labels, and flip the classroom orientation
- Generate configurable student groups and rounds, with a seed value (0 = random)
- Review schedule quality and student co-occurrence with the heatmap
- Export generated group plans to a text file
- Choose a light or dark theme and adjust the application font size

## Run from source
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 group-maker.py
```

## Linux AppImage
```bash
wget https://github.com/magnussimonsen/StudentGroupMaker/releases/latest/download/GroupMaker-x86_64.AppImage
chmod +x GroupMaker-x86_64.AppImage
./GroupMaker-x86_64.AppImage
# If you hit FUSE issues:
./GroupMaker-x86_64.AppImage --appimage-extract-and-run
```

## Build (optional)
- Linux executable: `./build-wrapper.sh` → `dist/GroupMaker`
- AppImage: `./app-image-scripts/build-appimage.sh` → `GroupMaker-x86_64.AppImage`
- Windows: build with PyInstaller on Windows


## License
MIT
