import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import tempfile,json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import app
from dialogue import NARRATOR
application=QApplication([])
real_root=app.ROOT
first=app.Window()
def check():
 if first.scan.isRunning():QTimer.singleShot(200,check);return
 voices=first.voices
 first.save_timer.stop();first.dialogue_timer.stop()
 with tempfile.TemporaryDirectory() as folder:
  app.ROOT=Path(folder)
  app.STATE_ROOT=Path(folder)
  first.mode.setCurrentIndex(1)
  first.dialogue_text.setPlainText('Listen to this conversation.\nMai: Hello.\nNam: Good morning.\nNow listen again\nMai: Hello.\nNam: Good morning.')
  first.identify_dialogue()
  first.role_voices={NARRATOR:voices[0].path,'Mai':voices[1].path,'Nam':voices[2].path}
  first.turn_gap.setValue(.7);first.is_dark_theme=False
  first.dictionary=[{'word':'AI','pronunciation':'ây ai'}]
  first.save_session();first.save_timer.stop()
  expected=dict(first.role_voices)
  app.VoiceScanWorker.run=lambda self:self.ready.emit(voices)
  second=app.Window();second.scan.wait();application.processEvents()
  second.save_timer.stop();second.dialogue_timer.stop()
  assert second.mode.currentIndex()==1
  assert second.dialogue_text.toPlainText()==first.dialogue_text.toPlainText()
  assert second.role_voices==expected
  assert second.turn_gap.value()==.7 and not second.is_dark_theme
  assert second.dictionary==first.dictionary
  assert all(second.role_combos[r].currentData()==p for r,p in expected.items())
  second.language.setCurrentText('English');second.identify_dialogue()
  assert all(second.role_combos[r].currentData()==p for r,p in expected.items())
  second.save_timer.stop();second.dialogue_timer.stop()
  print('PASS session restore, all role voices, filters, gap, theme, dictionary')
 app.ROOT=real_root
 app.STATE_ROOT=real_root
 application.quit()
QTimer.singleShot(500,check)
application.exec()
