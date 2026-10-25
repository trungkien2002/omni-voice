"""Installed entry point, with errors visible even without a terminal."""
import os
import sys
import traceback
from pathlib import Path

os.environ['OMNI_INSTALLED'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
from paths import ROOT, STATE_ROOT
STATE_ROOT.mkdir(parents=True, exist_ok=True)
logs = STATE_ROOT / 'logs'
logs.mkdir(exist_ok=True)
stream = (logs/'app.log').open('a', encoding='utf-8', buffering=1)
sys.stdout = sys.stderr = stream
os.environ['PATH'] = str(ROOT/'bin') + os.pathsep + os.environ.get('PATH', '')
os.environ['HF_HOME'] = str(STATE_ROOT/'cache')

try:
    if '--self-test' in sys.argv:
        from packaging_smoke import run
        run(sys.argv[sys.argv.index('--self-test') + 1])
    else:
        from main import main
        sys.exit(main())
except Exception:
    traceback.print_exc()
    import ctypes
    ctypes.windll.user32.MessageBoxW(None,
        'Không mở được Omni Voice. Chi tiết lỗi được lưu tại:\n'+str(logs/'app.log'),
        'Omni Voice', 0x10)
    sys.exit(1)
