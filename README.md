# Macro Recorder

A lightweight, high-precision Python-based tool designed to record and playback mouse and keyboard actions.

## Features
- **High-Precision Playback:** Utilizes Windows API (`SetProcessDpiAwareness`) for accurate cursor movement.
- **Configurable Modes:** Choose between "Mouse + Keyboard" or "Mouse Only" recording.
- **Seamless Operation:** Global Hotkeys for controlling the recording and playback processes.
- **Always-on-Top:** The UI remains visible while recording to monitor status easily.

## Hotkeys
| Action | Key |
| :--- | :--- |
| **Start Recording** | `F8` |
| **Stop Recording/Playback** | `F9` |
| **Start Playback** | `F10` |

## Requirements
- Windows OS
- Python 3.x (if running from source)
- Dependencies: `tkinter`, `pynput`, `threading`

## Usage
### From Source
1. Clone the repository or download the source code.
2. Install dependencies: `pip install pynput`
3. Run the script: `python macro_record_keys-clicker.py`

### Compiled Version (Recommended)
1. Navigate to the **[Releases](https://github.com/nathakorn-io/macro_record/releases)** section.
2. Download the latest `.zip` release package.
3. Extract the contents.
4. Run `macro_record_keys-clicker.exe` inside the folder.
   > **Note:** Run the application as **Administrator** for better compatibility with background processes.
