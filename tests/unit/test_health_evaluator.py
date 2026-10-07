import pytest
from app.services.health.evaluator import HealthEvaluator

def test_metric_threshold_cpu():
    # Normal
    sev, reason = HealthEvaluator.evaluate_metric_threshold("cpu", 45.0)
    assert sev == "HEALTHY"
    assert reason is None

    # Warning (>= 70%)
    sev, reason = HealthEvaluator.evaluate_metric_threshold("cpu", 75.0)
    assert sev == "WARNING"
    assert "75.0%" in reason

    # Critical (>= 90%)
    sev, reason = HealthEvaluator.evaluate_metric_threshold("cpu", 95.0)
    assert sev == "CRITICAL"
    assert "95.0%" in reason

def test_metric_threshold_custom_override():
    custom = {"cpu_warning": 50.0, "cpu_critical": 80.0}
    sev, reason = HealthEvaluator.evaluate_metric_threshold("cpu", 55.0, custom)
    assert sev == "WARNING"
    sev, reason = HealthEvaluator.evaluate_metric_threshold("cpu", 85.0, custom)
    assert sev == "CRITICAL"

def test_overall_server_health_priority():
    # 1. Healthy server
    h1 = HealthEvaluator.evaluate_overall_server_health(
        agent_status="ONLINE",
        consecutive_failures=0,
        components=[{"status": "HEALTHY"}],
        metric_severities=["HEALTHY", "HEALTHY"]
    )
    assert h1 == "HEALTHY"

    # 2. Warning metric pulls health to WARNING
    h2 = HealthEvaluator.evaluate_overall_server_health(
        agent_status="ONLINE",
        consecutive_failures=0,
        components=[{"status": "HEALTHY"}],
        metric_severities=["HEALTHY", "WARNING"]
    )
    assert h2 == "WARNING"

    # 3. Critical component pulls health to CRITICAL even if metrics are WARNING
    h3 = HealthEvaluator.evaluate_overall_server_health(
        agent_status="ONLINE",
        consecutive_failures=0,
        components=[{"status": "CRITICAL"}],
        metric_severities=["WARNING"]
    )
    assert h3 == "CRITICAL"

    # 4. Consecutive failures >= 3 forces DOWN regardless of components
    h4 = HealthEvaluator.evaluate_overall_server_health(
        agent_status="OFFLINE",
        consecutive_failures=3,
        components=[{"status": "HEALTHY"}],
        metric_severities=["HEALTHY"]
    )
    assert h4 == "DOWN"
