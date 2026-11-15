import json, pathlib, unittest
R=pathlib.Path(__file__).resolve().parents[1]
class Data(unittest.TestCase):
 def test_choices_and_sources(self):
  questions=json.loads((R/'data/fragen.json').read_text())['fragen'];ids=set();units={}
  for q in questions:
   self.assertNotIn(q['id'],ids);ids.add(q['id']);self.assertEqual(q['typ'],'auswahl')
   self.assertGreaterEqual(len(q['optionen']),2);self.assertEqual(len({o['text'] for o in q['optionen']}),len(q['optionen']))
   n=sum(o['richtig'] for o in q['optionen']);self.assertGreater(n,0);self.assertLess(n,len(q['optionen']))
   self.assertEqual(q['modus'],'multiple' if n>1 else 'single')
   for b in q['belege']:
    units.setdefault(b['einheit'],json.loads((R/'data/einheit'/f"{b['einheit']}.json").read_text()))
    pages={p['nr'] for p in units[b['einheit']]['seiten']}
    for nr in b['seiten']:self.assertIn(nr,pages)
   if q.get('herkunft')=='folien-luecke':
    self.assertEqual(q['status'],'ki-entwurf');self.assertIn(next(o['text'] for o in q['optionen'] if o['richtig']),q['quelltext'])
 def test_images(self):
  for f in (R/'data/einheit').glob('*.json'):
   d=json.loads(f.read_text())
   for p in d['seiten']:
    if d['eintrag']['typ']=='pdf':self.assertTrue(p['bild'])
    if p['bild']:self.assertTrue((R/p['bild'].removeprefix('/ph-lernen-7k3q9x/')).is_file())
if __name__=='__main__':unittest.main()
