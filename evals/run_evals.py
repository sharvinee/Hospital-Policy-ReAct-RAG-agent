"""Run policy-answer evaluations in LangSmith."""

import argparse
from typing import Any


def run_agent(inputs: dict[str, Any]) -> dict[str, Any]:
    """Ask hospital policy agent one evaluation question."""
    from src.agent import agent

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


def main() -> None:
    """Parse options and run the requested LangSmith evaluation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--split", choices=["optimization", "holdout"], required=True)
    parser.add_argument("--experiment-prefix", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()

    from langsmith import Client, evaluate

    from evals.code_judges import retrieval_precision, retrieval_recall, tool_match
    from evals.llm_judges import correctness, groundedness
    from src.settings import get_settings

    client = Client(api_key=get_settings().langsmith_api_key)
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
        description=args.description,
        client=client,
        blocking=True
    )

    experiment_results.wait()
    print(f"Completed experiment {experiment_results.experiment_name}.")


if __name__ == "__main__":
    main()
