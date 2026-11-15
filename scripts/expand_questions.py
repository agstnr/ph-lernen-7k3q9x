"""Reproducible, source-exact cloze questions. Does NOT certify semantic/visual coverage."""
import collections, hashlib, json, random, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WORD=re.compile(r'[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß-]{4,}')
STOP=set('dieser diese dieses einer eines einem einen durch unter sowie wurde werden welche welcher welches nicht einer keine können their these those there where which about other using between public health medizinische universität zentrum grundlagen statistik seite folien abteilung vorlesung'.split())
def norm(s):return re.sub(r'\s+',' ',s).strip()
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
def chunks(page, repeated):
 lines=[]
 for line in page['text'].splitlines():
  line=norm(line)
  if re.search(r'https?://|www\.|doi\.org|\S+@\S+',line):continue
  if not line or re.fullmatch(r'[\d\s./|–-]+',line) or line in repeated:continue
  lines.append(line)
 text='\n'.join(lines)
 # Respect bullet boundaries, then sentences; retain continuations rather than isolated wrapped lines.
 blocks=re.split(r'\n(?=[•●▪►➢\uf0a7]|[–-] |\d+[.)] )|(?<=[.!?])\s+(?=[A-ZÄÖÜ])',text)
 out=[]
 for block in blocks:
  block=norm(re.sub(r'^[•●▪►➢\uf0a7–-]\s*','',block))
  if len(block)<50:continue
  if len(block)<100 and re.search(r'©|copyright|all rights reserved',block,re.I):continue
  words=block.split(); parts=[]; part=[]
  for word in words:
   if sum(map(len,part))+len(part)+len(word)>500 and part:parts.append(' '.join(part));part=[]
   part.append(word)
  if part:parts.append(' '.join(part))
  out.extend(parts)
 return out

def main():
 data=json.loads((ROOT/'data/fragen.json').read_text());qs=[q for q in data['fragen'] if q.get('herkunft')!='folien-luecke']; originals=[dict(q, typ='karte', antwort=q.get('antwort', q.get('antwort_original'))) for q in qs if q.get('antwort') or q.get('antwort_original')]
 # Conversion retains stable IDs and original answers; changes are no longer marked as reviewed.
 for q in qs:
  if q['typ']!='karte':continue
  answer=q.pop('antwort');q['antwort_original']=answer;q['typ']='auswahl';q['modus']='single';q['status']='ki-entwurf';q.pop('freigabe',None)
  candidates=[x['antwort'] for x in originals if x['typ']=='karte' and x['id']!=q['id'] and x['einheit'].split('--')[1]==q['einheit'].split('--')[1] and x['antwort']!=answer]
  candidates=list(dict.fromkeys(candidates));random.Random(q['id']).shuffle(candidates)
  assert len(candidates)>=3,q['id']
  q['optionen']=[{'text':answer,'richtig':True,'erklaerung':'Antwort aus der bisherigen Lernkarte.'}]+[{'text':a,'richtig':False,'erklaerung':'Diese Antwort gehört zu einer anderen Frage; siehe Seitenbeleg für die gesuchte Antwort.'} for a in candidates[:3]]
  q['konvertiert_aus']='karte'
 report={'hinweis':'Textstellen-Abdeckung ist keine Bestätigung, dass alle Aussagen und Grafiken fachlich abgefragt sind. Neue Fragen sind automatisch erzeugte Entwürfe.','einheiten':[]}
 for file in sorted((ROOT/'data/einheit').glob('*.json')):
  d=json.loads(file.read_text());meta=d['eintrag'];unit=meta['id']
  if meta['rolle'] not in ('lerninhalt','quelle'):continue
  counts=collections.Counter(norm(l) for p in d['seiten'] for l in set(p['text'].splitlines()))
  repeated={l for l,n in counts.items() if n>=max(3,len(d['seiten'])//4) and len(l)<100}
  vocabulary=sorted(set(w for p in d['seiten'] for w in WORD.findall(p['text']) if w.lower() not in STOP and not w.endswith('-')))
  entry={'einheit':unit,'seiten':len(d['seiten']),'fragen_neu':0,'seitendetails':[]}
  for p in d['seiten']:
   blocks=chunks(p,repeated);ids=[];offen=[]
   for j,block in enumerate(dict.fromkeys(blocks)):
    candidates=[w for w in WORD.findall(block) if w.lower() not in STOP and not w.endswith('-')]
    if not candidates:offen.append(block);continue
    rng=random.Random(unit+str(p['nr'])+str(j))
    # Prefer a technical noun over function words; deterministic source wording keeps the key auditable.
    nouns=[w for w in candidates if w[0].isupper() and len(w)>6 and w not in {'Rieder','Papantoniou','Fragner','Zlabinger','November','Oktober','Literatur','References','Quellen'}];key=rng.choice(nouns or candidates)
    wrong=[w for w in vocabulary if w.lower()!=key.lower() and w.lower() not in block.lower() and w[0].isupper()==key[0].isupper()]
    wrong.sort(key=lambda w:abs(len(w)-len(key)));pool=wrong[:80];rng.shuffle(pool)
    if len(pool)<3:offen.append(block);continue
    cloze=re.sub(r'(?<!\w)'+re.escape(key)+r'(?!\w)','[…] ',block).replace('  ',' ')
    qid=f"{unit}--text-{p['nr']}-{hashlib.sha256(block.encode()).hexdigest()[:10]}"
    qs.append({'id':qid,'typ':'auswahl','modus':'single','frage':'Welcher Begriff ergänzt den Folientext im Originalwortlaut?\n'+cloze,'optionen':[{'text':key,'richtig':True}]+[{'text':w,'richtig':False} for w in pool[:3]],'erklaerung':'Originalwortlaut: '+block,'quelltext':block,'konzepte':[],'belege':[{'einheit':unit,'seiten':[p['nr']]}],'einheit':unit,'herkunft':'folien-luecke','status':'ki-entwurf'})
    ids.append(qid)
   entry['fragen_neu']+=len(ids)
   entry['seitendetails'].append({'seite':p['nr'],'textfragen':len(ids),'bild_vorhanden':bool(p['bild']),'visuell_pruefen':bool(p['textarm']),'offene_textstellen':offen,'status':'textfragen-vorhanden' if ids else 'inhalt-pruefen'})
  report['einheiten'].append(entry)
 for q in qs:
  assert q['typ']=='auswahl'
  q['modus']='multiple' if sum(o['richtig'] for o in q['optionen'])>1 else 'single'
 assert len({q['id'] for q in qs})==len(qs)
 dump(ROOT/'data/fragen.json',{'fragen':qs});dump(ROOT/'data/abdeckung.json',report)
 print('Questions:',len(qs),'new:',sum(e['fragen_neu'] for e in report['einheiten']))
 print('Pages without generated text question:',sum(not p['textfragen'] for e in report['einheiten'] for p in e['seitendetails']))
if __name__=='__main__':main()
