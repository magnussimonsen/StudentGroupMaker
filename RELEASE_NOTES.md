# Release Notes

## 0.4.0 — November 2025

Highlights for this release:

- UI/UX
	- Output header is cleaner and aligned (monospace + tab stops)
	- “Remove selected student(s)” with confirmation dialog
	- Student list is sorted by first name on save
	- Heatmap window is resizable/movable (non‑modal)

- Heatmap
	- Integer‑only colorbar ticks (no fractional labels)
	- Improved layout (no clipped axis labels when saving PNG)

- Theming
	- Unified dark/light variables; added hover/pressed states and splitter styling

- Randomness
	- Seed “0” now means “Random”; explained in UI and reflected in output

- Packaging
	- Windows EXE icon + runtime window icon
	- AppImage uses a single icon source (`src/icons/icon.png`); build scripts simplified

Distribution: Linux AppImage and Windows EXE are both supported in this release.
