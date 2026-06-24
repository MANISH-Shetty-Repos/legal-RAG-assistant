"""
LLM Wrapper — Groq Cloud LLM (Qwen3-32B) for response generation.
"""

import sys
from loguru import logger
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from src.config import get_config


_llm: ChatGroq | None = None


def get_llm() -> ChatGroq:
    """Get or create the singleton LLM instance."""
    global _llm

    if _llm is None:
        config = get_config()

        if not config.llm.api_key:
            logger.error(
                "GROQ_API_KEY is not set. "
                "Get your free API key at https://console.groq.com/keys "
                "and add it to your .env file: GROQ_API_KEY=your_key_here"
            )
            sys.exit(1)

        logger.info(f"Initializing LLM: {config.llm.model} via Groq Cloud")

        _llm = ChatGroq(
            model=config.llm.model,
            api_key=config.llm.api_key,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            reasoning_format="hidden",
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
