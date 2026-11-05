"""Judge answer correctness and policy-evidence grounding for evaluation runs."""

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from evals.judge_tools import get_value
from src.settings import get_settings

settings = get_settings()


class JudgeResult(BaseModel):
    """Define the structured result returned by either LLM judge."""

    passed: bool = Field(
        description="True when the assistant answer satisfies the criterion."
    )
    reasoning: str = Field(
        description=(
            "A short explanation of the decision, naming any relevant omission "
            "or unsupported claim."
        )
    )


judge = init_chat_model(
    "openai:gpt-5.6-terra",
    temperature=0,
    api_key=settings.openai_api_key,
).with_structured_output(JudgeResult)


def messages_from(run):
    """Return the agent message history from an evaluation run."""
    outputs = get_value(run, "outputs", {}) or {}
    return get_value(outputs, "messages", []) or []


def _text_from_content(content) -> str:
    """Convert string or content-block messages into readable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(get_value(block, "text", ""))
            for block in content
            if get_value(block, "text")
        )
    return str(content or "")


def final_answer(run) -> str:
    """Return the final answer written by the policy agent."""
    for message in reversed(messages_from(run)):
        if get_value(message, "type") == "ai":
            answer = _text_from_content(get_value(message, "content", ""))
            if answer:
                return answer
    return ""


def user_question(run, example) -> str:
    """Return the question that the agent was asked."""
    run_inputs = get_value(run, "inputs", {}) or {}
    example_inputs = get_value(example, "inputs", {}) or {}
    return str(
        get_value(run_inputs, "human")
        or get_value(example_inputs, "human")
        or ""
    )


def retrieved_evidence(run) -> str:
    """Return policy text supplied by search_kb during the agent run."""
    evidence = [
        _text_from_content(get_value(message, "content", ""))
        for message in messages_from(run)
        if get_value(message, "name") == "search_kb"
    ]
    return "\n\n".join(text for text in evidence if text)


def reference_answer(example) -> str:
    """Return the expected answer from the golden dataset."""
    outputs = get_value(example, "outputs", {}) or {}
    return str(get_value(outputs, "reference_output", "") or "")


def correctness(run, example):
    """Judge whether the answer directly and accurately answers the question."""
    result = judge.invoke(
        f"""You are grading a hospital-policy assistant.

Decide whether the assistant answers the user's question accurately and directly.
Use the reference answer to identify required facts, but require only facts that
are relevant to the user's question. The assistant may use different wording.
Fail if it omits a requested policy fact, adds a materially incorrect claim, or
buries the answer in unrelated detail. Concise answers pass when they fully
answer the question; do not require unrelated facts merely because they appear
in the reference answer.

User question:
{user_question(run, example)}

Reference answer:
{reference_answer(example)}

Assistant answer:
{final_answer(run)}
"""
    )

    return {"score": int(result.passed), "comment": result.reasoning}


def groundedness(run, example):
    """Judge policy claims against the evidence retrieved in this run."""
    result = judge.invoke(
        f"""You are judging whether a hospital-policy answer is grounded in its
retrieved policy evidence. The retrieved passages are the only source of truth
for policy claims; do not use the reference answer as evidence.

Check each policy-specific factual claim and citation in the answer against the
retrieved passages. The answer may be concise and does not need to repeat every
fact in the passages. Fail unsupported policy claims, invented details, or
citations that do not match the passages.

A greeting, refusal, clarifying question, or direction to contact a supervisor
or hospital line is routing behavior, not a policy claim; do not fail it solely
because it is absent from retrieved passages. However, a statement that a policy
requires something or does not specify a requested detail is a policy claim.
For a claim that a policy omits a detail, pass only when relevant policy evidence
was retrieved and that evidence supports the limited statement. An empty
retrieval result cannot establish that the policy corpus lacks the information.

User question:
{user_question(run, example)}

Retrieved policy evidence:
{retrieved_evidence(run)}

Assistant answer:
{final_answer(run)}
"""
    )

    return {"score": int(result.passed), "comment": result.reasoning}
