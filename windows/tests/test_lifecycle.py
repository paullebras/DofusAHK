from contextlib import nullcontext
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_launcher import launcher


class LifecycleTests(unittest.TestCase):
    def test_distinguishes_game_from_our_same_named_launcher(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            helper = Mock(info={'name': 'Dofus.exe'})
            helper.exe.return_value = str(root / 'helper' / 'Dofus.exe')
            game = Mock(info={'name': 'Dofus.exe'})
            game.exe.return_value = str(root / 'game' / 'Dofus.exe')
            (root / 'game' / 'Dofus_Data').mkdir(parents=True)
            with patch.object(launcher.psutil, 'process_iter', return_value=[helper]):
                self.assertFalse(launcher.is_dofus_running())
            with patch.object(launcher.psutil, 'process_iter', return_value=[helper, game]):
                self.assertTrue(launcher.is_dofus_running())

    def test_retro_and_unreadable_client_keep_session_alive(self):
        retro = Mock(info={'name': 'Dofus Retro.exe'})
        unreadable = Mock(info={'name': 'Dofus.exe'})
        unreadable.exe.side_effect = launcher.psutil.AccessDenied(123)
        for process in (retro, unreadable):
            with self.subTest(process=process), patch.object(launcher.psutil, 'process_iter', return_value=[process]):
                self.assertTrue(launcher.is_dofus_running())

    def simulate(self, clients, launcher_running, times, relaunches=None):
        ahk = Mock()
        ahk.wait.side_effect = [subprocess.TimeoutExpired('ahk', 2) for _ in clients] + [0]
        with patch.object(launcher, 'is_dofus_running', side_effect=clients), patch.object(launcher, 'is_process_running', return_value=launcher_running), patch.object(launcher.time, 'monotonic', side_effect=times), patch.object(launcher, 'stop_shortcuts') as stop:
            relaunch = Mock(side_effect=relaunches) if relaunches else lambda: False
            self.assertEqual(launcher.watch_session(ahk, relaunch), 0)
        return stop

    def test_stops_after_last_client_even_if_launcher_stays_open(self):
        stop = self.simulate([True, False, False, False], True, [0, 8, 16])
        stop.assert_called_once()

    def test_waits_for_first_client_while_launcher_is_open(self):
        self.simulate([False, False, False], True, []).assert_not_called()

    def test_stops_if_launcher_closed_without_ever_starting_game(self):
        self.simulate([False, False, False], False, [0, 8, 16]).assert_called_once()

    def test_reopened_client_resets_grace_period(self):
        self.simulate([True, False, False, True, False, False], True, [0, 8, 25, 33]).assert_not_called()

    def test_second_launch_rearms_waiting_during_shutdown_grace_period(self):
        self.simulate([True, False, False, False], True, [0], [False, False, True, False]).assert_not_called()

    def test_manual_ahk_exit_returns_without_scanning_processes(self):
        ahk = Mock()
        ahk.wait.return_value = 0
        with patch.object(launcher, 'is_dofus_running') as scan:
            self.assertEqual(launcher.watch_session(ahk), 0)
            scan.assert_not_called()

    def test_cleanup_targets_only_our_ahk_process(self):
        ahk = Mock()
        ahk.poll.return_value = None
        launcher.stop_shortcuts(ahk)
        ahk.terminate.assert_called_once()
        ahk.wait.assert_called_once_with(timeout=5)

    def test_cleanup_kills_our_child_if_termination_times_out(self):
        ahk = Mock()
        ahk.poll.return_value = None
        ahk.wait.side_effect = [subprocess.TimeoutExpired('ahk', 5), 0]
        launcher.stop_shortcuts(ahk)
        ahk.kill.assert_called_once()

    def test_repeated_launch_reuses_session_instead_of_starting_ahk(self):
        with patch.object(launcher, 'single_instance', return_value=nullcontext((False, lambda: False))), patch.object(launcher, 'open_ankama_launcher') as reopen, patch.object(launcher, 'run_session') as start:
            self.assertEqual(launcher.main(), 0)
            start.assert_not_called()
            reopen.assert_called_once()

    def test_named_guard_closes_handles_and_consumes_relaunch_event(self):
        kernel = Mock()
        kernel.CreateMutexW.return_value = 0x123456789
        kernel.CreateEventW.return_value = 0x987654321
        kernel.WaitForSingleObject.side_effect = [0, 258]
        with patch.object(launcher.ctypes, 'WinDLL', return_value=kernel), patch.object(launcher.ctypes, 'get_last_error', return_value=0):
            with launcher.single_instance() as (first, relaunched):
                self.assertTrue(first)
                self.assertTrue(relaunched())
                self.assertFalse(relaunched())
        kernel.SetEvent.assert_not_called()
        self.assertEqual(kernel.CloseHandle.call_count, 2)
        self.assertIs(kernel.CreateMutexW.restype, launcher.wintypes.HANDLE)

    def test_second_instance_signals_existing_session(self):
        kernel = Mock()
        kernel.CreateMutexW.return_value = 123
        kernel.CreateEventW.return_value = 456
        with patch.object(launcher.ctypes, 'WinDLL', return_value=kernel), patch.object(launcher.ctypes, 'get_last_error', return_value=183):
            with launcher.single_instance() as (first, _):
                self.assertFalse(first)
        kernel.SetEvent.assert_called_once_with(456)
        self.assertEqual(kernel.CloseHandle.call_count, 2)


if __name__ == '__main__':
    unittest.main()
