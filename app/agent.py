from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_client, observe

try:
    from langfuse import propagate_attributes
except Exception:  # pragma: no cover
    propagate_attributes = None


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="agent-run", capture_input=False, capture_output=False)
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        langfuse = langfuse_client()

        started = time.perf_counter()
        attr_context = (
            propagate_attributes(
                user_id=hash_user_id(user_id),
                session_id=session_id,
                tags=["lab", feature, self.model],
                trace_name="chat-request",
                metadata={"feature": feature, "model": self.model},
            )
            if propagate_attributes is not None
            else None
        )

        if attr_context is None:
            docs, response = self._run_steps(message, feature, langfuse)
        else:
            with attr_context:
                if langfuse is not None:
                    langfuse.set_current_trace_io(
                        input={"message_preview": summarize_text(message), "feature": feature},
                    )
                    langfuse.update_current_span(metadata={"feature": feature, "model": self.model})
                docs, response = self._run_steps(message, feature, langfuse)

        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)

        if langfuse is not None:
            langfuse.set_current_trace_io(
                output={"answer_preview": summarize_text(response.text)},
            )
            langfuse.update_current_span(
                output={"answer_preview": summarize_text(response.text)},
                metadata={"doc_count": len(docs), "latency_ms": latency_ms, "quality_score": quality_score},
            )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

    def _run_steps(self, message: str, feature: str, langfuse) -> tuple[list[str], Any]:
        docs = retrieve(message)
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"

        if langfuse is None:
            return docs, self.llm.generate(prompt)

        with langfuse.start_as_current_observation(
            as_type="generation",
            name="fake-llm-generate",
            model=self.model,
            input={"prompt_preview": summarize_text(prompt)},
        ):
            response = self.llm.generate(prompt)
            langfuse.update_current_generation(
                output=summarize_text(response.text),
                usage_details={
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                },
            )
            return docs, response

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
