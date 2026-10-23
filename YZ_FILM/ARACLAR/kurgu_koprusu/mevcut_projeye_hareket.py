"""Select an existing local draft; write motion to a separate sibling draft."""
import os
import sys
import traceback
from pathlib import Path
from hareket import read_content,clone_project
from hareket_arayuz import choose_options

def main():
    import tkinter as tk
    from tkinter import filedialog,messagebox
    root=tk.Tk();root.withdraw();root.attributes('-topmost',True)
    default=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData'/'Local')))/'CapCut'/'User Data'/'Projects'/'com.lveditor.draft'
    try:
        if not messagebox.askokcancel('Kurgu Koprusu V5','CapCut kapali olmali. Orijinal proje korunacak; hareketli yeni bir kopya olusturulacak.',parent=root):return
        selected=filedialog.askdirectory(title='Projenin klasorunu sec (icinde draft_content.json olmali)',initialdir=str(default),parent=root)
    finally:root.destroy()
    if not selected:return
    source=Path(selected)
    content=read_content(source/'draft_content.json')
    settings=choose_options(content=content)
    if settings is None:return
    track_ids=settings.pop('track_ids')
    # Choose root explicitly: works with custom CapCut storage locations, avoids accidental parent imports.
    root=tk.Tk();root.withdraw();root.attributes('-topmost',True)
    try:dest=filedialog.askdirectory(title='CapCut taslak ANA klasorunu sec (com.lveditor.draft)',initialdir=str(default),parent=root)
    finally:root.destroy()
    if not dest:return
    target,report=clone_project(source,Path(dest),track_ids,settings)
    text=f"Yeni proje: {target.name}\nHareket eklendi: {len(report['applied'])}\nKorunan/atlanan: {len(report['skipped'])}\n\nCapCut'i acip yeni projeyi kontrol edin."
    print(text,flush=True)
    root=tk.Tk();root.withdraw()
    messagebox.showinfo('Tamam',text,parent=root);root.destroy()

if __name__=='__main__':
    try:main()
    except Exception:
        msg=traceback.format_exc();print(msg)
        Path(__file__).with_name('hareket_hata.txt').write_text(msg,encoding='utf-8')
        sys.exit(1)
