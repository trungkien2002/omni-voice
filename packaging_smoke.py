"""Installed-runtime verification; invoked only by the explicit --self-test switch."""
def run(report_path):
    import os,json,hashlib,socket
    from pathlib import Path
    import faulthandler
    faulthandler.dump_traceback_later(120, repeat=True)
    from paths import ROOT,STATE_ROOT
    os.environ['QT_QPA_PLATFORM']='offscreen'
    os.environ['HF_HOME']=str(Path(report_path).parent/'empty-hf-cache')
    report={'stages':[],'errors':[],'network_attempts':[]}
    def deny_network(self,address):
        report['network_attempts'].append(str(address))
        raise RuntimeError('Network disabled for installed-package test')
    socket.socket.connect=deny_network
    import sys,torch,transformers,soundfile,subprocess
    from PySide6.QtWidgets import QApplication,QMessageBox
    from PySide6.QtGui import QFont,QFontDatabase
    from PySide6.QtCore import QTimer
    from app import Window
    from dialogue import NARRATOR
    from service import valid_audio
    from process.tts.model_manager import ensure_model_downloaded
    destination=Path(report_path);destination.parent.mkdir(parents=True,exist_ok=True)
    report.update(root=str(ROOT),state=str(STATE_ROOT),executable=sys.executable,
        torch=torch.__version__,transformers=transformers.__version__,cuda=torch.cuda.is_available(),
        imports={m.__name__:str(Path(m.__file__).resolve()) for m in [torch,transformers,soundfile]})
    assert all(str(ROOT) in path for path in report['imports'].values())
    assert Path(ensure_model_downloaded()).is_relative_to(ROOT)
    manifest=json.loads((ROOT/'bundle-manifest.json').read_text(encoding='utf-8'))
    for relative,expected in manifest.items():
        h=hashlib.sha256()
        with (ROOT/relative).open('rb') as f:
            for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
        assert h.hexdigest()==expected,relative
    report['manifest_verified']=len(manifest)
    report['ffmpeg']=subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
    print('SELF-TEST: imports, model hashes and bundled FFmpeg verified',flush=True)
    assert str(ROOT/'bin') in os.environ['PATH']
    application=QApplication([])
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
    application.setFont(QFont('Segoe UI',11))
    window=Window();window.show()
    # Persist only a controlled QA session, with no developer session included in bundle.
    QMessageBox.warning=lambda *args:report['errors'].append(str(args[-1]))
    QMessageBox.information=lambda *args:report['errors'].append(str(args[-1]))
    def next_stage():
        index=len(report['stages'])
        if index==2:
            report['ui_reenabled']=window.create.isEnabled() and not window.stop.isEnabled()
            window.resize(1220,900);application.processEvents()
            window.grab().save(str(destination.with_suffix('.png')))
            window.player.stop();window.save_timer.stop();window.dialogue_timer.stop()
            destination.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            application.quit();return
        window.steps.setCurrentText('16');window.srt.setChecked(True);window.watermark.setChecked(False)
        window.dictionary=[];window.pauses={};window.speed.setValue(1);window.pitch.setValue(1)
        window.output_dir.setText(str(destination.parent/('dialogue' if index==0 else 'cpu')))
        window.device.setCurrentIndex(0 if index==0 else 1)
        window.format.setCurrentIndex(window.format.findData('mp3' if index==0 else 'wav'))
        window.language.setCurrentText('English')
        if index==0:
            window.mode.setCurrentIndex(1)
            window.dialogue_text.setPlainText('Listen to this conversation.\nAnna: Good morning.\nBob: Hello, Anna.\nNow listen again\nAnna: Good morning.\nBob: Hello, Anna.')
            window.identify_dialogue()
            for role,filename in [(NARRATOR,'Teacher_English_Male.wav'),('Anna','Radiant_Girl_English.wav'),('Bob','Adam_Stone.wav')]:
                combo=window.role_combos[role];combo.setCurrentIndex(combo.findData(str(ROOT/'data/voices'/filename)))
        else:
            window.mode.setCurrentIndex(0);window.text.setPlainText('Hello. The application works offline.')
            window.voice.setCurrentIndex(window.voice.findData(str(ROOT/'data/voices/Adam_Stone.wav')))
        window.generate()
        if not window.worker:
            report['errors'].append('Worker did not start');application.quit();return
        worker=window.worker
        def completed(ok,message):
            stage={'device':'auto' if index==0 else 'cpu','ok':ok,'message':message,'turns':len(worker.timeline)}
            if ok:
                path=window.outputs[-1];stage['audio']=path;stage['valid_audio']=valid_audio(path)
            report['stages'].append(stage)
        worker.completed.connect(completed)
        worker.finished.connect(lambda:QTimer.singleShot(50,next_stage))
    def start():
        if window.scan.isRunning():QTimer.singleShot(200,start);return
        report['voices']=len(window.voices)
        print('SELF-TEST: scanned',len(window.voices),'voices',flush=True)
        report['initial_session_exists']=(STATE_ROOT/'config/session.json').exists()
        next_stage()
    QTimer.singleShot(400,start)
    application.exec()
    faulthandler.cancel_dump_traceback_later()
    assert len(report['stages'])==2 and all(s['ok'] and s['valid_audio'] for s in report['stages']),report
    assert report['stages'][0]['turns']==6
    assert not report['network_attempts'] and not report['errors'],report
