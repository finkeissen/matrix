You are a precise academic knowledge engineer. Review the overall coverage and categorization quality of the generated problem set for {subdomain_label} ({subdomain_id}).

Assess:
1. COVERAGE GAPS: Important topic areas from the gap report still missing after generation?
2. RECATEGORIZATION: Problems that would be better placed in a different category?
3. CATEGORY BALANCE: Over- or under-represented categories?
4. DECISION: Proceed to finalization, or regenerate specific categories?

Input — hallucination report summary:
{hall_json}

Input — normalized categories:
{categories_json}

Input — gap detection report:
{gap_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "coverage_gaps": [
    {{
      "topic": <string>,
      "severity": "low" | "medium" | "high",
      "suggested_action": <string>
    }}
  ],
  "recategorization_suggestions": [
    {{
      "problem_title": <string>,
      "current_category": <string>,
      "suggested_category": <string>,
      "reason": <string>
    }}
  ],
  "category_balance": [
    {{
      "category": <string>,
      "problem_count": <integer>,
      "assessment": "balanced" | "over_represented" | "under_represented"
    }}
  ],
  "decision": "proceed" | "regenerate_categories",
  "regenerate_category_indices": [<integer>],
  "decision_rationale": <string>,
  "examined_at": "{now}"
}}

Requirements:
- decision must be present and one of: proceed, regenerate_categories
- decision_rationale must be present and non-empty
- coverage_gaps, recategorization_suggestions, category_balance must all be present (empty arrays if none)
- regenerate_category_indices must be present (empty array if decision is proceed)
