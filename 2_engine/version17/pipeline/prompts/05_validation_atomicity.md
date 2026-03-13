You are an academic quality reviewer. Check whether each problem is truly atomic — it cannot be meaningfully split into two or more independent problems without losing context.

For each problem return:
- is_atomic: true/false
- self_contained: true/false (solvable without external data not in the problem text)
- issue: null or a short description

Problems:
{problems_json}

Return ONLY a JSON array. One entry per problem, same order. No preamble, no markdown.

[
  {{
    "title": <string>,
    "is_atomic": <boolean>,
    "self_contained": <boolean>,
    "issue": <string or null>
  }}
]

Requirements:
- return exactly one entry per input problem, same order
- is_atomic and self_contained must be boolean
- issue must be null if both is_atomic and self_contained are true
