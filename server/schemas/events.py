"""Mirror frontend/lib/types/agent-events.ts for JSON SSE lines."""

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class RetrievalChunkModel(BaseModel):
    id: str
    title: str
    excerpt: str
    score: float
    source: Optional[str] = None


class PipelineMetricsModel(BaseModel):
    freshnessMinutes: float
    volume24h: float
    schemaHealth: Literal["ok", "degraded", "stale"]
    label: Optional[str] = None


class StepStartedEvent(BaseModel):
    type: Literal["step_started"] = "step_started"
    stepId: str
    label: str
    node: Literal["supervisor", "retrieval", "policy", "synthesis"]


class RouteDecisionEvent(BaseModel):
    type: Literal["route_decision"] = "route_decision"
    route: str
    reason: str


class RetrievalResultEvent(BaseModel):
    type: Literal["retrieval_result"] = "retrieval_result"
    chunks: list[RetrievalChunkModel]


class ConfidenceSignalEvent(BaseModel):
    type: Literal["confidence_signal"] = "confidence_signal"
    level: Literal["high", "medium", "low"]
    reason: Optional[str] = None


class HumanCheckpointEvent(BaseModel):
    type: Literal["human_checkpoint"] = "human_checkpoint"
    prompt: str
    context: Optional[str] = None


class EmailDraftEvent(BaseModel):
    type: Literal["email_draft"] = "email_draft"
    draftId: str
    to: str
    subject: str
    body: str


class TokenEvent(BaseModel):
    type: Literal["token"] = "token"
    delta: str


class PipelineSignalEvent(BaseModel):
    type: Literal["pipeline_signal"] = "pipeline_signal"
    metrics: PipelineMetricsModel


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str
    code: Optional[str] = None


class DoneEvent(BaseModel):
    type: Literal["done"] = "done"
    traceId: Optional[str] = None


AgentEventModel = Annotated[
    Union[
        StepStartedEvent,
        RouteDecisionEvent,
        RetrievalResultEvent,
        ConfidenceSignalEvent,
        HumanCheckpointEvent,
        EmailDraftEvent,
        TokenEvent,
        PipelineSignalEvent,
        ErrorEvent,
        DoneEvent,
    ],
    Field(discriminator="type"),
]
