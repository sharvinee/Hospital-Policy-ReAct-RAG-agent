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

### Changed

- Refined policy-answer instructions for supported, partial, and unsupported questions, including a retry when relevant evidence is missing.
- Updated correctness and groundedness judges to assess answers against retrieved policy evidence.
- Lowered the default retrieval relevance threshold from 0.5 to 0.42.
- Evaluation runs now require a description; pass it with the `--description` option.
- Updated the legal-hold reference answer and added hospital-location routing to the assistant.

### Removed

- The redundant tracked policy JSON snapshot; the Markdown policy sources remain the inputs to the knowledge-base build.
