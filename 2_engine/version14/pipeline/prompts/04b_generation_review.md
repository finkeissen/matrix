You are a rigorous academic quality reviewer. Review and refine atomic problems for the category {category_name} within {subdomain_label} (ID: {subdomain_id}).

For each problem in the draft, apply these checks:
1. ATOMICITY: Can this problem be split further without losing context? If yes, split or flag it.
2. SELF-CONTAINMENT: Is it fully solvable without external data? If not, set requires_context: true.
3. HALLUCINATION RISK: Is this a well-established fact with a stable, verifiable answer?
4. DIFFICULTY: Is the assigned difficulty appropriate?
5. CANONICAL SOURCE: Is canonical_source specific and authoritative? Improve vague references.
6. DUPLICATION: Are any two problems asking essentially the same thing? Merge or remove duplicates.

Then check the gap detection report: are important topics missing? Add problems for missing topics.

Input scope:
{scope_json}

Input draft problems:
{draft_json}

Input gap detection report:
{gap_json}

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "category": "{category_name}",
  "category_index": {category_index},
  "problem_count": <integer>,
  "problems_added": <integer>,
  "problems_removed": <integer>,
  "problems_modified": <integer>,
  "changes_made": [
    {{
      "action": "added" | "removed" | "modified" | "split",
      "title": <string>,
      "reason": <string>
    }}
  ],
  "problems": [
    {{
      "title": <string: max 80 chars, English>,
      "problem_statement": <string: full self-contained problem, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string>,
      "verifiable": <boolean>,
      "hallucination_risk": "low" | "medium" | "high",
      "requires_context": <boolean>,
      "tags": [<string>]
    }}
  ]
}}

Requirements:
- problems array must be non-empty
- problem_count must equal length of problems array
- problems_added, problems_removed, problems_modified must all be present (0 if none)
- changes_made must be present (empty array if no changes)
- all field-level requirements from 04a apply to every problem in this output
