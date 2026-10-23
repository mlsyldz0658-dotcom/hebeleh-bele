"""Small Turkish Windows UI shared by both workflows."""
from hareket import MODES, options, photo_tracks
LABELS=('Otomatik sirayla', 'Hafif yakinlas', 'Hafif uzaklas', 'Sagdan yaklas', 'Soldan yaklas', 'Hareket kapali')

def choose_options(settings=None, content=None):
    import tkinter as tk
    from tkinter import ttk,messagebox
    settings=settings or {}
    root=tk.Tk();root.title('Kurgu Koprusu V5 - Fotograf hareketi');root.resizable(False,False)
    root.attributes('-topmost',True)
    pane=ttk.Frame(root,padding=18);pane.pack(fill='both',expand=True)
    ttk.Label(pane,text='Fotograflara hafif hareket',font=('Segoe UI',13,'bold')).pack(anchor='w',pady=5)
    ttk.Label(pane,text='Sesler, videolar ve haber bantlari sabit kalir.').pack(anchor='w')
    ttk.Label(pane,text='Hareket turu:').pack(anchor='w',pady=(12,2))
    combo=ttk.Combobox(pane,values=LABELS,state='readonly',width=40);combo.pack(fill='x')
    combo.current(MODES.index(settings.get('fotograf_hareketi','otomatik')))
    ttk.Label(pane,text='Zoom degisimi (%1-15, onerilen 8):').pack(anchor='w',pady=(10,2))
    zoom=tk.StringVar(value=str(settings.get('hareket_yuzdesi',8)));ttk.Entry(pane,textvariable=zoom).pack(fill='x')
    ttk.Label(pane,text='Yatay kayma (%0-3, onerilen 2):').pack(anchor='w',pady=(10,2))
    pan=tk.StringVar(value=str(settings.get('kaydirma_yuzdesi',2)));ttk.Entry(pane,textvariable=pan).pack(fill='x')
    tracks=photo_tracks(content) if content else []
    box=None
    if content:
        ttk.Label(pane,text='Hareket uygulanacak fotograf kanallari:').pack(anchor='w',pady=(12,2))
        box=tk.Listbox(pane,selectmode='multiple',exportselection=False,height=min(6,max(2,len(tracks))),width=62)
        box.pack(fill='x')
        defaults=[]
        for i,(t,n) in enumerate(tracks):
            box.insert('end',f"{t.get('name') or 'Isimsiz kanal'} - {n} fotograf")
            if t.get('name','').lower() in ('fotograflar','fotoğraflar'):defaults.append(i)
        # No automatic selection of an unknown overlay track.
        for i in defaults:box.selection_set(i)
        ttk.Label(pane,text='Mevcut animasyonlar/anahtar kareler ve ozel kadrajlar korunur.').pack(anchor='w',pady=8)
    result=[]
    def submit():
        try:
            out={'fotograf_hareketi':MODES[combo.current()],
                 'hareket_yuzdesi':float(zoom.get().replace(',','.')),
                 'kaydirma_yuzdesi':float(pan.get().replace(',','.'))}
            options(out)
            if box is not None:
                out['track_ids']=[tracks[int(i)][0]['id'] for i in box.curselection()]
                if not out['track_ids']:raise ValueError('En az bir fotograf kanali secin.')
            result.append(out);root.destroy()
        except ValueError as e:messagebox.showerror('Ayar',str(e),parent=root)
    ttk.Button(pane,text='Uygula',command=submit).pack(fill='x',pady=(12,4))
    ttk.Button(pane,text='Iptal',command=root.destroy).pack(fill='x')
    root.mainloop()
    return result[0] if result else None
