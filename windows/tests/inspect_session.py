"""Read-only snapshot of the running shortcut session; never starts a client."""

import ctypes
from ctypes import wintypes
import importlib.util
from pathlib import Path
import time

import psutil


def main():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('launcher', root / 'src' / 'ahk_launcher.py')
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    helper_path = (root / 'dist' / 'Dofus.exe').resolve()
    helpers = []
    shortcuts = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            name = (process.info['name'] or '').casefold()
            if name == 'dofus.exe' and Path(process.exe()).resolve() == helper_path:
                helpers.append(process)
            elif name in ('autohotkey64.exe', 'autohotkey32.exe', 'autohotkey.exe'):
                if any(Path(arg).name.casefold() == 'windowswitcher.ahk' for arg in process.cmdline()[1:]):
                    shortcuts.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenMutexW.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR)
    kernel.OpenMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
    handle = kernel.OpenMutexW(0x00100000, False, r'Local\DofusAHK.WindowSwitcher')
    guard = 'present' if handle else f'unavailable (Windows error {ctypes.get_last_error()})'
    if handle:
        kernel.CloseHandle(handle)

    ankama = launcher.is_process_running('Ankama Launcher.exe')
    clients = launcher.is_dofus_running()
    print('Ankama running:', ankama)
    print('Dofus client running:', clients)
    print('Helper processes:', len(helpers), '(normally 2 for one packaged session)')
    print('AHK switchers:', len(shortcuts))
    print('Single-instance guard:', guard)
    if ankama and not clients and helpers and shortcuts:
        print('Expected phase BEFORE the first client: waiting for game launch; no shutdown timeout.')

    watched = helpers + shortcuts
    before = {}
    for process in watched:
        try:
            cpu = process.cpu_times()
            before[process.pid] = cpu.user + cpu.system
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    started = time.monotonic()
    time.sleep(3)
    elapsed = time.monotonic() - started
    print('Observed CPU over 3 seconds (100% = one CPU core):')
    for process in watched:
        try:
            cpu = process.cpu_times()
            delta = (cpu.user + cpu.system - before[process.pid]) / elapsed * 100
            memory = process.memory_info().rss / (1024 * 1024)
            print(f'  PID {process.pid}: {process.name()}, CPU {delta:.2f}%, working set {memory:.1f} MiB')
        except (KeyError, psutil.NoSuchProcess, psutil.AccessDenied):
            print(f'  PID {process.pid}: exited or inaccessible during observation')
    print('No application was launched, closed or signaled by this check.')


if __name__ == '__main__':
    main()
