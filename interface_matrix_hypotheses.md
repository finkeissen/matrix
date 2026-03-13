# Matrix → Hypotheses: Integration Interface (Information Hiding Contract)

**Status:** Normative (interface-level).  
**Scope:** Defines the *structural* exchange between the Matrix repository (Layer-3) and the Hypotheses repository (Layer-4).  
**Non-scope:** Does not define how Matrix builds its internal snapshot/index, nor how Hypotheses executes tests; it only defines the admissible payload shapes exchanged across the boundary.

---

## 1) Purpose

This interface enforces **information hiding**:

- Hypotheses must not depend on Matrix internals (storage layout, indexing strategy, query engine).
- Matrix must not depend on Hypotheses internals (model language, evaluation engine, scoring, labelling).
- The boundary payload must be **self-contained**, **mechanically verifiable**, and compatible with **append-only** evolution.

At this boundary, Matrix exports *structured state*; Hypotheses imports *structured state* and exports *falsifiable hypothesis artifacts* plus run logs/outcomes.

---

## 2) Layer Roles & Authority Boundary

### 2.1 Roles
- **Matrix (Layer-3):** records instantiations, conflicts, STOPs, and explicit absences; does not decide.
- **Hypotheses (Layer-4):** produces falsifiable hypothesis artifacts under declared structural conditions; does not decide.

### 2.2 Authority rule
No epistemic authority exists in layers 0–5. Any prioritization, acceptance, or decision is external (Layer-6).

---

## 3) Invariants (MUST hold)

1. **Append-only semantics**  
   Payloads are immutable. Updates are new payloads with new IDs.

2. **Snapshot / view explicitness**  
   Hypotheses MUST NOT depend on “latest Matrix state” implicitly.
   Each input MUST declare which Matrix snapshot/view it binds to.

3. **No implicit decisions**  
   Neither side resolves conflicts, chooses winners, or suppresses contradictions.
   Conflicts and absences remain first-class.

4. **Traceable provenance**  
   Any hypothesis produced MUST be traceably bound to:
   - the Matrix snapshot/view used
   - the producing run
   - the referenced Matrix artifacts (via IDs)

5. **No silent repair**  
   If validation fails, the receiving side MUST record an ingestion failure (STOP-equivalent) in its own run system.

6. **Information hiding**  
   Boundary references MUST be interpretable without reading the other repo
   (no implicit file paths, no “call internal query X”).

---

## 4) Exchange Overview

### 4.1 Matrix → Hypotheses (input bundle)
Matrix exports a **Hypothesis Input Bundle**:

- interface metadata
- matrix context (commit/version identifiers)
- a **snapshot descriptor** (what state/view this is)
- a set of **referenced artifacts** (claims/relations/conflicts/absences/logs)
- optional integrity (hashes, counts)

### 4.2 Hypotheses → Matrix (output bundle) *(optional but recommended)*
Hypotheses exports a **Hypothesis Output Bundle**:

- interface metadata
- hypotheses context (commit/version identifiers)
- run manifests/outcomes (SUCCESS/STOP/UNKNOWN/CONFLICT/NOCLAIM)
- produced hypothesis artifacts + logs
- explicit binding to the input snapshot

> If you want a strictly one-way interface, you can omit 4.2 and instead route Hypotheses outputs back through MMS.  
> The schemas below support both patterns.

---

## 5) Envelope Schema: Matrix → Hypotheses (SELF-CONTAINED)

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "matrix-hypotheses.interface.schema.json",
  "title": "Matrix ↔ Hypotheses Interface (self-contained)",
  "type": "object",
  "additionalProperties": false,
  "required": ["direction"],
  "properties": {
    "direction": {
      "type": "string",
      "enum": ["MATRIX_TO_HYPOTHESES", "HYPOTHESES_TO_MATRIX"]
    }
  },

  "allOf": [
    {
      "if": { "properties": { "direction": { "const": "MATRIX_TO_HYPOTHESES" } }, "required": ["direction"] },
      "then": { "$ref": "#/$defs/matrix_to_hypotheses" }
    },
    {
      "if": { "properties": { "direction": { "const": "HYPOTHESES_TO_MATRIX" } }, "required": ["direction"] },
      "then": { "$ref": "#/$defs/hypotheses_to_matrix" }
    }
  ],

  "$defs": {
    "matrix_to_hypotheses": {
      "type": "object",
      "additionalProperties": false,
      "required": ["interface", "matrix_context", "snapshot", "artifacts"],
      "properties": {
        "interface": { "$ref": "#/$defs/interface_meta_matrix_input" },
        "matrix_context": { "$ref": "#/$defs/matrix_context" },
        "snapshot": { "$ref": "#/$defs/snapshot_descriptor" },
        "artifacts": { "$ref": "#/$defs/matrix_artifact_sets" }
      }
    },

    "hypotheses_to_matrix": {
      "type": "object",
      "additionalProperties": false,
      "required": ["interface", "hypotheses_context", "binding", "runs", "artifacts"],
      "properties": {
        "interface": { "$ref": "#/$defs/interface_meta_hyp_output" },
        "hypotheses_context": { "$ref": "#/$defs/hyp_context" },
        "binding": { "$ref": "#/$defs/snapshot_binding" },
        "runs": {
          "type": "array",
          "items": { "$ref": "#/$defs/hyp_run_manifest_v1" },
          "minItems": 1
        },
        "artifacts": { "$ref": "#/$defs/hyp_artifact_sets" },
        "integrity": { "$ref": "#/$defs/integrity_block" }
      }
    },

    "interface_meta_matrix_input": {
      "type": "object",
      "required": ["name", "version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "name": { "const": "matrix-hypotheses-input" },
        "version": { "type": "string" },
        "produced_at": { "type": "string", "format": "date-time" },
        "generator": { "type": "string" },
        "notes": { "type": "string" }
      }
    },

    "interface_meta_hyp_output": {
      "type": "object",
      "required": ["name", "version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "name": { "const": "hypotheses-matrix-output" },
        "version": { "type": "string" },
        "produced_at": { "type": "string", "format": "date-time" },
        "generator": { "type": "string" },
        "notes": { "type": "string" }
      }
    },

    "matrix_context": {
      "type": "object",
      "required": ["matrix_commit"],
      "additionalProperties": false,
      "properties": {
        "matrix_commit": { "type": "string" },
        "contract": {
          "type": "object",
          "required": ["id", "version"],
          "additionalProperties": false,
          "properties": {
            "id": { "type": "string" },
            "version": { "type": "string" }
          }
        }
      }
    },

    "snapshot_descriptor": {
      "type": "object",
      "required": ["snapshot_id", "created_at", "view"],
      "additionalProperties": false,
      "properties": {
        "snapshot_id": { "type": "string", "minLength": 1 },
        "created_at": { "type": "string", "format": "date-time" },
        "view": {
          "type": "object",
          "required": ["mode"],
          "additionalProperties": false,
          "properties": {
            "mode": { "type": "string" },
            "parameters": { "type": "object", "additionalProperties": true }
          }
        },
        "integrity": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "snapshot_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
          }
        }
      }
    },

    "matrix_artifact_sets": {
      "type": "object",
      "required": ["claims", "relations", "conflicts", "absences", "logs"],
      "additionalProperties": false,
      "properties": {
        "claims": { "$ref": "#/$defs/artifact_collection_matrix_ref" },
        "relations": { "$ref": "#/$defs/artifact_collection_matrix_ref" },
        "conflicts": { "$ref": "#/$defs/artifact_collection_matrix_ref" },
        "absences": { "$ref": "#/$defs/artifact_collection_matrix_ref" },
        "logs": { "$ref": "#/$defs/artifact_collection_matrix_ref" }
      }
    },

    "artifact_collection_matrix_ref": {
      "type": "object",
      "required": ["format", "items"],
      "additionalProperties": false,
      "properties": {
        "format": { "type": "string" },
        "items": {
          "type": "array",
          "items": { "$ref": "#/$defs/matrix_artifact_ref_v1" },
          "default": []
        },
        "uri": { "type": "string" },
        "content_hash": { "type": "string" }
      }
    },

    "matrix_artifact_ref_v1": {
      "type": "object",
      "required": ["origin", "run_id", "artifact_id"],
      "additionalProperties": true,
      "properties": {
        "origin": { "type": "string" },
        "run_id": { "type": "string" },
        "artifact_id": { "type": "string" },
        "content_hash": { "type": "string" },
        "artifact_type": { "type": "string" }
      }
    },

    "snapshot_binding": {
      "type": "object",
      "required": ["input_snapshot_id"],
      "additionalProperties": false,
      "properties": {
        "input_snapshot_id": { "type": "string" },
        "input_snapshot_hash": { "type": "string" }
      }
    },

    "hyp_context": {
      "type": "object",
      "required": ["hypotheses_commit"],
      "additionalProperties": false,
      "properties": {
        "hypotheses_commit": { "type": "string" },
        "contract": {
          "type": "object",
          "required": ["id", "version"],
          "additionalProperties": false,
          "properties": {
            "id": { "type": "string" },
            "version": { "type": "string" }
          }
        }
      }
    },

    "hyp_artifact_sets": {
      "type": "object",
      "required": ["hypotheses", "tests", "conflicts", "logs"],
      "additionalProperties": false,
      "properties": {
        "hypotheses": { "$ref": "#/$defs/artifact_collection_hyp" },
        "tests": { "$ref": "#/$defs/artifact_collection_hyp" },
        "conflicts": { "$ref": "#/$defs/artifact_collection_hyp" },
        "logs": { "$ref": "#/$defs/artifact_collection_hyp" }
      }
    },

    "artifact_collection_hyp": {
      "type": "object",
      "required": ["format", "items"],
      "additionalProperties": false,
      "properties": {
        "format": { "type": "string" },
        "items": {
          "type": "array",
          "items": { "$ref": "#/$defs/hyp_artifact_v1" },
          "default": []
        },
        "uri": { "type": "string" },
        "content_hash": { "type": "string" }
      }
    },

    "hyp_run_manifest_v1": {
      "type": "object",
      "required": ["run_id", "created_at", "outcome", "binding"],
      "additionalProperties": false,
      "properties": {
        "run_id": { "type": "string" },
        "created_at": { "type": "string", "format": "date-time" },
        "outcome": {
          "type": "string",
          "enum": ["SUCCESS", "NOCLAIM", "UNKNOWN", "CONFLICT", "STOP"]
        },
        "binding": { "$ref": "#/$defs/snapshot_binding" },
        "failure": { "$ref": "#/$defs/failure_block" }
      },
      "allOf": [
        {
          "if": { "properties": { "outcome": { "enum": ["STOP", "UNKNOWN"] } } },
          "then": { "required": ["failure"] }
        }
      ]
    },

    "hyp_artifact_v1": {
      "type": "object",
      "required": ["run_id", "artifact_id"],
      "additionalProperties": true,
      "properties": {
        "run_id": { "type": "string" },
        "artifact_id": { "type": "string" },
        "content_hash": { "type": "string" },
        "artifact_type": { "type": "string" }
      }
    },

    "failure_block": {
      "type": "object",
      "required": ["code", "message", "blame"],
      "additionalProperties": false,
      "properties": {
        "code": { "type": "string" },
        "message": { "type": "string" },
        "blame": { "type": "string" },
        "evidence_refs": { "type": "array", "items": { "type": "string" } }
      }
    },

    "integrity_block": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "bundle_hash": { "type": "string" },
        "counts": { "type": "object", "additionalProperties": { "type": "integer" } }
      }
    }
  }
}


## 6) Envelope Schema: Hypotheses → Matrix (SELF-CONTAINED)

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "hypotheses-matrix-output.schema.json",
  "title": "Hypotheses → Matrix Output Envelope (self-contained)",
  "type": "object",
  "additionalProperties": false,
  "required": ["interface", "hypotheses_context", "binding", "runs", "artifacts"],
  "properties": {
    "interface": {
      "type": "object",
      "additionalProperties": false,
      "required": ["name", "version", "produced_at"],
      "properties": {
        "name": { "const": "hypotheses-matrix-output" },
        "version": { "type": "string", "description": "SemVer. Breaking changes bump MAJOR." },
        "produced_at": { "type": "string", "format": "date-time" },
        "generator": { "type": "string" },
        "notes": { "type": "string" }
      }
    },

    "hypotheses_context": {
      "type": "object",
      "additionalProperties": false,
      "required": ["hypotheses_commit"],
      "properties": {
        "hypotheses_commit": { "type": "string" },
        "contract": {
          "type": "object",
          "additionalProperties": false,
          "required": ["id", "version"],
          "properties": {
            "id": { "type": "string" },
            "version": { "type": "string" }
          }
        }
      }
    },

    "binding": {
      "type": "object",
      "additionalProperties": false,
      "required": ["input_snapshot_id"],
      "properties": {
        "input_snapshot_id": { "type": "string", "minLength": 1 },
        "input_snapshot_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    },

    "runs": {
      "type": "array",
      "items": { "$ref": "#/$defs/hyp_run_manifest_v1" },
      "minItems": 1
    },

    "artifacts": {
      "type": "object",
      "additionalProperties": false,
      "required": ["hypotheses", "tests", "conflicts", "logs"],
      "properties": {
        "hypotheses": { "$ref": "#/$defs/artifact_collection" },
        "tests":      { "$ref": "#/$defs/artifact_collection" },
        "conflicts":  { "$ref": "#/$defs/artifact_collection" },
        "logs":       { "$ref": "#/$defs/artifact_collection" }
      }
    },

    "integrity": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "bundle_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "counts": { "type": "object", "additionalProperties": { "type": "integer", "minimum": 0 } }
      }
    }
  },

  "$defs": {
    "artifact_collection": {
      "type": "object",
      "additionalProperties": false,
      "required": ["format", "items"],
      "properties": {
        "format": { "type": "string", "enum": ["INLINE_JSON_ARRAY", "JSONL_URI", "OTHER"] },
        "items": {
          "type": "array",
          "items": { "$ref": "#/$defs/hyp_artifact_v1" },
          "default": []
        },
        "uri": { "type": "string" },
        "content_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      },
      "allOf": [
        {
          "if": { "properties": { "format": { "const": "JSONL_URI" } }, "required": ["format"] },
          "then": { "required": ["uri"] }
        }
      ]
    },

    "hyp_run_manifest_v1": {
      "type": "object",
      "additionalProperties": false,
      "required": ["run_id", "created_at", "outcome", "binding"],
      "properties": {
        "run_id": { "type": "string", "minLength": 1 },
        "created_at": { "type": "string", "format": "date-time" },
        "outcome": { "type": "string", "enum": ["SUCCESS", "NOCLAIM", "UNKNOWN", "CONFLICT", "STOP"] },

        "binding": {
          "type": "object",
          "additionalProperties": false,
          "required": ["input_snapshot_id"],
          "properties": {
            "input_snapshot_id": { "type": "string", "minLength": 1 }
          }
        },

        "failure": {
          "type": "object",
          "additionalProperties": false,
          "required": ["code", "message", "blame"],
          "properties": {
            "code": {
              "type": "string",
              "enum": [
                "SNAPSHOT_INVALID",
                "ADMISSIBILITY_MISSING",
                "SCHEMA_INVALID",
                "POLICY_BLOCKED",
                "INTERNAL_ERROR",
                "UNKNOWN"
              ]
            },
            "message": { "type": "string" },
            "blame": { "type": "string", "enum": ["INPUT", "SCHEMA", "GENERATOR", "POLICY", "UNKNOWN"] },
            "evidence_refs": { "type": "array", "items": { "type": "string" } }
          }
        }
      },

      "allOf": [
        {
          "if": { "properties": { "outcome": { "enum": ["STOP", "UNKNOWN"] } }, "required": ["outcome"] },
          "then": { "required": ["failure"] }
        }
      ]
    },

    "hyp_artifact_v1": {
      "type": "object",
      "additionalProperties": true,
      "required": ["run_id", "artifact_id"],
      "properties": {
        "run_id": { "type": "string", "minLength": 1 },
        "artifact_id": { "type": "string", "minLength": 1 },
        "content_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },

        "artifact_type": {
          "type": "string",
          "enum": ["HYPOTHESIS", "TEST", "CONFLICT", "LOG", "OTHER"]
        },

        "depends_on": {
          "type": "array",
          "items": { "$ref": "#/$defs/matrix_ref_v1" }
        }
      }
    },

    "matrix_ref_v1": {
      "type": "object",
      "additionalProperties": false,
      "required": ["snapshot_id", "run_id", "artifact_id"],
      "properties": {
        "snapshot_id": { "type": "string", "minLength": 1 },
        "run_id": { "type": "string", "minLength": 1 },
        "artifact_id": { "type": "string", "minLength": 1 },
        "content_hash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    }
  }
}


## 7) Minimal Fixtures (recommended)

Provide at least these fixtures alongside the schemas:

**Input fixtures (Matrix → Hypotheses)**
- matrix_snapshot.full.minimal.json (1 snapshot, 1 claim ref)
- matrix_snapshot.conflict.minimal.json (snapshot with a conflict ref)
- matrix_snapshot.absence.minimal.json (snapshot with an absence ref)

**Output fixtures (Hypotheses → Matrix)**
- hyp_run.success.minimal.json (1 run, 1 hypothesis)
- hyp_run.stop.minimal.json (STOP with failure localization, logs present, no hypothesis)
- hyp_run.conflict.minimal.json (CONFLICT outcome + conflict artifact)
These fixtures serve as contract-tests for both repos.


