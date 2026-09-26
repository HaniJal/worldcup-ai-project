from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.data.database import Base


class IpRequestCount(Base):
    """
    Tracks, per (ip_address, endpoint) pair, how many times that IP has ever
    called that endpoint. Used to enforce a lifetime cap per visitor on the
    costly AI endpoints, independent of any time window.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6-safe length
    endpoint: Mapped[str] = mapped_column(String(50), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (UniqueConstraint("ip_address", "endpoint", name="uq_ip_endpoint"),)


class ApiSpendLog(Base):
    """
    One row per billable API call (Claude generation, Tavily search), with
    an estimated USD cost. The running total across all rows is compared
    against a hard budget ceiling before allowing further calls.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    endpoint: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # "anthropic" | "tavily"
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class ResponseCache(Base):
    """
    Permanent cache of (endpoint, normalized_question) -> full JSON response.
    A repeat of the same question, from any visitor, is served from here
    instead of making a fresh paid API call. Cache hits don't count against
    a visitor's rate limit or add to the spend total, since no paid call
    was made.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    endpoint: Mapped[str] = mapped_column(String(50), nullable=False)
    question_key: Mapped[str] = mapped_column(String(500), nullable=False)
    response_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (UniqueConstraint("endpoint", "question_key", name="uq_endpoint_question"),)
