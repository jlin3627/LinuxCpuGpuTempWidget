# CPU Temperature Monitor (Linux)

A lightweight, floating desktop widget for monitoring CPU temperature.

## Features
- **Floating Window:** Undecorated and compact.
- **Always on Top:** Stays visible over other windows.
- **Draggable:** Click and drag anywhere to move.
- **Color-coded:** Changes color based on temperature (Green < 55°C, Amber < 75°C, Red >= 75°C).
- **Controls:** Right-click to exit.

## Quick Start
Run the following command to start the monitor:
```bash
./run.sh
```

## Requirements
- Python 3
- `psutil` (automatically handled by the virtual environment)
- `Tkinter` (usually pre-installed on most Linux distributions)
