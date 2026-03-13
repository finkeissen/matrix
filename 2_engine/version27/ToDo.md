# ToDo for version26: nächste Tests + Änderungen

## Ausgangslage

Die lokale Pfadangabe `/home/ef/ram/venv/version26/ingestion/archive/imports/` war in meiner Ausführungsumgebung nicht direkt zugänglich. Ich habe daher die äquivalente Struktur aus dem hochgeladenen Projekt-Archiv (`version25.zip`, als naheliegende Basis für `version26`) geprüft.

Dabei sichtbar:

- Archiv-Imports vorhanden als:
  - `ingestion/archive/imports/atomic.zip`
  - `ingestion/archive/imports/cases.zip`
  - `ingestion/archive/imports/contradictions.zip`
  - `ingestion/archive/imports/icd11_enriched_ultra_flat.jsonl.zip`
  - `ingestion/archive/imports/meta.zip`
  - `ingestion/archive/imports/partials.zip`
  - `ingestion/archive/imports/structural.zip`
- Entpackte Imports vorhanden als:
  - `ingestion/imports/atomic/...`
  - `ingestion/imports/cases/...`
  - `ingestion/imports/contradictions/...`
  - `ingestion/imports/meta/...`
  - `ingestion/imports/partials/...`
  - `ingestion/imports/structural/...`
- Größenordnung der entpackten Imports:
  - `partials`: sehr groß
  - `atomic`: groß
  - `structural`, `meta`, `cases`: mittel
- Kein klar sichtbarer thermodynamics-spezifischer Importpfad in den Archiv-/Import-Namen.

## Zentrale Beobachtung

`version26` läuft jetzt stabil. Der Engpass ist nicht mehr die Laufstabilität, sondern die inhaltliche Qualität und die Frage, wie die Ingestion systematisch in Richtung **Subdomänen + konkrete Problemformulierung** genutzt wird.

## Priorität A — Bestand sauber erfassen

### A1. Archiv-Imports vollständig inventarisieren
- [ ] `ingestion/archive/imports/*.zip` mit Inhaltstabellen auflisten
- [ ] pro Archiv dokumentieren:
  - Themenbereich
  - Dateitypen
  - mögliche Relevanz für thermodynamics
- [ ] prüfen, ob in den Archiven bereits thermodynamics-nahe Inhalte versteckt sind

### A2. Entpackte Imports nach domänischer Relevanz prüfen
- [ ] Volltextsuche nach:
  - `thermodynamics`
  - `heat`
  - `entropy`
  - `enthalpy`
  - `compressor`
  - `turbine`
  - `phase change`
  - `control volume`
- [ ] Treffer in einer kleinen Mapping-Datei sammeln
- [ ] festhalten, welche Importfamilien für thermodynamics real verwendbar sind

### A3. Gaps dokumentieren
- [ ] explizit notieren, was **nicht** vorhanden ist:
  - keine Thermodynamik-Taxonomie
  - keine thermodynamics-spezifischen Seeds
  - keine Subdomänen-Tags
  - keine konkreten numerischen Problembausteine

## Priorität B — Tests auf Ingestion-Nutzen

### B1. Test: Nutzt `02_seed_expansion` die Ingestion sinnvoll?
- [ ] `02_seed_expansion.json` für `thermodynamics` gegen Roh-Imports vergleichen
- [ ] prüfen, wie viele Seeds wirklich aus Ingestion kommen und wie viele nur generiert sind
- [ ] entscheiden, ob die aktuellen Seeds fachlich brauchbar oder nur generisch sind

### B2. Test: Nutzt `03_categories` echte Taxonomie oder Fallback?
- [ ] bestätigen, dass `category_source` aktuell Fallback ist
- [ ] Testfall bauen, bei dem eine echte Domain-Taxonomie vorhanden ist
- [ ] prüfen, ob die Pipeline diese sauber übernimmt

### B3. Regressionstest für `case_gates`
- [ ] sicherstellen, dass die entschärften Gates keine triviale Sprache mehr blocken
- [ ] Testfälle aufnehmen für problematische Tokens wie:
  - `to`
  - `new`
  - `mode`
  - `scope`
  - `assumption`
- [ ] sicherstellen, dass nur spezifische Phrasen blocken

## Priorität C — Step 04 strategisch weiterentwickeln

### C1. Subdomänen explizit einführen
- [ ] `THERMO_CONTEXTS` um Feld `subdomain` ergänzen, z. B.:
  - `closed_systems`
  - `control_volumes`
  - `heat_exchangers`
  - `compressible_flow`
  - `phase_change`
  - `gas_power_devices`
  - `refrigeration`
- [ ] `subdomain` in `tags` aufnehmen
- [ ] später optional in Export aufnehmen

### C2. Von Seeds zu echten Aufgaben wechseln
- [ ] Step 04 von `ask the solver to ...` stärker auf echte Aufgabenform umstellen
- [ ] Zielstruktur pro Problem:
  - Szenario
  - gegebene Größen
  - gesuchte Größe
  - knappe Modellannahme
- [ ] mindestens 5–10 numerische oder semiquantitative Slots definieren

### C3. Konkretere Problembausteine einführen
- [ ] pro Subdomäne typische Größen ergänzen, z. B.:
  - Druck
  - Temperatur
  - Volumen
  - Massenstrom
  - Wirkungsgrad
  - Enthalpie
  - Entropieänderung
- [ ] pro Subdomäne typische Zielfragen definieren
- [ ] pro Subdomäne verbotene oder unplausible Kombinationen vermeiden

### C4. Titel verbessern
- [ ] mechanische Titel (`Analyze ... case 3`) ersetzen durch inhaltsnähere Titel
- [ ] Muster:
  - `Rigid tank filling: determine the final state`
  - `Throttling valve: identify the governing constraint`
  - `Heat exchanger bottleneck: compare two interpretations`

## Priorität D — Validation wieder sinnvoll schärfen

### D1. `05_validation` nicht nur formal, sondern fachlich brauchbar machen
- [ ] prüfen, ob `accepted = 30/30` zu tolerant ist
- [ ] neue Checks erwägen für:
  - minimale Konkretion
  - Verbot rein generischer Aufgabenformeln
  - redundante Satzmuster
- [ ] dabei keine Rückkehr zu den alten, zu aggressiven Gates

### D2. Längenregel konsistent halten
- [ ] `_fit_statement()` beibehalten
- [ ] zusätzlich Test schreiben, dass alle `problem_statement` unter dem finalen Limit bleiben
- [ ] keine weitere Lockerung in `result_quality.py`, solange Step 04 die Länge selbst kontrollieren kann

## Priorität E — Bewertungs- und Vergleichstests

### E1. Qualitative Vergleichsruns
- [ ] `version25` vs `version26` für `thermodynamics` direkt vergleichen
- [ ] Kriterien:
  - fachliche Konkretion
  - Varianz
  - Natürlichkeit
  - direkte Nutzbarkeit als Aufgabe

### E2. Domänen-Transfer testen
- [ ] dieselbe Pipeline auf 1–2 andere Domains laufen lassen
- [ ] prüfen, ob die neue Step-04-Strategie robust bleibt oder zu stark thermodynamics-spezifisch ist

### E3. Ranking prüfen
- [ ] Top-10 aus `07_ranking` manuell prüfen
- [ ] fragen:
  - stehen wirklich die besten Aufgaben oben?
  - bevorzugt das Ranking nur längere / schwerere Probleme?

## Priorität F — Optionaler nächster Strategiesprung

### F1. Hybridmodus evaluieren
- [ ] optional zweiten Step-04-Modus bauen:
  - deterministischer Seed
  - LLM-Rewrite in natürlichere Aufgabe
- [ ] nur testen, nicht sofort als Standard setzen
- [ ] Ziel: bessere Natürlichkeit ohne Verlust der Reproduzierbarkeit

### F2. Step 01 robuster machen
- [ ] `step.llm_fallback` gezielt untersuchen
- [ ] prüfen, ob Prompt oder Formatvorgabe verbessert werden kann
- [ ] Ziel: sauberer strukturierter Scope ohne Fallback

## Konkrete Reihenfolge für die nächsten 5 Arbeitsschritte

1. [ ] Archiv- und Import-Bestand für thermodynamics-relevante Inhalte durchsuchen
2. [ ] explizite Subdomänen in `04_problem_generation.py` einführen
3. [ ] Problemtexte auf **gegeben / gesucht / Annahme** umstellen
4. [ ] Validation leicht nachschärfen, aber ohne aggressive Gates
5. [ ] `version25` vs `version26` qualitativ vergleichen und Top-10 manuell reviewen

## Definition of Done für den nächsten Meilenstein

Der nächste sinnvolle Meilenstein ist erreicht, wenn:

- [ ] `version26` weiterhin stabil komplett durchläuft
- [ ] Step 04 explizite Subdomänen nutzt
- [ ] die finalen Probleme nicht mehr nur Seeds, sondern echte Aufgabenformulierungen sind
- [ ] mindestens ein kleiner qualitativer Vergleich `v25` vs `v26` dokumentiert ist
- [ ] Validation wieder etwas selektiver ist, ohne triviale Sprache zu blocken
