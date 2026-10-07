from app.services.notifications.smtp_service import SMTPService

def test_render_problem_email_template():
    rendered = SMTPService.render_problem_email(
        server_name="SERVER-01",
        component_name="CPU Core 0",
        metric_name="CPU Utilization",
        current_value="96%",
        threshold="90%",
        severity="CRITICAL",
        detected_at="2026-10-07 14:00:00 UTC"
    )

    assert "[CRITICAL] SERVER-01" in rendered["subject"]
    assert "Server:        SERVER-01" in rendered["plain"]
    assert "Current Value: 96%" in rendered["plain"]
    assert "Threshold:     90%" in rendered["plain"]
    assert "#ef4444" in rendered["html"]  # Critical color

def test_render_recovery_email_template():
    rendered = SMTPService.render_recovery_email(
        server_name="SERVER-01",
        problem_title="CPU Usage High",
        previous_severity="CRITICAL",
        start_time="2026-10-07 14:00:00 UTC",
        recovery_time="2026-10-07 14:12:00 UTC",
        duration="12 minutes 0 seconds",
        current_value="54%"
    )

    assert "[RECOVERED] SERVER-01 - CPU Usage High" in rendered["subject"]
    assert "Duration:          12 minutes 0 seconds" in rendered["plain"]
    assert "Previous Severity: CRITICAL" in rendered["plain"]
    assert "Current Value:     54%" in rendered["plain"]
    assert "#22c55e" in rendered["html"]  # Recovery green color
