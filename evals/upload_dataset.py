"""Upload one evaluation split, placing local example IDs in LangSmith metadata."""

import argparse
import json
from pathlib import Path

from langsmith import Client
from src.settings import get_settings

DATASET_NAME = "northbridge-policy-golden"
DATASET_PATH = Path(__file__).resolve().parent / "data" / "golden_dataset.json"


def load_examples(split: str) -> list[dict]:
    """Return LangSmith payloads without modifying the local examples."""
    local_examples = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    examples = [
        {
            "inputs": example["inputs"],
            "reference_outputs": example["outputs"],
            "metadata": {**example["metadata"], "id": example["id"]},
            "split": example["split"],
        }
        for example in local_examples
        if example["split"] == split
    ]
    if not examples:
        raise ValueError(f"No local examples found for split {split!r}.")
    if len({example["metadata"]["id"] for example in examples}) != len(examples):
        raise ValueError("Local example IDs must be unique within the split.")
    return examples

def main() -> None:
    """Upload the requested split to a new LangSmith dataset."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["optimization", "holdout"], required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    examples = load_examples(args.split)
    settings = get_settings()
    client = Client(api_key=settings.langsmith_api_key)

    dataset = client.create_dataset(dataset_name=DATASET_NAME)
    client.create_examples(dataset_id=dataset.id, examples=examples)
    dataset_version = client.read_dataset_version(dataset_id=dataset.id, tag="latest")
    client.update_dataset_tag(
        dataset_id=dataset.id,
        as_of=dataset_version.as_of,
        tag=args.tag,
    )
    print(f"Uploaded {len(examples)} {args.split} examples to {DATASET_NAME}.")


if __name__ == "__main__":
    main()
