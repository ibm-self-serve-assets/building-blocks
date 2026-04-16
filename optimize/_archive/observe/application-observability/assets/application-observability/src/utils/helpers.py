"""
Helper Utilities Module

Provides utility functions for data processing and formatting.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import re


def parse_time_range(time_str: str) -> Dict[str, int]:
    """
    Convert natural language time range to millisecond timestamps.
    
    Args:
        time_str: Natural language time string (e.g., "last 24 hours", "last 1 hour")
        
    Returns:
        dict: Dictionary with 'windowSize' in milliseconds
        
    Examples:
        >>> parse_time_range("last 1 hour")
        {'windowSize': 3600000}
        >>> parse_time_range("last 24 hours")
        {'windowSize': 86400000}
    """
    # Extract number and unit from string
    match = re.search(r'(\d+)\s*(hour|hours|h|day|days|d|minute|minutes|m)', time_str.lower())
    
    if not match:
        # Default to 1 hour
        return {'windowSize': 3600000}
    
    value = int(match.group(1))
    unit = match.group(2)
    
    # Convert to milliseconds
    if unit in ['hour', 'hours', 'h']:
        milliseconds = value * 3600000
    elif unit in ['day', 'days', 'd']:
        milliseconds = value * 86400000
    elif unit in ['minute', 'minutes', 'm']:
        milliseconds = value * 60000
    else:
        milliseconds = 3600000  # Default 1 hour
    
    return {'windowSize': milliseconds}


def format_timestamp(ts: int, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert millisecond timestamp to readable string.
    
    Args:
        ts: Timestamp in milliseconds
        format_str: strftime format string
        
    Returns:
        str: Formatted timestamp string
    """
    try:
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime(format_str)
    except (ValueError, OSError):
        return "Invalid timestamp"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling zero division.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return if division by zero
        
    Returns:
        float: Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def normalize_metric(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """
    Normalize a value to 0-100 range.
    
    Args:
        value: Value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range
        
    Returns:
        float: Normalized value (0-100)
    """
    try:
        if max_val == min_val:
            return 50.0  # Middle value if no range
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))  # Clamp to 0-100
    except (TypeError, ZeroDivisionError):
        return 0.0


def extract_metric_value(metrics_dict: Dict, metric_key: str, default: float = 0.0) -> float:
    """
    Extract metric value from Instana response format [[timestamp, value]].
    
    Args:
        metrics_dict: Metrics dictionary from Instana API
        metric_key: Key to extract (e.g., 'calls', 'errors', 'latency')
        default: Default value if extraction fails
        
    Returns:
        float: Extracted metric value
    """
    try:
        if not isinstance(metrics_dict, dict):
            return default
        
        metric_data = metrics_dict.get(metric_key, [])
        
        # Handle [[timestamp, value]] format
        if isinstance(metric_data, list) and len(metric_data) > 0:
            if isinstance(metric_data[0], list) and len(metric_data[0]) >= 2:
                return float(metric_data[0][1])
        
        return default
    except (TypeError, ValueError, IndexError):
        return default


def calculate_health_score(error_rate: float, latency: float, calls: int) -> float:
    """
    Calculate composite health score (0-100) based on metrics.
    
    Weighting:
    - Error rate: 40% (lower is better)
    - Latency: 30% (lower is better)
    - Call volume: 30% (higher is better, indicates activity)
    
    Args:
        error_rate: Error rate percentage (0-100)
        latency: Average latency in milliseconds
        calls: Number of calls
        
    Returns:
        float: Health score (0-100, higher is better)
    """
    try:
        # Error rate component (inverted, 0% error = 100 points)
        error_component = (100 - min(error_rate, 100)) * 0.4
        
        # Latency component (normalized, <100ms = 100 points, >1000ms = 0 points)
        latency_normalized = max(0, min(100, 100 - (latency / 10)))
        latency_component = latency_normalized * 0.3
        
        # Call volume component (normalized, >1000 calls = 100 points)
        calls_normalized = min(100, (calls / 10))
        calls_component = calls_normalized * 0.3
        
        health_score = error_component + latency_component + calls_component
        return round(health_score, 2)
    except (TypeError, ZeroDivisionError):
        return 0.0


def format_number(num: float, precision: int = 2) -> str:
    """
    Format number with appropriate suffix (K, M, B).
    
    Args:
        num: Number to format
        precision: Decimal precision
        
    Returns:
        str: Formatted number string
    """
    try:
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.{precision}f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.{precision}f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.{precision}f}K"
        else:
            return f"{num:.{precision}f}"
    except (TypeError, ValueError):
        return "0"


def get_severity_color(severity: str) -> str:
    """
    Return color code for severity level.
    
    Args:
        severity: Severity level string
        
    Returns:
        str: Color code (hex or name)
    """
    severity_colors = {
        'CRITICAL': '#da1e28',
        'HIGH': '#ff832b',
        'MEDIUM': '#f1c21b',
        'LOW': '#24a148',
        'INFO': '#0f62fe'
    }
    
    return severity_colors.get(severity.upper(), '#525252')


def get_health_status(score: float) -> tuple[str, str]:
    """
    Get health status label and color based on score.
    
    Args:
        score: Health score (0-100)
        
    Returns:
        tuple: (status_label, color_code)
    """
    if score >= 80:
        return ("Healthy", "#24a148")
    elif score >= 60:
        return ("Warning", "#f1c21b")
    elif score >= 40:
        return ("Degraded", "#ff832b")
    else:
        return ("Critical", "#da1e28")

# Made with Bob
