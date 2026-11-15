"""Render only editorially selected graphic rectangles from verified local PDFs.
Usage: python scripts/extract_graphics.py /path/to/download-manifest.json
The manifest has the same structure used by restore_slides.py.
"""
import hashlib,json,sys
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main(path):
 downloads={x['value']['einheit']:Path(x['value']['download']['path']) for x in json.loads(Path(path).read_text()) if x['status']=='fulfilled'}
 config=json.loads((ROOT/'data/redaktion/grafik-ausschnitte.json').read_text());verified=set()
 for g in config['grafiken']:
  unit=g['einheit'];src=downloads[unit]
  if unit not in verified:
   meta=json.loads((ROOT/'data/einheit'/f'{unit}.json').read_text())['eintrag'];assert hashlib.sha256(src.read_bytes()).hexdigest()==meta['sha256'];verified.add(unit)
  with fitz.open(src) as doc:
   page=doc[g['seite']-1];x0,y0,x1,y1=g['ausschnitt'];assert 0<=x0<x1<=1 and 0<=y0<y1<=1
   r=fitz.Rect(x0*page.rect.width,y0*page.rect.height,x1*page.rect.width,y1*page.rect.height)
   pix=page.get_pixmap(clip=r,matrix=fitz.Matrix(1800/r.width,1800/r.width),alpha=False)
   dest=ROOT/g['src'].removeprefix('/ph-lernen-7k3q9x/');dest.parent.mkdir(parents=True,exist_ok=True)
   Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(dest,quality=85)
 (ROOT/'data/grafiken.json').write_text(json.dumps(config,ensure_ascii=False,separators=(',',':'))+'\n')
if __name__=='__main__':main(sys.argv[1])
