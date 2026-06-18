"""
LLM-as-a-Judge Evaluation Helpers — Reusable metrics for faithfulness,
answer relevancy, and correctness.
"""

from loguru import logger
from src.generation.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


def judge_with_llm(prompt: str, system_instruction: str) -> str:
    """Helper to query the local LLM as an evaluation judge."""
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=prompt),
        ]
        res = llm.invoke(messages)
        return res.content.strip()
    except Exception as e:
        logger.warning(f"LLM-as-a-judge evaluation failed: {e}")
        return "UNKNOWN (LLM error)"


def evaluate_faithfulness(context: str, response: str) -> float:
    """Check if the response is fully faithful to the context (no hallucinations)."""
    if not context.strip():
        # If no context was retrieved, and LLM generated an answer, it might be hallucinating
        return 0.0 if response.strip() else 1.0

    sys_instruction = "You are a strict QA evaluator. Your task is to check if the generated answer contains any claims or details NOT supported by the context."
    prompt = f"""## Context
{context}

## Generated Answer
{response}

Is the Generated Answer entirely supported by the Context? Do not allow any extrapolation.
Reply with exactly one word: 'YES' or 'NO'."""

    result = judge_with_llm(prompt, sys_instruction)
    return 1.0 if "YES" in result.upper() else 0.0


def evaluate_relevancy(question: str, response: str) -> float:
    """Check if the response actually answers the question."""
    sys_instruction = "You are a strict QA evaluator. Your task is to check if the generated answer directly and fully addresses the user question."
    prompt = f"""## Question
{question}

## Generated Answer
{response}

Does the Generated Answer directly and relevantly answer the Question?
Reply with exactly one word: 'YES' or 'NO'."""

    result = judge_with_llm(prompt, sys_instruction)
    return 1.0 if "YES" in result.upper() else 0.0


def evaluate_context_precision(
    retrieved_context: list[dict],
    ground_truth_source: str,
    ground_truth_page: str | int,
) -> float:
    """Evaluate how much of the retrieved context is relevant to the ground truth source."""
    if not retrieved_context:
        return 0.0

    matched = 0
    for chunk in retrieved_context:
        meta = chunk.get("metadata", {})
        if meta.get("filename") == ground_truth_source and str(meta.get("page_number")) == str(ground_truth_page):
            matched += 1

    return matched / len(retrieved_context)


def evaluate_context_recall(
    retrieved_context: list[dict],
    ground_truth_source: str,
    ground_truth_page: str | int,
) -> float:
    """Evaluate whether the ground truth source is present in the retrieved context."""
    if not retrieved_context:
        return 0.0

    for chunk in retrieved_context:
        meta = chunk.get("metadata", {})
        if meta.get("filename") == ground_truth_source and str(meta.get("page_number")) == str(ground_truth_page):
            return 1.0

    return 0.0


def evaluate_hallucination_rate(response: str, retrieved_context: str) -> float:
    """Estimate hallucination rate from response against the retrieved context."""
    if not response.strip():
        return 0.0

    sys_instruction = (
        "You are a strict evaluator. Determine whether any part of the generated answer is unsupported by the retrieved context. "
        "If the answer contains any hallucinated or invented details, reply with 'NO'. Otherwise reply with 'YES'."
    )
    prompt = f"""## Retrieved Context
{retrieved_context}

## Generated Answer
{response}

Is the Generated Answer fully supported by the Retrieved Context?
Reply with exactly one word: 'YES' or 'NO'."""

    result = judge_with_llm(prompt, sys_instruction)
    supported = "YES" in result.upper()
    return 0.0 if supported else 1.0


def evaluate_correctness(expected: str, response: str) -> float:
    """Evaluate how correct the response is compared to the expected answer."""
    sys_instruction = "You are a strict QA evaluator. Your task is to evaluate the semantic similarity and correctness of the generated answer compared to the expected ground truth answer."
    prompt = f"""## Expected Ground Truth Answer
{expected}

## Generated Answer
{response}

Evaluate the Generated Answer against the Expected Ground Truth Answer.
Is the Generated Answer:
1. 'CORRECT' (covers all key points of the expected answer)
2. 'PARTIAL' (covers some but not all points)
3. 'INCORRECT' (wrong or says it doesn't know when the expected answer exists)

Reply with exactly one word: 'CORRECT', 'PARTIAL', or 'INCORRECT'."""

    result = judge_with_llm(prompt, sys_instruction)
    result_upper = result.upper()
    if "CORRECT" in result_upper:
        return 1.0
    elif "PARTIAL" in result_upper:
        return 0.5
    else:
        return 0.0
