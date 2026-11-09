"""Upload the full evaluation dataset with split labels to LangSmith."""

import argparse
import json
from pathlib import Path

from langsmith import Client
from src.settings import get_settings

DATASET_NAME = "northbridge-policy-golden"
DATASET_PATH = Path(__file__).resolve().parent / "data" / "golden_dataset.json"
SPLITS = ("optimization", "holdout")


# -----------------------------------------------------------------------------
# Step 1: Prepare the requested examples and validate their local IDs.
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Step 2: Create or reuse the dataset and upload missing splits.
# -----------------------------------------------------------------------------

def main() -> None:
    """Upload both splits and tag the resulting dataset version."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    examples_by_split = {split: load_examples(split) for split in SPLITS}
    settings = get_settings()
    client = Client(api_key=settings.langsmith_api_key)

    # Reuse the dataset so optimization and holdout can share one dataset.
    if client.has_dataset(dataset_name=DATASET_NAME):
        dataset = client.read_dataset(dataset_name=DATASET_NAME)
    else:
        dataset = client.create_dataset(dataset_name=DATASET_NAME)

    # Check both splits before uploading so partial datasets are not duplicated.
    missing_splits = []
    for split, examples in examples_by_split.items():
        existing = list(client.list_examples(dataset_id=dataset.id, splits=[split]))
        if not existing:
            missing_splits.append(split)
            continue

        local_ids = {example["metadata"]["id"] for example in examples}
        remote_ids = [(example.metadata or {}).get("id") for example in existing]
        if len(existing) != len(examples) or set(remote_ids) != local_ids:
            raise ValueError(
                f"The {split!r} split is incomplete or does not match local example IDs; "
                "review it in LangSmith before uploading."
            )
        print(f"Skipping existing {split} split ({len(existing)} examples).")

    for split in missing_splits:
        examples = examples_by_split[split]
        client.create_examples(dataset_id=dataset.id, examples=examples)
        print(f"Uploaded {len(examples)} {split} examples to {DATASET_NAME}.")

    dataset_version = client.read_dataset_version(dataset_id=dataset.id, tag="latest")
    client.update_dataset_tag(
        dataset_id=dataset.id,
        as_of=dataset_version.as_of,
        tag=args.tag,
    )
    print(f"Tagged dataset version as {args.tag!r}.")


if __name__ == "__main__":
    main()
