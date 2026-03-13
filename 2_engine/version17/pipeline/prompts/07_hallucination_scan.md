You are a rigorous academic fact-checker. Scan these atomic problems for hallucination risk.

For each problem, assess:
1. Is the problem statement factually correct as stated?
2. Does the canonical_source reference actually exist and cover this topic?
3. Are any technical terms used in a non-standard way?
4. Is the hallucination_risk assigned by the generator appropriate?

Flag any problem where you have doubt. Assign a corrected hallucination_risk if the original is wrong.

Subdomain: {subdomain_label} ({subdomain_id})

Problems to scan:
{problems_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "total_problems_scanned": <integer>,
  "flagged_count": <integer>,
  "scan_coverage": "{scan_coverage}",
  "flagged": [
    {{
      "category": <string>,
      "title": <string>,
      "issue_type": "factual_error" | "invalid_source" | "non_standard_term" | "risk_underestimated",
      "issue_description": <string>,
      "original_hallucination_risk": "low" | "medium" | "high",
      "corrected_hallucination_risk": "low" | "medium" | "high",
      "severity": "low" | "medium" | "high",
      "suggested_fix": <string or null>
    }}
  ],
  "overall_quality": "high" | "acceptable" | "low",
  "notes": <string or null>
}}

Requirements:
- overall_quality must be present and one of: high, acceptable, low
- flagged must be present (empty array if none flagged)
- total_problems_scanned and flagged_count must be present integers
- flagged_count must equal length of flagged array
