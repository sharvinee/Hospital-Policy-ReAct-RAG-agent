# Business Document: Hospital Policy Assistant

## Purpose

Northbridge Hospital needs a way for staff, patients, and representatives to
find answers to questions about hospital policies. The policy assistant aims to
provide concise answers grounded in the available policy documents, with
citations so users can identify the supporting sections.

## What the agent does

- Answers questions about patient care, operations, and IT and information
  governance policies using the available policy knowledge base.
- Searches the policy documents, filters retrieved passages for relevance,
  and cites the policy sections used in its answer.
- Answers supported parts of a question and explains when it cannot confirm a
  requested detail from the available information.
- Routes questions outside its policy scope according to its instructions.

## Business goals

- Make policy information easier and faster to find.
- Provide accurate, grounded answers that users can trace to policy sections.
- Keep the operating cost low while maintaining acceptable retrieval quality.

## Evaluation and findings

The agent was evaluated using an optimization dataset of 35 examples. The
experiments measured retrieval precision and recall, tool selection, answer
correctness, groundedness, latency, and recorded run cost.

The project uses **80% retrieval precision as a working target**. In experiment
15, the agent achieved **86.19% mean retrieval precision**, above that target.
The same experiment scored 100% on retrieval recall, tool match, correctness,
and groundedness on the evaluated examples. Its recorded root-run cost was
approximately **$0.0296 for 35 runs**, excluding separately traced evaluator
calls. Results are summarized in `evals/results/results.md`.

Experiment 16 achieved 86.67% mean retrieval precision, with 100% on the
other measured quality scores. Its recorded root-run cost was approximately
$0.0332. These figures describe the optimization examples.

The latest holdout experiment achieved 81.11% mean retrieval precision,
93.33% recall and correctness, and 100% tool match and groundedness. Its
recorded root-run cost was approximately $0.0155. The holdout results show
that some questions still need review, even though precision remains above the
working target.

Experiment 13 achieved higher precision (89.05%) and a lower recorded run cost,
but scored below experiment 15 on recall and correctness. The recorded results
do not by themselves establish which change caused the differences or prove
that one configuration will always be cheaper.

## Quality and cost decision

The goal was to build the best practical agent within a low operating cost, not
to maximize retrieval precision at any cost. A precision score above 80% was
considered good enough for this stage. Having reached approximately 86% while
the other measured scores met the current target, the decision was to stop
optimizing precision for now and retain a balanced solution.

This is a **working business decision**, not a claim that 86% is a universal
standard or that this configuration is the cheapest possible. The score is a
mean against the dataset's expected policy-section IDs; a returned section not
listed as expected reduces precision even if it provides useful context.

## Boundaries and next review

The reported results describe a small optimization set and include LLM judge
scores. They do not establish performance on all hospital questions or confirm
that every policy answer will be safe or correct. The holdout evaluation also
found errors; review those answers before treating the results as evidence of
readiness for wider use.

Revisit the quality and cost decision when policy content, user needs, models,
pricing, or evaluation results change. Confirm the intended users, acceptable
error rates, and what should happen when the agent cannot confidently answer.
