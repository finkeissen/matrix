"""
constants.py v14 — Single source of truth for the pipeline.
All names, status values, ID formats, and path patterns live here.
"""

class ContentState:
    CANDIDATE  = "candidate"
    VERIFIED   = "verified"
    ACCEPTED   = "accepted"
    DISPUTED   = "disputed"
    SUPERSEDED = "superseded"
    REJECTED   = "rejected"

class PromptState:
    DRAFT      = "draft"
    ACTIVE     = "active"
    DEPRECATED = "deprecated"
    ARCHIVED   = "archived"

class ReviewStatus:
    DRAFT    = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"

class PipelineStatus:
    VALIDATED      = "validated"
    PARTIAL        = "partial"
    INSUFFICIENT   = "insufficient"
    STOP           = "stop"
    RUNNING        = "running"
    DONE           = "done"
    DUPLICATE_SKIP = "duplicate_skip"

class StopCode:
    LLM_OUTPUT_INVALID            = "llm_output_invalid"
    RETRIEVAL_EMPTY               = "retrieval_empty"
    DETERMINISTIC_STEP_ERROR      = "deterministic_step_error"
    SCOPE_CLARIFICATION_EXHAUSTED = "scope_clarification_exhausted"
    AUDIT_WRITE_FAILURE           = "audit_write_failure"
    SCHEMA_VALIDATION_FAILED      = "schema_validation_failed"

COMMIT_MIN_STATE = ContentState.VERIFIED
RUN_ID_PATTERN   = r"^\d{4}-\d{2}-\d{2}_\d{3}_SD-\d{3}$"

def make_created_by(version: str, run_id: str) -> str:
    return f"pipeline_v{version}/run_{run_id}"

class ArtifactKey:
    SCOPE                = "01_scope:scope"
    SCOPE_CONFIDENCE     = "01_scope_confidence:scope_confidence"
    CANONICAL_STRUCTURE  = "02_retrieval:canonical_structure"
    CATEGORIES           = "03_enrichment_01_categories:categories"
    NORMALIZED           = "03_enrichment_02_normalize:normalized_categories"
    GAP_DETECTION        = "03_enrichment_03_gap_detection:gap_detection"
    VALIDATION_REPORT    = "05_validation:validation_report"
    HALLUCINATION_REPORT = "07_examination_01_hallucination_scan:hallucination_report"
    ALTERNATIVE_CHECK    = "07_examination_02_alternative_check:alternative_check"
    FINAL_PROBLEMS       = "08_finalization:final_problems"
    RUN_AUDIT            = "08_finalization:run_audit"
    COMMIT_RECORD        = "09_commit:commit_record"

    @staticmethod
    def draft(cat_idx: int) -> str:
        return f"04a_generation:cat_{cat_idx:02d}:problems_draft"

    @staticmethod
    def reviewed(cat_idx: int) -> str:
        return f"04b_generation_review:cat_{cat_idx:02d}:problems_reviewed"

VALID_DIFFICULTIES   = {"basic", "intermediate", "advanced", "expert"}
VALID_ANSWER_TYPES   = {"factual", "procedural", "analytical", "evaluative"}
VALID_HALLUC_RISKS   = {"low", "medium", "high"}
VALID_CONTENT_STATES = {ContentState.CANDIDATE, ContentState.VERIFIED,
                        ContentState.ACCEPTED, ContentState.DISPUTED,
                        ContentState.SUPERSEDED, ContentState.REJECTED}

SCHEMA_DIR   = "schema"
SCHEMA_FILES = {
    "atomic_problem":        f"{SCHEMA_DIR}/atomic_problem.schema.json",
    "scope":                 f"{SCHEMA_DIR}/scope.schema.json",
    "normalized_categories": f"{SCHEMA_DIR}/normalized_categories.schema.json",
    "validation_report":     f"{SCHEMA_DIR}/validation_report.schema.json",
    "run_record":            f"{SCHEMA_DIR}/run_record.schema.json",
    "manifest":              f"{SCHEMA_DIR}/manifest.schema.json",
}

SYSTEM_VERSION   = "14.0.0"
PIPELINE_VERSION = "14.0.0"

# LLM steps and their model class (for telemetry routing)
STEP_MODEL_CLASS = {
    "01_scope":               "19b",
    "01_scope_confidence":    "19b",
    "03_categories":          "35b",
    "03_gap_detection":       "35b",
    "04a_generation":         "35b",
    "04b_generation_review":  "122b",
    "05_validation":          "35b",
    "06_clarification":       "19b",
    "07_hallucination_scan":  "122b",
    "07_alternative_check":   "35b",
    "08_finalization":        "19b",
    # Sub-prompt keys (used by steps internally)
    "05_validation_atomicity":    "35b",
    "08_finalization_summary":    "19b",
}

# Steps that have prompts (LLM steps)
# LLM_STEPS used by orchestrator for prompt_versions in run_record
# Sub-keys (05_validation_atomicity, 08_finalization_summary) are loaded by steps directly
LLM_STEPS = {
    "01_scope", "01_scope_confidence",
    "03_categories", "03_gap_detection",
    "04a_generation", "04b_generation_review",
    "05_validation_atomicity",
    "06_clarification",
    "07_hallucination_scan", "07_alternative_check",
    "08_finalization_summary",
}

# Steps that are purely deterministic (no prompt file needed)
DETERMINISTIC_STEPS = {"02_retrieval", "03_normalize", "09_commit"}
