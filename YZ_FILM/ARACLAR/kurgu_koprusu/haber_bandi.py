"""Render bounded lower-third cards with measured text; never clip or truncate."""
from pathlib import Path
import os

def _font(size):
    from PIL import ImageFont
    candidates = [Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'/'arialbd.ttf',
                  Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'/'segoeuib.ttf',
                  Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    raise ValueError('Haber bandi icin Arial Bold veya Segoe UI Bold fontu bulunamadi.')

def _fit(draw, text, width, height, maximum, minimum, max_lines):
    # Prefer the largest readable font; at most two balanced lines.
    words=text.split()
    variants=[text]
    if max_lines>1:
        variants += [' '.join(words[:i])+'\n'+' '.join(words[i:]) for i in range(1,len(words))]
    for size in range(maximum, minimum-1, -1):
        font=_font(size); spacing=max(2, size//5)
        fits=[]
        for value in variants:
            box=draw.multiline_textbbox((0,0), value, font=font, spacing=spacing)
            if box[2]-box[0]<=width and box[3]-box[1]<=height:
                fits.append((box[2]-box[0],value,box))
        if fits:
            _,value,box=min(fits)
            return value,font,spacing,box
    raise ValueError('Haber bandi metni alana sigmiyor. Basligi/etiketi kisaltin; metin kesilmedi.')

def render_band(text, label, width, height):
    from PIL import Image,ImageDraw
    if width<640 or height<360 or width/height<1.3:
        raise ValueError('Bu haber bandi yatay en az 640x360 projeler icindir.')
    im=Image.new('RGBA',(width,height),(0,0,0,0));d=ImageDraw.Draw(im)
    x=int(width*.05); right=width-x; bottom=int(height*.94)
    band_h=int(height*.14); top=bottom-band_h;pad=max(8,int(width*.018))
    d.rectangle((x,top,right,bottom),fill='white')
    d.rectangle((x,top,x+max(4,int(width*.005)),bottom),fill='#ce111d')
    value,font,spacing,box=_fit(d,text,right-x-2*pad,band_h-int(height*.035),int(height*.056),max(12,int(height*.027)),2)
    px=x+pad-box[0];py=top+(band_h-(box[3]-box[1]))//2-box[1]
    d.multiline_text((px,py),value,font=font,fill='#111111',spacing=spacing)
    if label:
        label_h=int(height*.05);lp=int(width*.012)
        value,font,spacing,box=_fit(d,label,int(width*.48)-2*lp,label_h-int(height*.012),int(height*.031),max(10,int(height*.022)),1)
        lw=box[2]-box[0]+2*lp
        d.rectangle((x,top-label_h,x+lw,top),fill='#ce111d')
        d.text((x+lp-box[0],top-label_h+(label_h-(box[3]-box[1]))//2-box[1]),value,font=font,fill='white')
    return im
