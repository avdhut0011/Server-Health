import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.server import Server
from app.models.alert import Alert
from app.services.alerts.state_machine import AlertStateMachine

@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_alert_deduplication_and_escalation(async_db: AsyncSession):
    # Create test server
    server = Server(
        id="srv-test-01",
        hostname="web-srv-01",
        display_name="Production Web 01",
        ip_address="192.168.1.10",
        os_type="LINUX",
        agent_status="ONLINE",
        overall_health="HEALTHY",
        is_in_maintenance=False
    )
    async_db.add(server)
    await async_db.commit()

    # 1. Trigger initial WARNING alert
    alert1, is_new, should_notify = await AlertStateMachine.process_problem(
        db=async_db,
        server=server,
        component_id=None,
        component_identifier="cpu",
        metric_name="CPU Utilization",
        trigger_value="75%",
        threshold_value="70%",
        severity="WARNING",
        problem_title="CPU High"
    )
    await async_db.commit()

    assert is_new is True
    assert should_notify is True
    assert alert1.status == "ACTIVE"
    assert alert1.severity == "WARNING"

    # 2. Repeated breach at 76% (same severity) -> Must be deduplicated (no notify)
    alert2, is_new2, should_notify2 = await AlertStateMachine.process_problem(
        db=async_db,
        server=server,
        component_id=None,
        component_identifier="cpu",
        metric_name="CPU Utilization",
        trigger_value="76%",
        threshold_value="70%",
        severity="WARNING",
        problem_title="CPU High"
    )
    await async_db.commit()

    assert is_new2 is False
    assert should_notify2 is False  # DEDUPLICATED
    assert alert2.id == alert1.id
    assert alert2.trigger_value == "76%"

    # 3. Severity escalation to CRITICAL (95%) -> Should notify
    alert3, is_new3, should_notify3 = await AlertStateMachine.process_problem(
        db=async_db,
        server=server,
        component_id=None,
        component_identifier="cpu",
        metric_name="CPU Utilization",
        trigger_value="95%",
        threshold_value="90%",
        severity="CRITICAL",
        problem_title="CPU Critical"
    )
    await async_db.commit()

    assert is_new3 is False
    assert should_notify3 is True  # Escalation triggers notification
    assert alert3.severity == "CRITICAL"
    assert alert3.trigger_value == "95%"

    # 4. Recovery -> Transition to RECOVERED
    recovered = await AlertStateMachine.process_recovery(
        db=async_db,
        server=server,
        component_identifier="cpu",
        metric_name="CPU Utilization",
        current_value="35%"
    )
    await async_db.commit()

    assert recovered is not None
    assert recovered.status == "RECOVERED"
    assert recovered.recovered_at is not None
