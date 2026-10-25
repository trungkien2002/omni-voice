import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
from dialogue import parse_dialogue, NARRATOR
from service import Job, GenerationWorker, read_srt
from process.tts import omnivoice_engine as engine

FIXTURES = Path(__file__).parent / 'fixtures'

class ParserTests(unittest.TestCase):
    def test_both_complete_user_examples_preserve_intro_repeat_and_roles(self):
        for name, roles in [('listening_lan_duy.txt', ['Lan', 'Duy']), ('listening_mai_nam.txt', ['Mai', 'Nam'])]:
            with self.subTest(name=name):
                script = parse_dialogue((FIXTURES/name).read_text(encoding='utf-8'))
                self.assertEqual(script.roles, [NARRATOR] + roles)
                self.assertEqual(len(script.turns), 22)
                self.assertEqual(script.turns[0].role, NARRATOR)
                self.assertTrue(script.turns[0].text.startswith('Part II.'))
                self.assertEqual(script.turns[11].text, 'Now listen again')
                self.assertEqual(script.turns[11].role, NARRATOR)
                self.assertEqual([(t.role,t.text) for t in script.turns[1:11]], [(t.role,t.text) for t in script.turns[12:]])
                self.assertFalse(any(t.text.startswith(r + ':') for r in roles for t in script.turns))
        self.assertNotIn('Nam', parse_dialogue((FIXTURES/'listening_lan_duy.txt').read_text()).roles)

    def test_arbitrary_role_count_unicode_case_and_continuation(self):
        script = parse_dialogue('Hướng dẫn: hãy nghe.\nAn: Một\n  dòng nối\nAN: Hai\nBình：Ba\nC: Bốn\nD: Năm\nE: Sáu\nF: Bảy\nNow listen again')
        self.assertEqual(script.roles, [NARRATOR,'An','Bình','C','D','E','F'])
        self.assertEqual(script.turns[1].text, 'Một\ndòng nối')
        self.assertEqual(script.turns[2].role, 'An')
        self.assertEqual(script.turns[-1].role, NARRATOR)

    def test_no_guessing_unlabelled_roles(self):
        script = parse_dialogue('Listen to Nam and Lan.\nHello there.\nHow are you?')
        self.assertEqual(script.roles, [NARRATOR])
        self.assertTrue(script.warnings)

class DialogueOutputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        script = parse_dialogue((FIXTURES/'listening_lan_duy.txt').read_text(encoding='utf-8'))
        self.paths = {}
        for i,role in enumerate(script.roles):
            path = self.root/f'voice{i}.wav'
            sf.write(path,np.ones(2400)*0.1,24000)
            self.paths[role] = str(path)
        self.job = Job('',str(self.root/'out'),self.paths[NARRATOR],{'output_format':'wav'},
                       turns=script.turns,role_voices=self.paths,turn_gap=0.25)

    def tearDown(self): self.temp.cleanup()

    def fake_audio(self,text,path,config,cancel,srt_path=None):
        self.calls.append((text,config.voice_path))
        amplitude = (list(self.paths.values()).index(config.voice_path)+1)*0.1
        sf.write(path,np.full(2400,amplitude),24000)
        if srt_path: Path(srt_path).write_text(f'1\n00:00:00,000 --> 00:00:00,100\n{text}\n',encoding='utf-8')
        yield 'generated'

    def test_roles_intro_both_repeats_and_real_duration_timeline(self):
        self.calls=[]
        worker=GenerationWorker(self.job)
        with patch.object(engine,'tts_omnivoice',self.fake_audio):
            [(audio,srt)]=worker.execute()
        # Twelve unique turns generated, all twenty-two turns included in the output.
        self.assertEqual(len(self.calls),12)
        self.assertEqual(self.calls[0][1],self.paths[NARRATOR])
        self.assertEqual(next(p for text,p in self.calls if text=='Now listen again'),self.paths[NARRATOR])
        self.assertEqual(len(worker.timeline),22)
        data,rate=sf.read(audio)
        self.assertEqual(rate,24000)
        self.assertEqual(len(data),22*2400+21*6000)
        for index,turn in enumerate(self.job.turns):
            start=index*8400
            expected=(list(self.paths).index(turn.role)+1)*0.1
            self.assertAlmostEqual(float(data[start+100]),expected,places=4)
        cues=read_srt(srt)
        self.assertEqual(len(cues),22)
        self.assertAlmostEqual(cues[11]['start'],11*0.35,places=3)
        self.assertEqual(cues[11]['text'],'Now listen again')
        self.assertAlmostEqual(cues[-1]['end'],len(data)/rate,places=3)

    def test_failure_in_one_actor_preserves_existing_outputs(self):
        out=self.root/'out'; out.mkdir()
        previous=out/'Bai hoi thoai.wav'; previous.write_bytes(b'previous')
        def fail(text,path,config,cancel,srt_path=None):
            if config.voice_path==self.paths['Duy']: raise RuntimeError('failed actor')
            yield from self.fake_audio(text,path,config,cancel,srt_path)
        self.calls=[]
        with patch.object(engine,'tts_omnivoice',fail):
            with self.assertRaises(RuntimeError): GenerationWorker(self.job).execute()
        self.assertEqual(previous.read_bytes(),b'previous')
        self.assertEqual(list(out.glob('*.srt')),[])
        self.assertEqual(len(list(out.iterdir())),1)

    def test_cancellation_does_not_publish_partial_dialogue(self):
        self.calls=[]
        def cancel(text,path,config,event,srt_path=None):
            yield from self.fake_audio(text,path,config,event,srt_path)
            event.set()
        with patch.object(engine,'tts_omnivoice',cancel):
            self.assertEqual(GenerationWorker(self.job).execute(),[])
        self.assertEqual(list((self.root/'out').iterdir()),[])

    def test_missing_voice_is_rejected_before_generation(self):
        del self.job.role_voices['Duy']
        with patch.object(engine,'tts_omnivoice',side_effect=AssertionError('must not generate')):
            with self.assertRaisesRegex(ValueError,'Duy'): GenerationWorker(self.job).execute()

    def test_three_four_and_six_actors_route_to_their_assigned_voice(self):
        for count in (3,4,6):
            with self.subTest(count=count):
                script=parse_dialogue('Instructions.\n'+'\n'.join(f'Actor {i}: Sentence {i}.' for i in range(count)))
                paths={role:self.paths[list(self.paths)[i%3]] for i,role in enumerate(script.roles)}
                job=Job('',str(self.root/f'out{count}'),paths[NARRATOR],{'output_format':'wav'},turns=script.turns,role_voices=paths)
                calls=[]
                def render(text,path,config,cancel,srt_path=None):
                    calls.append((text,config.voice_path))
                    sf.write(path,np.ones(2400)*0.1,24000)
                    if srt_path: Path(srt_path).write_text(f'1\n00:00:00,000 --> 00:00:00,100\n{text}\n',encoding='utf-8')
                    yield 'ok'
                with patch.object(engine,'tts_omnivoice',render): GenerationWorker(job).execute()
                self.assertEqual(calls,[(t.text,paths[t.role]) for t in script.turns])

if __name__=='__main__': unittest.main()
