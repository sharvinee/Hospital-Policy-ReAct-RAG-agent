"""Export a LangSmith experiment summary to evals/results."""

import argparse
import json
import math
import statistics
import sys
from datetime import UTC
from decimal import Decimal
from pathlib import Path
from typing import Any

from langsmith import Client
from langsmith.schemas import Run

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.settings import get_settings

# -----------------------------------------------------------------------------
# Step 1: Define the local output paths and evaluator names.
# -----------------------------------------------------------------------------

RESULTS_DIR = PROJECT_ROOT / "evals" / "results"
RESULTS_TABLE = RESULTS_DIR / "results.md"
EVALUATOR_KEYS = (
    "retrieval_precision",
    "retrieval_recall",
    "tool_match",
    "correctness",
    "groundedness",
)


# -----------------------------------------------------------------------------
# Step 2: Summarize experiment latency, recorded costs, and evaluator scores.
# -----------------------------------------------------------------------------


def percentile(sorted_values: list[float], pct: float) -> float:
    """Return a nearest-rank percentile from an already sorted list."""
    if not sorted_values:
        return 0.0
    index = max(0, math.ceil(pct / 100 * len(sorted_values)) - 1)
    return sorted_values[min(index, len(sorted_values) - 1)]


def latency_seconds(run: Run) -> float | None:
    """Return the run duration in seconds when both timestamps exist."""
    if run.start_time and run.end_time:
        return (run.end_time - run.start_time).total_seconds()
    return None


def feedback_score(run: Run, key: str) -> float | None:
    """Read an evaluator's average score from LangSmith run feedback stats."""
    stats = (run.feedback_stats or {}).get(key)
    if stats and stats.get("avg") is not None:
        return float(stats["avg"])
    return None


def evaluator_summary(runs: list[Run], key: str) -> dict[str, Any] | None:
    """Summarize mean score and perfect-score count for one evaluator."""
    scores = [
        score
        for score in (feedback_score(run, key) for run in runs)
        if score is not None
    ]
    if not scores:
        return None
    return {
        "mean_score": round(statistics.fmean(scores), 4),
        "rows_passed": sum(score == 1.0 for score in scores),
        "rows_judged": len(scores),
    }


def build_summary(experiment_name: str, runs: list[Run], dataset_name: str | None) -> dict[str, Any]:
    """Build the JSON summary for an experiment's root runs."""
    latencies = sorted(
        duration
        for duration in (latency_seconds(run) for run in runs)
        if duration is not None
    )
    started_at = min((run.start_time for run in runs if run.start_time), default=None)
    # Root run cost includes recorded child-run costs without double-counting.
    costs = [run.total_cost for run in runs if run.total_cost is not None]
    summary: dict[str, Any] = {
        "experiment_name": experiment_name,
        "dataset_name": dataset_name,
        "run_started_at": (
            started_at.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            if started_at
            else None
        ),
        "total_examples": len(runs),
        "errors": sum(bool(run.error) for run in runs),
        "latency_seconds": {
            "p50": round(percentile(latencies, 50), 2),
            "p99": round(percentile(latencies, 99), 2),
            "max": round(latencies[-1], 2) if latencies else 0.0,
        },
        # An incomplete cost must not be presented as the experiment total.
        "total_cost_usd": float(sum(costs, Decimal("0"))) if len(costs) == len(runs) else None,
        "runs_with_cost": len(costs),
    }
    for key in EVALUATOR_KEYS:
        if block := evaluator_summary(runs, key):
            summary[key] = block
    return summary


# -----------------------------------------------------------------------------
# Step 3: Save experiment results and update the comparison table.
# -----------------------------------------------------------------------------

def update_results_table(summary: dict[str, Any], table_path: Path) -> None:
    """Add or update one experiment row without changing other rows."""
    name = summary["experiment_name"]
    metrics = [summary.get(key, {}).get("mean_score") for key in EVALUATOR_KEYS]
    values = [f"{value:.4f}" if value is not None else "N/A" for value in metrics]
    latency = summary["latency_seconds"]
    cost = summary["total_cost_usd"]
    row = (
        f"| `{name}` | " + " | ".join(values)
        + f" | {latency['p50']:.2f} | {latency['p99']:.2f} | "
        + (f"${cost:.8f}" if cost is not None else "N/A") + " |"
    )
    contents = table_path.read_text(encoding="utf-8")
    lines = contents.splitlines()
    prefix = f"| `{name}` |"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = row
            break
    else:
        lines.append(row)
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_experiment(experiment_name: str) -> Path:
    """Fetch an experiment from LangSmith and write its summary JSON."""
    if Path(experiment_name).name != experiment_name:
        raise SystemExit("Experiment name must not contain path components.")

    client = Client(api_key=get_settings().langsmith_api_key)
    project = client.read_project(project_name=experiment_name)
    runs = list(client.list_runs(project_name=experiment_name, is_root=True))
    if not runs:
        raise SystemExit(f"No runs found in experiment {experiment_name!r}.")

    dataset_name = None
    if project.reference_dataset_id:
        dataset = client.read_dataset(dataset_id=project.reference_dataset_id)
        dataset_name = dataset.name

    summary = build_summary(experiment_name, runs, dataset_name)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / f"{experiment_name}.json"
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    update_results_table(summary, RESULTS_TABLE)
    scores = ", ".join(
        f"{key} {block['rows_passed']}/{block['rows_judged']}"
        for key in EVALUATOR_KEYS
        if (block := summary.get(key))
    )
    suffix = f"; {scores}" if scores else ""
    print(f"Wrote {output_path} ({len(runs)} runs{suffix}).")
    return output_path


def main() -> None:
    """Parse command-line arguments and export the requested experiment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_name", help="LangSmith experiment/project name.")
    args = parser.parse_args()
    export_experiment(args.experiment_name)


if __name__ == "__main__":
    main()
