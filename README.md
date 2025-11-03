# GroupMaker

**GroupMaker** is a simple desktop app for teachers to create random student groups with minimal pair repetition.  
Built with **Python** and **PySide6**, and easily packaged as a standalone Windows `.exe` (no Python required).

---

## ✨ Features

- Add and manage multiple **classes**
- Save student lists automatically as JSON files
- Use **checkboxes** to mark attendance (only present students are grouped)
- Adjustable **number of groups**, **rounds**, **restarts**, and **random seed**
- View detailed **grouping results** and a **quality index**
- **Export plans** as `.txt` files
- Adjustable **font size** for better visibility

---

## 🚀 Run from Source

Requirements: Python 3.9+

```bash
pip install PySide6
python group_maker.py
```

---

## 📦 Build a Windows `.exe`

To create a standalone app that runs without Python:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name GroupMaker --collect-all PySide6 group_maker.py
```

This creates `dist/GroupMaker.exe`.

---

## 🖱️ How to Use

1. Create or select a class.
2. Add students and mark attendance with checkboxes.
3. Choose number of groups and rounds.
4. Click **Generate plan** to create random groups.
5. Optionally export the plan to a text file.

---

## 📂 Data Storage

Student lists are stored automatically in your home folder:
```
~/.GroupMaker/classes/
```

---

## 🧠 Algorithm Summary

- Students are grouped using a **greedy randomized heuristic**.
- The algorithm minimizes repeated pairs between rounds.
- Higher **restarts** improve pairing diversity but take longer.

---

## 🛡️ License

MIT License

```
MIT License

Copyright (c) 2025 <Your Name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙌 Acknowledgements

- **PySide6** (Qt for Python) for the GUI
- **PyInstaller** for packaging
