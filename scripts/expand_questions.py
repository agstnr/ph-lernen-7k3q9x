"""Build complete-statement choice questions and the editorial page/graphic additions. No cloze generation."""
import collections,hashlib,json,random,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def dump(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def words(s):return {w[:7] for w in re.findall(r'[a-zäöüß]{5,}',s.lower())}
def main():
 old=read('data/fragen.json')['fragen']
 qs=[q for q in old if q.get('herkunft') not in ('folien-luecke','folien-aussagen','seiten-redaktion')]
 sources={f.stem:json.loads(f.read_text()) for f in (ROOT/'data/einheit').glob('*.json')}
 bank=read('data/redaktion/fehlaussagen.json');blocks=read('data/redaktion/textbausteine.json')
 repeated={}
 for u,d in sources.items():
  counter=collections.Counter(line.strip() for p in d['seiten'] for line in set(p['text'].splitlines()) if 8<len(line.strip())<160)
  repeated[u]=[line for line,n in counter.items() if n>=max(5,len(d['seiten'])*.3)]
 def clean(u,t):
  for line in sorted(repeated[u],key=len,reverse=True): t=t.replace(line,' ')
  t=re.sub(r'\d*Wolfgang Dür, Theorie der Gesundheit und Gesundheitsförderung\.?\s*MPH Meduni Wien, November 2026',' ',t)
  t=re.sub(r'MPH Meduni Wien, November 2026',' ',t)
  t=re.sub(r'copyright by willy oggier.*?beratungen',' ',t,flags=re.I)
  t=re.sub(r'\s+',' ',t).strip(' •–-')
  return t
 def statement(t):
  if re.search(r'\b(ist|sind|wird|werden|kann|können|hat|haben|bedeutet|bezeichnet|führt|erfolgt|erhöht|senkt|beschreibt|is|are|has|have|can|was|were|means|requires|increases)\b',t,re.I):return t
  return 'Die Unterlage nennt: '+t.rstrip('.')+'.'
 pageblocks=collections.defaultdict(list)
 for b in blocks:pageblocks[(b['einheit'],b['seite'])].append(b['text'])
 graphics=read('data/grafiken.json')['grafiken'];gmap=collections.defaultdict(list)
 for g in graphics:gmap[(g['einheit'],g['seite'])].append({k:g[k] for k in ('src','alt','einheit','seite')})
 def attach(q,unit,nr):q['grafiken']=gmap.get((unit,nr),[])
 for q in qs:
  q['grafiken']=[]
  for b in q['belege']:
   for nr in b['seiten']:q['grafiken'].extend(gmap.get((b['einheit'],nr),[]))
  q['grafiken']=list({g['src']:g for g in q['grafiken']}.values())
 def base(unit,nr,qid,question,options,explanation,origin):
  q={'id':qid,'typ':'auswahl','modus':'multiple' if sum(o['richtig'] for o in options)>1 else 'single','frage':question,'optionen':options,'erklaerung':explanation,'konzepte':[],'belege':[{'einheit':unit,'seiten':[nr]}],'einheit':unit,'herkunft':origin,'status':'ki-entwurf'}
  attach(q,unit,nr);return q
 for b in blocks:
  unit,nr,text=b['einheit'],b['seite'],b['text'];course=unit.split('--')[1]
  seed=unit+str(nr)+text;rng=random.Random(seed)
  page=next(p for p in sources[unit]['seiten'] if p['nr']==nr)
  headings=[s.strip() for s in page['text'].splitlines() if 8<len(s.strip())<100 and not re.search(r'https?://|www\.|Department of|Universit|Zentrum für|Abteilung für|Grundlagen der Statistik|Anwendung statistischer|copyright',s,re.I)]
  headings=[h for h in headings if not re.search(r'2026|Dür, Theorie|Quelle:|Dr\.|Prof\.|Träger Wirkprinzip|Odds ratio\s*=',h)]
  heading=(headings[0] if headings else sources[unit]['eintrag']['kurs']).strip('• –-')
  heading=re.sub(r'^\d+\s*[·.)]?\s*','',heading)
  full=clean(unit,text)
  alternatives=[clean(unit,t) for t in pageblocks[(unit,nr)] if clean(unit,t)!=full and len(clean(unit,t))>50]
  if len(full)<50 and alternatives: full=full+': '+max(alternatives,key=len)
  if not full: full=text
  full=statement(full)
  correct=[full];peers=[statement(t) for t in alternatives if statement(t)!=full]
  if peers and rng.random()<.4:correct.append(rng.choice(peers))
  query=words(text);wrong=list(bank[course]);rng.shuffle(wrong);wrong.sort(key=lambda s:len(words(s)&query),reverse=True)
  wrong=[s for s in wrong if s not in correct][:4-len(correct)]
  options=[{'text':t,'richtig':True,'erklaerung':f'Inhalt der Unterlage, Seite {nr}.'} for t in correct]+[{'text':t,'richtig':False,'erklaerung':'Diese Aussage ist unzutreffend. Beachte die fachlichen Aussagen in der Auflösung und den Seitenbeleg.'} for t in wrong]
  singular=len(correct)==1
  stem=f'Welche Aussage zum Thema „{heading}“ ist laut Unterlage richtig?' if singular else f'Welche Aussagen zum Thema „{heading}“ treffen laut Unterlage zu?'
  qid=f"{unit}--inhalt-{nr}-{hashlib.sha256(text.encode()).hexdigest()[:10]}"
  q=base(unit,nr,qid,stem,options,'Richtige Einordnung nach der Unterlage: '+' / '.join(correct),'folien-aussagen');q['quelltexte']=correct;qs.append(q)
 missing=read('data/redaktion/seitenauswahl.json');indices=[]
 for line in (ROOT/'data/redaktion/offene-seiten.tsv').read_text().splitlines():
  idx,question,right,*wrong=line.split('|');idx=int(idx);indices.append(idx);p=missing[idx];unit,nr=p['einheit'],p['seite']
  options=[{'text':right,'richtig':True}]+[{'text':s,'richtig':False} for s in wrong]
  q=base(unit,nr,f'{unit}--seite-{nr}-redaktion',question,options,right,'seiten-redaktion');q['redaktions_index']=idx;qs.append(q)
 assert sorted(indices)==list(range(len(missing)))
 concepts=read('data/netz.json')['konzepte'];pageconcepts=collections.defaultdict(set)
 for c in concepts:
  for b in c.get('belege',[]):
   for nr in b['seiten']:pageconcepts[(b['einheit'],nr)].add(c['id'])
 for q in qs:
  if q.get('herkunft') not in ('folien-aussagen','seiten-redaktion'):continue
  text=q['frage']+' '+ ' '.join(o['text'] for o in q['optionen'] if o['richtig'])
  tags=set(pageconcepts[(q['einheit'],q['belege'][0]['seiten'][0])])
  for c in concepts:
   samecourse=any(b['einheit'].split('--')[1]==q['einheit'].split('--')[1] for b in c.get('belege',[]))
   if samecourse and any(len(name)>=4 and re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',text,re.I) for name in [c['name']]+c.get('synonyme',[])):tags.add(c['id'])
  q['konzepte']=sorted(tags)
 assert len(qs)==len({q['id'] for q in qs})
 covered=collections.Counter((b['einheit'],nr) for q in qs for b in q['belege'] for nr in b['seiten'])
 report={'hinweis':'Jede Lernseite ist mit Auswahlfragen verbunden. Seitenabdeckung ist kein Nachweis einer unabhängigen fachlichen Einzelprüfung jeder Aussage. Grafik-Ausschnitte sind explizit zugeordnet; Originalfolien werden in Fragen nicht automatisch gezeigt.','einheiten':[]}
 for unit,d in sorted(sources.items()):
  if d['eintrag']['rolle'] not in ('lerninhalt','quelle'):continue
  details=[{'seite':p['nr'],'fragen':covered[(unit,p['nr'])],'grafiken':len(gmap.get((unit,p['nr']),[])),'ergaenzt_aus_offenen_seiten':{'einheit':unit,'seite':p['nr']} in missing,'status':'fragen-vorhanden' if covered[(unit,p['nr'])] else 'offen'} for p in d['seiten']]
  report['einheiten'].append({'einheit':unit,'seiten':len(d['seiten']),'seitendetails':details})
 assert all(p['fragen'] for e in report['einheiten'] for p in e['seitendetails'])
 approval=read('data/redaktion/freigaben.json');approved=set(approval['fragen_ids'])
 for q in qs:
  if q['id'] in approved:q['status']='geprueft';q['freigabe']=approval['freigabe']
 dump('data/fragen.json',{'fragen':qs});dump('data/abdeckung.json',report)
 print('Questions',len(qs),collections.Counter(q['modus'] for q in qs),'editorial additions',len(indices),'graphics',len(graphics))
if __name__=='__main__':main()
