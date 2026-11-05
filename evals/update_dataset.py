"""Update existing LangSmith examples while keeping local IDs only in metadata."""

import argparse
from langsmith import Client
from evals.upload_dataset import DATASET_NAME, load_examples
from src.settings import get_settings

def build_updates(examples: list[dict], existing: list) -> list[dict]:
    """Return updates matched to unique existing LangSmith example UUIDs."""
    updates = []
    matched_ids = set()
    for example in examples:
        local_id = example["metadata"]["id"]
        matches = [
            remote for remote in existing
            if (remote.metadata or {}).get("id") == local_id
        ]
        if not matches:
            matches = [
                remote for remote in existing
                if not (remote.metadata or {}).get("id")
                and remote.inputs == example["inputs"]
            ]
        if len(matches) != 1:
            raise ValueError(
                f"{local_id}: expected one existing example, found {len(matches)}."
            )
        remote = matches[0]
        if remote.id in matched_ids:
            raise ValueError(f"{local_id}: another local example has the same target.")
        matched_ids.add(remote.id)

        updates.append({
            "example_id": remote.id,
            "inputs": example["inputs"],
            "outputs": example["reference_outputs"],
            "metadata": {**(remote.metadata or {}), **example["metadata"]},
            "split": example["split"],
        })
    return updates

def main() -> None:
    """Update the requested split without creating or deleting examples."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["optimization", "holdout"], required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    examples = load_examples(args.split)
    settings = get_settings()
    client = Client(api_key=settings.langsmith_api_key)

    dataset = client.read_dataset(dataset_name=DATASET_NAME)
    existing = list(client.list_examples(dataset_id=dataset.id, splits=[args.split]))
    updates = build_updates(examples, existing)
    for update in updates:
        client.update_example(dataset_id=dataset.id, **update)

    dataset_version = client.read_dataset_version(dataset_id=dataset.id, tag="latest")
    client.update_dataset_tag(
        dataset_id=dataset.id,
        as_of=dataset_version.as_of,
        tag=args.tag,
    )
    print(f"Updated {len(updates)} {args.split} examples in {DATASET_NAME}.")


if __name__ == "__main__":
    main()
