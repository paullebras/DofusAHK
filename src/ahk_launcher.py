import subprocess
import psutil

autohotkey_executable = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'
ahk_script_path = r'./windowSwitcher.ahk'
version_file_path = r"C:\Users\Paul Le Bras\AppData\Local\Ankama\Dofus\VERSION"
ankama_launcher_exe = "Ankama Launcher.exe"
ankama_launcher_path = rf"C:\Program Files\Ankama\Ankama Launcher\{ankama_launcher_exe}"


def get_dofus_version():
    try:
        with open(version_file_path, 'r') as file:
            version = file.read()
            return version.strip()
    except FileNotFoundError:
        print(f"The file '{version_file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def run_executable(executable, path='', argument_value=''):
    try:
        subprocess.Popen([executable, path, argument_value], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.DETACHED_PROCESS)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False


def main():
    if is_process_running(ankama_launcher_exe):
        print(f"{ankama_launcher_exe} is already running. Exiting the script.")
        return None
    dofus_version = get_dofus_version()
    if dofus_version is None:
        print("Failed to get Dofus version.")
        return None
    run_executable(autohotkey_executable, ahk_script_path, dofus_version)
    run_executable(ankama_launcher_path)


if __name__ == "__main__":
    main()
