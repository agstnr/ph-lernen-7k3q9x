# PH Lernen

Statische Lernanwendung für GitHub Pages.

## Auswahlfragen

Der Bestand enthält 2.764 vollständige Auswahlfragen: 2.369 Single-Choice- und 395 Multiple-Choice-Fragen. Es gibt keine Lückentextaufgaben. Multiple Choice verlangt die vollständige richtige Antwortmenge; fehlende oder zusätzliche Antworten werden nicht als richtig gewertet. Antworten lassen sich vor dem expliziten Prüfen ändern.

Die bisherigen 260 Fragen bleiben erhalten, darunter 171 umgestellte Freitextkarten mit stabilen IDs und gespeicherten Originalantworten. 2.042 Fragen behandeln vollständige Aussagen aus den Unterlagen. 462 zusätzliche redaktionelle Auswahlfragen bearbeiten die zuvor offenen Seiten, darunter Verständnisfragen zu Diagrammen, Tabellen und Methoden. Auch Kapiteltrenner, Kontakt- und reine Illustrationsseiten sind eingeordnet. Diese liefern selbst keine neuen fachlichen Ergebnisse.

Alle 1.824 Seiten mit der Rolle Lerninhalt/Quelle sind mit Fragen verknüpft. Ein Fragenbeleg je Seite bestätigt die Seitenabdeckung, nicht die unabhängige Prüfung jedes einzelnen Lernziels. Neu erstellte und veränderte Fragen bleiben als Entwürfe erkennbar und können im Tool gelernt oder als fehlerhaft gemeldet werden. Aussagenfragen verwenden belegte Quelltexte und explizit falsche Antwortalternativen aus einer fachspezifischen Sammlung; nicht jede automatisch kombinierte Frage wurde einzeln didaktisch geprüft.

## Grafiken

Fragen zeigen nur explizit zugeordnete Ausschnitte von Diagrammen, Tabellen, Modellen oder vergleichbaren fachlichen Abbildungen. Die Grafikliste liegt in `data/grafiken.json`, die Ausschnittkoordinaten in `data/redaktion/grafik-ausschnitte.json`. Logos, dekorative Fotos und vollständige Folien werden nicht automatisch an Fragen angehängt. Die 1.830 vollständigen PDF-Seitenbilder bleiben in der Quellenansicht verfügbar.

## Umfang und Lernstand

„Alle Fragen dieser Auswahl durchgehen“ startet eine Runde mit allen aktiven Fragen der aktuellen Filterauswahl, auch bereits gelernten, unabhängig vom Tageslimit. Die reguläre Wiederholungsrunde und die individuellen Lernstände bleiben erhalten. „Folienabdeckung ansehen“ zeigt die Seitenbelege und die zugeordneten Grafiken.

## Pflege

- `data/redaktion/textbausteine.json`: vollständige Textstellen mit Seitenbelegen.
- `data/redaktion/offene-seiten.tsv`: die 462 ergänzten redaktionellen Fragen.
- `data/redaktion/fehlaussagen.json`: explizit falsche Aussagen, ausschließlich als falsche Antwortoptionen.
- `data/redaktion/seitenauswahl.json`: stabile Zuordnung der ursprünglich offenen Seiten.
- `python scripts/expand_questions.py`: reproduzierbare Erzeugung der Fragen und Abdeckungsdaten.

Literaturlisten, Datensatz und originale Prüfungsdokumente werden nicht künstlich zu Folieninhalten umgedeutet; vorhandene Fragen dazu bleiben verfügbar.

## Prüfungen

```sh
node --test tests/choice.test.cjs
python tests/data.test.py
PH_TEST_URL=http://localhost:8765/ph-lernen-7k3q9x/ node tests/browser.cjs
```

Der Browsertest benötigt Playwright und Chromium. `scripts/restore_slides.py` rendert vollständige Quellenbilder aus lokalen, SHA-256-geprüften PDF-Originalen. `scripts/extract_graphics.py` verwendet dieselben lokalen Originale und die redaktionell festgelegten Ausschnittkoordinaten für die Fragegrafiken. Zugangsdaten und private Downloadlinks gehören nicht ins Repository.
