"""Run policy-answer evaluations in LangSmith."""

import argparse
from langsmith import Client, evaluate
from src.agent import agent
from src.settings import get_settings
from evals.code_judges import (
    retrieval_precision,
    retrieval_recall,
    tool_match
)
from evals.llm_judges import correctness, groundedness

settings = get_settings()
client = Client(api_key=settings.langsmith_api_key)


def run_agent(inputs: dict) -> dict:
    """Ask hospital policy agent one evaluation question."""
    return agent.invoke(
        {
            "messages": [
                {
                    "role": "human",
                    "content": inputs["human"]
                }
            ]
        }
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--split", choices=["optimization", "holdout"], required=True)
    parser.add_argument("--experiment-prefix", required=True)
    args = parser.parse_args()

    examples = list(
        client.list_examples(
            dataset_name=args.dataset_name,
            splits=[args.split],
        )
    )

    experiment_results = evaluate(
        run_agent,
        data=examples,
        evaluators=[
            retrieval_precision,
            retrieval_recall,
            tool_match,
            correctness,
            groundedness
        ],
        experiment_prefix=args.experiment_prefix,
        client=client,
        blocking=True
    )

    experiment_results.wait()
    print(f"Completed experiment {experiment_results.experiment_name}.")
