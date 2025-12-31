"""API request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from app.agents.state import TestCase


class GenerateRequest(BaseModel):
    """Request schema for POST /api/generate."""

    query: str = Field(
        description="User's problem description or coding task",
        min_length=1,
        max_length=1000,
        examples=["Write a function that calculates the average of a list of numbers"],
    )

    llm_provider: Literal["openai", "anthropic"] = Field(
        default="openai",
        description="LLM provider to use",
    )

    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for resuming/tracking",
    )

    user_provided_tests: Optional[list[TestCase]] = Field(
        default=None,
        description="Optional user-provided test cases (Directive 17)",
    )

    max_iterations: int = Field(
        default=5,
        description="Maximum iterations for error fixing",
        ge=1,
        le=10,
    )


class HealthResponse(BaseModel):
    """Response schema for GET /api/health."""

    status: str = Field(description="Health status", examples=["healthy"])
    app: str = Field(description="Application name")
    version: str = Field(description="Application version")


class MessageDTO(BaseModel):
    """Single message DTO for history playback"""
    type: str
    content: dict
    timestamp: str
    order: int

class SessionResponse(BaseModel):
    """Response schema for session endpoints."""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    status: str
    llm_provider: str
    total_tokens: int
    total_cost_usd: float
    iterations: int
    messages: Optional[List[MessageDTO]] = None

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
