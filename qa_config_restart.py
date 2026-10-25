"""Verify automatic preferences persistence across two isolated app processes."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['OMNI_INSTALLED'] = '1'
import json
import sys
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import app
from dialogue import NARRATOR

application = QApplication([])
window = app.Window()
phase = sys.argv[1]
report = Path(sys.argv[2])
session = app.STATE_ROOT / 'config' / 'session.json'
expected = report.with_suffix('.expected.json')

def check_saved():
    data = json.loads(session.read_text(encoding='utf-8'))
    assert data['options']['speed'] == 0.85
    assert data['role_voices'] == window.role_voices
    assert data['turn_gap'] == 0.7
    expected.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    window.close()
    print('PASS automatic save before close')
    application.quit()

def check():
    if window.scan.isRunning():
        QTimer.singleShot(100, check)
        return
    if phase == 'write':
        window.mode.setCurrentIndex(1)
        window.dialogue_text.setPlainText('Listen.\nMai: Hello.\nNam: Good morning.')
        window.identify_dialogue()
        window.role_voices = {NARRATOR: window.voices[0].path, 'Mai': window.voices[1].path, 'Nam': window.voices[2].path}
        window.speed.setValue(0.85)
        window.pitch.setValue(1.1)
        window.volume.setValue(1.2)
        window.turn_gap.setValue(0.7)
        window.steps.setCurrentText('8')
        window.device.setCurrentIndex(window.device.findData('cpu'))
        window.format.setCurrentIndex(window.format.findData('mp3'))
        window.output_dir.setText(str(app.STATE_ROOT / 'audio-output'))
        window.is_dark_theme = False
        window.dictionary = [{'word': 'AI', 'pronunciation': 'ay eye'}]
        window.srt.setChecked(False)
        # Wait for the actual debounce timer; do not call save_session.
        QTimer.singleShot(1600, check_saved)
    else:
        data = json.loads(expected.read_text(encoding='utf-8'))
        assert window.options() == data['options']
        assert window.role_voices == data['role_voices']
        assert all(window.role_combos[r].currentData() == p for r, p in data['role_voices'].items())
        assert window.mode.currentIndex() == data['mode']
        assert window.dialogue_text.toPlainText() == data['dialogue_text']
        assert window.turn_gap.value() == data['turn_gap']
        assert window.output_dir.text() == data['output']
        assert window.dictionary == data['dictionary']
        assert window.srt.isChecked() == data['srt']
        assert window.is_dark_theme == data['is_dark_theme']
        report.write_text(json.dumps({'passed': True, 'app_module': app.__file__, 'session': str(session), 'separate_processes': True, 'automatic_save': True}, indent=2), encoding='utf-8')
        print('PASS restored preferences and all role voices in a new process')
        window.close()
        application.quit()

QTimer.singleShot(300, check)
application.exec()
