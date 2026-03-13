You are a precise academic knowledge engineer. A scope definition has produced validation issues. Generate a refined scope that resolves these issues.

This is clarification round {round_num} of maximum {max_rounds}.

Current scope:
{scope_json}

Validation issues that triggered this clarification:
{issues_json}

Produce a refined scope object that resolves these issues. Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": <string>,
  "subdomain_id": <string>,
  "parent_domain": <string>,
  "canonical_source": <string>,
  "boundaries": [<string>],
  "exclusions": [<string>],
  "ambiguities": [{{"topic": <string>, "resolution": <string>}}],
  "refinement_round": {round_num},
  "changes_made": [
    {{
      "field": "boundaries" | "exclusions" | "ambiguities",
      "change": <string>
    }}
  ]
}}

Requirements:
- subdomain, subdomain_id, boundaries, exclusions must all be present
- boundaries must be non-empty (at least 6 items)
- exclusions must be non-empty (at least 3 items)
- ambiguities must be present (at least 2 items)
- changes_made must be present and non-empty — explain what was changed and why
- refinement_round must equal {round_num}
