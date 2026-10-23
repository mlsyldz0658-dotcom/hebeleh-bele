import copy,json,tempfile,subprocess,wave
from pathlib import Path
import pycapcut as cc
from kurgu_koprusu import validate_plan,build_project
from haber_bandi import render_band

def rejected(p,root):
    try:validate_plan(p,root)
    except ValueError:return
    raise AssertionError('Invalid plan accepted')

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder);drafts=root/'drafts';drafts.mkdir()
    vid=root/'v.mp4';audio=root/'a.wav'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x180:d=4','-c:v','libx264','-y',str(vid)],check=True)
    with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\0\0'*64000)
    p={'surum':3,'kurgu_adi':'V4 Test','videolar':{'V':str(vid)},'sesler':{'S':str(audio)},'video_kesimleri':[{'dosya':'V','kaynak':[0,2],'cizelge':[0,2],'orijinal_ses':False},{'dosya':'V','kaynak':[2,4],'cizelge':[2,4],'orijinal_ses':True}],'yorum_kesimleri':[{'dosya':'S','kaynak':[0,2],'cizelge':[0,2]}],'goruntu_bosluklari':[],'haber_bantlari':[{'metin':'WHAT THE RECORDS SHOW','etiket':'ANALYSIS','cizelge':[0,2]},{'metin':'A CLOSER LOOK AT THE TESTIMONY','cizelge':[2,4]}],'ayarlar':{'genislik':1920,'yukseklik':1080,'fps':30,'beklenen_sure':4,'anlatici_goruntusu_zorunlu':True}}
    target=build_project(cc,p,root,drafts)
    d=json.loads((target/'draft_content.json').read_text())
    assert d['duration']==4000000
    tracks=d['tracks'];segs=[s for t in tracks for s in t['segments']]
    visual=next(t for t in tracks if t['name']=='Videolar')['segments'];assert visual[0]['volume']==0 and visual[1]['volume']==1
    narration=next(t for t in tracks if t['name']=='Yorum')['segments'];assert narration[0]['volume']==1
    bands=next(t for t in tracks if t['name']=='Haber Bantlari')['segments'];assert len(bands)==2
    assert bands[1]['target_timerange']=={'start':2000000,'duration':2000000}
    assert bands[0]['render_index']>visual[0]['render_index']
    from PIL import Image
    for f in (target/'haber_bantlari').glob('*.png'):
        im=Image.open(f);assert im.size==(1920,1080) and im.getpixel((0,0))[3]==0
    bad=copy.deepcopy(p);bad['video_kesimleri'][0]['orijinal_ses']=True;rejected(bad,root)
    bad=copy.deepcopy(p);bad['video_kesimleri']=bad['video_kesimleri'][1:];rejected(bad,root)
    bad=copy.deepcopy(p);bad['haber_bantlari'][1]['cizelge']=[1,4];rejected(bad,root)
    bad=copy.deepcopy(p);bad['haber_bantlari'][1]['cizelge']=[2,5];rejected(bad,root)
    for text in ['WHAT THE RECORDS SHOW','TRUMP FACING GROWING REPUBLICAN REVOLT WITH 47 DAYS TO MIDTERMS','İŞÇİLERİN ÖDEMELERİ VE GÜNCEL DURUM']:
        render_band(text,'ANALYSIS',1920,1080)
    try:render_band('W'*240,'',1920,1080)
    except ValueError:pass
    else:raise AssertionError('Overflow not rejected')
print('PASS: timed overlays, foreground ordering, saved PNG assets, mute versus original audio, narration coverage, band overlap/range/overflow, Turkish text.')
