"""Build a relocatable app with its own full Python runtime and offline model."""
from pathlib import Path
import sys, shutil, subprocess, json, hashlib, os
ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT/'packaging/stage/OmniVoice'
STAGE.mkdir(parents=True, exist_ok=True)
def copy_file(source,destination):
    source,destination=Path(source),Path(destination)
    if destination.exists() and source.stat().st_size==destination.stat().st_size and source.stat().st_mtime_ns==destination.stat().st_mtime_ns:
        return str(destination)
    print('Copy file',source.name,flush=True)
    return shutil.copy2(source,destination)
def copy_tree(source, destination, extra=()):
    def incremental(src,dst):
        a,b=Path(src),Path(dst)
        if b.exists() and a.stat().st_size==b.stat().st_size and a.stat().st_mtime_ns==b.stat().st_mtime_ns:
            return str(b)
        return shutil.copy2(src,dst)
    shutil.copytree(source, destination, dirs_exist_ok=True,
        copy_function=incremental,ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git', *extra))
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
runtime=STAGE/'_runtime';runtime.mkdir(exist_ok=True)
base=Path(sys.base_prefix)
print('Copy Python runtime', flush=True)
for name in ['python.exe','pythonw.exe','python3.dll','python312.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt']:
    copy_file(base/name,runtime/name)
for name in ['DLLs','Lib','tcl']:
    copy_tree(base/name,runtime/name,('site-packages','test','tests') if name=='Lib' else ())
print('Copy dependencies (CPU/CUDA supported)',flush=True)
copy_tree(ROOT/'.venv/Lib/site-packages',runtime/'Lib/site-packages')
(runtime/'python312._pth').write_text('.\nDLLs\nLib\nLib/site-packages\n..\nimport site\n',encoding='utf-8')
for name in ['main.py','bootstrap.py','paths.py','app.py','dialogue.py','service.py','packaging_smoke.py']:
    shutil.copy2(ROOT/name,STAGE/name)
for name in ['assets','process','omnivoice','data']:
    print('Copy',name,flush=True);copy_tree(ROOT/name,STAGE/name)
(STAGE/'config').mkdir(exist_ok=True)
shutil.copy2(ROOT/'config/resources.json',STAGE/'config/resources.json')
# No user session, personal inputs, generated recordings or credentials are packaged.
bins=STAGE/'bin';bins.mkdir(exist_ok=True)
for name in ['ffmpeg','ffprobe']:
    shutil.copy2(shutil.which(name),bins/(name+'.exe'))
licenses=STAGE/'licenses';licenses.mkdir(exist_ok=True)
ffmpeg_root=Path(shutil.which('ffmpeg')).parents[1]
shutil.copy2(ffmpeg_root/'LICENSE',licenses/'FFmpeg-LICENSE.txt')
shutil.copy2(base/'LICENSE.txt',licenses/'Python-LICENSE.txt')
shutil.copy2(ROOT/'packaging/OmniVoice-LICENSE.txt',licenses/'OmniVoice-LICENSE.txt')
for name in ['msvcp140.dll','msvcp140_1.dll','msvcp140_2.dll','msvcp140_atomic_wait.dll','msvcp140_codecvt_ids.dll','concrt140.dll','vcomp140.dll']:
    source=Path(os.environ['WINDIR'])/'System32'/name
    if source.exists():copy_file(source,runtime/name)
(licenses/'THIRD-PARTY-NOTICES.txt').write_text(
    'OmniVoice model and package: k2-fsa/OmniVoice, Apache-2.0.\n'
    'https://github.com/k2-fsa/OmniVoice\n'
    'FFmpeg: Gyan.dev build; see FFmpeg-LICENSE.txt and https://www.gyan.dev/ffmpeg/builds/\n'
    'Python: see Python-LICENSE.txt.\n'
    'PySide6/Qt: LGPLv3; source and license information: https://code.qt.io/ and https://doc.qt.io/qtforpython-6/licenses.html\n'
    'Runtime package license files are retained under _runtime/Lib/site-packages, including *.dist-info/licenses.\n'
    'Microsoft Visual C++ app-local runtime DLLs; Windows 10/11 x64 required.\n',encoding='utf-8')
# Generate a simple application icon from vector drawing, preserving the UI palette.
from PySide6.QtGui import QImage,QPainter,QColor,QPen
from PySide6.QtCore import Qt,QRectF
canvas=QImage(256,256,QImage.Format_ARGB32);canvas.fill(QColor('#2563eb'))
p=QPainter(canvas);p.setRenderHint(QPainter.Antialiasing)
p.setPen(Qt.NoPen);p.setBrush(QColor('white'));p.drawRoundedRect(QRectF(100,40,56,115),28,28)
p.setBrush(Qt.NoBrush);p.setPen(QPen(QColor('white'),12));p.drawArc(QRectF(76,78,104,104),180*16,180*16)
p.drawLine(128,182,128,214);p.drawLine(96,214,160,214);p.end()
png=ROOT/'packaging/omni.png';canvas.save(str(png))
assert canvas.save(str(ROOT/'packaging/omni.ico'),'ICO'), 'Cannot write icon'
csc=Path(os.environ['WINDIR'])/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
subprocess.run([str(csc),'/nologo','/target:winexe','/platform:x64',
    '/reference:System.Windows.Forms.dll','/win32icon:'+str(ROOT/'packaging/omni.ico'),
    '/out:'+str(STAGE/'OmniVoice.exe'),str(ROOT/'packaging/Launcher.cs')],check=True)
print('Hash model and runtime essentials',flush=True)
essentials=list((STAGE/'data/models').rglob('*'))+[runtime/'pythonw.exe',runtime/'python312.dll',STAGE/'OmniVoice.exe']
manifest={p.relative_to(STAGE).as_posix():digest(p) for p in essentials if p.is_file()}
(STAGE/'bundle-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Build installer',flush=True)
subprocess.run([str(ROOT/'packaging/tools/inno/ISCC.exe'),str(ROOT/'packaging/OmniVoice.iss')],check=True)
print('BUILD COMPLETE',flush=True)
