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
