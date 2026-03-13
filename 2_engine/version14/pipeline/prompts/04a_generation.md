You are a precise academic problem designer. Generate atomic problems for a specific category within the subdomain {subdomain_label}.

An atomic problem is:
- Single, self-contained — can be posed and answered independently
- Granular — cannot be meaningfully split further without losing context
- Specific — a correct answer exists or a clear evaluation rubric can be applied
- NOT trivial (e.g. "What is 2+2?") and NOT too broad (e.g. "Explain {subdomain_label}")

Subdomain scope:
{scope_json}

Category to generate problems for:
Name: {category_name}
Description: {category_description}
Estimated problem count: {estimated_count}

{gap_section}

Generate atomic problems for this category. Cover the full range of the description.
Include all difficulty levels: basic, intermediate, advanced, expert.
Include all answer types: factual, procedural, analytical, evaluative.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain_id": "{subdomain_id}",
  "category": "{category_name}",
  "category_index": {category_index},
  "problem_count": <integer>,
  "problems": [
    {{
      "title": <string: max 80 chars, English>,
      "problem_statement": <string: full self-contained problem, English>,
      "difficulty": "basic" | "intermediate" | "advanced" | "expert",
      "answer_type": "factual" | "procedural" | "analytical" | "evaluative",
      "canonical_source": <string: authoritative reference>,
      "verifiable": <boolean>,
      "hallucination_risk": "low" | "medium" | "high",
      "requires_context": <boolean>,
      "tags": [<string>]
    }}
  ]
}}

Requirements:
- problems array must be non-empty
- every problem must have all fields listed above
- title must not exceed 80 characters
- difficulty must be one of: basic, intermediate, advanced, expert
- answer_type must be one of: factual, procedural, analytical, evaluative
- hallucination_risk must be one of: low, medium, high
- verifiable and requires_context must be boolean
- problem_count must equal length of problems array
