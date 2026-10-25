"""Single-text and multi-role TTS jobs with atomic, streamed output assembly."""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import threading
import re
from PySide6.QtCore import QThread, Signal
from dialogue import Turn, NARRATOR, role_name

from paths import ROOT, STATE_ROOT

@dataclass
class Job:
    text: str
    output_dir: str
    voice_path: str
    options: dict
    srt: bool = True
    dictionary: list = field(default_factory=list)
    pauses: dict = field(default_factory=dict)
    turns: list[Turn] = field(default_factory=list)
    role_voices: dict[str, str] = field(default_factory=dict)
    turn_gap: float = 0.4

def read_text(path):
    raw = Path(path).read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        import chardet
        return raw.decode(chardet.detect(raw).get('encoding') or 'utf-8', errors='replace')

def unique_output(folder, stem, fmt):
    stem = re.sub(r'[\\/:*?"<>|]', '_', stem).strip(' .')[:100] or 'Giong doc'
    path = Path(folder) / f'{stem}.{fmt}'
    index = 2
    while path.exists() or path.with_suffix('.srt').exists():
        path = Path(folder) / f'{stem} ({index}).{fmt}'
        index += 1
    return path

def valid_audio(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size < 44:
        return False
    try:
        import soundfile as sf
        info = sf.info(str(path))
        return info.frames > 0 and info.samplerate > 0
    except Exception:
        try:
            result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', str(path)],
                capture_output=True, text=True, timeout=30, creationflags=0x08000000)
            return result.returncode == 0 and float(result.stdout.strip()) > 0
        except Exception:
            return False

def read_srt(path):
    from process.tts.srt_generator import parse_timestamp
    cues = []
    for block in Path(path).read_text(encoding='utf-8-sig').strip().split('\n\n'):
        lines = block.splitlines()
        if len(lines) >= 3 and '-->' in lines[1]:
            start, end = lines[1].split('-->', 1)
            cues.append({'start': parse_timestamp(start.strip()), 'end': parse_timestamp(end.strip()),
                         'text': '\n'.join(lines[2:])})
    return cues

def publish(audio, subtitle, destination):
    final_srt = destination.with_suffix('.srt') if subtitle else None
    published = []
    try:
        if subtitle:
            os.replace(subtitle, final_srt)
            published.append(final_srt)
        os.replace(audio, destination)
        published.append(destination)
    except Exception:
        for path in published:
            path.unlink(missing_ok=True)
        raise
    return destination, final_srt

class GenerationWorker(QThread):
    message = Signal(str)
    progress = Signal(int, int)
    output = Signal(str)
    completed = Signal(bool, str)

    def __init__(self, job):
        super().__init__()
        self.job = job
        self.cancel = threading.Event()
        self.result = None
        self.timeline = []

    def stop(self):
        self.cancel.set()

    def run(self):
        try:
            outputs = self.execute()
            if self.cancel.is_set():
                self.result = (False, 'Đã dừng. Bài đang xử lý chưa được lưu; kết quả trước đó vẫn được giữ.')
            else:
                self.result = (True, f'Đã tạo xong {len(outputs)} bài âm thanh.')
        except Exception as exc:
            import traceback
            (STATE_ROOT / 'config').mkdir(parents=True, exist_ok=True)
            (STATE_ROOT / 'config' / 'last_error.log').write_text(traceback.format_exc(), encoding='utf-8')
            self.result = (False, str(exc))
        self.completed.emit(*self.result)

    def execute(self):
        from process.tts.omnivoice_engine import OmniVoiceConfig
        from process.tts.pronunciation import set_dictionary
        from process.tts.punctuation import PunctuationConfig, set_punctuation_config
        set_dictionary(self.job.dictionary)
        set_punctuation_config(PunctuationConfig(**self.job.pauses))
        if self.cancel.is_set():
            return []
        config = OmniVoiceConfig(voice_path=self.job.voice_path, **self.job.options)
        folder = Path(self.job.output_dir)
        folder.mkdir(parents=True, exist_ok=True)
        destination = unique_output(folder, 'Bai hoi thoai' if self.job.turns else 'Giong doc', config.output_format)
        with tempfile.TemporaryDirectory(prefix='.omni_', dir=folder) as temp_dir:
            temp = Path(temp_dir)
            audio = temp / ('final.' + config.output_format)
            subtitle = temp / 'final.srt' if self.job.srt else None
            if self.job.turns:
                self.generate_dialogue(temp, audio, subtitle, config)
            else:
                if not self.job.text.strip():
                    raise ValueError('Hãy nhập văn bản muốn đọc.')
                self.render(self.job.text, audio, subtitle, config)
            if self.cancel.is_set():
                return []
            if not valid_audio(audio):
                raise RuntimeError('Kết quả âm thanh không hợp lệ; chưa lưu bài.')
            if subtitle and (not subtitle.exists() or not read_srt(subtitle)):
                raise RuntimeError('Chưa tạo được phụ đề; chưa lưu bài.')
            result = publish(audio, subtitle, destination)
        self.output.emit(str(destination))
        self.progress.emit(1, 1)
        return [result]

    def render(self, text, audio, subtitle, config):
        from process.tts.omnivoice_engine import tts_omnivoice
        for message in tts_omnivoice(text, str(audio), config, self.cancel,
                                     srt_path=str(subtitle) if subtitle else None):
            self.message.emit(message)
        if self.cancel.is_set():
            return
        if not valid_audio(audio):
            raise RuntimeError('Một lượt thoại chưa tạo được âm thanh; chưa lưu bài thiếu nội dung.')
        if subtitle and (not subtitle.exists() or not read_srt(subtitle)):
            raise RuntimeError('Một lượt thoại chưa tạo được phụ đề.')

    def generate_dialogue(self, temp, audio, subtitle, config):
        import numpy as np
        import soundfile as sf
        from process.tts.omnivoice_engine import SAMPLE_RATE
        from process.tts.srt_generator import write_srt
        turns = self.job.turns
        required = {t.role for t in turns}
        missing = [role_name(r) for r in required if not self.job.role_voices.get(r)]
        if missing:
            raise ValueError('Chưa chọn giọng cho: ' + ', '.join(missing))
        for role in required:
            if not Path(self.job.role_voices[role]).is_file():
                raise ValueError('Không tìm thấy giọng của ' + role_name(role))
        if not 0 <= self.job.turn_gap <= 5:
            raise ValueError('Khoảng nghỉ giữa lượt phải từ 0 đến 5 giây.')
        assembled = temp / 'assembled.wav'
        cache, cues = {}, []
        gap_frames = round(self.job.turn_gap * SAMPLE_RATE)
        current_frame = 0
        watermark_interval = config.watermark_interval
        wm_enabled = config.watermark_enabled and bool(config.watermark_text.strip())
        if wm_enabled and watermark_interval <= 0:
            raise ValueError('Chu kỳ lời nhận diện phải lớn hơn 0.')
        next_watermark = float(watermark_interval)
        self.timeline = []
        with sf.SoundFile(str(assembled), mode='w', samplerate=SAMPLE_RATE, channels=1,
                          format='WAV', subtype='PCM_16') as writer:
            def append_turn(role, text, tag):
                nonlocal current_frame
                key = (role, text)
                if key not in cache:
                    turn_audio = temp / f'turn_{len(cache):04d}.wav'
                    turn_srt = turn_audio.with_suffix('.srt') if subtitle else None
                    voice = self.job.role_voices.get(role, self.job.voice_path)
                    turn_config = replace(config, voice_path=voice, output_format='wav', watermark_enabled=False)
                    self.render(text, turn_audio, turn_srt, turn_config)
                    if self.cancel.is_set():
                        return False
                    cache[key] = (turn_audio, turn_srt)
                turn_audio, turn_srt = cache[key]
                start = current_frame / SAMPLE_RATE
                with sf.SoundFile(str(turn_audio)) as reader:
                    if reader.samplerate != SAMPLE_RATE or reader.channels != 1:
                        raise RuntimeError('Định dạng lượt thoại không phù hợp để ghép.')
                    while True:
                        if self.cancel.is_set():
                            return False
                        block = reader.read(65536, dtype='float32')
                        if not len(block):
                            break
                        writer.write(block)
                        current_frame += len(block)
                end = current_frame / SAMPLE_RATE
                if turn_srt:
                    for cue in read_srt(turn_srt):
                        cues.append({'start': start + cue['start'], 'end': min(end, start + cue['end']), 'text': cue['text']})
                self.timeline.append({'role': role, 'text': text, 'start': start, 'end': end, 'kind': tag})
                return True

            for index, turn in enumerate(turns):
                if self.cancel.is_set():
                    return
                self.message.emit(f'Đang đọc lượt {index + 1}/{len(turns)} — {role_name(turn.role)}')
                if wm_enabled and current_frame / SAMPLE_RATE >= next_watermark:
                    if not append_turn(NARRATOR, config.watermark_text, 'watermark'):
                        return
                    next_watermark = (int(current_frame / SAMPLE_RATE / watermark_interval) + 1) * watermark_interval
                if not append_turn(turn.role, turn.text, 'dialogue'):
                    return
                if index < len(turns) - 1 and gap_frames:
                    writer.write(np.zeros(gap_frames, dtype='float32'))
                    current_frame += gap_frames
                self.progress.emit(index + 1, len(turns))
        if self.cancel.is_set():
            return
        self.message.emit('Đang ghép lời dẫn và các vai thành một bài âm thanh…')
        self.encode(assembled, audio, config.output_format)
        if subtitle:
            write_srt(cues, str(subtitle))

    def encode(self, source, destination, fmt):
        if fmt == 'wav':
            shutil.copyfile(source, destination)
        elif fmt == 'mp3':
            subprocess.run(['ffmpeg', '-y', '-i', str(source), '-codec:a', 'libmp3lame',
                            '-b:a', '192k', str(destination)], capture_output=True, check=True,
                           creationflags=0x08000000)
        else:
            import soundfile as sf
            with sf.SoundFile(str(source)) as reader, sf.SoundFile(str(destination), mode='w',
                samplerate=reader.samplerate, channels=reader.channels,
                format={'flac':'FLAC','ogg':'OGG'}[fmt], subtype={'flac':'PCM_16','ogg':'VORBIS'}[fmt]) as writer:
                while True:
                    if self.cancel.is_set():
                        return
                    block = reader.read(65536, dtype='float32')
                    if not len(block):
                        break
                    writer.write(block)
