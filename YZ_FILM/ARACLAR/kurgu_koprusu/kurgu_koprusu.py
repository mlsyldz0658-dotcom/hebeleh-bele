# -*- coding: utf-8 -*-
"""Kurgu Koprusu V5: JSON plan secimi, pyCapCut 0.0.3."""
from datetime import datetime
from pathlib import Path
from decimal import Decimal, InvalidOperation
import json
import io
import os
import re
import sys
import time
import traceback
import uuid
SEC = 1_000_000

def load_audio(cc, filename):
    try:
        return cc.AudioMaterial(filename)
    except TypeError:
        from decimal import Decimal
        from pymediainfo import MediaInfo
        info = MediaInfo.parse(filename)
        if info.video_tracks or not info.audio_tracks:
            raise ValueError("Yorum dosyasi yalnizca ses icermeli.")
        duration_ms = info.audio_tracks[0].duration
        if duration_ms is None and info.general_tracks:
            duration_ms = info.general_tracks[0].duration
        if duration_ms is None:
            raise ValueError("Ses kaydinin suresi okunamadi.")
        duration = Decimal(str(duration_ms)) * 1000
        if not duration.is_finite() or duration <= 0:
            raise ValueError("Gecersiz ses suresi.")
        material = cc.AudioMaterial.__new__(cc.AudioMaterial)
        material.material_name = Path(filename).name
        material.material_id = uuid.uuid4().hex
        material.path = str(Path(filename).resolve())
        material.duration = int(duration)
        return material


def load_video(cc, filename):
    try:
        return cc.VideoMaterial(filename)
    except TypeError:
        # 0.0.3 multiplies MediaInfo's duration by a float without converting it.
        # Some containers return a numeric string (or omit video duration).
        from decimal import Decimal
        from pymediainfo import MediaInfo
        info = MediaInfo.parse(filename, mediainfo_options={"File_TestContinuousFileNames": "0"})
        if not info.video_tracks:
            raise ValueError("Dosyada video akisi bulunamadi.")
        video = info.video_tracks[0]
        duration_ms = video.duration
        if duration_ms is None and info.general_tracks:
            duration_ms = info.general_tracks[0].duration
        if duration_ms is None:
            raise ValueError("Video suresi okunamadi; dosyayi donusturmek gerekebilir.")
        duration = Decimal(str(duration_ms)) * 1000
        if not duration.is_finite() or duration <= 0:
            raise ValueError("Gecersiz video suresi.")
        # Same fields initialized by the inspected 0.0.3 constructor.
        material = cc.VideoMaterial.__new__(cc.VideoMaterial)
        material.material_name = Path(filename).name
        material.material_id = uuid.uuid4().hex
        material.local_material_id = ""
        material.path = str(Path(filename).resolve())
        material.crop_settings = cc.CropSettings()
        material.material_type = "video"
        material.duration = int(duration)
        material.width = int(video.width)
        material.height = int(video.height)
        return material


def complete_metadata(draft_path, name, duration):
    """Populate local media registry; adapted from pyCapCut issue #13.

    That workaround was reported for 9.1.0 macOS, not verified for 9.5.0.
    This only changes metadata inside the newly generated draft.
    """
    content = json.loads((draft_path / "draft_content.json").read_text(encoding="utf-8"))
    meta_path = draft_path / "draft_meta_info.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    now = time.time_ns() // 1000
    meta.update({
        "draft_id": content.get("id") or str(uuid.uuid4()).upper(),
        "draft_name": name,
        "draft_fold_path": str(draft_path),
        "draft_root_path": str(draft_path.parent),
        "tm_duration": duration,
        "tm_draft_create": now,
        "tm_draft_modified": now,
    })
    entries = []
    media = [(m, "photo" if m.get("type") == "photo" else "video") for m in content["materials"]["videos"]]
    media += [(m, "music") for m in content["materials"].get("audios", [])]
    for material, kind in media:
        entries.append({
            "ai_group_type": "", "create_time": -1,
            "duration": material["duration"], "enter_from": 0,
            "extra_info": material.get("material_name") or material.get("name", ""), "file_Path": material["path"],
            "height": material.get("height", 0), "width": material.get("width", 0),
            "id": material["id"], "import_time": -1, "import_time_ms": -1,
            "item_source": 1, "material_color_tag": "", "md5": "",
            "metetype": kind, "type": 0,
            "roughcut_time_range": {"duration": -1, "start": -1},
            "sub_time_range": {"duration": -1, "start": -1},
        })
    groups = meta.setdefault("draft_materials", [])
    group = next((g for g in groups if g.get("type") == 0), None)
    if group is None:
        group = {"type": 0, "value": []}
        groups.append(group)
    group["value"] = entries
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def exact_keys(obj, required, optional=()):
    if not isinstance(obj, dict):
        raise ValueError('Plan ve kesim kayitlari JSON nesnesi olmali.')
    missing = set(required) - obj.keys()
    extra = obj.keys() - set(required) - set(optional)
    if missing or extra:
        raise ValueError(f'Eksik alanlar: {sorted(missing)}; taninmayan alanlar: {sorted(extra)}')


def micros(value):
    if isinstance(value, bool):
        raise ValueError('Zaman true/false olamaz.')
    try:
        if isinstance(value, str) and ':' in value:
            if not re.fullmatch(r'\d{2,}:\d{2}:\d{2}(?:\.\d{1,6})?', value):
                raise ValueError('Zaman HH:MM:SS veya HH:MM:SS.fff olmali.')
            h, m, s = map(Decimal, value.split(':'))
            if m >= 60 or s >= 60:
                raise ValueError('Dakika ve saniye 60 altinda olmali.')
            number = h * 3600 + m * 60 + s
        else:
            number = Decimal(str(value))
        if not number.is_finite() or number < 0 or number * SEC != (number * SEC).to_integral_value():
            raise ValueError('Zaman negatif olmamali ve en fazla 6 ondalik basamak icermeli.')
        return int(number * SEC)
    except (InvalidOperation, TypeError):
        raise ValueError(f'Gecersiz zaman: {value!r}') from None


def interval(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError('Aralik [baslangic, bitis] biciminde olmali.')
    start, end = map(micros, value)
    if start >= end:
        raise ValueError(f'Aralikta bitis baslangictan buyuk olmali: {value}')
    return start, end


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])


def validate_plan(plan, base):
    exact_keys(plan, ['surum', 'kurgu_adi', 'videolar', 'sesler', 'video_kesimleri',
                      'yorum_kesimleri', 'goruntu_bosluklari', 'ayarlar'], ['fotograflar', 'fotograf_kesimleri', 'haber_bantlari'])
    if type(plan['surum']) is not int or plan['surum'] not in (1, 2, 3):
        raise ValueError('Desteklenen plan surumu: 1, 2 veya 3')
    name = plan['kurgu_adi']
    if not isinstance(name, str) or not name.strip() or len(name) > 60 or re.search(r'[<>:"/\\|?*\x00-\x1f]', name):
        raise ValueError('Kurgu adi 1-60 karakter olmali, dosya adinda yasak karakter icermemeli.')
    settings = plan['ayarlar']
    exact_keys(settings, ['genislik', 'yukseklik', 'fps', 'beklenen_sure'], ['anlatici_goruntusu_zorunlu', 'fotograf_hareketi', 'hareket_yuzdesi', 'kaydirma_yuzdesi'])
    from hareket import options
    options(settings)
    if type(settings.get('anlatici_goruntusu_zorunlu', False)) is not bool:
        raise ValueError('anlatici_goruntusu_zorunlu true veya false olmali.')
    for key, maximum in [('genislik', 7680), ('yukseklik', 7680), ('fps', 120)]:
        if type(settings[key]) is not int or not 1 <= settings[key] <= maximum:
            raise ValueError(f'Gecersiz {key}')
    expected = micros(settings['beklenen_sure'])
    sources = {}
    for kind in ['videolar', 'sesler', 'fotograflar']:
        if not isinstance(plan.get(kind, {}), dict):
            raise ValueError(f'{kind} kimlik: dosya_yolu eslestirmesi olmali.')
        sources[kind] = {}
        for alias, filename in plan.get(kind, {}).items():
            if not alias or not isinstance(filename, str) or not filename.strip():
                raise ValueError('Kaynak kimligi ve dosya yolu bos olamaz.')
            path = Path(os.path.expandvars(filename)).expanduser()
            path = path if path.is_absolute() else base / path
            if not path.is_file():
                raise FileNotFoundError(f'{alias} bulunamadi: {path}')
            sources[kind][alias] = str(path.resolve())
    cuts = {'video': [], 'yorum': [], 'fotograf': []}
    for kind, key, source_key in [('video', 'video_kesimleri', 'videolar'), ('yorum', 'yorum_kesimleri', 'sesler')]:
        if not isinstance(plan[key], list):
            raise ValueError(f'{key} liste olmali.')
        for item in plan[key]:
            required = ['dosya', 'kaynak', 'cizelge'] + (['orijinal_ses'] if kind == 'video' else [])
            exact_keys(item, required)
            if not isinstance(item['dosya'], str) or item['dosya'] not in sources[source_key]:
                raise ValueError(f'Tanimsiz kaynak: {item["dosya"]}')
            source, target = interval(item['kaynak']), interval(item['cizelge'])
            if source[1] - source[0] != target[1] - target[0]:
                raise ValueError(f'{item["dosya"]}: kaynak ve cizelge sureleri esit olmali; hiz 1x.')
            if kind == 'video' and type(item['orijinal_ses']) is not bool:
                raise ValueError('orijinal_ses true veya false olmali.')
            cuts[kind].append(dict(path=sources[source_key][item['dosya']], source=source, target=target,
                                   volume=1.0 if item.get('orijinal_ses', True) else 0.0))
        cuts[kind].sort(key=lambda c: c['target'][0])
        for a, b in zip(cuts[kind], cuts[kind][1:]):
            if overlaps(a['target'], b['target']):
                raise ValueError(f'{kind} kanalinda kesimler ust uste geliyor.')
    if not isinstance(plan.get('fotograf_kesimleri', []), list):
        raise ValueError('fotograf_kesimleri liste olmali.')
    for item in plan.get('fotograf_kesimleri', []):
        exact_keys(item, ['dosya', 'cizelge'], ['hareket'])
        from hareket import MODES
        if item.get('hareket', 'otomatik') not in MODES:
            raise ValueError('Gecersiz fotograf hareketi')
        if not isinstance(item['dosya'], str) or item['dosya'] not in sources['fotograflar']:
            raise ValueError('Tanimsiz fotograf: ' + str(item['dosya']))
        target = interval(item['cizelge'])
        cuts['fotograf'].append(dict(path=sources['fotograflar'][item['dosya']],
            source=(0, target[1]-target[0]), target=target, volume=0.0, hareket=item.get('hareket', settings.get('fotograf_hareketi','otomatik'))))
    visuals = sorted(cuts['video'] + cuts['fotograf'], key=lambda c: c['target'][0])
    for a, b in zip(visuals, visuals[1:]):
        if overlaps(a['target'], b['target']):
            raise ValueError('Video ve fotograf kesimleri ust uste geliyor.')
    if settings.get('anlatici_goruntusu_zorunlu', False):
        for audio in cuts['yorum']:
            cursor=audio['target'][0]
            for visual in visuals:
                a,b=visual['target']
                if b<=cursor:continue
                if a>cursor:break
                cursor=max(cursor,b)
                if cursor>=audio['target'][1]:break
            if cursor<audio['target'][1]:
                raise ValueError('Anlatici araliginda goruntu eksik: '+str(audio['target']))
    all_cuts = visuals + cuts['yorum']
    if not all_cuts or expected <= 0 or max(c['target'][1] for c in all_cuts) > expected:
        raise ValueError('Kesim bitisi beklenen sureyi asiyor veya plan bos.')
    for v in cuts['video']:
        for a in cuts['yorum']:
            if v['volume'] and overlaps(v['target'], a['target']):
                raise ValueError('Yorum ile orijinal video sesi ust uste geliyor. Plani duzeltin veya video sesini acikca false yapin.')
    if not isinstance(plan['goruntu_bosluklari'], list):
        raise ValueError('goruntu_bosluklari liste olmali.')
    gaps = sorted(interval(g) for g in plan['goruntu_bosluklari'])
    for gap in gaps:
        if gap[1] > expected or any(overlaps(gap, v['target']) for v in visuals):
            raise ValueError('Goruntu boslugu video ile cakisiyor veya toplam sureyi asiyor.')
    for a, b in zip(gaps, gaps[1:]):
        if overlaps(a, b):
            raise ValueError('Goruntu bosluklari birbiriyle cakisiyor.')
    last_end = max(c['target'][1] for c in all_cuts)
    if last_end < expected and not any(g[0] <= last_end and g[1] == expected for g in gaps):
        raise ValueError('Sondaki bos sure goruntu_bosluklari icinde belirtilmeli.')
    bands=plan.get('haber_bantlari', [])
    if not isinstance(bands, list):raise ValueError('haber_bantlari liste olmali.')
    band_ranges=[]
    for item in bands:
        exact_keys(item, ['metin', 'cizelge'], ['etiket'])
        if not isinstance(item['metin'],str) or not item['metin'].strip() or len(item['metin'])>240:
            raise ValueError('Haber basligi 1-240 karakter olmali.')
        if not isinstance(item.get('etiket',''),str) or len(item.get('etiket',''))>40:
            raise ValueError('Etiket en fazla 40 karakter olmali.')
        span=interval(item['cizelge'])
        if span[1]>expected:raise ValueError('Haber bandi toplam sureyi asiyor.')
        if any(overlaps(span,other) for other in band_ranges):raise ValueError('Haber bantlari ust uste geliyor.')
        band_ranges.append(span)
    return cuts, gaps, expected


def build_project(cc, plan, base, draft_root):
    cuts, gaps, expected = validate_plan(plan, base)
    if not draft_root.is_dir():
        raise FileNotFoundError(f'CapCut proje klasoru bulunamadi: {draft_root}')
    prepared = {'video': [], 'yorum': [], 'fotograf': []}
    cache = {}
    # Load and validate every source and construct segments BEFORE creating a draft.
    for kind in prepared:
        for cut in cuts[kind]:
            key = kind, cut['path']
            if key not in cache:
                print('Kaynak kontrol ediliyor:', cut['path'], flush=True)
                cache[key] = (load_audio if kind == 'yorum' else load_video)(cc, cut['path'])
            material = cache[key]
            if kind == 'video' and material.material_type != 'video':
                raise ValueError(f'Video akisi bulunamadi: {cut["path"]}')
            if kind == 'fotograf' and material.material_type != 'photo':
                raise ValueError(f'Fotograf dosyasi bekleniyor: {cut["path"]}')
            if cut['source'][1] > material.duration:
                raise ValueError(f'Kaynak suresi yetersiz: {cut["path"]}. Istenen bitis {cut["source"][1]/SEC:g} sn; dosya {material.duration/SEC:g} sn. Otomatik kisaltilmadi.')
            length = cut['source'][1] - cut['source'][0]
            ctor = cc.AudioSegment if kind == 'yorum' else cc.VideoSegment
            prepared[kind].append(ctor(material, cc.Timerange(cut['target'][0], length),
                source_timerange=cc.Timerange(cut['source'][0], length), speed=1.0, volume=cut['volume']))
    # A transparent still preserves an explicitly reserved trailing blank region.
    last_end = max(c['target'][1] for group in cuts.values() for c in group)
    if last_end < expected:
        blank = load_video(cc, str(Path(__file__).with_name('BOS_ALAN.png')))
        prepared['fotograf'].append(cc.VideoSegment(blank, cc.Timerange(last_end, expected-last_end), volume=0.0))
    # Measure/render all titles before creating the new draft.
    from haber_bandi import render_band
    rendered=[]
    for item in plan.get('haber_bantlari', []):
        image=render_band(' '.join(item['metin'].split()), ' '.join(item.get('etiket','').split()),
            plan['ayarlar']['genislik'], plan['ayarlar']['yukseklik'])
        buf=io.BytesIO();image.save(buf,format='PNG');image.close()
        rendered.append((buf.getvalue(), interval(item['cizelge'])))
    name = 'Kurgu Koprusu ' + plan['kurgu_adi'].strip().rstrip('.') + ' ' + datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
    settings = plan['ayarlar']
    draft = cc.DraftFolder(str(draft_root)).create_draft(name, settings['genislik'], settings['yukseklik'], fps=settings['fps'], allow_replace=False)
    for kind, track, track_type in [('video', 'Videolar', cc.TrackType.video), ('yorum', 'Yorum', cc.TrackType.audio), ('fotograf', 'Fotograflar', cc.TrackType.video)]:
        if prepared[kind]:
            draft.add_track(track_type, track)
            for segment in prepared[kind]:
                draft.add_segment(segment, track)
    if rendered:
        assets=draft_root/name/'haber_bantlari';assets.mkdir()
        draft.add_track(cc.TrackType.video, 'Haber Bantlari', relative_index=10)
        for i,(image,(start,end)) in enumerate(rendered,1):
            path=assets/f'bant_{i:03d}.png';path.write_bytes(image)
            material=load_video(cc,str(path))
            draft.add_segment(cc.VideoSegment(material,cc.Timerange(start,end-start),volume=0.0),'Haber Bantlari')
    draft.content.setdefault('config', {})['maintrack_adsorb'] = False
    draft.save()
    target = draft_root / name
    content = json.loads((target / 'draft_content.json').read_text(encoding='utf-8'))
    if content['config']['maintrack_adsorb'] is not False:
        raise RuntimeError('Ana parca miknatis ayari kaydedilemedi.')
    if content.get('duration') != expected:
        raise RuntimeError(f'Kaydedilen proje suresi beklenenden farkli. Olusan proje: {target}')
    from hareket import apply_motion, write_json
    tracks = [t['id'] for t in content['tracks'] if t.get('name') == 'Fotograflar']
    overrides = {seg.segment_id: cut['hareket'] for seg,cut in zip(prepared['fotograf'],cuts['fotograf'])}
    motion_report = apply_motion(content, tracks, settings, overrides)
    write_json(target/'draft_content.json', content)
    write_json(target/'kurgu_hareket_raporu.json', motion_report)
    print('Hareket eklendi:', len(motion_report['applied']), '| Korunan/atlanan:', len(motion_report['skipped']))
    complete_metadata(target, name, expected)
    (target / 'kurgu_plani.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\nPROJE OLUSTURULDU: {name}\nToplam: {expected/SEC:g} saniye. Ana parca miknatisi KAPALI.')
    print('CapCut icinde acip zamanlari ve sesleri kontrol edin; kapatip yeniden acarak bosluklarin korundugunu kontrol edin.')
    return target


def main():
    if len(sys.argv) > 2:
        raise ValueError('Tek bir JSON plan dosyasi secin.')
    if len(sys.argv) == 2:
        selected = sys.argv[1]
    else:
        import tkinter as tk
        from tkinter import filedialog
        window = tk.Tk(); window.withdraw(); window.attributes('-topmost', True)
        try:
            selected = filedialog.askopenfilename(parent=window, title='Kurgu Koprusu - plan sec', filetypes=[('Kurgu plani', '*.json')])
        finally:
            window.destroy()
    if not selected:
        print('Plan secilmedi.'); return
    path = Path(selected).resolve()
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'JSON icinde tekrar eden alan: {key}')
            result[key] = value
        return result
    plan = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=no_duplicates)
    from hareket_arayuz import choose_options
    chosen = choose_options(plan['ayarlar'])
    if chosen is None:
        print('Islem iptal edildi.'); return
    plan['ayarlar'].update(chosen)
    import pycapcut as cc
    draft_root = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local'))) / 'CapCut' / 'User Data' / 'Projects' / 'com.lveditor.draft'
    build_project(cc, plan, path.parent, draft_root)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='replace'); sys.stderr.reconfigure(errors='replace')
    try:
        main()
    except Exception:
        details = traceback.format_exc()
        print('\nHATA: Islem tamamlanamadi.\n' + details)
        try:
            Path(__file__).with_name('kurgu_koprusu_hata.txt').write_text(details, encoding='utf-8')
        except OSError:
            pass
        sys.exit(1)
