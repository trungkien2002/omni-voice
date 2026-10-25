"""Separate bundled resources from per-user writable settings."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INSTALLED = os.environ.get('OMNI_INSTALLED') == '1'
STATE_ROOT = (Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'OmniVoice') if INSTALLED else ROOT
DEFAULT_OUTPUT = (Path.home() / 'Documents' / 'OmniVoice') if INSTALLED else ROOT / 'outputs'
