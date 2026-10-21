import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'ahk_launcher.py'
spec = importlib.util.spec_from_file_location('launcher', SOURCE)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def test_source_and_bundled_resource_paths(self):
        with patch.object(sys, 'frozen', False, create=True):
            self.assertEqual(launcher.get_script_path(), SOURCE.with_name('windowSwitcher.ahk'))
        with patch.object(sys, 'frozen', True, create=True), patch.object(sys, '_MEIPASS', 'bundle', create=True):
            self.assertEqual(launcher.get_script_path(), Path('bundle/src/windowSwitcher.ahk'))

    def test_detect_v2_without_accepting_v1(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(launcher.os.environ, {'ProgramFiles': temp}, clear=True):
            root = Path(temp) / 'AutoHotkey'
            root.mkdir()
            (root / 'AutoHotkey.exe').touch()
            with self.assertRaises(FileNotFoundError):
                launcher.find_autohotkey()
            (root / 'v2').mkdir()
            expected = root / 'v2' / 'AutoHotkey64.exe'
            expected.touch()
            self.assertEqual(launcher.find_autohotkey(), expected)

    def test_custom_interpreter(self):
        with tempfile.TemporaryDirectory() as temp:
            executable = Path(temp) / 'custom.exe'
            executable.touch()
            with patch.dict(launcher.os.environ, {'AUTOHOTKEY_EXE': str(executable)}):
                self.assertEqual(launcher.find_autohotkey(), executable)
                executable.unlink()
                with self.assertRaises(FileNotFoundError):
                    launcher.find_autohotkey()

    def test_startup_with_launcher_running_and_stopped(self):
        for running in (False, True):
            with self.subTest(running=running), patch.object(launcher, 'find_autohotkey', return_value=Path('v2.exe')), patch.object(launcher, 'is_process_running', return_value=running), patch.object(launcher.subprocess, 'run', return_value=Mock(returncode=0)), patch.object(launcher.subprocess, 'Popen') as popen:
                popen.return_value.wait.return_value = 0
                self.assertEqual(launcher.main(), 0)
                self.assertEqual(popen.call_count, 1 if running else 2)
                self.assertEqual(len(popen.call_args_list[0].args[0]), 2)
                popen.return_value.wait.assert_called_once()

    def test_validation_failure_starts_no_applications(self):
        with patch.object(launcher, 'find_autohotkey', return_value=Path('v2.exe')), patch.object(launcher.subprocess, 'run', return_value=Mock(returncode=2, stdout='invalid script')), patch.object(launcher.subprocess, 'Popen') as popen, patch('sys.stderr', new_callable=io.StringIO) as stderr:
            self.assertEqual(launcher.main(), 1)
            popen.assert_not_called()
            self.assertIn('invalid script', stderr.getvalue())

    def test_missing_interpreter_is_reported(self):
        with patch.object(launcher, 'find_autohotkey', side_effect=FileNotFoundError('v2 missing')), patch.object(launcher.subprocess, 'Popen') as popen, patch('sys.stderr', new_callable=io.StringIO) as stderr:
            self.assertEqual(launcher.main(), 1)
            popen.assert_not_called()
            self.assertIn('v2 missing', stderr.getvalue())

    def test_missing_ankama_does_not_stop_shortcuts(self):
        ahk = Mock()
        ahk.wait.return_value = 0
        with patch.object(launcher, 'find_autohotkey', return_value=Path('v2.exe')), patch.object(launcher, 'is_process_running', return_value=False), patch.object(launcher.subprocess, 'run', return_value=Mock(returncode=0)), patch.object(launcher.subprocess, 'Popen', side_effect=[ahk, FileNotFoundError('missing')]), patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(launcher.main(), 0)
            ahk.wait.assert_called_once()

    def test_ignores_processes_without_a_name(self):
        processes = [Mock(info={'name': None}), Mock(info={'name': 'ANKAMA LAUNCHER.EXE'})]
        with patch.object(launcher.psutil, 'process_iter', return_value=processes):
            self.assertTrue(launcher.is_process_running('Ankama Launcher.exe'))


if __name__ == '__main__':
    unittest.main()
