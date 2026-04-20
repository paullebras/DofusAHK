# DofusAHK
Python and AutoHotkey scripts for Dofus

## Windows Script

### Description
The Windows script uses Python and AutoHotkey to manage Dofus windows.

### Usage
1. **Install Requirements**:
   ```
   python -m pip freeze > requirements.txt
   python -m pip install > requirements.txt
   ```
2. **Build the Executable**:
   ```
   pyinstaller --clean --onefile --name Dofus --add-data src/windowSwitcher.ahk:src --icon .\src\assets\logo.png src/ahk_launcher.py
   ```

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
