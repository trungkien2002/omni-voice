"""Resolve existing local weights without downloading or modifying shared data."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
MODEL_STATUS = {"message": "", "phase": "idle"}

def ensure_model_downloaded(progress_callback=None):
    settings = ROOT / "config" / "resources.json"
    configured = json.loads(settings.read_text(encoding="utf-8")) if settings.exists() else {}
    candidates = [ROOT / "data" / "models" / "models--k2-fsa--OmniVoice"]
    if configured.get("model_path"):
        specified=Path(configured["model_path"])
        candidates.append(specified if specified.is_absolute() else ROOT/specified)
    for path in candidates:
        if (path / "config.json").is_file() and (path / "model.safetensors").is_file():
            MODEL_STATUS.update(phase="ready", message="Model cục bộ đã sẵn sàng")
            return str(path)
    MODEL_STATUS.update(phase="error", message="Không tìm thấy model. Kiểm tra đường dẫn trong config/resources.json.")
    return None

def get_model_status():
    return dict(MODEL_STATUS)
