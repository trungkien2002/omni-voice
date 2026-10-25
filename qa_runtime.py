"""Real GPU generation with the actual dialogue UI and Qt worker."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QFontDatabase
from app import Window
from service import ROOT,valid_audio,read_srt
application=QApplication([])
QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
application.setFont(QFont('Segoe UI',11))
Window.save_session=lambda self:None
window=Window();window.show()
root=ROOT/'_qa'/'dialogue-real';root.mkdir(parents=True,exist_ok=True)
report={'stages':[],'errors':[]}
QMessageBox.warning=lambda *args:report['errors'].append(str(args[-1]))
QMessageBox.information=lambda *args:report['errors'].append(str(args[-1]))
stages=[('single','Xin chào. Đây là bài kiểm tra giọng đọc.','wav'),
 ('lan_duy',(ROOT/'tests/fixtures/listening_lan_duy.txt').read_text(encoding='utf-8'),'wav'),
 ('mai_nam',(ROOT/'tests/fixtures/listening_mai_nam.txt').read_text(encoding='utf-8'),'mp3'),
 ('four_roles','Listen to four people.\nAnna: Hello, everyone.\nBen: Good morning.\nChris: Shall we start?\nDiana: Yes, let us begin.','wav')]
def start():
 if window.scan.isRunning():QTimer.singleShot(300,start);return
 window.steps.setCurrentText('16');window.device.setCurrentIndex(0)
 window.watermark.setChecked(False);window.srt.setChecked(True)
 window.speed.setValue(1);window.volume.setValue(1);window.pitch.setValue(1)
 window.dictionary=[];window.pauses={};window.turn_gap.setValue(.4)
 window.language.setCurrentText('Tất cả ngôn ngữ');window.gender.setCurrentIndex(0)
 next_stage()
def next_stage():
 index=len(report['stages'])
 if index==len(stages):
  window.audio.setVolume(.02);window.listen_result();QTimer.singleShot(1800,finish);return
 name,text,fmt=stages[index]
 window.mode.setCurrentIndex(0 if name=='single' else 1)
 window.format.setCurrentIndex(window.format.findData(fmt));window.output_dir.setText(str(root/name))
 if name=='single':
  window.text.setPlainText(text)
  voice=next(v for v in window.voices if v.language=='Vietnamese')
  window.voice.setCurrentIndex(window.voice.findData(voice.path))
 else:
  window.dialogue_text.setPlainText(text);window.identify_dialogue()
  names=['Teacher_English_Male.wav','Radiant_Girl_English.wav','Adam_Stone.wav','Michael_Vincent.wav','Captivating_English_female.wav']
  for i,role in enumerate(window.dialogue_script.roles):
   path=str(ROOT/'data'/'voices'/names[i%len(names)])
   assert Path(path).is_file(),path
   combo=window.role_combos[role];combo.setCurrentIndex(combo.findData(path))
  before=dict(window.role_voices)
  window.language.setCurrentText('Tiếng Việt');window.identify_dialogue()
  assert all(window.role_combos[r].currentData()==p for r,p in before.items() if r in window.role_combos)
  window.language.setCurrentText('Tất cả ngôn ngữ')
 print('START',name,flush=True);window.generate()
 if not window.worker:raise RuntimeError('UI did not start: '+repr(report['errors']))
 worker=window.worker
 stage={'name':name,'format':fmt,'voices':dict(window.role_voices) if name!='single' else {}}
 def done(ok,message):
  stage.update(ok=ok,message=message,timeline=list(worker.timeline))
  if ok:
   path=Path(window.outputs[-1]);stage.update(audio=str(path),valid_audio=valid_audio(path),cues=len(read_srt(path.with_suffix('.srt'))))
   if name!='single':
    turns=window.dialogue_script.turns
    assert [t['text'] for t in worker.timeline]==[t.text for t in turns]
    assert [t['role'] for t in worker.timeline]==[t.role for t in turns]
    if name in ('lan_duy','mai_nam'):assert len(worker.timeline)==22
  report['stages'].append(stage);print('DONE',name,ok,flush=True)
 worker.completed.connect(done)
 worker.finished.connect(lambda:QTimer.singleShot(50,next_stage))
def finish():
 report['playback']={'duration_ms':window.player.duration(),'position_ms':window.player.position(),'error':window.player.errorString()}
 report['ui_reenabled']=window.create.isEnabled() and not window.stop.isEnabled()
 window.resize(1220,900);application.processEvents();window.grab().save(str(root/'result.png'))
 (root/'runtime-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':all(s['ok'] for s in report['stages']),'playback':report['playback'],'errors':report['errors']},ensure_ascii=False),flush=True)
 window.player.stop();application.quit()
QTimer.singleShot(600,start)
application.exec()
