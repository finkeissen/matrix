# Domain Coverage, Strategy & Disclosure
<!--
Dieses Dokument ist absichtlich KEIN Datenkatalog.
Es beschreibt Steuerungslogik, Nachweisstrategie und Offenlegungsregeln
für Domänen innerhalb der Matrix.

Zielgruppe:
- interne Systementwicklung
- Governance & Strategie
- Investoren (Proof of Generalisierbarkeit)

Dieses Dokument wächst etappenweise.
-->

---

## 0. Zweck und Geltungsbereich

Die Matrix ist domänenagnostisch entworfen,  
aber **Domänenwahl, Umsetzungsgrad und Sichtbarkeit sind strategische Entscheidungen**.

Dieses Dokument beantwortet NICHT:
- welche Aussagen in einer Domäne „richtig“ sind
- welche Inhalte vollständig vorliegen

Dieses Dokument beantwortet:
- welche Domänen warum adressiert werden
- in welchem Umfang sie umgesetzt werden müssen
- für wen sie sichtbar sind
- wie der Beweis der Übertragbarkeit geführt wird

<!--
Wichtig:
Investoren lesen dieses Dokument nicht als Feature-Liste,
sondern als Beweis von Kontrolle, Bewusstsein und Risikomanagement.
-->

---

## 1. Grundannahmen (explizit)

1. Die Matrix muss nicht alle Domänen vollständig abbilden, um vollständig zu sein.
2. Glaubwürdigkeit entsteht durch:
   - wenige tiefe Beweise
   - viele bewusst begrenzte Umsetzungen
3. Nicht jede relevante Domäne darf oder soll veröffentlicht werden.
4. Domänen-Coverage ist kein Marketing-Thema, sondern Governance.

---

## 2. Definition der Coverage-Level

Coverage beschreibt **strukturelle Tiefe**, nicht Datenmenge.

### Level 0 — Catalog Only
- Domäne existiert nur als Eintrag im Domain-Catalog
- keine Probleme, Claims oder Inhalte
- dient Sichtbarkeit und Roadmap-Transparenz

Beispiel-Zweck:
- geplante Domänen
- interne Systemtests
- nicht priorisierte Bereiche

---

### Level 1 — Problem & Claim Presence (~1–5 %)

- definierte Probleme
- erste Claims
- keine vollständige Argumentationskette erforderlich

Zweck:
- zeigen, dass die Domäne modellierbar ist
- frühe Strukturerprobung

<!--
Dieses Level ist wichtig, um Skepsis zu begegnen:
„Ihr habt X vergessen“ → „Nein, bewusst Level 1.“
-->

---

### Level 2 — Argumentationskette (~5–10 %)

- vollständige Kette:
  Problem → Claim → Source → Relation
- mindestens ein Konflikt ODER explizite Konfliktfreiheit
- valide Sources

Zweck:
- Demonstration funktionierender Analyse
- belastbarer Minimalbeweis

---

### Level 3 — Konflikt, Supersession & Zeit (~10–20 %)

- explizite Conflicts
- Supersession oder Deaktivierung
- temporale Felder aktiv genutzt
- Historie bleibt rekonstruierbar

Zweck:
- realitätsnahe Domänenabbildung
- Umgang mit Widersprüchen beweisen

---

### Level 4 — Snapshot & Replay (Proof Complete)

- vollständiger Snapshot
- replayfähige Zeitpunkte
- Export für externe Betrachtung
- investor-tauglicher Demonstrator

<!--
Level 4 ist NICHT für viele Domänen gedacht.
2–3 Domänen reichen, wenn sie gut gewählt sind.
-->

---

## 3. Disclosure-Klassen (Sichtbarkeit)

Nicht jede Domäne ist gleich sichtbar.

### D0 — Intern, nicht veröffentlichbar
Gründe können sein:
- rechtlich
- sicherheitsrelevant
- ethisch
- strategisch

Diese Domänen existieren, werden aber extern nicht gezeigt.

---

### D1 — Eingeschränkt
- nur aggregiert
- anonymisiert
- oder nur als Snapshot

Zweck:
- Systembeweis ohne Inhaltsfreigabe

---

### D2 — Öffentlich
- voll einsehbar
- Teil der öffentlichen Matrix
- geeignet für Demonstration & Nutzung

---

## 4. Interessengruppen (Stakeholder Mapping)

Domänen werden nicht abstrakt bewertet, sondern **relativ zu Zielgruppen**.

Mögliche Gruppen:
- Privatpersonen
- Unternehmen
- Öffentliche Hand
- Wissenschaft / Forschung
- Regulatoren
- Investoren

<!--
Eine Domäne kann mehrere Zielgruppen haben,
aber immer eine primäre.
-->

---

## 5. Etappe 1 — Rahmen (Status: verbindlich)

Diese Definitionen gelten ab sofort:
- Coverage-Level 0–4
- Disclosure-Klassen D0–D2
- Stakeholder-Mapping als Pflichtmetadatum

Noch NICHT festgelegt:
- vollständige Domänenliste
- konkrete Einstufungen

<!--
Diese Etappe beweist Strukturkompetenz,
nicht inhaltliche Tiefe.
-->

---

## 6. Etappe 2 — Referenz- / Beweisdomänen (geplant)

Ziel:
Ein klarer, nachvollziehbarer Beweis,
dass die Matrix komplexe, widersprüchliche Domänen tragen kann.

Kriterien für Beweisdomänen:
- hohe Komplexität
- reale Konflikte
- zeitliche Abhängigkeiten
- regulatorische oder normative Aspekte

Voraussichtliche Kandidaten (nicht final):
- Medizin
- Jura
- Finanzen

Für jede Beweisdomäne festzulegen:
- Ziel-Coverage-Level (voraussichtlich 3 oder 4)
- Disclosure-Klasse
- adressierte Stakeholder
- zugehörige Commits / Snapshots

<!--
Wichtig:
Die Auswahl ist begründet, nicht politisch.
-->

---

## 7. Etappe 3 — Breite Domänenabdeckung (geplant)

Ziel:
Glaubwürdige Skalierung auf ~80 Domänen.

Inhalt:
- vollständige Domänenliste
- Ziel-Coverage-Level pro Domäne
- Disclosure-Klasse
- primäre Interessengruppe

Explizit erlaubt:
- viele Domänen auf Level 0 oder 1
- klare Kennzeichnung von „nicht vermarktet“

---

## 8. Etappe 4 — Governance & Veränderung

Domänenklassifikationen sind änderbar,
aber niemals implizit.

Regeln:
- jede Änderung ist ein Lifecycle-Ereignis
- Coverage-Aufstieg braucht Begründung
- Disclosure-Änderungen sind besonders zu dokumentieren

<!--
Damit wird verhindert,
dass Marketing-, Produkt- oder Investorendruck
stille Strukturänderungen erzwingt.
-->

---

## 9. Leselogik für Investoren (Hinweis)

Investoren sollten dieses Dokument lesen als:
1. Beweis strategischer Kontrolle
2. Beweis bewusster Begrenzung
3. Beweis skalierbarer Architektur

Nicht als:
- Feature-Liste
- Vollständigkeitsversprechen
- Produkt-Roadmap

