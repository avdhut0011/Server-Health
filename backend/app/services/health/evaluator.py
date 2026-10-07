from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings

class HealthEvaluator:
    # Priority order from highest severity to lowest
    SEVERITY_ORDER = ["DOWN", "CRITICAL", "WARNING", "INFO", "HEALTHY"]

    @classmethod
    def compare_severity(cls, sev1: str, sev2: str) -> str:
        """Returns the higher priority severity among two states."""
        idx1 = cls.SEVERITY_ORDER.index(sev1) if sev1 in cls.SEVERITY_ORDER else len(cls.SEVERITY_ORDER)
        idx2 = cls.SEVERITY_ORDER.index(sev2) if sev2 in cls.SEVERITY_ORDER else len(cls.SEVERITY_ORDER)
        return cls.SEVERITY_ORDER[min(idx1, idx2)]

    @classmethod
    def evaluate_metric_threshold(
        cls,
        metric_name: str,
        value: Optional[float],
        custom_thresholds: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluates a metric against thresholds.
        Returns (Severity: HEALTHY|WARNING|CRITICAL, Reason)
        """
        if value is None:
            return ("HEALTHY", None)
            
        custom = custom_thresholds or {}
        
        if metric_name == "cpu":
            warn_th = custom.get("cpu_warning", settings.CPU_WARNING_THRESHOLD)
            crit_th = custom.get("cpu_critical", settings.CPU_CRITICAL_THRESHOLD)
            if value >= crit_th:
                return ("CRITICAL", f"CPU utilization {value:.1f}% exceeded critical threshold of {crit_th:.1f}%")
            if value >= warn_th:
                return ("WARNING", f"CPU utilization {value:.1f}% exceeded warning threshold of {warn_th:.1f}%")

        elif metric_name == "memory":
            warn_th = custom.get("memory_warning", settings.MEMORY_WARNING_THRESHOLD)
            crit_th = custom.get("memory_critical", settings.MEMORY_CRITICAL_THRESHOLD)
            if value >= crit_th:
                return ("CRITICAL", f"RAM utilization {value:.1f}% exceeded critical threshold of {crit_th:.1f}%")
            if value >= warn_th:
                return ("WARNING", f"RAM utilization {value:.1f}% exceeded warning threshold of {warn_th:.1f}%")

        elif metric_name == "disk":
            warn_th = custom.get("disk_warning", settings.DISK_WARNING_THRESHOLD)
            crit_th = custom.get("disk_critical", settings.DISK_CRITICAL_THRESHOLD)
            if value >= crit_th:
                return ("CRITICAL", f"Disk utilization {value:.1f}% exceeded critical threshold of {crit_th:.1f}%")
            if value >= warn_th:
                return ("WARNING", f"Disk utilization {value:.1f}% exceeded warning threshold of {warn_th:.1f}%")

        elif metric_name == "ping_latency":
            warn_th = custom.get("latency_warning", settings.LATENCY_WARNING_MS)
            crit_th = custom.get("latency_critical", settings.LATENCY_CRITICAL_MS)
            if value >= crit_th:
                return ("CRITICAL", f"Network latency {value:.1f}ms exceeded critical threshold of {crit_th:.1f}ms")
            if value >= warn_th:
                return ("WARNING", f"Network latency {value:.1f}ms exceeded warning threshold of {warn_th:.1f}ms")

        elif metric_name == "packet_loss":
            warn_th = custom.get("packet_loss_warning", settings.PACKET_LOSS_WARNING_PCT)
            crit_th = custom.get("packet_loss_critical", settings.PACKET_LOSS_CRITICAL_PCT)
            if value >= crit_th:
                return ("CRITICAL", f"Packet loss {value:.1f}% exceeded critical threshold of {crit_th:.1f}%")
            if value >= warn_th:
                return ("WARNING", f"Packet loss {value:.1f}% exceeded warning threshold of {warn_th:.1f}%")

        return ("HEALTHY", None)

    @classmethod
    def evaluate_overall_server_health(
        cls,
        agent_status: str,
        consecutive_failures: int,
        components: List[Dict[str, Any]],
        metric_severities: List[str]
    ) -> str:
        """
        Determines overall server health based on deterministic priority:
        1. DOWN if consecutive_failures >= configured limit or agent_status is OFFLINE for > limit
        2. CRITICAL if any component or metric is CRITICAL or FAILED
        3. WARNING if any component or metric is WARNING
        4. INFO if any component or metric is INFO
        5. Otherwise HEALTHY
        """
        if consecutive_failures >= settings.CONSECUTIVE_FAILURES_FOR_DOWN or agent_status == "OFFLINE":
            return "DOWN"
            
        current_health = "HEALTHY"
        
        # Check components status
        for comp in components:
            c_status = comp.get("status", "HEALTHY").upper()
            if c_status in ["FAILED", "CRITICAL"]:
                return "CRITICAL"
            elif c_status == "WARNING":
                current_health = cls.compare_severity(current_health, "WARNING")
            elif c_status == "INFO":
                current_health = cls.compare_severity(current_health, "INFO")
                
        # Check metric evaluated severities
        for m_sev in metric_severities:
            if m_sev == "CRITICAL":
                return "CRITICAL"
            elif m_sev == "WARNING":
                current_health = cls.compare_severity(current_health, "WARNING")
            elif m_sev == "INFO":
                current_health = cls.compare_severity(current_health, "INFO")
                
        return current_health
