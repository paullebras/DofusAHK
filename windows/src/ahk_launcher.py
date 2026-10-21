import os
from pathlib import Path
import subprocess
import sys

import psutil


def get_script_path():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'src' / 'windowSwitcher.ahk'
    return Path(__file__).resolve().with_name('windowSwitcher.ahk')


def find_autohotkey():
    override = os.environ.get('AUTOHOTKEY_EXE')
    if override:
        executable = Path(override)
        if not executable.is_file():
            raise FileNotFoundError(f'AUTOHOTKEY_EXE does not exist: {executable}')
        return executable

    roots = [Path(os.environ[key]) / 'AutoHotkey' for key in
             ('ProgramFiles', 'ProgramFiles(x86)') if os.environ.get(key)]
    if os.environ.get('LOCALAPPDATA'):
        roots.append(Path(os.environ['LOCALAPPDATA']) / 'Programs' / 'AutoHotkey')
    for root in roots:
        for name in ('AutoHotkey64.exe', 'AutoHotkey32.exe'):
            executable = root / 'v2' / name
            if executable.is_file():
                return executable
    raise FileNotFoundError(
        'AutoHotkey v2 was not found. Install v2 or set AUTOHOTKEY_EXE '
        'to the full path of its AutoHotkey64.exe / AutoHotkey32.exe.'
    )


def is_process_running(process_name):
    for process in psutil.process_iter(['name']):
        try:
            if (process.info['name'] or '').casefold() == process_name.casefold():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def main():
    try:
        script = get_script_path()
        if not script.is_file():
            raise FileNotFoundError(f'AutoHotkey script does not exist: {script}')
        executable = find_autohotkey()
        validation = subprocess.run(
            [str(executable), '/ErrorStdOut', '/validate', str(script)],
            capture_output=True, text=True, errors='replace', timeout=15,
        )
        if validation.returncode:
            raise RuntimeError(
                'AutoHotkey v2 script validation failed:\n'
                + (validation.stdout or validation.stderr or 'Unknown error')
            )
        ahk = subprocess.Popen([str(executable), str(script)], cwd=script.parent)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'Cannot start Dofus shortcuts: {error}', file=sys.stderr)
        return 1

    if not is_process_running('Ankama Launcher.exe'):
        launcher = (Path(os.environ.get('ProgramFiles', r'C:\Program Files'))
                    / 'Ankama' / 'Ankama Launcher' / 'Ankama Launcher.exe')
        try:
            subprocess.Popen([str(launcher)])
        except OSError as error:
            print(f'Cannot start Ankama Launcher: {error}. '
                  'Shortcuts remain available; open the launcher manually.', file=sys.stderr)

    # Keep PyInstaller's extracted script available while AutoHotkey uses it.
    try:
        return ahk.wait()
    except KeyboardInterrupt:
        ahk.terminate()
        ahk.wait()
        return 0


if __name__ == '__main__':
    sys.exit(main())
