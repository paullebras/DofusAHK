# DofusAHK
Python and AutoHotkey scripts for Dofus

## Windows Script

### Description
The Windows script uses Python and **AutoHotkey v2** to manage Dofus windows.
Install AutoHotkey v2 from https://www.autohotkey.com/ (v1 alone is not supported).
The launcher detects the v2 interpreter in the standard system or per-user installation.
For a portable/custom installation, set `$env:AUTOHOTKEY_EXE` to the full path of its v2 interpreter.

F1: Baabu; F2: Sanguor; F3: Takamori; F4: Ninomae-inanis.
Edit these names in `windows/src/windowSwitcher.ahk` to match your characters.
F12 toggles window switching. Missing windows are ignored. Titles are matched by substring,
without reading Dofus's `VERSION` file. The shortcuts start even when Ankama Launcher is already running.
The switcher disables AHK's default 100 ms post-activation delay (`SetWinDelay(-1)`)
and uses `#WinActivateForce` to reduce taskbar flashing during rapid switches.
It caches window handles (rechecking their titles to avoid stale handles) and requests foreground focus
with Windows `SetForegroundWindow`; minimized windows or refused requests use AHK's `WinActivate` fallback.
It does not intercept or replay mouse clicks: Windows still routes physical clicks
according to the window active when each click is processed.

### Usage
Run the following commands from the `windows/` directory.

1. **Install dependencies** (creates isolated `.venv` automatically):
   ```
   uv sync --dev
   ```
2. **Run from source** (no build needed):
   ```powershell
   uv run python src/ahk_launcher.py
   ```
   The script path is resolved independently of the current working directory.
   A missing interpreter or an invalid AHK script is reported before applications are launched.

3. **Build the Executable**:
   ```
   uv run pyinstaller --clean --onefile --windowed --name Dofus --add-data src/windowSwitcher.ahk:src --icon .\src\assets\logo.png src/ahk_launcher.py
   ```
   The output `Dofus.exe` will be in `windows/dist/`. AutoHotkey v2 must also be installed
   on the machine running the executable; it is not bundled. The executable runs in the background
   without a terminal window and keeps the extracted AHK script available. Exit AutoHotkey from its
   tray icon to stop the shortcuts and their background launcher. Startup failures appear in a dialog;
   application output is not forwarded to a console. Running the Python source keeps terminal errors
   available for debugging. If Ankama Launcher is not installed at the default
   location, open it manually; the shortcuts remain available.

4. **Verify changes**:
   ```powershell
   uv run python -m unittest discover -s tests -v
   $validation = Start-Process -FilePath "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe" -ArgumentList '/ErrorStdOut', '/validate', "`"$((Resolve-Path .\src\windowSwitcher.ahk).Path)`"" -Wait -PassThru
   $validation.ExitCode # 0 means successful validation
   ```
   Tests simulate application launches; AHK validation loads the script without registering its shortcuts.

   For a focus timing check, close the switcher, then run `powershell -File .\tests\benchmark-switching.ps1`.
   This opens four temporary windows, compares native activation with `WinActivate`, and checks missing/closed
   windows, disabled switching and restore. It reports request and observed focus timings separately.
   It sends no mouse clicks. These synthetic windows cannot establish Dofus render/input latency;
   verify rapid F1-click-F2-click-F3-click-F4-click sequences in game as well.

### Background lifecycle

Only one shortcut session runs per Windows session, including repeated launches from different
PyInstaller extraction folders. Clicking the executable again reuses the current shortcut session. Each click invokes Ankama Launcher;
its own single-instance mechanism opens/restores the existing main window, including from the system tray. A relaunch also resets the session's shutdown grace period.

The background helper checks client processes every 2 seconds, outside the AHK hotkey handlers.
Before the first client, it waits while Ankama Launcher is running. After a client has been detected,
closing the last client stops AutoHotkey and the helper after approximately 15-19 seconds, even if
Ankama Launcher stays open. Reopening a client during this grace period cancels shutdown.
If no client was ever started, quitting Ankama Launcher also starts the grace period.
Use the AutoHotkey tray icon to exit immediately.

Detection covers this installation's Dofus Unity/beta (`Dofus.exe` with a sibling `Dofus_Data` directory)
and Dofus Retro (`Dofus Retro.exe`). The helper itself is also named `Dofus.exe` and is excluded.
If a matching client's executable cannot be read, the helper conservatively stays running.

The one-file executable normally has two `Dofus.exe` processes (bootstrap and Python worker), plus
its AutoHotkey child. These are one logical shortcut session, not duplicate sessions, and exit together.

## Linux Script

### Description
The `team_fitz_v2.sh` script is used to activate specific Dofus windows based on key presses. It can optionally reorder the window IDs based on an argument provided.

### Usage
1. **Default Behavior**: To use the script with the default behavior, run:
   ```
   xbindkeys -f ~/Documents/perso/code/DofusAHK/linux/team_fitz.keys
   ```
2. **Custom Order**: To use the script with a custom order, run:
   ```
   xbindkeys -f ~/Documents/perso/code/DofusAHK/linux/team_fitz.keys 4123
   ```
   - The argument `4123` specifies the order of the window IDs. For example, `4123` means:
     - The 4th element is in position 0
     - The 1st element is in position 1
     - The 2nd element is in position 2
     - The 3rd element is in position 3
     - The 5th element is not specified and stays the same.

3. **Kill the xbindkey process**
```
killall xbindkeys
```

### Script Details
- **Reading Window IDs**: The script reads the window IDs into the `window_ids` array.
- **Checking for Optional Argument**: It checks if a second argument (`$2`) is provided.
- **Reordering Window IDs**: If an argument is provided, it creates a new array `reordered_window_ids` and populates it based on the order specified in the argument.
- **Appending Remaining IDs**: Any window IDs not specified in the argument are appended to the `reordered_window_ids` array.
- **Using Reordered IDs**: The `window_ids` array is updated to the reordered array.
- **Activating Windows**: The script activates the windows based on the key pressed, using the potentially reordered `window_ids` array.
