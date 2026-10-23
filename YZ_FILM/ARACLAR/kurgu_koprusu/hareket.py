"""Conservative photo keyframes for new and existing CapCut drafts. Stdlib only."""
import copy
import json
import math
import re
import shutil
import time
import uuid
from pathlib import Path

MODES = ('otomatik', 'yakinlas', 'uzaklas', 'sagdan_yaklas', 'soldan_yaklas', 'kapali')
CYCLE = MODES[1:5]

def options(settings):
    mode = settings.get('fotograf_hareketi', 'otomatik')
    zoom = settings.get('hareket_yuzdesi', 8)
    pan = settings.get('kaydirma_yuzdesi', 2)
    if mode not in MODES: raise ValueError('Gecersiz fotograf_hareketi: '+str(mode))
    for key,value,low,high in [('hareket_yuzdesi',zoom,1,15),('kaydirma_yuzdesi',pan,0,3)]:
        if type(value) not in (int,float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{key}: {low}-{high} arasinda sayi olmali.')
    return mode, zoom, pan

def keyframes(prop, start, end, a, b):
    return {'id':uuid.uuid4().hex, 'material_id':'', 'property_type':prop,
        'keyframe_list':[{'id':uuid.uuid4().hex,'curveType':'Line','graphID':'','string_value':'',
        'left_control':{'x':0.0,'y':0.0},'right_control':{'x':0.0,'y':0.0},
        'time_offset':t,'values':[v]} for t,v in [(start,a),(end,b)]]}

def protected(material, track):
    name = (material.get('path','')+' '+material.get('material_name','')).replace('\\','/').lower()
    return (track.get('name','').lower() in ('haber bantlari','haber bantları') or
            any(x in name for x in ('haber_bantlari/', 'bos_alan.png', 'defaultplaceholder.png')) or
            re.search(r'(?:/|\s)bant_\d+\.png',name) is not None)

def apply_motion(content, track_ids, settings=None, overrides=None):
    """Only chosen photo tracks; skip preexisting animation/complex transforms. Return report."""
    mode, zoom, pan = options(settings or {})
    materials={m['id']:m for m in content.get('materials',{}).get('videos',[])}
    anims={m['id']:m for m in content.get('materials',{}).get('material_animations',[])}
    canvas=content.get('canvas_config',{})
    cw,ch=canvas.get('width',0),canvas.get('height',0)
    if not cw or not ch:raise ValueError('Tuval olculeri okunamadi.')
    fps=float(content.get('fps',30))
    if not math.isfinite(fps) or fps<=0:raise ValueError('Gecersiz FPS')
    report={'applied':[], 'skipped':[]}
    candidates=[]
    for t in content.get('tracks',[]):
        if t.get('id') not in track_ids or t.get('type')!='video':continue
        for s in t.get('segments',[]):
            m=materials.get(s.get('material_id'),{})
            if m.get('type')=='photo': candidates.append((t,s,m))
    candidates.sort(key=lambda item:item[1]['target_timerange']['start'])
    index=0
    for t,s,m in candidates:
        entry={'segment':s['id'],'dosya':m.get('material_name') or m.get('path',''),
               'baslangic_sn':s['target_timerange']['start']/1e6}
        why=None
        selected=(overrides or {}).get(s['id'],mode)
        if selected not in MODES:raise ValueError('Gecersiz hareket: '+str(selected))
        clip=s.get('clip') or {};scale=clip.get('scale',{});pos=clip.get('transform',{})
        sx,sy=scale.get('x',1),scale.get('y',1)
        w,h=m.get('width',0),m.get('height',0)
        crop=m.get('crop') or {}
        full_crop={'upper_left_x':0,'upper_left_y':0,'upper_right_x':1,'upper_right_y':0,
                   'lower_left_x':0,'lower_left_y':1,'lower_right_x':1,'lower_right_y':1}
        if selected=='kapali':why='Hareket kapali'
        elif protected(m,t):why='Bant veya bos alan'
        elif s.get('common_keyframes') or s.get('keyframe_refs'):why='Mevcut anahtar kareler korundu'
        elif any(anims.get(r,{}).get('animations') for r in s.get('extra_material_refs',[])):why='Mevcut animasyon korundu'
        elif s.get('visible') is False:why='Gizli kesim'
        elif s.get('speed',1)!=1 or s.get('reverse'):why='Hiz veya ters oynatma'
        elif not w or not h:why='Gorsel olculeri eksik'
        elif any(abs(float(crop.get(k,v))-v)>1e-6 for k,v in full_crop.items()):why='Ozel kirpma korundu'
        elif (abs(sx-sy)>1e-6 or sx<=0 or abs(clip.get('rotation',0))>1e-6 or
              abs(pos.get('x',0))>1e-6 or abs(pos.get('y',0))>1e-6):why='Ozel konum veya donusum korundu'
        elif any(s.get(k) for k in ('mask','masks')) or (m.get('matting') or {}).get('flag',0):why='Maske korunuyor'
        duration=s['target_timerange']['duration']
        if not why and duration<1_000_000:why='1 saniyeden kisa; hizli hareket atlandi'
        # Leave letterboxed/portrait compositions unchanged instead of aggressively cropping them.
        fit=min(cw/w,ch/h) if w and h else 1
        cover=max(cw/(w*fit),ch/(h*fit)) if w and h else 1
        if not why and cover>sx*1.02:why='Farkli en-boy orani; mevcut kadraj korundu'
        if why:
            report['skipped'].append(dict(entry,neden=why));continue
        actual=CYCLE[index%4] if selected=='otomatik' else selected
        # Short stills have smaller movement. A 4s+ shot gets the requested amount.
        strength=min(1.0,duration/4_000_000)
        z=zoom/100*strength
        base=max(sx,cover)
        if actual=='uzaklas': a,b=base*(1+z),base
        elif actual in ('sagdan_yaklas','soldan_yaklas'):a,b=base*(1+z*.5),base*(1+z)
        else:a,b=base,base*(1+z)
        x0=x1=0.0
        if actual in ('sagdan_yaklas','soldan_yaklas'):
            # Conservative half-margin keeps edges covered across linear interpolation.
            margin=max(0,(w*fit*a/cw-1)/2)
            shift=min(pan/100*strength,margin*.8)
            x0=shift if actual=='sagdan_yaklas' else -shift
        start=(s.get('source_timerange') or {}).get('start',0)
        last=start+max(1,duration-round(1_000_000/fps))
        s['common_keyframes']=[keyframes('KFTypeScaleX',start,last,a,b)]
        if x0:s['common_keyframes'].append(keyframes('KFTypePositionX',start,last,x0,x1))
        s.setdefault('clip',clip)
        clip['scale']={'x':a,'y':a}
        clip['transform']={'x':x0,'y':0.0}
        s['uniform_scale']={'on':True,'value':1.0}
        report['applied'].append(dict(entry,hareket=actual));index+=1
    return report

def read_content(path):
    try:
        d=json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (ValueError,UnicodeError) as e:
        raise ValueError('Taslak okunabilir JSON degil; bu CapCut taslak bicimi desteklenmiyor.') from e
    if not isinstance(d,dict) or not isinstance(d.get('tracks'),list):
        raise ValueError('CapCut taslagi bekleniyor; kurgu plani JSON dosyasi secmeyin.')
    return d

def photo_tracks(d):
    photos={m['id'] for m in d.get('materials',{}).get('videos',[]) if m.get('type')=='photo'}
    return [(t,sum(s.get('material_id') in photos for s in t.get('segments',[])))
            for t in d.get('tracks',[]) if t.get('type')=='video' and any(s.get('material_id') in photos for s in t.get('segments',[]))]

def rewrite_values(obj, replacements, path_pairs):
    if isinstance(obj,dict):return {k:rewrite_values(v,replacements,path_pairs) for k,v in obj.items()}
    if isinstance(obj,list):return [rewrite_values(v,replacements,path_pairs) for v in obj]
    if isinstance(obj,str):
        if obj in replacements:return replacements[obj]
        normalized=obj.replace('\\','/')
        for old,new in path_pairs:
            if normalized==old or normalized.startswith(old+'/'):return new+normalized[len(old):]
    return obj

def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')

def clone_project(source, draft_root, track_ids, settings=None, apply=True):
    """Never writes source. Clone local folder, rebase internal paths, mint project/timeline IDs."""
    source=Path(source).resolve();draft_root=Path(draft_root).resolve()
    original=read_content(source/'draft_content.json')
    meta=json.loads((source/'draft_meta_info.json').read_text(encoding='utf-8-sig'))
    project_file=source/'Timelines'/'project.json'
    timeline=None
    if project_file.exists():
        timeline=json.loads(project_file.read_text(encoding='utf-8-sig'))
        active=[t for t in timeline.get('timelines',[]) if not t.get('is_marked_delete')]
        if len(active)!=1 or timeline.get('main_timeline_id')!=original.get('id'):
            raise ValueError('Birden fazla veya farkli aktif zaman cizelgesi var; bu taslak otomatik degistirilmedi.')
        mirror=source/'Timelines'/original['id']/'draft_content.json'
        if not mirror.is_file() or read_content(mirror)!=original:
            raise ValueError('Ana taslak ve zaman cizelgesi kopyasi farkli. CapCut\'i kapatip tekrar deneyin.')
    changed=copy.deepcopy(original)
    report=apply_motion(changed,track_ids,settings) if apply else {'applied':[], 'skipped':[]}
    if not apply and (source/'kurgu_hareket_raporu.json').is_file():
        report=json.loads((source/'kurgu_hareket_raporu.json').read_text(encoding='utf-8-sig'))
    if apply and not report['applied']:
        raise ValueError('Hareket eklenebilecek fotograf yok. Mevcut animasyonlar ve ozel kadrajlar korunur.')
    if not draft_root.is_dir():raise ValueError('CapCut taslak ana klasoru bulunamadi.')
    name='Hareketli '+source.name[:65]+' '+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:5]
    dest=draft_root/name
    if source==draft_root or source in draft_root.parents:raise ValueError('Hedef, kaynak klasorun icinde olamaz.')
    new_id=str(uuid.uuid4()).upper()
    replacements={original['id']:new_id}
    if meta.get('draft_id'):replacements[meta['draft_id']]=str(uuid.uuid4()).upper()
    old_paths=[str(source).replace('\\','/'),str(meta.get('draft_fold_path','')).replace('\\','/')]
    path_pairs=[(p,str(dest).replace('\\','/')) for p in old_paths if p]
    # In timeline-folder paths, replace just the known timeline directory as well.
    def rewrite(obj):
        obj=rewrite_values(obj,replacements,path_pairs)
        def fix(v):
            if isinstance(v,dict):return {k:fix(x) for k,x in v.items()}
            if isinstance(v,list):return [fix(x) for x in v]
            if isinstance(v,str):return v.replace('/Timelines/'+original['id']+'/', '/Timelines/'+new_id+'/')
            return v
        return fix(obj)
    try:
        shutil.copytree(source,dest,ignore=shutil.ignore_patterns('*.bak','*.tmp','kurgu_hareket_raporu.json'))
        for f in dest.rglob('*.json'):
            try:obj=json.loads(f.read_text(encoding='utf-8-sig'))
            except (ValueError,UnicodeError):continue
            write_json(f,rewrite(obj))
        old_dir=dest/'Timelines'/original['id']
        if old_dir.is_dir():old_dir.rename(dest/'Timelines'/new_id)
        changed=rewrite(changed)
        write_json(dest/'draft_content.json',changed)
        if timeline:write_json(dest/'Timelines'/new_id/'draft_content.json',changed)
        meta=rewrite(meta)
        meta.update(draft_name=name,draft_fold_path=str(dest).replace('\\','/'),
                    draft_root_path=str(draft_root).replace('\\','/'),
                    tm_draft_create=time.time_ns()//1000,tm_draft_modified=time.time_ns()//1000)
        write_json(dest/'draft_meta_info.json',meta)
        write_json(dest/'kurgu_hareket_raporu.json',report)
    except Exception:
        if dest.is_dir():shutil.rmtree(dest)
        raise
    return dest,report
