import copy,json,tempfile,subprocess,wave
from pathlib import Path
from PIL import Image
import pycapcut as cc
from kurgu_koprusu import build_project,validate_plan

def inspect(path,expected):
    d=json.loads((path/'draft_content.json').read_text())
    assert d['duration']==expected
    assert d['config']['maintrack_adsorb'] is False
    return d

with tempfile.TemporaryDirectory() as folder:
    root=Path(folder);drafts=root/'drafts';drafts.mkdir()
    image=root/'test.jfif';Image.new('RGB',(320,180),(50,100,180)).save(image,'JPEG')
    jpeg=root/'test.jpeg';Image.new('RGB',(320,180),(180,100,50)).save(jpeg,'JPEG')
    vid=root/'test.mp4'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x180:d=3','-c:v','libx264','-y',str(vid)],check=True)
    audio=root/'test.wav'
    with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(b'\0\0'*16000*3)
    old={'surum':1,'kurgu_adi':'Old','videolar':{'V':str(vid)},'sesler':{'S':str(audio)},'video_kesimleri':[{'dosya':'V','kaynak':[0,2],'cizelge':[0,2],'orijinal_ses':True}],'yorum_kesimleri':[{'dosya':'S','kaynak':[0,2],'cizelge':[2,4]}],'goruntu_bosluklari':[[2,4]],'ayarlar':{'genislik':1920,'yukseklik':1080,'fps':30,'beklenen_sure':4}}
    inspect(build_project(cc,old,root,drafts),4000000)
    mixed=copy.deepcopy(old);mixed['kurgu_adi']='Mixed';mixed['surum']=2
    mixed['fotograflar']={'P':str(image)};mixed['fotograf_kesimleri']=[{'dosya':'P','cizelge':[2,4]}];mixed['goruntu_bosluklari']=[]
    d=inspect(build_project(cc,mixed,root,drafts),4000000)
    assert len(d['tracks'])==3
    bad=copy.deepcopy(mixed);bad['fotograf_kesimleri'][0]['cizelge']=[1,4]
    try:validate_plan(bad,root);raise AssertionError('overlap accepted')
    except ValueError:pass
    plan=json.loads(Path(__file__).with_name('WM_Video1_58_Gorsel.json').read_text())
    assert len(plan['fotograflar'])==58 and plan['fotograflar']['F58'].endswith('1 (58).jpeg')
    for k in plan['fotograflar']:plan['fotograflar'][k]=str(jpeg if k=='F58' else image)
    d=inspect(build_project(cc,plan,root,drafts),539000000)
    segments=[s for t in d['tracks'] for s in t['segments']]
    assert len(segments)==59
    expected=plan['fotograf_kesimleri']
    for i,item in enumerate(expected):
        from kurgu_koprusu import interval
        a,b=interval(item['cizelge']);assert segments[i]['target_timerange']=={'start':a,'duration':b-a}
    assert segments[-1]['target_timerange']=={'start':511000000,'duration':28000000}
    meta=json.loads((next(p for p in drafts.iterdir() if 'WM Video' in p.name)/'draft_meta_info.json').read_text())
    assert all(m['metetype']=='photo' for g in meta['draft_materials'] for m in g.get('value',[]))
print('PASS: old video/audio JSON; mixed video/audio/photo; overlap rejection; 58 exact intervals; 539s duration; trailing transparent 28s; photo metadata.')
