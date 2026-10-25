"""Omni Voice launcher. No external API is used for synthesis."""
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('TRANSFORMERS_OFFLINE','1')

def configure_ffmpeg():
    import shutil
    if shutil.which('ffmpeg') and shutil.which('ffprobe'): return
    capcut=Path(os.environ.get('LOCALAPPDATA',''))/'CapCut'/'Apps'
    candidates=list(capcut.glob('*/ffmpeg.exe')) if capcut.exists() else []
    if candidates:
        directory=max(candidates,key=lambda p:p.stat().st_mtime).parent
        os.environ['PATH']=str(directory)+os.pathsep+os.environ.get('PATH','')

def main():
    configure_ffmpeg()
    from PySide6.QtWidgets import QApplication, QComboBox, QSpinBox, QDoubleSpinBox
    from PySide6.QtGui import QFont, QFontDatabase
    from app import Window, STYLE
    application=QApplication(sys.argv)
    font_path=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'segoeui.ttf'
    if font_path.exists(): QFontDatabase.addApplicationFont(str(font_path))
    application.setApplicationName('Omni Voice')
    application.setFont(QFont('Segoe UI',11))
    application.setStyleSheet(STYLE)
    # Scrolling the page must not accidentally change a voice or reading setting.
    for cls in (QComboBox,QSpinBox,QDoubleSpinBox):
        cls.wheelEvent=lambda self,event:event.ignore()
    window=Window(); window.show()
    return application.exec()

if __name__=='__main__': sys.exit(main())
