"""Run with pycapcut 0.0.3 installed: python test_v5.py"""
import copy,json,tempfile
from pathlib import Path
from PIL import Image
import pycapcut as cc
from kurgu_koprusu import build_project,validate_plan
from hareket import apply_motion,options

with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);drafts=root/'drafts';drafts.mkdir()
 im=root/'photo.jpg';Image.new('RGB',(1920,1080),'teal').save(im)
 p={'surum':3,'kurgu_adi':'V5 test','videolar':{},'sesler':{},'fotograflar':{'F':str(im)},
    'video_kesimleri':[],'yorum_kesimleri':[],'fotograf_kesimleri':[{'dosya':'F','cizelge':[i*4,i*4+4]} for i in range(5)],
    'haber_bantlari':[{'metin':'TEST BAND','cizelge':[0,20]}],'goruntu_bosluklari':[],
    'ayarlar':{'genislik':1920,'yukseklik':1080,'fps':30,'beklenen_sure':20}}
 p['fotograf_kesimleri'][-1]['hareket']='kapali'
 target=build_project(cc,p,root,drafts);d=json.loads((target/'draft_content.json').read_text())
 report=json.loads((target/'kurgu_hareket_raporu.json').read_text())
 assert len(report['applied'])==4
 assert [r['hareket'] for r in report['applied']]==['yakinlas','uzaklas','sagdan_yaklas','soldan_yaklas']
 tracks={t['name']:t for t in d['tracks']};ss=tracks['Fotograflar']['segments']
 assert not ss[-1]['common_keyframes']
 assert not tracks['Haber Bantlari']['segments'][0]['common_keyframes']
 for i,s in enumerate(ss):assert s['target_timerange']=={'start':i*4_000_000,'duration':4_000_000}
 for i,s in enumerate(ss[:4]):
  k=s['common_keyframes'][0]['keyframe_list'];assert k[0]['time_offset']==0 and k[-1]['time_offset']==3966667
  if i==0:assert k[0]['values'][0]<k[1]['values'][0]
  if i==1:assert k[0]['values'][0]>k[1]['values'][0]
 assert ss[2]['common_keyframes'][1]['keyframe_list'][0]['values'][0]>0
 assert ss[3]['common_keyframes'][1]['keyframe_list'][0]['values'][0]<0
 untouched=copy.deepcopy(d);again=apply_motion(d,[t['id'] for t in d['tracks']],{'fotograf_hareketi':'kapali'});assert d==untouched
 for config in [{'hareket_yuzdesi':True},{'kaydirma_yuzdesi':float('nan')},{'fotograf_hareketi':'bad'}]:
  try:options(config)
  except ValueError:pass
  else:raise AssertionError('Invalid option accepted')
 bad=copy.deepcopy(p);bad['fotograf_kesimleri'][0]['hareket']='bad'
 try:validate_plan(bad,root)
 except ValueError:pass
 else:raise AssertionError('Invalid cut motion')
 print('PASS new draft: four directions, per-photo off, saved keyframes, banner exclusion, timings and invalid options.')
