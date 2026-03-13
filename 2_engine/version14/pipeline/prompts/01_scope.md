You are a precise academic knowledge engineer. Your task is to define the exact scope of a subdomain for an atomic problem generation pipeline.

Subdomain: {subdomain_label}
Parent domain: {parent_domain}
Subdomain ID: {subdomain_id}
Score: {score} (Tier {tier})

Define the scope of {subdomain_label} as a knowledge domain for the purpose of generating atomic problems. An atomic problem is a single, self-contained question or task that can be posed and answered independently, is granular enough that it cannot be meaningfully split further, and has a correct answer or a clear evaluation rubric.

Return ONLY a JSON object. No explanation, no preamble, no markdown fences.

{{
  "subdomain": "{subdomain_label}",
  "subdomain_id": "{subdomain_id}",
  "parent_domain": "{parent_domain}",
  "canonical_source": <string: the single most authoritative reference for {subdomain_label} as a whole>,
  "boundaries": <array of strings: what IS in scope — list at least 6 specific topic areas>,
  "exclusions": <array of strings: what is explicitly OUT of scope — list at least 3 areas>,
  "ambiguities": <array of objects with fields "topic" and "resolution": at least 2 boundary cases>
}}

Requirements:
- boundaries must list at least 6 specific topic areas
- exclusions must list at least 3 areas that could be confused with {subdomain_label}
- ambiguities must address at least 2 boundary cases
- All values in English
- Be precise: boundaries and exclusions will be used to validate generated problems
