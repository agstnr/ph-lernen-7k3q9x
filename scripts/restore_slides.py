"""Restore page images from SHA-256 verified local originals; no Drive credentials in the repo."""
import concurrent.futures, hashlib, json, sys
from pathlib import Path
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def restore(item):
 v=item['value']; unit=v['einheit']; src=Path(v['download']['path'])
 target=ROOT/'data/einheit'/f'{unit}.json'; data=json.loads(target.read_text()); meta=data['eintrag']
 assert hashlib.sha256(src.read_bytes()).hexdigest()==meta['sha256'], unit
 doc=fitz.open(src);assert len(doc)==len(data['seiten']),unit
 dest=ROOT/'daten/bilder'/unit;dest.mkdir(parents=True,exist_ok=True)
 for page,s in zip(doc,data['seiten']):
  pix=page.get_pixmap(matrix=fitz.Matrix(1400/page.rect.width,1400/page.rect.width),alpha=False)
  Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(dest/f"{s['nr']}.webp",quality=82)
  s['bild']=f"/ph-lernen-7k3q9x/daten/bilder/{unit}/{s['nr']}.webp"
 target.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
 return len(doc)
if __name__=='__main__':
 items=json.loads(Path(sys.argv[1]).read_text());assert all(x['status']=='fulfilled' for x in items)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: print('Restored pages:',sum(pool.map(restore,items)))
