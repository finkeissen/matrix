You are a precise academic knowledge engineer. Your task is to identify the thematic categories within a subdomain for an atomic problem generation pipeline.

You will receive:
1. A scope definition for the subdomain {subdomain_label}
2. A canonical structure (authoritative table of contents or topic index)

Produce a flat list of thematic categories. Each category will be a generation unit — one LLM call per category generates all atomic problems for that category.

Input scope:
{scope_json}

Input canonical structure:
{structure_json}

Rules:
- Categories must be mutually exclusive and collectively exhaustive
- Category names in English, Title Case
- Specific enough to guide problem generation (no "Miscellaneous" or "Other")
- estimated_problem_count per category: 5–40; split larger topics, merge smaller ones
- Base categories on canonical structure; add categories for important gaps

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "category_count": <integer>,
  "items": [
    {{
      "name": <string: Title Case English>,
      "description": <string: one sentence — what problems belong here>,
      "canonical_chapter_ref": <integer or null>,
      "estimated_problem_count": <integer between 5 and 40>
    }}
  ]
}}

Requirements:
- items array must be non-empty
- every item must have name and description
- estimated_problem_count must be between 5 and 40 for every item
- no item may have name "Miscellaneous", "Other", or "General"
- category_count must equal length of items array
