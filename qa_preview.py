"""Render the actual Qt window offscreen for layout inspection."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QFontDatabase
from app import Window, STYLE
from service import ROOT

application=QApplication([])
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
QFontDatabase.addApplicationFont('C:/Windows/Fonts/seguiemj.ttf')
application.setFont(QFont('Segoe UI', 11)); application.setStyleSheet(STYLE)
Window.save_session=lambda self:None
window=Window(); window.show()

def capture():
    if window.scan.isRunning():
        QTimer.singleShot(500,capture); return
    (ROOT/'_qa').mkdir(exist_ok=True)
    window.resize(1220,900)
    window.mode.setCurrentIndex(0)
    application.processEvents()
    window.grab().save(str(ROOT/'_qa'/'interface.png'))
    print('Voices:',len(window.voices),'Vietnamese:',window.voice.count(),'Window:',window.size())
    window.mode.setCurrentIndex(1)
    window.dialogue_text.setPlainText((ROOT/'tests/fixtures/listening_lan_duy.txt').read_text(encoding='utf-8'))
    window.identify_dialogue()
    window.resize(1000,740)
    application.processEvents()
    window.grab().save(str(ROOT/'_qa'/'dialogue-small.png'))
    window.toggle_theme()
    application.processEvents()
    window.grab().save(str(ROOT/'_qa'/'dialogue-light.png'))
    window.resize(1220,900)
    window.dialogue_text.setPlainText('Listen to four people.\nAnna: Hello, everyone.\nBen: Good morning.\nChris: Shall we start?\nDiana: Yes, let us begin.')
    window.identify_dialogue()
    window.language.setCurrentText('English')
    for index, role in enumerate(window.dialogue_script.roles):
        window.role_combos[role].setCurrentIndex(index + 1)
    application.processEvents()
    window.grab().save(str(ROOT/'_qa'/'dialogue-four-roles.png'))
    application.quit()

QTimer.singleShot(1000,capture)
application.exec()
