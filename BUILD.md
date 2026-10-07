# Building GroupMaker

GroupMaker is packaged with [PyInstaller](https://pyinstaller.org) using `GroupMaker.spec`.
PyInstaller builds for the platform it runs on, so build the Windows `.exe` on Windows
and the Linux executable/AppImage on Linux.

## 1. Set up the virtual environment (once)

Windows:
```powershell
python create-python-venv-win.py
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

Linux:
```bash
python3 create-python-venv-linux.py
.venv/bin/python -m pip install pyinstaller
```

## 2. Build

### Windows (`dist\GroupMaker.exe`)

From the project root in PowerShell:
```powershell
.\.venv\Scripts\pyinstaller.exe --noconfirm .\GroupMaker.spec
```

The result is a single file, `dist\GroupMaker.exe` (~75 MB), that runs without Python installed.

### Linux (`dist/GroupMaker`)

```bash
source .venv/bin/activate
./build-wrapper.sh
```

### Linux AppImage (`GroupMaker-x86_64.AppImage`)

Build `dist/GroupMaker` first (above), then:
```bash
chmod +x app-image-scripts/appimagetool-x86_64.AppImage
chmod +x app-image-scripts/build-appimage.sh
./app-image-scripts/build-appimage.sh
```

See [app-image-scripts/README.md](app-image-scripts/README.md) for details.

## Troubleshooting

**`PermissionError: [WinError 5]` / "Access denied" on `dist\GroupMaker.exe`**
The old exe is still running. Close all GroupMaker windows (or end `GroupMaker.exe` in
Task Manager) and build again.

**`.sh` scripts "not recognized" in PowerShell**
The `.sh` scripts are for Linux only. On Windows, use the PyInstaller command above.

**`ModuleNotFoundError` when building or running**
Install the dependencies into the virtual environment:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Missing `libxcb-*.so` warnings on Linux**
Usually harmless. To silence them, install:
```bash
sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0
```

**Clean rebuild**
Delete the `build/` and `dist/` folders and build again. Do not delete `GroupMaker.spec`;
it is part of the repository.
