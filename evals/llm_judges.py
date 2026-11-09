"""Judge answer correctness and policy-evidence grounding for evaluation runs."""

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from evals.judge_tools import get_value
from src.settings import get_settings
from src.prompts import HOSPITAL_ADDRESS, HOSPITAL_CONTACT_NUMBER

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

Decide whether the assistant answers the user’s question accurately, directly,
and completely.

Use the reference answer to identify the facts required to answer the question,
but treat it as a potentially non-exhaustive example. The assistant may use
different wording and may include additional directly relevant details.

Pass an answer when it covers all requested facts and any added detail is
consistent with the reference, retrieved evidence, and the question’s scope.
Do not fail an answer merely because it is more complete than the reference.

Fail an answer if it:
- omits a fact necessary to answer the user’s question;
- states a materially incorrect or contradictory claim;
- adds irrelevant, unsupported, or out-of-scope detail; or
- buries the requested answer in unnecessary information.

A concise answer passes when it fully answers the question. Do not require
unrelated facts solely because they appear in the reference answer.

User question:
{user_question(run, example)}

Reference answer:
{reference_answer(example)}

Retrieved policy evidence:
{retrieved_evidence(run)}

Assistant answer:
{final_answer(run)}
"""
    )

    return {"score": int(result.passed), "comment": result.reasoning}


def groundedness(run, example):
    """Judge policy claims against the evidence retrieved in this run."""
    result = judge.invoke(
    f"""You are judging whether a hospital-policy answer is grounded in the
policy evidence retrieved during this run. Retrieved passages are the only
source of truth for policy-specific claims. Do not use the reference answer as
evidence.

Check every policy-specific factual claim and every citation in the assistant
answer against the retrieved passages. Pass concise answers; they do not need to
repeat all retrieved facts. Fail an answer if it contains an unsupported policy
claim, an invented detail, or a citation that does not support the claim it
accompanies.

Greetings, refusals, clarifying questions, and directions to contact a
supervisor or hospital line are routing behavior rather than policy claims.
Do not fail them merely because they are absent from retrieved passages.

A refusal such as “I am not permitted to answer that question” is an
instruction-based scope restriction, not a claim about hospital policy.
Pass it without retrieved evidence, provided it does not invent a specific
hospital policy or cite unsupported policy text.

The agent is given the following approved hospital contact information:
- Address: {HOSPITAL_ADDRESS}
- General line: {HOSPITAL_CONTACT_NUMBER}

These contact details do not require retrieved policy evidence. A different
address or phone number must be supported by evidence.

Claims that a policy requires something, permits something, or does not specify
a requested detail are policy claims. A “not specified” claim passes only when
relevant policy text was retrieved and that text supports the limited claim.
The claim must be scoped to the retrieved policy information; it must not imply
that the entire policy corpus lacks the detail.

An empty retrieval result cannot support a claim about what hospital policies
do or do not specify. When no relevant evidence was retrieved, a non-policy
uncertainty response or the approved contact information above may pass. Do
not pass a claim that the policies lack a detail solely because retrieval
returned no evidence.

User question:
{user_question(run, example)}

Retrieved policy evidence:
{retrieved_evidence(run)}

Assistant answer:
{final_answer(run)}
"""
    )

    return {"score": int(result.passed), "comment": result.reasoning}
