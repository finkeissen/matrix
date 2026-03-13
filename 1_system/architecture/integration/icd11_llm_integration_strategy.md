# Strategie zur ICD-11-Integration in ein LLM-System (Kurzfassung)

## Ziel
Ein LLM soll **ICD-11-konform, nachvollziehbar und halluzinationsarm** arbeiten, indem die ICD-11-Daten als **externe, prüfbare Wissensquelle** genutzt werden.

---

## 1) Retrieval-Augmented Generation (RAG) als Faktenanker
- ICD-11-JSON (oder API) wird in **durchsuchbare Dokumente** überführt (Chunks) und in eine **Vektordatenbank** geladen.
- Bei Nutzerinput (Symptome/Anamnese) werden **relevante ICD-Knoten** abgerufen und als Kontext in den Prompt gegeben.
- Ergebnis: Antworten basieren auf **Definitionen/Kriterien** statt Modell-“Gedächtnis”.

**Kernprinzip:** *LLM antwortet nur mit dem, was im Retrieval-Kontext steht.*

---

## 2) Embedding-Aufbereitung: “Rich Chunks” statt rohes JSON
**Problem:** ICD-Information ist über viele Felder verteilt → semantische Fragmentierung.  
**Lösung:** Pro ICD-Knoten einen **semantisch vollständigen Text-Chunk** bauen mit:
- Breadcrumb/Hierarchiepfad (Kapitel → Gruppe → …)
- Code + Titel
- Definition
- diagnostische Kriterien (wenn vorhanden)
- Einschlussterme (Synonyme/Patientensprache)
- Ausschlussterme (Negativabgrenzung)

**Metadaten für Retrieval-Filter:**
- `code`, `parent_code`, `ancestor_codes`, `chapter`, `depth`
- Flags wie `has_definition`, `has_diagnostic_criteria`

---

## 3) Hierarchische Validierung (Guided Search)
- Das LLM wird geführt: **Kapitel → Gruppe → Untergruppe → Code** statt “Code raten”.
- Ein **Validator** prüft jeden Schritt gegen den ICD-Baum:
  - Ist der vorgeschlagene Code in der aktuellen Teilhierarchie erlaubt?
  - Passt er logisch zu Nachbarknoten / Elternknoten?
- Ergebnis: robuste Navigation im ICD-Tree + weniger Fehlklassifikationen.

---

## 4) Multi-Agent / Self-Check (Diagnostik + Prüfer + Skript)
**Ablauf (bewährt):**
1. *Agent A (Diagnostiker)*: macht Vorschlag + Begründung.
2. *Validator (Skript)*: zieht **offizielle** Definition/Kriterien des vorgeschlagenen Codes aus JSON/API.
3. *Agent B (Prüfer)*: vergleicht Fall vs. Kriterien, markiert fehlende Kriterien, schlägt Alternativen vor.
4. Optional: *Finaler Entscheider*: konsolidiert und gibt Ausgabe inkl. Unsicherheiten.

---

## 5) Chunking-Strategie je nach Knotentyp
- Kurze Knoten: **1 Chunk**
- Mittlere Knoten: **2 überlappende Chunks** (Header als Anker: Code + Breadcrumb)
- Sehr lange/übergeordnete Knoten: **Metadaten-Chunk**, Details über Kindknoten abdecken

---

## 6) Ausgabe- und Sicherheitsregeln (Produktionsrelevant)
- Ausgabe enthält immer: **ICD-Code, Titel, Zitat/Paraphrase der Definition**, Kriterienabgleich, ggf. Ausschlüsse.
- Das System fragt nach fehlenden Informationen statt zu raten.
- Medizinischer Disclaimer/Scope: **keine ärztliche Diagnose**, nur Klassifikations-/Kodierhilfe.

---

## Empfehlung zur Datenquelle
- **WHO ICD-11 API** für Aktualität + Smart Search (wenn online möglich).
- **Lokales JSON** für Offline, Latenz, reproduzierbare Validierung.

---

## Minimaler “Blueprint”
**Pipeline:**  
`User Text → Retrieval (VDB) → Prompt mit ICD-Kontext → LLM Vorschlag → Tree-Validation → Self-Check → Ergebnis + Quellen (ICD-Auszug)`
