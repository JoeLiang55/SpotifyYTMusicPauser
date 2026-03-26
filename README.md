# Music Hotkey Controller (Windows)

Background utility that lets you control media playback globally (Spotify + YouTube Music web sessions + other Windows media sessions) with configurable global hotkeys.

Default hotkeys: `F6` (play/pause), `F7` (next track)

## Features

- Global hotkey works while another window is focused (including games)
- Toggles all active media sessions together (pause when anything is playing, otherwise play)
- Skips to the next track globally from supported media sessions
- System tray app with a simple hotkey editor
- Config persisted in `config.json`

## Requirements

- Windows 10 or newer
- Python 3.10+

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

When running, use the tray icon to:

- Toggle media immediately
- Skip to next track immediately
- Change hotkeys (play/pause and next track)
- Exit the app

## Build EXE

```powershell
pyinstaller --noconfirm --onefile --windowed --name MusicHotkeyController main.py
```

The executable is created in `dist\MusicHotkeyController.exe`.

## Notes

- Global hotkey libraries can require elevated privileges in some environments.
- This app controls Windows media sessions exposed through SMTC, so behavior depends on whether the target app/session is registered with Windows media controls.
