"""
Instana Integration Module

Provides API client for Instana observability data and data processing functions.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from src.config import Config
from src.utils.logger import setup_logger, log_api_call, log_error
from src.utils.helpers import extract_metric_value, calculate_health_score


class InstanaClient:
    """Instana API client for observability data."""
    
    def __init__(self, base_url: str = None, api_token: str = None):
        """
        Initialize Instana client.
        
        Args:
            base_url: Instana instance URL (defaults to Config.INSTANA_BASE_URL)
            api_token: API token (defaults to Config.INSTANA_API_TOKEN)
        """
        self.base_url = (base_url or Config.INSTANA_BASE_URL).rstrip('/')
        self.api_token = api_token or Config.INSTANA_API_TOKEN
        self.headers = Config.get_instana_headers()
        self.logger = setup_logger(__name__, Config.LOG_LEVEL)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.max_retries = Config.MAX_RETRIES
        self.timeout = Config.REQUEST_TIMEOUT
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            dict: Response with 'success' flag and 'data' or 'error'
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method, 
                    url, 
                    timeout=self.timeout, 
                    **kwargs
                )
                
                duration = time.time() - start_time
                log_api_call(self.logger, endpoint, response.status_code, duration)
                
                response.raise_for_status()
                data = response.json()
                
                # Handle paginated responses (dict with 'items' key)
                if isinstance(data, dict) and 'items' in data:
                    return {"success": True, "data": data['items']}
                
                return {"success": True, "data": data}
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    return {"success": False, "error": "Request timed out", "data": []}
                time.sleep(1)  # Wait before retry
                
            except requests.exceptions.HTTPError as e:
                log_error(self.logger, e, {"endpoint": endpoint, "status": e.response.status_code})
                return {"success": False, "error": f"HTTP {e.response.status_code}", "data": []}
                
            except Exception as e:
                log_error(self.logger, e, {"endpoint": endpoint})
                return {"success": False, "error": str(e), "data": []}
        
        return {"success": False, "error": "Max retries exceeded", "data": []}
    
    def get_application_id(self, app_name: str) -> Optional[str]:
        """
        Get application ID by name.
        
        Args:
            app_name: Application name to search for
            
        Returns:
            str: Application ID or None if not found
        """
        self.logger.info(f"Fetching application ID for: {app_name}")
        
        response = self._make_request("GET", "/api/application-monitoring/applications")
        
        if not response["success"]:
            self.logger.error(f"Failed to fetch applications: {response.get('error')}")
            return None
        
        applications = response["data"]
        
        # Search for application by name
        for app in applications:
            # Handle both 'name' and 'label' fields
            app_label = app.get('label') or app.get('name', '')
            if app_label.lower() == app_name.lower():
                app_id = app.get('id')
                self.logger.info(f"Found application '{app_name}' with ID: {app_id}")
                return app_id
        
        self.logger.warning(f"Application '{app_name}' not found")
        return None
    
    def get_services(self, app_id: str) -> List[Dict]:
        """
        Get services for an application.
        
        Args:
            app_id: Application ID
            
        Returns:
            list: List of service dictionaries
        """
        self.logger.info(f"Fetching services for application ID: {app_id}")
        
        endpoint = f"/api/application-monitoring/applications;id={app_id}/services"
        response = self._make_request("GET", endpoint)
        
        if not response["success"]:
            self.logger.error(f"Failed to fetch services: {response.get('error')}")
            return []
        
        services = response["data"]
        self.logger.info(f"Found {len(services)} services")
        return services
    
    def get_service_metrics(
        self, 
        service_id: str, 
        timeframe: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific service.
        
        Args:
            service_id: Service ID
            timeframe: Time window (e.g., {'windowSize': 3600000})
            
        Returns:
            dict: Service metrics
        """
        self.logger.debug(f"Fetching metrics for service: {service_id}")
        
        payload = {
            "serviceId": service_id,
            "metrics": [
                {"metric": "calls", "aggregation": "SUM"},
                {"metric": "errors", "aggregation": "MEAN"},
                {"metric": "latency", "aggregation": "MEAN"}
            ],
            "timeFrame": timeframe
        }
        
        response = self._make_request(
            "POST",
            "/api/application-monitoring/metrics/services",
            json=payload
        )
        
        if not response["success"]:
            self.logger.error(f"Failed to fetch service metrics: {response.get('error')}")
            return {}
        
        return response["data"]
    
    def get_trace_data(
        self, 
        app_name: str, 
        timeframe: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Get trace data for an application.
        
        Args:
            app_name: Application name
            timeframe: Time window
            
        Returns:
            dict: Trace data with aggregated metrics
        """
        self.logger.info(f"Fetching trace data for application: {app_name}")
        
        payload = {
            "timeFrame": timeframe,
            "tagFilterExpression": {
                "type": "TAG_FILTER",
                "name": "application.name",
                "operator": "EQUALS",
                "value": app_name
            },
            "metrics": [
                {"metric": "calls", "aggregation": "SUM"},
                {"metric": "errors", "aggregation": "SUM"},
                {"metric": "latency", "aggregation": "MEAN"}
            ],
            "group": {
                "groupbyTag": "service.name"
            }
        }
        
        response = self._make_request(
            "POST",
            "/api/application-monitoring/analyze/call-groups",
            json=payload
        )
        
        if not response["success"]:
            self.logger.error(f"Failed to fetch trace data: {response.get('error')}")
            return {}
        
        return response["data"]
    
    def fetch_all_data(self, app_name: str) -> Dict[str, Any]:
        """
        Fetch all observability data concurrently.
        
        Args:
            app_name: Application name
            
        Returns:
            dict: All fetched data
        """
        self.logger.info(f"Fetching all data for application: {app_name}")
        
        # Get application ID first
        app_id = self.get_application_id(app_name)
        if not app_id:
            return {
                "error": f"Application '{app_name}' not found",
                "services": [],
                "metrics": {},
                "app_id": None
            }
        
        # Fetch services
        services = self.get_services(app_id)
        
        # Fetch trace data
        timeframe = {"windowSize": Config.DEFAULT_TIMEFRAME}
        trace_data = self.get_trace_data(app_name, timeframe)
        
        return {
            "app_id": app_id,
            "services": services,
            "trace_data": trace_data,
            "timeframe": timeframe
        }


def process_service_health(services: List[Dict], trace_data: Dict) -> pd.DataFrame:
    """
    Process service data into DataFrame with health metrics.
    
    Args:
        services: List of service dictionaries
        trace_data: Trace data from Instana
        
    Returns:
        pd.DataFrame: Processed service health data
    """
    if not services:
        return pd.DataFrame()
    
    service_data = []
    
    for service in services:
        # Handle field name variations
        service_name = service.get('label') or service.get('name', 'Unknown')
        service_id = service.get('id') or service.get('serviceId', '')
        
        # Extract metrics from trace data if available
        calls = 0
        errors = 0
        latency = 0
        
        if trace_data and isinstance(trace_data, dict):
            metrics = trace_data.get('metrics', {})
            calls = extract_metric_value(metrics, 'calls', 0)
            errors = extract_metric_value(metrics, 'errors', 0)
            latency = extract_metric_value(metrics, 'latency', 0)
        
        # Calculate error rate
        error_rate = (errors / calls * 100) if calls > 0 else 0
        
        # Calculate health score
        health_score = calculate_health_score(error_rate, latency, calls)
        
        service_data.append({
            'service_name': service_name,
            'service_id': service_id,
            'calls': int(calls),
            'errors': int(errors),
            'error_rate': round(error_rate, 2),
            'latency': round(latency, 2),
            'health_score': health_score
        })
    
    df = pd.DataFrame(service_data)
    return df.sort_values('calls', ascending=False) if not df.empty else df


def aggregate_metrics(data: Dict) -> Dict[str, Any]:
    """
    Aggregate metrics for summary display.
    
    Args:
        data: Raw data from Instana
        
    Returns:
        dict: Aggregated metrics
    """
    services = data.get('services', [])
    trace_data = data.get('trace_data', {})
    
    # Process service health
    df = process_service_health(services, trace_data)
    
    if df.empty:
        return {
            'total_services': 0,
            'total_calls': 0,
            'avg_error_rate': 0,
            'avg_latency': 0,
            'avg_health_score': 0
        }
    
    return {
        'total_services': len(df),
        'total_calls': int(df['calls'].sum()),
        'avg_error_rate': round(df['error_rate'].mean(), 2),
        'avg_latency': round(df['latency'].mean(), 2),
        'avg_health_score': round(df['health_score'].mean(), 2)
    }

# Made with Bob
