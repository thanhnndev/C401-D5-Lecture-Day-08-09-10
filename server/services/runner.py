"""Gọi `src.rag_answer` và map kết quả sang luồng sự kiện SSE (AgentEvent)."""

from __future__ import annotations

import asyncio
import uuid
from typing import AsyncIterator

from server.schemas.events import (
    ConfidenceSignalEvent,
    DoneEvent,
    ErrorEvent,
    PipelineMetricsModel,
    PipelineSignalEvent,
    RetrievalChunkModel,
    RetrievalResultEvent,
    RouteDecisionEvent,
    StepStartedEvent,
    TokenEvent,
)
from server.schemas.chat import ChatMessage


def _last_user_query(messages: list[ChatMessage]) -> str | None:
    for m in reversed(messages):
        if m.role == "user":
            q = m.content.strip()
            return q if q else None
    return None


def _chunks_to_retrieval_event(chunks: list[object]) -> RetrievalResultEvent:
    items: list[RetrievalChunkModel] = []
    for i, c in enumerate(chunks):
        if not isinstance(c, dict):
            continue
        meta = c.get("metadata") or {}
        text = str(c.get("text") or "")
        src = meta.get("source", "unknown")
        excerpt = text[:300] + ("..." if len(text) > 300 else "")
        score = c.get("score", 0.0)
        try:
            score_f = float(score)
        except (TypeError, ValueError):
            score_f = 0.0
        items.append(
            RetrievalChunkModel(
                id=f"chunk-{i}",
                title=str(src),
                excerpt=excerpt,
                score=score_f,
                source=str(src) if src else None,
            )
        )
    return RetrievalResultEvent(chunks=items)


def _token_deltas(answer: str) -> list[str]:
    if not answer:
        return ["\n"]
    parts: list[str] = []
    words = answer.split(" ")
    for i, w in enumerate(words):
        parts.append((" " if i > 0 else "") + w)
    return parts if parts else [answer]


async def stream_rag_events(
    *,
    messages: list[ChatMessage],
    thread_id: str | None,
) -> AsyncIterator[
    StepStartedEvent
    | RouteDecisionEvent
    | RetrievalResultEvent
    | ConfidenceSignalEvent
    | PipelineSignalEvent
    | TokenEvent
    | ErrorEvent
    | DoneEvent
]:
    trace_id = thread_id or str(uuid.uuid4())

    yield StepStartedEvent(
        stepId="sv-1",
        label="Supervisor đang phân tích yêu cầu",
        node="supervisor",
    )
    yield RouteDecisionEvent(
        route="rag_dense",
        reason="Chọn pipeline RAG grounded (src/rag_answer.py)",
    )

    query = _last_user_query(messages)
    if not query:
        yield ErrorEvent(message="Thiếu tin nhắn user.", code="no_user_message")
        yield DoneEvent(traceId=trace_id)
        return

    yield StepStartedEvent(
        stepId="ret-1",
        label="Retrieval (dense)",
        node="retrieval",
    )

    def _call_rag():
        from src.rag_answer import rag_answer

        return rag_answer(query, retrieval_mode="dense", verbose=False)

    try:
        result = await asyncio.to_thread(_call_rag)
    except NotImplementedError as e:
        yield ErrorEvent(message=str(e), code="not_implemented")
        yield DoneEvent(traceId=trace_id)
        return
    except Exception as e:
        yield ErrorEvent(message=str(e), code="rag_error")
        yield DoneEvent(traceId=trace_id)
        return

    chunks = result.get("chunks_used") or []
    yield _chunks_to_retrieval_event(chunks)

    yield StepStartedEvent(
        stepId="pol-1",
        label="Policy (tùy chọn)",
        node="policy",
    )
    yield StepStartedEvent(
        stepId="syn-1",
        label="Synthesis",
        node="synthesis",
    )

    yield ConfidenceSignalEvent(
        level="medium",
        reason="RAG grounded từ retrieved chunks",
    )

    answer = str(result.get("answer") or "")
    for delta in _token_deltas(answer):
        yield TokenEvent(delta=delta)

    yield PipelineSignalEvent(
        metrics=PipelineMetricsModel(
            freshnessMinutes=45.0,
            volume24h=120.0,
            schemaHealth="ok",
            label="demo",
        )
    )

    yield DoneEvent(traceId=trace_id)
