"""Exercise and archive real touch input in the dedicated Garden diagnostic app."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from collect_android_profile import verify_profile_build

ROOT = Path(__file__).resolve().parents[1]
ADB = Path.home() / 'Library/Android/sdk/platform-tools/adb'
PACKAGE = 'org.godotengine.gardendreams.profile'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', required=True)
    parser.add_argument('--build-report', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()

    def adb(*command):
        return subprocess.check_output([str(ADB), '-s', args.device, *command])

    def report():
        return json.loads(adb('exec-out', 'run-as', PACKAGE, 'cat', 'files/garden-phone-profile.json'))

    build = json.loads(args.build_report.read_text())
    fixture, _ = verify_profile_build(build, adb)
    current = report()
    assert current['status'] == 'ready_for_taps'
    assert not current['touch_events'], 'Start from an untouched completed diagnostic run'
    assert current['build'] == fixture, 'Wrong diagnostic APK is running'
    stages = [
        ('cast', 'Cast at the table', True, 'qinfang_ting', 'Close'),
        ('recast', 'Cast again', True, 'qinfang_ting', 'Close'),
        ('close', 'Close', False, 'qinfang_ting', 'Finish the demo'),
        ('finale', 'Finish the demo', False, 'qinfang_ting', 'Begin again'),
        ('replay', 'Begin again', False, 'terminal_room', 'Enter the garden'),
    ]
    for stage, button, reading, room, next_button in stages:
        before = len(current['touch_events'])
        control = current['buttons'][button]
        width, height = current['native_window_size']
        x, y = map(round, control['screen_center'])
        assert 0 <= x < width and 0 <= y < height, 'Touch target outside native screen'
        assert control['screen_size'][1] >= 48 * current['ui_content_scale_factor']
        adb('shell', 'input', 'tap', str(x), str(y))
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current = report()
            if (len(current['touch_events']) == before + 2
                    and current.get('reading_open') is reading
                    and current.get('room_after_touch') == room
                    and next_button in current['buttons']):
                break
            time.sleep(.25)
        else:
            raise AssertionError('Touch did not reach expected state: ' + stage)
        assert current['touch_events'][-2]['pressed'] is True
        assert current['touch_events'][-1]['pressed'] is False
        assert current['texture_memory_after_touch_bytes'] > 0
        subprocess.run(['python3', str(ROOT / 'scripts/collect_android_profile.py'),
                        '--device', args.device, '--build-report', str(args.build_report),
                        '--destination', str(args.destination / stage)], check=True)
        print('NATIVE_TOUCH_STAGE', stage, 'texture_bytes=', current['texture_memory_after_touch_bytes'], flush=True)
    assert len(current['touch_events']) == 10
    assert set(current['buttons']) == {'Read the terminal', 'Enter the garden'}
    print('ANDROID_NATIVE_TOUCH_SEQUENCE_PASS cast/recast/close/finale/replay', flush=True)


if __name__ == '__main__':
    main()
