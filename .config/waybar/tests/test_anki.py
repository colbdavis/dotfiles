"""Mock-only regression tests: no Anki, wofi, network or collection access."""
import importlib.util
import io
import json
import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import dock_anki as anki

spec = importlib.util.spec_from_file_location('dock_apps', ROOT / 'scripts/dock-apps.py')
apps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apps)


class AnkiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.enterContext(patch.dict(os.environ, {'XDG_STATE_HOME': self.temp.name}))
        self.running = self.enterContext(patch.object(anki, 'instances', return_value=[]))
        self.ready = self.enterContext(patch.object(anki, 'api_ready', return_value=False))
        self.notify = self.enterContext(patch.object(anki, 'notify'))
        self.popen = self.enterContext(patch.object(anki.subprocess, 'Popen'))
        self.popen.return_value.poll.return_value = None
        self.run = self.enterContext(patch.object(anki.subprocess, 'run'))
        self.enterContext(patch.object(anki.time, 'sleep'))
        self.focus = Mock(return_value=True)

    def test_menu_always_has_both_options(self):
        for running in ([], [(1, 'GUI')], [(2, 'backend')]):
            self.running.return_value = running
            self.run.return_value = subprocess.CompletedProcess([], 0, 'Open GUI\n')
            with patch.object(anki, 'launch') as launch:
                anki.menu(self.focus)
                launch.assert_called_once_with('GUI', self.focus)
                self.assertEqual(self.run.call_args.kwargs['input'],
                                 anki.MENU + ('Stop GUI\n' if running == [(1, 'GUI')] else
                                              'Stop AnkiConnect backend\n' if running else ''))
                self.assertEqual(self.run.call_args.args[0], ['wofi', '--dmenu', '--prompt', 'Anki'])

    def test_stop_backend_menu_only_when_backend_running(self):
        self.run.return_value = subprocess.CompletedProcess([], 0, 'Stop AnkiConnect backend\n')
        for running in ([], [(1, 'GUI')], [(1, 'unknown')], [(1, 'backend')]):
            self.running.return_value = running
            with patch.object(anki, 'stop_backend') as stop:
                anki.menu(self.focus)
                self.assertEqual(stop.call_count, int(running == [(1, 'backend')]))

    def test_stop_backend_waits_for_exit(self):
        self.running.side_effect = [[(1, 'backend')], [(1, 'backend')], []]
        with patch.object(anki, 'request_close', return_value=True) as close:
            anki.stop_backend()
            close.assert_called_once()
        self.assertIn('backend stopped', self.notify.call_args.args[0])
        self.popen.assert_not_called()

    def test_stop_backend_handles_failure_timeout_and_changed_mode(self):
        self.running.return_value = [(1, 'backend')]
        with patch.object(anki, 'request_close', return_value=False):
            anki.stop_backend()
        self.assertIn('Could not stop', self.notify.call_args.args[0])
        with patch.object(anki, 'request_close', return_value=True):
            anki.stop_backend()
        self.assertIn('still closing', self.notify.call_args.args[0])
        self.running.return_value = [(1, 'GUI')]
        with patch.object(anki, 'request_close') as close:
            anki.stop_backend()
            close.assert_not_called()

    def test_stop_gui_selection(self):
        self.running.return_value = [(1, 'GUI')]
        self.run.return_value = subprocess.CompletedProcess([], 0, 'Stop GUI\n')
        with patch.object(anki, 'stop_gui') as stop:
            anki.menu(self.focus)
            stop.assert_called_once_with(self.focus)
        self.running.return_value = [(1, 'backend')]
        with patch.object(anki, 'stop_gui') as stop:
            anki.menu(self.focus)
            stop.assert_not_called()

    def test_stop_gui_uses_graceful_api_close(self):
        self.running.return_value = [(1, 'GUI')]
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"result":null,"error":null}'
        with patch.object(anki.urllib.request, 'build_opener') as build:
            build.return_value.open.return_value = response
            anki.stop_gui(self.focus)
            req = build.return_value.open.call_args.args[0]
            self.assertEqual(json.loads(req.data)['action'], 'guiExitAnki')
        self.popen.assert_not_called()

    def test_stop_gui_handles_failed_api_and_changed_mode(self):
        self.running.return_value = [(1, 'GUI')]
        with patch.object(anki.urllib.request, 'build_opener', side_effect=OSError):
            anki.stop_gui(self.focus)
        self.focus.assert_called_once_with('anki')
        self.assertIn('Could not close', self.notify.call_args.args[0])
        self.running.return_value = [(1, 'backend')]
        with patch.object(anki.urllib.request, 'build_opener') as build:
            anki.stop_gui(self.focus)
            build.assert_not_called()

    def test_backend_selection_and_cancel(self):
        with patch.object(anki, 'launch') as launch:
            self.run.return_value = subprocess.CompletedProcess([], 0, 'Start AnkiConnect backend\n')
            anki.menu(self.focus)
            launch.assert_called_once_with('backend', self.focus)
            launch.reset_mock()
            for code, text in ((1, ''), (0, ''), (0, '$(touch unsafe)')):
                self.run.return_value = subprocess.CompletedProcess([], code, text)
                anki.menu(self.focus)
            launch.assert_not_called()

    def test_status_either_mode_green(self):
        self.assertEqual(anki.status()['class'], 'inactive')
        for kind in ('GUI', 'backend', 'unknown'):
            self.running.return_value = [(1, kind)]
            self.assertEqual(anki.status()['class'], 'active')
            self.assertIn(kind, anki.status()['tooltip'])
        self.ready.assert_not_called()

    def test_gui_focus_not_second_launch(self):
        self.running.return_value = [(1, 'GUI')]
        anki.launch('GUI', self.focus)
        self.focus.assert_called_once_with('anki')
        self.popen.assert_not_called()

    def test_backend_switch_waits_before_gui_launch(self):
        self.running.side_effect = [[(1, 'backend')], [(1, 'backend')], []]
        self.ready.side_effect = [False, True]
        with patch.object(anki, 'request_close', return_value=True) as close:
            anki.launch('GUI', self.focus)
            close.assert_called_once()
        self.popen.assert_called_once()
        self.assertFalse(self.popen.call_args.kwargs['env'].get('QT_QPA_PLATFORM', '').startswith('offscreen'))

    def test_failed_or_blocked_backend_shutdown_blocks_launch(self):
        self.running.return_value = [(1, 'backend')]
        for success in (False, True):
            with patch.object(anki, 'request_close', return_value=success):
                anki.launch('GUI', self.focus)
        self.popen.assert_not_called()

    def test_unknown_instance_blocks_gui(self):
        self.running.return_value = [(1, 'unknown')]
        with patch.object(anki, 'request_close') as close:
            anki.launch('GUI', self.focus)
            close.assert_not_called()
        self.popen.assert_not_called()

    def test_backend_reuses_gui_even_if_api_unavailable(self):
        self.running.return_value = [(1, 'GUI')]
        anki.launch('backend', self.focus)
        self.assertIn('not responding', self.notify.call_args.args[0])
        self.popen.assert_not_called()
        self.ready.return_value = True
        anki.launch('backend', self.focus)
        self.assertIn('is responding', self.notify.call_args.args[0])

    def test_unidentified_api_blocks_launch(self):
        self.ready.return_value = True
        anki.launch('GUI', self.focus)
        self.popen.assert_not_called()
        self.assertIn('not identified', self.notify.call_args.args[0])

    def test_backend_launch_argv_environment_and_log(self):
        self.ready.side_effect = [False, True]
        anki.launch('backend', self.focus)
        args, kw = self.popen.call_args
        self.assertEqual(args, (['anki'],))
        self.assertEqual(kw['env']['QT_QPA_PLATFORM'], 'offscreen')
        self.assertTrue(kw['start_new_session'])
        self.assertNotIn('shell', kw)
        self.assertIn('starting Anki backend', (Path(self.temp.name) / 'waybar/anki.log').read_text())

    def test_gui_drops_inherited_offscreen(self):
        self.ready.side_effect = [False, True]
        with patch.dict(os.environ, {'QT_QPA_PLATFORM': 'offscreen'}):
            anki.launch('GUI', self.focus)
        self.assertNotIn('QT_QPA_PLATFORM', self.popen.call_args.kwargs['env'])

    def test_startup_failure_and_timeout_never_kill(self):
        self.popen.return_value.poll.return_value = 1
        anki.launch('backend', self.focus)
        self.assertIn('exited', self.notify.call_args.args[0])
        self.popen.return_value.poll.return_value = None
        anki.launch('backend', self.focus)
        self.assertIn('not responding', self.notify.call_args.args[0])
        self.popen.return_value.kill.assert_not_called()
        self.popen.return_value.terminate.assert_not_called()

    def test_competing_click_does_not_launch(self):
        with patch.object(anki.fcntl, 'flock', side_effect=BlockingIOError):
            anki.launch('backend', self.focus)
        self.popen.assert_not_called()
        self.assertIn('already starting', self.notify.call_args.args[0])

    def test_launcher_routes_anki_before_settings_or_focus(self):
        with patch.object(sys, 'argv', ['dock-apps.py', 'launch', 'anki']), \
                patch.object(anki, 'menu') as menu, patch.object(apps, 'load_settings') as settings:
            apps.main()
            menu.assert_called_once_with(apps.focus)
            settings.assert_not_called()

    def test_native_process_detection(self):
        # Use the original scanner with a fake /proc tree.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = [
                (1, b'/usr/bin/python\0/usr/bin/anki\0', b'QT_QPA_PLATFORM=wayland;xcb\0'),
                (2, b'/usr/bin/anki\0', b'QT_QPA_PLATFORM=offscreen\0'),
                (3, b'python3\0-m\0aqt\0', b''),
                (4, b'python3\0/tmp/not-anki.py\0', b''),
                (5, b'anki\0--syncserver\0', b''),
                (6, b'vim\0/usr/bin/anki\0', b''),
            ]
            for pid, cmd, env in entries:
                entry = root / str(pid)
                entry.mkdir()
                (entry / 'cmdline').write_bytes(cmd)
                (entry / 'environ').write_bytes(env)
            self.assertEqual(sorted(ORIGINAL_INSTANCES(root)), [(1, 'GUI'), (2, 'backend'), (3, 'GUI')])
            with patch.object(anki.os, 'getuid', return_value=os.getuid() + 1):
                self.assertEqual(ORIGINAL_INSTANCES(root), [])

    def test_api_probe_validation_and_no_proxy(self):
        for payload, expected in (({'result': 6, 'error': None}, True),
                                  ({'result': None, 'error': 'key required'}, False),
                                  ({'result': True, 'error': None}, False), ([], False)):
            response = Mock()
            response.__enter__ = Mock(return_value=response)
            response.__exit__ = Mock(return_value=False)
            response.read.return_value = json.dumps(payload).encode()
            with patch.object(anki.urllib.request, 'build_opener') as build:
                build.return_value.open.return_value = response
                self.assertEqual(ORIGINAL_READY(), expected)
                req = build.return_value.open.call_args.args[0]
                self.assertEqual(req.full_url, 'http://127.0.0.1:8765/')
                self.assertEqual(json.loads(req.data)['action'], 'version')
        with patch.object(anki.urllib.request, 'build_opener', side_effect=OSError):
            self.assertFalse(ORIGINAL_READY())

    def test_image_adapter_uses_launcher_status(self):
        self.run.return_value = subprocess.CompletedProcess([], 0, json.dumps({
            'class': 'active', 'tooltip': 'Anki · GUI running'}))
        output = io.StringIO()
        with patch.object(sys, 'argv', ['dock-icons.py', 'anki']), patch.object(sys, 'stdout', output):
            runpy.run_path(str(ROOT / 'scripts/dock-icons.py'), run_name='__main__')
        self.assertEqual(self.run.call_args.args[0],
                         [str(ROOT / 'scripts/dock-apps.py'), 'status', 'anki'])
        self.assertEqual(output.getvalue().splitlines(),
                         [str(ROOT / 'icons/anki-active.svg'), 'Anki · GUI running'])

    def test_config_and_svg_contract(self):
        config = json.loads((ROOT / 'config.jsonc').read_text())
        self.assertEqual(config['modules-left'].count('image#anki'), 1)
        self.assertEqual(config['image#anki']['size'], 16)
        self.assertTrue(config['image#anki']['exec'].endswith('dock-icons.py anki'))
        self.assertTrue(config['image#anki']['on-click'].endswith('dock-apps.py launch anki'))
        for state, color in (('active', '#50fa7b'), ('inactive', '#c5bdd9')):
            svg = ET.parse(ROOT / 'icons' / f'anki-{state}.svg').getroot()
            self.assertEqual(svg.attrib['width'], '16')
            self.assertEqual(svg.attrib['height'], '16')
            self.assertIn(color, ET.tostring(svg).decode())
        active = (ROOT / 'icons/anki-active.svg').read_text()
        inactive = (ROOT / 'icons/anki-inactive.svg').read_text()
        self.assertEqual(active.replace('#50fa7b', '#c5bdd9'), inactive)


ORIGINAL_INSTANCES = anki.instances
ORIGINAL_READY = anki.api_ready
if __name__ == '__main__':
    unittest.main()
