from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.getenv("LANGFUSE_BASE_URL") and os.getenv("LANGFUSE_HOST"):
    os.environ["LANGFUSE_BASE_URL"] = os.getenv("LANGFUSE_HOST", "")

try:
    from langfuse import get_client, observe
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    def get_client() -> Any:
        return None


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def langfuse_client() -> Any:
    if not tracing_enabled():
        return None
    return get_client()


def flush_traces() -> None:
    if not tracing_enabled():
        return
    client = langfuse_client()
    if client is not None:
        client.flush()
