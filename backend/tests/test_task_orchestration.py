import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.research import create_task, list_tasks, update_task
from app.db import Base
from app.models import TaskConfigVersion
from app.schemas import ResearchTaskCreate
from app.schemas import ResearchTaskUpdate


def test_task_accepts_multiple_unique_idx_tickers():
    task = ResearchTaskCreate(
        name="Banking quality",
        thesis="Compare large Indonesian banks under one repeatable research mandate.",
        tickers=["bbca", "BBRI", "bbca"],
        horizon_days=120,
        capital_idr="250000000",
    )
    assert task.tickers == ["BBCA", "BBRI"]
    assert task.ticker == "BBCA"
    assert task.cadence == "manual"
    assert "ai_review" in task.analysis_modules


def test_legacy_single_ticker_payload_remains_supported():
    task = ResearchTaskCreate(ticker="tlkm")
    assert task.ticker == "TLKM"
    assert task.tickers == ["TLKM"]
    assert task.name == "TLKM research task"


def test_task_rejects_more_than_ten_tickers():
    with pytest.raises(ValidationError):
        ResearchTaskCreate(tickers=[f"IDX{i}" for i in range(11)])


def test_task_rejects_unknown_methodology_module():
    with pytest.raises(ValidationError):
        ResearchTaskCreate(ticker="BBCA", analysis_modules=["technical", "prompt_decides_action"])


def test_task_crud_publishes_immutable_config_versions():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        created = create_task(
            ResearchTaskCreate(
                name="IDX banks",
                thesis="Repeatable comparison",
                tickers=["BBCA", "BBRI"],
            ),
            db,
        )
        assert created.tickers == ["BBCA.JK", "BBRI.JK"]
        assert created.config_version == 1

        updated = update_task(
            created.id,
            ResearchTaskUpdate(tickers=["BBCA", "BBRI", "BMRI"], horizon_days=180),
            db,
        )
        assert updated.tickers == ["BBCA.JK", "BBRI.JK", "BMRI.JK"]
        assert updated.horizon_days == 180
        assert updated.config_version == 2
        assert db.query(TaskConfigVersion).filter_by(task_id=created.id).count() == 2
        assert list_tasks(db)[0].config_hash == updated.config_hash
    finally:
        db.close()
        engine.dispose()
