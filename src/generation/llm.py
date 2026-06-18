"""
LLM Wrapper — Ollama-served LLM (Qwen3/Llama3) for response generation.
"""

from loguru import logger
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_config


_llm: ChatOllama | None = None


def get_llm() -> ChatOllama:
    """Get or create the singleton LLM instance."""
    global _llm

    if _llm is None:
        config = get_config()

        logger.info(f"Initializing LLM: {config.llm.model} @ {config.llm.base_url}")

        _llm = ChatOllama(
            model=config.llm.model,
            base_url=config.llm.base_url,
            temperature=config.llm.temperature,
            num_predict=config.llm.max_tokens,
        )

        logger.info(f"LLM initialized: {config.llm.model}")

    return _llm


def generate_response(
    query: str,
    context_chunks: list[dict],
    system_prompt: str | None = None,
    response_mode: str = "normal",
) -> str:
    """
    Generate a response using the LLM with retrieved context.

    Args:
        query: User's question
        context_chunks: List of retrieved chunk dicts (must have 'text', 'metadata' keys)
        system_prompt: Optional custom system prompt
        response_mode: The response mode ('legal', 'simple', 'normal')

    Returns:
        LLM-generated response string
    """
    from src.generation.prompts import build_system_prompt, build_user_prompt

    llm = get_llm()

    sys_prompt = system_prompt or build_system_prompt(response_mode)
    user_prompt = build_user_prompt(query, context_chunks)

    messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_prompt),
    ]

    logger.info(f"Generating response for: '{query[:80]}...' [Mode: {response_mode}]")

    response = llm.invoke(messages)
    response_text = response.content

    logger.info(f"Response generated ({len(response_text)} chars)")

    return response_text
