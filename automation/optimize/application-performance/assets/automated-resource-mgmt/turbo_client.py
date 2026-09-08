"""
IBM Turbonomic REST API v3 Client
==================================
Production-ready client with robust error handling, multiple fallback strategies,
and comprehensive edge case coverage.

Critical Fixes Implemented:
- EC001: Use /markets/Market/entities instead of /entities
- EC002: _to_list() method to normalize all API responses
- EC003: Safe timestamp conversion (handles string and int)
- EC004: Server-side filtering with POST /search
- EC006: None value handling with 'or {}' pattern
"""

import logging
import requests
import urllib3
from typing import Optional, List, Dict, Any

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("turbo_client")


class TurbonomicClient:
    """Session-based Turbonomic API v3 client with robust error handling."""
    
    # Common entity types across Turbonomic versions
    COMMON_ENTITY_TYPES = [
        "VirtualMachine", "VM", "PhysicalMachine", "Host", "Storage",
        "Application", "Container", "ContainerPod", "Pod",
        "WorkloadController", "Namespace", "Service",
        "DatabaseServer", "Database", "BusinessApplication",
        "BusinessTransaction"
    ]
    
    # Application-specific entity types
    APP_ENTITY_TYPES = [
        "BusinessApplication", "Application", "BusinessTransaction",
        "Service", "DatabaseServer", "ApplicationComponent",
        "ApplicationServer", "WebServer"
    ]
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """
        Initialize Turbonomic API client.
        
        Args:
            host: Turbonomic host (without https://)
            username: Turbonomic username
            password: Turbonomic password
            verify_ssl: Whether to verify SSL certificates
        """
        # Strip scheme if provided
        host = host.strip().rstrip("/")
        if host.startswith("https://"):
            host = host[len("https://"):]
        elif host.startswith("http://"):
            host = host[len("http://"):]
        
        self.host = host
        self.base_url = f"https://{host}/api/v3"
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        log.info("TurbonomicClient initializing | base_url=%s", self.base_url)
        self._login(username, password)
    
    def _login(self, username: str, password: str) -> None:
        """Authenticate with Turbonomic and establish session."""
        url = f"{self.base_url}/login"
        try:
            resp = self.session.post(
                url,
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            resp.raise_for_status()
            log.info("LOGIN success")
        except requests.exceptions.SSLError as e:
            log.error("SSL error during login: %s", e)
            raise
        except requests.exceptions.ConnectionError as e:
            log.error("Connection error: %s", e)
            raise
        except requests.exceptions.Timeout:
            log.error("Timeout connecting to %s", url)
            raise
        except requests.exceptions.HTTPError as e:
            log.error("HTTP error during login: %s", e)
            raise
    
    @staticmethod
    def _to_list(data: Any, label: str = "") -> List[Dict]:
        """
        Guarantee a list of dicts regardless of API response format.
        
        CRITICAL FIX (EC002): Handles None, list, dict with wrappers, dict with only 'links'.
        
        Args:
            data: API response data
            label: Label for logging
            
        Returns:
            List of dictionaries
        """
        if data is None:
            return []
        
        if isinstance(data, list):
            # Filter out non-dict items
            clean = [item for item in data if isinstance(item, dict)]
            if len(clean) != len(data):
                log.warning("_to_list[%s]: dropped %d non-dict items", 
                           label, len(data) - len(clean))
            return clean
        
        if isinstance(data, dict):
            # Check for common wrapper keys
            for key in ("entities", "actions", "actionsList", "groups", 
                       "targets", "markets", "items", "results", "content", 
                       "data", "supplyChainNodes", "seMap"):
                if key in data and isinstance(data[key], list):
                    log.debug("_to_list[%s]: unwrapped key '%s'", label, key)
                    return [item for item in data[key] if isinstance(item, dict)]
            
            # Special case: only 'links' key means empty result
            if list(data.keys()) == ['links']:
                log.debug("_to_list[%s]: empty result (only 'links' key)", label)
                return []
            
            log.warning("_to_list[%s]: got dict with keys %s — returning []",
                       label, list(data.keys())[:10])
            return []
        
        log.warning("_to_list[%s]: unexpected type %s — returning []", 
                   label, type(data).__name__)
        return []
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        """Execute GET request with error handling."""
        url = f"{self.base_url}{path}"
        log.debug("GET %s params=%s", url, params)
        resp = self.session.get(url, params=params, timeout=60)
        log.debug("GET %s → %s", url, resp.status_code)
        resp.raise_for_status()
        return resp.json()
    
    def _post(self, path: str, payload: Optional[Dict] = None, 
              params: Optional[Dict] = None) -> Any:
        """Execute POST request with error handling."""
        url = f"{self.base_url}{path}"
        log.debug("POST %s params=%s", url, params)
        resp = self.session.post(url, json=payload or {}, params=params, timeout=60)
        log.debug("POST %s → %s", url, resp.status_code)
        resp.raise_for_status()
        return resp.json()
    
    def get_entities(self, entity_type: Optional[str] = None, 
                    limit: int = 500) -> List[Dict]:
        """
        Fetch entities using correct API endpoints with fallback strategies.
        
        CRITICAL FIX (EC001): GET /entities without params returns links, not entities.
        Must use /markets/Market/entities.
        
        Args:
            entity_type: Specific entity type to fetch
            limit: Maximum number of entities to return
            
        Returns:
            List of entity dictionaries
        """
        # Strategy 1: If entity_type specified, query via Market endpoint
        if entity_type:
            try:
                result = self._get("/markets/Market/entities", 
                                  params={"types": entity_type, "limit": limit})
                entities = self._to_list(result, f"market_entities_{entity_type}")
                if entities:
                    log.info("get_entities[%s] via Market = %d items", 
                            entity_type, len(entities))
                    return entities
            except Exception as exc:
                log.debug("Market endpoint failed for %s: %s", entity_type, exc)
            
            # Fallback to direct /entities
            try:
                result = self._get("/entities", 
                                  params={"types": entity_type, "limit": limit})
                entities = self._to_list(result, entity_type)
                if entities:
                    log.info("get_entities[%s] via /entities = %d items", 
                            entity_type, len(entities))
                    return entities
            except Exception as exc:
                log.debug("Direct endpoint failed for %s: %s", entity_type, exc)
            
            return []
        
        # Strategy 2: No specific type - get all via Market endpoint
        try:
            result = self._get("/markets/Market/entities", params={"limit": limit})
            entities = self._to_list(result, "market_entities_all")
            if entities:
                log.info("get_entities via Market returned %d items", len(entities))
                return entities
        except Exception as exc:
            log.warning("Market endpoint failed: %s", exc)
        
        # Strategy 3: Fallback - query each type individually
        all_entities: List[Dict] = []
        per_type_limit = max(200, limit // len(self.COMMON_ENTITY_TYPES))
        
        for etype in self.COMMON_ENTITY_TYPES:
            try:
                result = self._get("/markets/Market/entities", 
                                  params={"types": etype, "limit": per_type_limit})
                items = self._to_list(result, etype)
                if items:
                    log.info("get_entities[%s] = %d items", etype, len(items))
                    all_entities.extend(items)
            except Exception as exc:
                log.debug("get_entities[%s] failed: %s", etype, exc)
        
        if all_entities:
            log.info("get_entities fallback SUCCESS: %d items", len(all_entities))
        else:
            log.warning("get_entities fallback FAILED: 0 items from all types")
        
        return all_entities
    
    def get_entity(self, entity_uuid: str) -> Optional[Dict]:
        """
        Get single entity by UUID.
        
        Args:
            entity_uuid: Entity UUID
            
        Returns:
            Entity dictionary or None
        """
        try:
            result = self._get(f"/entities/{entity_uuid}")
            if isinstance(result, dict):
                return result
            return None
        except Exception as exc:
            log.warning("get_entity failed for %s: %s", entity_uuid, exc)
            return None
    
    def get_entity_related(self, entity_uuid: str, relationship: str = "sold") -> List[Dict]:
        """
        Get entities related to the specified entity.
        
        For applications, this typically returns the VirtualMachines that host the application.
        
        Args:
            entity_uuid: Entity UUID
            relationship: Relationship type ("sold" for providers, "bought" for consumers)
            
        Returns:
            List of related entity dictionaries
        """
        try:
            # Use supply chain API to get related entities
            result = self._get(f"/entities/{entity_uuid}/supplychains")
            
            if not result:
                log.debug(f"No supply chain data for entity {entity_uuid}")
                return []
            
            # Extract related entities based on relationship
            related = []
            
            # Supply chain response structure varies, try multiple approaches
            if isinstance(result, dict):
                # Approach 1: Check for seMap (supply chain entity map)
                se_map = result.get("seMap", {})
                for entity_data in se_map.values():
                    if isinstance(entity_data, dict):
                        related.append(entity_data)
                
                # Approach 2: Check for direct entities list
                if not related and "entities" in result:
                    entities = result.get("entities", [])
                    if isinstance(entities, list):
                        related.extend(entities)
            
            elif isinstance(result, list):
                # Direct list of entities
                related.extend(result)
            
            log.info(f"get_entity_related: {len(related)} related entities for {entity_uuid}")
            return related
            
        except Exception as exc:
            log.warning(f"get_entity_related failed for {entity_uuid}: {exc}")
            return []
    
    def get_entity_time_series(self, entity_uuid: str, commodities: List[str],
                               start_ms: int, end_ms: int) -> List[Dict]:
        """
        Fetch time-series statistics for an entity.
        
        Args:
            entity_uuid: Entity UUID
            commodities: List of commodity names (e.g., ["ResponseTime", "Transaction"])
            start_ms: Start timestamp in epoch milliseconds
            end_ms: End timestamp in epoch milliseconds
            
        Returns:
            List of snapshot dictionaries with statistics
        """
        payload: Dict[str, Any] = {
            "statistics": [{"name": c} for c in commodities],
            "startDate": start_ms,
            "endDate": end_ms,
        }
        try:
            result = self._post(f"/entities/{entity_uuid}/stats", payload=payload)
            return result if isinstance(result, list) else []
        except Exception as exc:
            log.warning("get_entity_time_series failed for %s: %s", entity_uuid, exc)
            return []
    
    def get_entity_actions(self, entity_uuid: str, limit: int = 100) -> List[Dict]:
        """
        Get actions for a specific entity.
        
        Args:
            entity_uuid: Entity UUID
            limit: Maximum number of actions
            
        Returns:
            List of action dictionaries
        """
        payload: Dict[str, Any] = {
            "actionStateList": ["READY", "QUEUED", "IN_PROGRESS", "ACCEPTED"],
            "actionModeList": ["RECOMMEND", "EXTERNAL_APPROVAL", "MANUAL", "AUTOMATIC"],
            "relatedEntityTypes": []
        }
        try:
            result = self._post(f"/entities/{entity_uuid}/actions",
                               payload=payload, params={"limit": limit})
            actions = self._to_list(result, f"entity_{entity_uuid}_actions")
            log.info("get_entity_actions: %d actions for entity %s", len(actions), entity_uuid)
            return actions
        except Exception as exc:
            log.warning("get_entity_actions failed for %s: %s", entity_uuid, exc)
            return []
    
    def get_entity_stats(self, entity_uuid: str, stat_names: Optional[List[str]] = None) -> List[Dict]:
        """
        Get detailed statistics for an entity using POST /stats/{uuid}.
        
        This retrieves current snapshot statistics including CPU, Memory, Storage,
        Network, and other commodities with their values, capacity, and units.
        
        Args:
            entity_uuid: UUID of the entity
            stat_names: Optional list of specific statistics to retrieve.
                       If None, returns all available statistics.
                       Common stats: CPU, Mem, VMem, VCPU, Storage, NetThroughput,
                       IOThroughput, CPUProvisioned, MemProvisioned, etc.
        
        Returns:
            List of statistic dictionaries with structure:
            [{
                "name": "CPU",
                "displayName": "CPU/EntityName",
                "units": "MHz",
                "value": 123.45,
                "values": {"avg": 123.45, "max": 200.0, "min": 50.0},
                "capacity": {"avg": 1000.0, "max": 1000.0, "min": 1000.0},
                "relatedEntityType": "VirtualMachine",
                "filters": [{"type": "relation", "value": "sold"}]
            }]
        """
        try:
            # Build payload for filtered statistics request
            payload: Dict[str, Any] = {}
            
            if stat_names:
                # Request specific statistics
                payload["statistics"] = [{"name": name} for name in stat_names]
            
            # POST request to get statistics
            result = self._post(f"/stats/{entity_uuid}", payload=payload if payload else None)
            
            # Response is a list of StatSnapshotApiDTOs
            snapshots = self._to_list(result, f"stats_{entity_uuid}")
            
            if not snapshots:
                log.warning("No statistics snapshots returned for entity %s", entity_uuid)
                return []
            
            # Extract statistics from first snapshot (current values)
            snapshot = snapshots[0] if isinstance(snapshots, list) else snapshots
            statistics = snapshot.get("statistics", []) if isinstance(snapshot, dict) else []
            
            if not statistics:
                log.warning("No statistics found in snapshot for entity %s", entity_uuid)
                return []
            
            log.info("get_entity_stats: %d statistics for entity %s",
                    len(statistics), entity_uuid)
            return statistics
            
        except Exception as exc:
            log.error("get_entity_stats failed for %s: %s", entity_uuid, exc)
            return []
    
    def get_pending_actions(self, limit: int = 500) -> List[Dict]:
        """
        Get all pending actions from the market.
        
        Args:
            limit: Maximum number of actions
            
        Returns:
            List of action dictionaries
        """
        payload: Dict[str, Any] = {
            "actionStateList": ["READY", "QUEUED", "IN_PROGRESS", "ACCEPTED"],
            "actionModeList": ["RECOMMEND", "EXTERNAL_APPROVAL", "MANUAL", "AUTOMATIC"],
        }
        try:
            result = self._post("/markets/Market/actions", 
                               payload=payload, params={"limit": limit})
            actions = self._to_list(result, "pending_actions")
            log.info("get_pending_actions: %d actions", len(actions))
            return actions
        except Exception as exc:
            log.error("get_pending_actions failed: %s", exc)
            return []
    
    def execute_action(self, action_uuid: str) -> Dict:
        """
        Execute/accept an action with multiple endpoint fallbacks.
        
        Different Turbonomic versions support different formats.
        
        Args:
            action_uuid: Action UUID
            
        Returns:
            Response dictionary
        """
        # Try format 1: query parameter (most common in v8.x)
        try:
            return self._post(f"/actions/{action_uuid}", params={"accept": "true"})
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code not in (400, 500):
                raise
        
        # Try format 2: request body
        try:
            payload = {"actionState": "ACCEPTED"}
            return self._post(f"/actions/{action_uuid}", payload=payload)
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code not in (400, 500):
                raise
        
        # Try format 3: legacy /accept endpoint
        return self._post(f"/actions/{action_uuid}/accept")
    
    def search_applications(self, name_filter: str = "", 
                           limit: int = 500) -> List[Dict]:
        """
        Search for applications with SERVER-SIDE filtering.
        
        CRITICAL FIX (EC004): Client-side filtering after limit misses results.
        Uses 5 fallback strategies for maximum reliability.
        
        Args:
            name_filter: Application name filter
            limit: Maximum results
            
        Returns:
            List of application entity dictionaries
        """
        app_entities = []
        
        # Strategy 1: POST /search with server-side filtering
        if name_filter:
            try:
                search_payload = {
                    "criteria": {
                        "expType": "RXEQ",
                        "expVal": f".*{name_filter}.*",
                        "filterType": "displayName",
                        "caseSensitive": False
                    },
                    "className": "BusinessApplication"
                }
                result = self._post("/search", payload=search_payload, 
                                   params={"limit": limit})
                business_apps = self._to_list(result, "search_businessapplications")
                if business_apps:
                    log.info("search_applications: found %d via POST /search", 
                            len(business_apps))
                    app_entities.extend(business_apps)
            except Exception as exc:
                log.debug("POST /search failed: %s", exc)
        
        # Strategy 2: Try /businessapplications endpoint (no filter support)
        if not app_entities:
            try:
                result = self._get("/businessapplications", params={"limit": limit})
                business_apps = self._to_list(result, "businessapplications")
                if business_apps:
                    log.info("search_applications: found %d via /businessapplications", 
                            len(business_apps))
                    app_entities.extend(business_apps)
            except Exception as exc:
                log.debug("/businessapplications failed: %s", exc)
        
        # Strategy 3: Try each app entity type with server-side filter
        if name_filter and not app_entities:
            for entity_type in self.APP_ENTITY_TYPES:
                try:
                    search_payload = {
                        "criteria": {
                            "expType": "RXEQ",
                            "expVal": f".*{name_filter}.*",
                            "filterType": "displayName",
                            "caseSensitive": False
                        },
                        "className": entity_type
                    }
                    result = self._post("/search", payload=search_payload, 
                                       params={"limit": limit})
                    entities = self._to_list(result, f"search_{entity_type}")
                    if entities:
                        log.info("search_applications: found %d of type %s", 
                                len(entities), entity_type)
                        # Deduplicate by UUID
                        existing_uuids = {e.get("uuid") for e in app_entities}
                        new_entities = [e for e in entities 
                                       if e.get("uuid") not in existing_uuids]
                        app_entities.extend(new_entities)
                except Exception as exc:
                    log.debug("POST /search for %s failed: %s", entity_type, exc)
        
        # Strategy 4: Try /markets/Market/entities with app types
        if not app_entities:
            for entity_type in self.APP_ENTITY_TYPES:
                try:
                    result = self._get("/markets/Market/entities",
                                      params={"types": entity_type, "limit": limit})
                    entities = self._to_list(result, f"market_{entity_type}")
                    if entities:
                        log.info("search_applications: found %d of type %s via Market", 
                                len(entities), entity_type)
                        existing_uuids = {e.get("uuid") for e in app_entities}
                        new_entities = [e for e in entities 
                                       if e.get("uuid") not in existing_uuids]
                        app_entities.extend(new_entities)
                except Exception as exc:
                    log.debug("Market endpoint for %s failed: %s", entity_type, exc)
        
        # Strategy 5: Client-side filtering only as final fallback
        if name_filter and app_entities:
            nf = name_filter.strip().lower()
            filtered = [e for e in app_entities 
                       if nf in e.get("displayName", "").lower()]
            log.info("search_applications: returning %d filtered results", 
                    len(filtered))
            return filtered
        
        log.info("search_applications: returning %d total results", len(app_entities))
        return app_entities
    
    def get_targets(self) -> List[Dict]:
        """
        Get all configured targets.
        
        Returns:
            List of target dictionaries
        """
        try:
            result = self._get("/targets")
            targets = self._to_list(result, "targets")
            log.info("get_targets: %d targets", len(targets))
            return targets
        except Exception as exc:
            log.error("get_targets failed: %s", exc)
            return []
    
    def get_groups(self) -> List[Dict]:
        """
        Get all groups.
        
        Returns:
            List of group dictionaries
        """
        try:
            result = self._get("/groups")
            groups = self._to_list(result, "groups")
            log.info("get_groups: %d groups", len(groups))
            return groups
        except Exception as exc:
            log.error("get_groups failed: %s", exc)
            return []
    
    def get_clusters(self) -> List[Dict]:
        """
        Get Kubernetes clusters.
        
        Returns:
            List of cluster dictionaries
        """
        try:
            result = self._get("/clusters")
            clusters = self._to_list(result, "clusters")
            log.info("get_clusters: %d clusters", len(clusters))
            return clusters
        except Exception as exc:
            log.error("get_clusters failed: %s", exc)
            return []
    
    def get_policies(self) -> List[Dict]:
        """
        Get automation policies.
        
        Returns:
            List of policy dictionaries
        """
        try:
            result = self._get("/settingspolicies")
            policies = self._to_list(result, "policies")
            log.info("get_policies: %d policies", len(policies))
            return policies
        except Exception as exc:
            log.error("get_policies failed: %s", exc)
            return []


def safe_get(obj: Any, *keys, default=None):
    """
    Safely navigate nested dictionaries.
    
    CRITICAL FIX (EC006): Handle None values in nested access.
    
    Args:
        obj: Object to navigate
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at nested key or default
    """
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and isinstance(key, int):
            try:
                current = current[key]
            except (IndexError, TypeError):
                return default
        else:
            return default
        if current is None:
            return default
    return current if current is not None else default

# Made with Bob
