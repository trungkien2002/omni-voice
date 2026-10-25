import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
from service import Job, GenerationWorker
from process.tts.break_tags import build_generation_plan
from process.tts.punctuation import set_punctuation_config, PunctuationConfig
from process.tts import omnivoice_engine as engine

class JobsTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.voice=self.root/'voice.wav'
        sf.write(self.voice,np.ones(2400)*0.1,24000)
        self.job=Job('Xin chào.',str(self.root/'out'),str(self.voice),{'output_format':'wav'})

    def tearDown(self):
        self.temp.cleanup()
        set_punctuation_config(PunctuationConfig())

    @staticmethod
    def fake_audio(text,path,config,cancel,srt_path=None):
        sf.write(path,np.ones(2400)*0.1,24000)
        if srt_path: Path(srt_path).write_text('1\n00:00:00,000 --> 00:00:00,100\nXin chào\n',encoding='utf-8')
        yield 'done'

    def test_failure_does_not_publish_or_mark_completed(self):
        def failing(text,path,config,cancel,srt_path=None):
            sf.write(path,np.ones(2400)*0.1,24000)
            raise RuntimeError('model failed')
            yield
        with patch.object(engine,'tts_omnivoice',failing):
            with self.assertRaises(RuntimeError): GenerationWorker(self.job).execute()
        self.assertFalse(list((self.root/'out').glob('*.wav')))
        self.assertFalse((self.root/'out'/'.omni_completed.json').exists())

    def test_cancellation_keeps_previous_output(self):
        out=self.root/'out'; out.mkdir()
        previous=out/'Giong doc.wav'; previous.write_bytes(b'previous-good-output')
        worker=GenerationWorker(self.job)
        def cancelled(text,path,config,cancel,srt_path=None):
            sf.write(path,np.ones(2400)*0.1,24000)
            cancel.set(); yield 'cancelled'
        with patch.object(engine,'tts_omnivoice',cancelled): worker.execute()
        self.assertEqual(previous.read_bytes(),b'previous-good-output')
        self.assertEqual(len(list(out.glob('*.wav'))),1)

    def test_punctuation_and_explicit_break_both_apply(self):
        set_punctuation_config(PunctuationConfig(enabled=True,period=0.4))
        plan=build_generation_plan('Xin chào. <break time=500ms/> Hẹn gặp lại.')
        self.assertEqual([p['seconds'] for p in plan if p['type']=='silence'],[0.4,0.5,0.4])

    def test_watermark_uses_audio_time_without_srt(self):
        class Runtime:
            device='cpu'
            def load_model(self,*args): pass
            def generate_chunk(self,**kwargs):
                calls.append(kwargs['text'])
                return np.ones(24000,dtype=np.float32)*0.1
        calls=[]
        config=engine.OmniVoiceConfig(watermark_enabled=True,watermark_text='Tên kênh',watermark_interval=1)
        with patch('process.tts.model_manager.ensure_model_downloaded',return_value='model'),patch.object(engine,'_get_runtime',return_value=Runtime()),patch.object(engine,'build_generation_plan',create=True):
            # Explicit break generates separate chunks without depending on chunk length.
            list(engine.tts_omnivoice('Câu một.<break time=1ms/>Câu hai.',str(self.root/'wm.wav'),config))
        self.assertIn('Tên kênh',calls)

if __name__=='__main__': unittest.main()
