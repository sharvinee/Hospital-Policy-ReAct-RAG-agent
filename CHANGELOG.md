# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Initial Northbridge Hospital policy assistant implemented as a LangChain ReAct RAG agent, using Chroma for policy retrieval and citations for retrieved sections.
- Markdown policy sources and a build script that creates the local searchable policy index.
- Direct, concise policy answers that use retrieved evidence, cover each part of multi-part questions, and route out-of-scope requests appropriately.
- Local LangGraph development server for running the LangChain agent.
- Evaluation datasets and LangSmith workflows for scoring answer correctness, groundedness, retrieval precision and recall, and tool selection.
- An experiment export command and saved summaries with evaluator scores, errors, and latency percentiles.
- A tracked table comparing mean scores across completed experiments.
- Model-based filtering of retrieved policy chunks before they are returned to the agent.
- A business document describing project goals, evaluation findings, and the quality and cost decision.
- Separate optimization and holdout experiment comparisons with recorded costs and p50 and p99 latency.

### Changed

- Refined policy-answer instructions for supported, partial, and unsupported questions, including per-detail evidence checks and focused retries.
- Reduced the default number of retrieved policy chunks per search from 3 to 2.
- Added summaries for experiments 17 and 18 to the comparison table.
- Updated correctness and groundedness judges to assess answers against retrieved policy evidence.
- Updated the groundedness judge to recognize approved hospital contact details and scope-based refusals without retrieved policy evidence.
- Changed the default chat model to GPT-6.1 Terra and added GPT-6 Luna as the light model for relevance filtering.
- Lowered the default retrieval relevance threshold from 0.5 to 0.405.
- Reduced the maximum number of retrieved policy chunks per search from 4 to 3.
- Evaluation runs now require a description; pass it with the `--description` option.
- Updated the legal-hold reference answer and added hospital-location routing to the assistant.
- Upload both evaluation splits to one LangSmith dataset, with checks to avoid duplicating existing examples.
- Update the experiment comparison table when exporting an experiment summary.
- Clarified policy-topic guidance, targeted search retries, and when to ask for clarification.

### Removed

- Removed the extra model-based relevance-filtering step after vector search; the agent now evaluates the retrieved evidence against the question.
- The redundant tracked policy JSON snapshot; the Markdown policy sources remain the inputs to the knowledge-base build.
