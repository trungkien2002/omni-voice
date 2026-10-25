"""Audit actual per-turn voice conditioning without changing saved preferences."""
import os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
import json,hashlib,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import soundfile as sf
import numpy as np
from service import ROOT,Job,GenerationWorker
from dialogue import parse_dialogue
from process.tts import omnivoice_engine as engine
from process.tts.voice_manager import _read_voice_metadata
root=ROOT/'_qa'/'voice-consistency';root.mkdir(parents=True,exist_ok=True)
session=json.loads((ROOT/'config/session.json').read_text(encoding='utf-8'))
script=parse_dialogue(session['dialogue_text'])
report={'assignment':session['role_voices'],'calls':[],'renders':[]}
runtime=engine._get_runtime()
original_prompt=runtime.get_voice_prompt
original_generate=runtime.generate_chunk
prompt_paths={}
def get_prompt(path,transcript=''):
 prompt=original_prompt(path,transcript)
 prompt_paths[id(prompt)]=path
 return prompt
def generate(*args,**kwargs):
 prompt=kwargs.get('voice_prompt')
 assert prompt is not None, 'AUTO VOICE DETECTED'
 tokens=prompt.ref_audio_tokens
 before=hashlib.sha256(tokens.detach().cpu().numpy().tobytes()).hexdigest()
 output=original_generate(*args,**kwargs)
 after=hashlib.sha256(tokens.detach().cpu().numpy().tobytes()).hexdigest()
 assert before==after,'PROMPT MUTATED'
 report['calls'].append({'text':kwargs.get('text'), 'voice':prompt_paths[id(prompt)],
  'prompt_id':id(prompt),'token_hash':before,'ref_text':prompt.ref_text})
 return output
runtime.get_voice_prompt=get_prompt
runtime.generate_chunk=generate
class AuditWorker(GenerationWorker):
 def render(self,text,audio,subtitle,config):
  super().render(text,audio,subtitle,config)
  target=root/'turns'/f'{len(report["renders"]):02d}_{Path(config.voice_path).stem}.wav'
  target.parent.mkdir(exist_ok=True);shutil.copyfile(audio,target)
  report['renders'].append({'text':text,'voice':config.voice_path,'audio':str(target)})
job=Job('',str(root/'same-settings'),session['role_voices'].get('__narrator__',''),session['options'],
 srt=True,turns=script.turns,role_voices=session['role_voices'],turn_gap=session['turn_gap'],
 dictionary=session.get('dictionary',[]),pauses=session.get('pauses',{}))
worker=AuditWorker(job)
worker.message.connect(lambda m:print(m,flush=True))
outputs=worker.execute()
report['timeline']=worker.timeline
report['outputs']=[str(a) for a,s in outputs]
nam=[c for c in report['calls'] if c['voice']==session['role_voices']['Nam']]
report['nam_prompt_count']=len({c['prompt_id'] for c in nam})
report['nam_token_hash_count']=len({c['token_hash'] for c in nam})
report['nam_generation_count']=len(nam)
assert len(nam)==5 and report['nam_prompt_count']==report['nam_token_hash_count']==1
report['routing_ok']=all(c['voice']==session['role_voices'][next(t.role for t in script.turns if t.text==c['text'])] for c in report['calls'])
# Compare exact repeated speech waveforms in the final file.
audio,rate=sf.read(report['outputs'][0])
identical=[]
for a,b in zip(worker.timeline[1:11],worker.timeline[12:22]):
 x=audio[round(a['start']*rate):round(a['end']*rate)]
 y=audio[round(b['start']*rate):round(b['end']*rate)]
 identical.append(np.array_equal(x,y))
report['repeated_dialogue_identical']=all(identical)
(root/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['nam_prompt_count','nam_token_hash_count','nam_generation_count','routing_ok','repeated_dialogue_identical']},ensure_ascii=False),flush=True)
