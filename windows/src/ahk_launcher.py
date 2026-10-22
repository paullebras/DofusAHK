from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import time

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


def report_error(message):
    if sys.stderr is not None:
        print(message, file=sys.stderr)
    else:
        # PyInstaller --windowed has no stderr; keep startup failures visible.
        ctypes.windll.user32.MessageBoxW(0, message, 'DofusAHK', 0x10)


@contextmanager
def single_instance():
    # These names are stable across PyInstaller's temporary extraction folders.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.CreateEventW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR)
    kernel.CreateEventW.restype = wintypes.HANDLE
    kernel.SetEvent.argtypes = (wintypes.HANDLE,)
    kernel.SetEvent.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel.CloseHandle.restype = wintypes.BOOL
    ctypes.set_last_error(0)
    handle = kernel.CreateMutexW(None, False, r'Local\DofusAHK.WindowSwitcher')
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    already_running = ctypes.get_last_error() == 183  # ERROR_ALREADY_EXISTS
    event = None
    try:
        event = kernel.CreateEventW(None, False, False, r'Local\DofusAHK.RestartSession')
        if not event:
            raise ctypes.WinError(ctypes.get_last_error())
        if already_running and not kernel.SetEvent(event):
            raise ctypes.WinError(ctypes.get_last_error())

        def relaunch_requested():
            result = kernel.WaitForSingleObject(event, 0)
            if result == 0xFFFFFFFF:
                raise ctypes.WinError(ctypes.get_last_error())
            return result == 0  # Auto-reset event: consume each relaunch request once.

        yield not already_running, relaunch_requested
    finally:
        if event:
            kernel.CloseHandle(event)
        kernel.CloseHandle(handle)


def is_dofus_running():
    for process in psutil.process_iter(['name']):
        try:
            name = (process.info['name'] or '').casefold()
            if name == 'dofus retro.exe':
                return True
            if name == 'dofus.exe':
                # Our packaged launcher is also called Dofus.exe. The Unity
                # client's data directory distinguishes it from helper copies.
                try:
                    executable = process.exe()
                except psutil.AccessDenied:
                    return True  # Do not stop shortcuts when a client is unreadable.
                if not executable or (Path(executable).parent / 'Dofus_Data').is_dir():
                    return True
        except psutil.NoSuchProcess:
            continue
    return False


def open_ankama_launcher():
    # Ankama handles a second invocation by restoring/focusing its main window.
    # A running background process alone does not mean its window is open.
    launcher = (Path(os.environ.get('ProgramFiles', r'C:\Program Files'))
                / 'Ankama' / 'Ankama Launcher' / 'Ankama Launcher.exe')
    try:
        subprocess.Popen(
            [str(launcher)], cwd=launcher.parent, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except OSError as error:
        report_error(f'Cannot start Ankama Launcher: {error}. '
                     'Shortcuts remain available; open the launcher manually.')


def stop_shortcuts(ahk):
    if ahk.poll() is None:
        ahk.terminate()
        try:
            ahk.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ahk.kill()
            ahk.wait(timeout=5)


def watch_session(ahk, relaunch_requested=lambda: False, grace_seconds=15):
    seen_client = False
    idle_since = None
    while True:
        # Sleep without consuming CPU and return immediately if AHK is quit manually.
        try:
            return ahk.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
        if relaunch_requested():
            seen_client = False
            idle_since = None
        if is_dofus_running():
            seen_client = True
            idle_since = None
        elif seen_client or not is_process_running('Ankama Launcher.exe'):
            now = time.monotonic()
            if idle_since is None:
                idle_since = now
            elif now - idle_since >= grace_seconds:
                stop_shortcuts(ahk)
                return 0
        else:
            # Before the first client, allow time to log in via Ankama Launcher.
            idle_since = None


def run_session(relaunch_requested=lambda: False):
    try:
        script = get_script_path()
        if not script.is_file():
            raise FileNotFoundError(f'AutoHotkey script does not exist: {script}')
        executable = find_autohotkey()
        validation = subprocess.run(
            [str(executable), '/ErrorStdOut', '/validate', str(script)],
            capture_output=True, text=True, errors='replace', timeout=15,
            stdin=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if validation.returncode:
            raise RuntimeError(
                'AutoHotkey v2 script validation failed:\n'
                + (validation.stdout or validation.stderr or 'Unknown error')
            )
        ahk = subprocess.Popen(
            [str(executable), str(script)], cwd=script.parent,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        report_error(f'Cannot start Dofus shortcuts: {error}')
        return 1

    # Keep PyInstaller's extracted script alive only for the current game session.
    try:
        open_ankama_launcher()
        return watch_session(ahk, relaunch_requested)
    except KeyboardInterrupt:
        return 0
    finally:
        stop_shortcuts(ahk)


def main():
    try:
        with single_instance() as (first_instance, relaunch_requested):
            if not first_instance:
                # Repeated clicks may reopen Ankama, but never start a second AHK.
                open_ankama_launcher()
                return 0
            return run_session(relaunch_requested)
    except OSError as error:
        report_error(f'Cannot start Dofus shortcuts: {error}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
