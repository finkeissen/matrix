"""
constants.py — Single source of truth for the pipeline.
All names, status values, ID formats, and path patterns live here.
No other file defines these — import from here.
"""

# ── Content states (core/content_states.md) ────────────────────────────────────
class ContentState:
    CANDIDATE  = "candidate"
    VERIFIED   = "verified"
    ACCEPTED   = "accepted"
    DISPUTED   = "disputed"
    SUPERSEDED = "superseded"
    REJECTED   = "rejected"

# ── Review status (atomic_problem schema) ─────────────────────────────────────
class ReviewStatus:
    DRAFT    = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"

# ── Pipeline status ────────────────────────────────────────────────────────────
class PipelineStatus:
    VALIDATED   = "validated"
    PARTIAL     = "partial"
    INSUFFICIENT = "insufficient"
    STOP        = "stop"
    RUNNING     = "running"
    DONE        = "done"
    DUPLICATE_SKIP = "duplicate_skip"

# ── Commit policy ─────────────────────────────────────────────────────────────
# Variant B (pragmatic): commit allowed at VERIFIED.
# Content state at commit is recorded per-problem.
COMMIT_MIN_STATE = ContentState.VERIFIED

# ── Run ID format ─────────────────────────────────────────────────────────────
# Format: YYYY-MM-DD_NNN_<subdomain_id>
# Example: 2026-03-05_001_SD-001
RUN_ID_PATTERN = r"^\d{4}-\d{2}-\d{2}_\d{3}_SD-\d{3}$"

# created_by format: pipeline_v<VERSION>/run_<RUN_ID>
# Example: pipeline_v2.1/run_2026-03-05_001_SD-001
def make_created_by(version: str, run_id: str) -> str:
    return f"pipeline_v{version}/run_{run_id}"

# ── Artifact keys (manifest) ─────────────────────────────────────────────────
class ArtifactKey:
    SCOPE              = "01_scope:scope"
    SCOPE_CONFIDENCE   = "01_scope_confidence:scope_confidence"
    CANONICAL_STRUCTURE = "02_retrieval:canonical_structure"
    CATEGORIES         = "03_enrichment_01_categories:categories"
    NORMALIZED         = "03_enrichment_02_normalize:normalized_categories"
    GAP_DETECTION      = "03_enrichment_03_gap_detection:gap_detection"
    VALIDATION_REPORT  = "05_validation:validation_report"
    HALLUCINATION_REPORT = "07_examination_01_hallucination_scan:hallucination_report"
    ALTERNATIVE_CHECK  = "07_examination_02_alternative_check:alternative_check"
    FINAL_PROBLEMS     = "08_finalization:final_problems"
    RUN_AUDIT          = "08_finalization:run_audit"
    COMMIT_RECORD      = "09_commit:commit_record"

    @staticmethod
    def draft(cat_idx: int) -> str:
        return f"04a_generation:cat_{cat_idx:02d}:problems_draft"

    @staticmethod
    def reviewed(cat_idx: int) -> str:
        return f"04b_generation_review:cat_{cat_idx:02d}:problems_reviewed"

# ── Stop codes ────────────────────────────────────────────────────────────────
class StopCode:
    LLM_OUTPUT_INVALID            = "llm_output_invalid"
    RETRIEVAL_EMPTY               = "retrieval_empty"
    DETERMINISTIC_STEP_ERROR      = "deterministic_step_error"
    SCOPE_CLARIFICATION_EXHAUSTED = "scope_clarification_exhausted"
    AUDIT_WRITE_FAILURE           = "audit_write_failure"
    SCHEMA_VALIDATION_FAILED      = "schema_validation_failed"

# ── Difficulty / answer_type / hallucination_risk enums ───────────────────────
VALID_DIFFICULTIES   = {"basic", "intermediate", "advanced", "expert"}
VALID_ANSWER_TYPES   = {"factual", "procedural", "analytical", "evaluative"}
VALID_HALLUC_RISKS   = {"low", "medium", "high"}
VALID_CONTENT_STATES = {ContentState.CANDIDATE, ContentState.VERIFIED,
                        ContentState.ACCEPTED, ContentState.DISPUTED,
                        ContentState.SUPERSEDED, ContentState.REJECTED}

# ── Schema file locations (relative to pipeline root) ─────────────────────────
SCHEMA_DIR = "schema"
SCHEMA_FILES = {
    "atomic_problem":      f"{SCHEMA_DIR}/atomic_problem.schema.json",
    "scope":               f"{SCHEMA_DIR}/scope.schema.json",
    "normalized_categories": f"{SCHEMA_DIR}/normalized_categories.schema.json",
    "validation_report":   f"{SCHEMA_DIR}/validation_report.schema.json",
    "run_record":          f"{SCHEMA_DIR}/run_record.schema.json",
    "manifest":            f"{SCHEMA_DIR}/manifest.schema.json",
}

# ── System version ─────────────────────────────────────────────────────────────
SYSTEM_VERSION   = "2.1.0"
PIPELINE_VERSION = "2.1.0"
