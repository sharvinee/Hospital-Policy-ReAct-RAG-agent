"""Score policy retrieval and tool choice recorded in LangSmith evaluation runs."""

import re
from evals.judge_tools import get_value


def get_retrieved_chunk_ids(run) -> list[str]:
    """Return chunk IDs that search_kb retrieved during agent run."""
    outputs = get_value(run, "outputs", {}) or {}
    messages = get_value(outputs, "messages", []) or []
    retrieved_chunk_ids: list[str] = []

    for message in messages:
        tool_name = get_value(message, "name")
        if tool_name == "search_kb":
            tool_result = str(get_value(message, "content", ""))
            retrieved_chunk_ids.extend(
                re.findall(r"Citation ID: (SEC_\d+)", tool_result)
            )

    return list(dict.fromkeys(retrieved_chunk_ids))


def get_expected_chunk_ids(example) -> list[str]:
    """Return ground-truth chunk IDs from the example metadata."""
    metadata = get_value(example, "metadata", {}) or {}
    return metadata.get("expected_chunk_ids", [])


def retrieval_precision(run, example):
    """Measure relevance of retrieved chunks."""
    expected_chunk_ids = get_expected_chunk_ids(example)
    retrieved_chunk_ids = get_retrieved_chunk_ids(run)

    if not expected_chunk_ids:
        return {
            "score": float(not retrieved_chunk_ids),
            "comment": (
                "No chunks were retrieved for a question with no expected chunks."
                if not retrieved_chunk_ids
                else "Retrieved chunks for a question with no expected chunks."
            ),
        }

    correct_chunk_ids = set(retrieved_chunk_ids) & set(expected_chunk_ids)
    if not retrieved_chunk_ids:
        score = 0.0
    else:
        score = len(correct_chunk_ids) / len(retrieved_chunk_ids)
    return {
        "score": score,
        "comment": (
            f"Retrieved {len(correct_chunk_ids)} expected chunk(s) out of "
            f"{len(retrieved_chunk_ids)} retrieved chunks."
        ),
    }


def retrieval_recall(run, example):
    """Measure whether retrieval found every expected chunk."""
    expected_chunk_ids = get_expected_chunk_ids(example)
    retrieved_chunk_ids = get_retrieved_chunk_ids(run)

    if not expected_chunk_ids:
        return {
            "score": float(not retrieved_chunk_ids),
            "comment": (
                "No chunks were retrieved for a question with no expected chunks."
                if not retrieved_chunk_ids
                else "Retrieved chunks for a question with no expected chunks."
            ),
        }

    correct_chunk_ids = set(retrieved_chunk_ids) & set(expected_chunk_ids)

    score = len(correct_chunk_ids) / len(expected_chunk_ids)

    return {
        "score": score,
        "comment": (
            f"Found {len(correct_chunk_ids)} of "
            f"{len(expected_chunk_ids)} expected chunk(s)."
        ),
    }

def tool_match(run, example):
    """Check that the agent selected the expected set of tools."""
    outputs = get_value(run, "outputs", {}) or {}
    messages = get_value(outputs, "messages", []) or []
    actual_tools = {
        get_value(message, "name")
        for message in messages
        if get_value(message, "type") == "tool"
    }

    metadata = get_value(example, "metadata", {}) or {}
    expected_tools = set(metadata.get("expected_tools", []))
    matched = actual_tools == expected_tools

    if matched:
        comment = f"Matched expected tools: {sorted(expected_tools)}."
    else:
        comment = (
            f"Expected tools: {sorted(expected_tools)}. "
            f"Actual tools: {sorted(actual_tools)}."
        )

    return {
        "key": "tool_match",
        "score": int(matched),
        "comment": comment,
    }
