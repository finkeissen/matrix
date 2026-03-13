You are a precise academic knowledge engineer. Your task is to assess the quality and clarity of a scope definition for an atomic problem generation pipeline.

Evaluate the following scope object for the subdomain {subdomain_label}. Rate it on three dimensions (0.0–1.0 each).

Input scope:
{scope_json}

1. boundary_clarity (0.0–1.0): Are boundaries specific enough to decide unambiguously whether a problem belongs here?
2. exclusion_coverage (0.0–1.0): Do exclusions cover the most likely confusion areas?
3. ambiguity_resolution (0.0–1.0): Are ambiguity resolutions clear and actionable?

Compute overall_score as arithmetic mean, rounded to 2 decimal places.
recommendation: "proceed" if overall_score >= {threshold}, otherwise "clarify"

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "scores": {{
    "boundary_clarity": <float 0.0–1.0>,
    "exclusion_coverage": <float 0.0–1.0>,
    "ambiguity_resolution": <float 0.0–1.0>
  }},
  "overall_score": <float 0.0–1.0>,
  "recommendation": "proceed" | "clarify",
  "flagged_ambiguities": [
    {{
      "topic": <string>,
      "issue": <string>,
      "severity": "low" | "medium" | "high"
    }}
  ],
  "notes": <string or null>
}}

Requirements:
- flagged_ambiguities must be present (empty array if none found)
- overall_score must equal arithmetic mean of the three dimension scores
- boundary_clarity, exclusion_coverage, ambiguity_resolution must all be between 0.0 and 1.0
