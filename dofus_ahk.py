import subprocess
import psutil
import time

autohotkey_executable = r'C:\Program Files\AutoHotkey\AutoHotkey.exe'
ahk_script_path = r'./sanguor.ahk'
version_file_path = r"C:\Users\Paul Le Bras\AppData\Local\Ankama\Dofus\VERSION"

def get_dofus_version():
    try:
        with open(version_file_path, 'r') as file:
            version = file.read()
            print(version)
            return version.strip()  # Strip to remove leading/trailing whitespaces
    except FileNotFoundError:
        print(f"The file '{version_file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def run_ahk_script(argument_value):
    try:
        subprocess.run([autohotkey_executable, ahk_script_path, f'--arg={argument_value}'], check=True)
        print("AutoHotKey script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing AutoHotKey script: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return

def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False

def main():
    process_name = "Ankama Launcher.exe"
    launcher_path = r"C:\Program Files\Ankama\Ankama Launcher\Ankama Launcher.exe"

    if is_process_running(process_name):
        print(f"{process_name} is already running. Exiting the script.")
        return None

    print(f"{process_name} is not running. Starting the process.")
    subprocess.Popen([launcher_path])
    # Add a delay if needed to allow the process to start
    time.sleep(5)
    # Check again if the process is running
    if is_process_running(process_name):
        print(f"{process_name} started successfully.")
        # Get the Dofus version
        dofus_version = get_dofus_version()
        if dofus_version is not None:
            # Pass the version as an argument to the AHK script
            run_ahk_script(dofus_version)
        else:
            print("Failed to get Dofus version.")
    else:
        print(f"Failed to start {process_name}.")

if __name__ == "__main__":
    main()
