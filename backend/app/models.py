from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchTask(Base):
    __tablename__ = "research_task"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, default=90)
    capital_idr: Mapped[str] = mapped_column(String(64), default="100000000")
    params_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    runs: Mapped[list["TaskRun"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class TaskConfigVersion(Base):
    __tablename__ = "task_config_version"
    __table_args__ = (UniqueConstraint("task_id", "version", name="uq_task_config_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(ForeignKey("research_task.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    config_hash: Mapped[str] = mapped_column(String(80), index=True)
    config_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TaskRun(Base):
    __tablename__ = "task_run"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Mapped[str] = mapped_column(ForeignKey("research_task.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    task: Mapped[ResearchTask] = relationship(back_populates="runs")


class RunEvent(Base):
    __tablename__ = "run_event"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(ForeignKey("task_run.id"), index=True)
    stage: Mapped[str] = mapped_column(String(64), index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RecommendationVersion(Base):
    __tablename__ = "recommendation_version"
    __table_args__ = (UniqueConstraint("run_id", "version", name="uq_recommendation_run_version"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(ForeignKey("task_run.id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    research_action: Mapped[str] = mapped_column(String(32))
    content_hash: Mapped[str] = mapped_column(String(80), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EvidenceItem(Base):
    __tablename__ = "evidence_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(ForeignKey("task_run.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(64))
    source_name: Mapped[str] = mapped_column(String(128))
    source_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    content_hash: Mapped[str] = mapped_column(String(80), index=True)
