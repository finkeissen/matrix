You are a precise academic knowledge engineer. Identify gaps and underrepresented areas in the category list for {subdomain_label} (SD: {subdomain_id}).

You will receive:
1. Scope definition
2. Canonical structure (authoritative table of contents)
3. Normalized category list

Identify:
- Topics from scope.boundaries NOT covered by any category
- Topics from canonical structure NOT covered by any category
- Categories with estimated_problem_count < 5 (underrepresented)
- Categories with estimated_problem_count > 40 (too broad — suggest split)

Input scope:
{scope_json}

Input canonical structure:
{structure_json}

Input normalized categories:
{categories_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "covered_topics": [<string>],
  "missing_topics": [
    {{
      "topic": <string>,
      "source": "scope_boundary" | "canonical_structure" | "domain_knowledge",
      "suggested_category": <string>,
      "action": "add_category" | "merge_into_existing" | "expand_existing"
    }}
  ],
  "underrepresented_categories": [
    {{
      "category_index": <integer>,
      "category_name": <string>,
      "issue": <string>,
      "suggestion": <string>
    }}
  ],
  "oversized_categories": [
    {{
      "category_index": <integer>,
      "category_name": <string>,
      "suggestion": <string>
    }}
  ],
  "overall_coverage": "good" | "acceptable" | "poor",
  "notes": <string or null>
}}

Requirements:
- overall_coverage must be present and one of: good, acceptable, poor
- missing_topics must be present (empty array if none found)
- covered_topics must list at least the topics that ARE covered
