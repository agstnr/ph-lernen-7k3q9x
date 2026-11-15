import json,pathlib,re,unittest
R=pathlib.Path(__file__).resolve().parents[1]
def load(path):return json.loads((R/path).read_text())
class Data(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.questions=load('data/fragen.json')['fragen'];cls.units={f.stem:json.loads(f.read_text()) for f in (R/'data/einheit').glob('*.json')}
  cls.graphics={g['src']:g for g in load('data/grafiken.json')['grafiken']}
 def test_only_choice_and_valid_answers(self):
  ids=set()
  for q in self.questions:
   self.assertNotIn(q['id'],ids);ids.add(q['id']);self.assertEqual(q['typ'],'auswahl');self.assertNotEqual(q.get('herkunft'),'folien-luecke')
   self.assertNotRegex(q['frage'],r'Welcher Begriff ergänzt|\[\s*[.…]+\s*\]');self.assertGreaterEqual(len(q['optionen']),3)
   self.assertEqual(len({o['text'] for o in q['optionen']}),len(q['optionen']))
   n=sum(o['richtig'] for o in q['optionen']);self.assertGreater(n,0);self.assertLess(n,len(q['optionen']));self.assertEqual(q['modus'],'multiple' if n>1 else 'single')
 def test_sources(self):
  for q in self.questions:
   for b in q['belege']:
    pages={p['nr'] for p in self.units[b['einheit']]['seiten']}
    for nr in b['seiten']:self.assertIn(nr,pages)
 def test_all_learning_pages_and_462_additions(self):
  covered={(b['einheit'],nr) for q in self.questions for b in q['belege'] for nr in b['seiten']}
  pages={(u,p['nr']) for u,d in self.units.items() if d['eintrag']['rolle'] in ('lerninhalt','quelle') for p in d['seiten']}
  self.assertEqual(len(pages),1824);self.assertFalse(pages-covered)
  missing=load('data/redaktion/seitenauswahl.json');editorial=[q for q in self.questions if q.get('herkunft')=='seiten-redaktion']
  self.assertEqual(len(editorial),462);self.assertEqual({q['redaktions_index'] for q in editorial},set(range(462)))
  for q in editorial:
   p=missing[q['redaktions_index']];self.assertEqual(q['einheit'],p['einheit']);self.assertEqual(q['belege'][0]['seiten'][0],p['seite'])
 def test_only_approved_cropped_question_graphics(self):
  for q in self.questions:
   sources={(b['einheit'],nr) for b in q['belege'] for nr in b['seiten']}
   for g in q['grafiken']:
    self.assertIn(g['src'],self.graphics);self.assertIn((g['einheit'],g['seite']),sources);self.assertIn('/daten/grafiken/',g['src']);self.assertNotIn('/daten/bilder/',g['src'])
  for g in self.graphics.values():
   self.assertTrue(g['geprueft']);self.assertTrue((R/g['src'].removeprefix('/ph-lernen-7k3q9x/')).is_file())
   x0,y0,x1,y1=g['ausschnitt'];self.assertTrue(0<=x0<x1<=1 and 0<=y0<y1<=1);self.assertLess((x1-x0)*(y1-y0),.9)
 def test_original_source_images_remain_available(self):
  for d in self.units.values():
   for p in d['seiten']:
    if d['eintrag']['typ']=='pdf':self.assertTrue(p['bild'])
    if p['bild']:self.assertTrue((R/p['bild'].removeprefix('/ph-lernen-7k3q9x/')).is_file())
 def test_false_bank_never_marked_correct(self):
  false={s for statements in load('data/redaktion/fehlaussagen.json').values() for s in statements}
  for q in self.questions:
   for o in q['optionen']:
    if o['text'] in false:self.assertFalse(o['richtig'])
if __name__=='__main__':unittest.main()
