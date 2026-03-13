# Policies: Completeness Strategy (Inventory)

Inventory completeness must be evaluated to avoid sampling bias.

Two complementary strategies are recommended:

## A) Taxonomy coverage (issue classes)
Maintain a taxonomy of problem classes (customizable):
- correctness, consistency
- performance, latency, throughput
- availability, resiliency
- security, privacy
- operability, observability
- scalability, cost
- governance, process
- data quality, semantics

Constraint: the inventory must contain at least N atomic problems per class
OR explicitly mark class as not applicable.

## B) Component coverage (system decomposition)
Maintain a system component map:
- components/subsystems/interfaces
- boundary conditions (inputs/outputs, failure modes)

Constraint: each component must have at least one linked atomic problem
OR explicit "no known problems" marker with evidence.

These strategies produce review queues, not truth.
