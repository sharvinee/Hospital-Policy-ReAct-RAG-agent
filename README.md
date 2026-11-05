# Northbridge Hospital Policy ReAct RAG Agent

A LangChain ReAct agent using retrieval-augmented generation (RAG) to answer questions about Northbridge Hospital policies. The model can call the `search_kb` tool, use the retrieved policy passages as evidence, and cite the matching `SEC_###` section in its response.

## How it works

1. Policy Markdown files in `policies/` are split into sections and indexed in a local Chroma vector store.
2. LangChain's `create_agent` runs the ReAct loop: the model decides whether to call `search_kb`, receives the tool's results, and then writes its answer.
3. `search_kb` embeds the question, retrieves relevant policy sections from Chroma, and returns their text and citation IDs.
4. The model answers from the retrieved evidence and cites the relevant `SEC_###` section.

The index is built from the Markdown files; edit those files when policy content changes.

## Requirements

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/)
- An OpenAI API key for chat and embeddings
- A LangSmith API key for the configured application and evaluation workflows

## Set up

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```dotenv
OPENAI_API_KEY=your-openai-api-key
LANGSMITH_API_KEY=your-langsmith-api-key
```

Then install the project dependencies:

```bash
uv sync --all-groups
```

The model names and retrieval settings can be changed with environment variables. Defaults are `openai:gpt-5.6-luna` for chat, `openai:text-embedding-3-small` for embeddings, `4` retrieved chunks, and a relevance threshold of `0.5`.

## Build the policy index

Run this after setting `OPENAI_API_KEY` and whenever the policy Markdown changes:

```bash
uv run python scripts/create_policies_kb.py
```

The script reads `policies/*.md`, writes a readable generated snapshot to `policies/northbridge_policies.json`, and rebuilds the Chroma index in `.chroma/policies_kb/`.

Each policy section must use Markdown headings for the document (`#`), section (`##`), and policy title (`###`), and end with a unique footer such as `*SEC_001*`. The build stops if a policy section is missing its ID.

## Run the assistant

Start the local LangGraph development server:

```bash
uv run langgraph dev
```

The graph is named `hospital-policy-agent` in `langgraph.json`. Build the policy index first so searches have data to query.

## Evaluation

Evaluation examples are stored in `evals/data/golden_dataset.json` and divided into `optimization` and `holdout` splits. Uploading or updating examples and running evaluations require a LangSmith API key.

Create a LangSmith dataset for a split:

```bash
uv run python evals/upload_dataset.py --split optimization --tag baseline
```

The uploader uses the fixed dataset name `northbridge-policy-golden`. Use `evals/update_dataset.py` to update an existing dataset from the local JSON:

```bash
uv run python evals/update_dataset.py --split optimization --tag updated
```

Run an evaluation on a split in that LangSmith dataset:

```bash
uv run python evals/run_evals.py \
  --dataset-name northbridge-policy-golden \
  --split optimization \
  --experiment-prefix baseline
```

LangSmith stores each experiment's runs and evaluator results. The local runner prints the experiment name and does not write local result files. Precision and recall are fractional for examples with expected chunks; with no expected chunks, each score is `1.0` only when retrieval returns no chunks.

## Project layout

- `policies/` — source policy Markdown
- `src/` — agent, prompt, settings, and retrieval tool
- `scripts/create_policies_kb.py` — policy chunking and Chroma index builder
- `evals/data/` — evaluation examples and prior experiment exports
- `evals/` — evaluators and LangSmith dataset/evaluation commands
