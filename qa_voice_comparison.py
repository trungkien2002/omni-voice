import os,sys,json
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
from pathlib import Path
import numpy as np,soundfile as sf
from service import ROOT,Job,GenerationWorker
from dialogue import parse_dialogue
root=ROOT/'_qa'/'voice-consistency'
r=json.loads((root/'report.json').read_text(encoding='utf-8'))
parts=[]
for item in r['renders']:
 if Path(item['voice']).stem=='Anh_Khoi':
  audio,sr=sf.read(item['audio']);parts.extend([audio,np.zeros(round(.6*sr))])
sf.write(root/'Nam_Anh_Khoi_comparison.wav',np.concatenate(parts[:-1]),sr)
s=json.loads((ROOT/'config/session.json').read_text(encoding='utf-8'))
text='\n'.join('Nam: '+item['text'] for item in r['renders'] if Path(item['voice']).stem=='Anh_Khoi')
voice=str(ROOT/'data/voices/Adam_Stone.wav')
job=Job('',str(root/'english-comparison'),voice,s['options'],srt=True,
 turns=parse_dialogue(text).turns,role_voices={'Nam':voice},turn_gap=.6,
 dictionary=s.get('dictionary',[]),pauses=s.get('pauses',{}))
w=GenerationWorker(job)
w.message.connect(lambda m:print(m,flush=True))
outputs=w.execute()
r['english_comparison']={'voice':voice,'audio':str(outputs[0][0]),'timeline':w.timeline,'note':'Controlled alternative voice; not a proven speaker-consistency fix.'}
r['nam_only_comparison']=str(root/'Nam_Anh_Khoi_comparison.wav')
(root/'report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE comparison',flush=True)
