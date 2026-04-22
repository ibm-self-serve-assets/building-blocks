"""
IBM Turbonomic Resource Management Dashboard
============================================
Production-ready Dash application with 8 tabs, comprehensive error handling,
and beautiful IBM Carbon dark theme.

All Critical Fixes Implemented:
- EC001: Correct API endpoints (/markets/Market/entities)
- EC002: Response normalization with _to_list()
- EC003: Safe timestamp conversion (string and int)
- EC004: Server-side filtering with POST /search
- EC005: Dropdown visibility CSS
- EC006: None value handling
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import dash
from dash import dcc, html, dash_table, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from turbo_client import TurbonomicClient, safe_get

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger("turbo_dash")

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Turbonomic Resource Management"
)

# ============================================================================
# COLOR SCHEMES AND STYLING
# ============================================================================

ACTION_COLORS = {
    "RESIZE": "#0072c3", "MOVE": "#6929c4", "SUSPEND": "#da1e28",
    "PROVISION": "#198038", "SCALE": "#f1620a", "ACTIVATE": "#198038",
    "DEACTIVATE": "#da1e28", "DELETE": "#da1e28"
}

ENTITY_COLORS = {
    "VirtualMachine": "#0072c3", "PhysicalMachine": "#6929c4",
    "Container": "#f1620a", "Storage": "#b28600", "Application": "#198038",
    "Host": "#6929c4", "Pod": "#f1620a", "Service": "#198038"
}

SEVERITY_COLORS = {
    "CRITICAL": "#da1e28", "MAJOR": "#ff832b",
    "MINOR": "#f1c21b", "NORMAL": "#42be65"
}

STATE_COLORS = {
    "ACTIVE": "#42be65", "IDLE": "#f1c21b", "SUSPEND": "#da1e28",
    "UNKNOWN": "#6f6f6f", "MAINTENANCE": "#0072c3"
}

BASE_LAYOUT = {
    "plot_bgcolor": "#0f1117",
    "paper_bgcolor": "#161b2e",
    "font": {"color": "#c8d8ee", "family": "IBM Plex Sans, Arial"},
}

_DEFAULT_MARGIN = dict(l=60, r=30, t=50, b=40)
GRID_COLOR = "#1e2a45"

# ============================================================================
# NAVIGATION ITEMS
# ============================================================================

NAV_ITEMS = [
    ("overview", "📊", "Overview"),
    ("actions", "⚡", "Pending Actions"),
    ("entities", "🖥️", "Entities"),
    ("app-stats", "📈", "App Statistics"),
    ("targets", "🎯", "Targets"),
    ("groups", "📁", "Groups"),
    ("clusters", "☸️", "Kubernetes"),
    ("policies", "⚙️", "Policies"),
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _df_to_records(df: pd.DataFrame) -> List[Dict]:
    """Convert DataFrame to records for DataTable."""
    return df.to_dict("records") if not df.empty else []


def get_client(session_data: Dict) -> TurbonomicClient:
    """Get or create Turbonomic client from session data."""
    if not session_data or "client_params" not in session_data:
        raise ValueError("Not authenticated")
    
    params = session_data["client_params"]
    return TurbonomicClient(
        host=params["host"],
        username=params["username"],
        password=params["password"],
        verify_ssl=params.get("verify_ssl", False)
    )


def safe_timestamp_to_datetime(ts_ms: Any) -> Optional[datetime]:
    """
    Convert timestamp to datetime safely.
    
    CRITICAL FIX (EC003): Handles both string and int timestamps.
    """
    try:
        if isinstance(ts_ms, str):
            if 'T' in ts_ms:
                # ISO 8601 format
                return datetime.fromisoformat(ts_ms.replace('Z', '+00:00'))
            else:
                # Epoch milliseconds as string
                ts_ms_int = int(ts_ms)
                return datetime.utcfromtimestamp(ts_ms_int / 1000) if ts_ms_int else None
        else:
            # Numeric epoch milliseconds
            ts_ms_int = int(ts_ms) if ts_ms else 0
            return datetime.utcfromtimestamp(ts_ms_int / 1000) if ts_ms_int else None
    except (ValueError, TypeError, OSError) as e:
        log.warning("Invalid timestamp: %s (error: %s)", ts_ms, e)
        return None


# ============================================================================
# APP LAYOUT
# ============================================================================

def create_sidebar():
    """Create sidebar navigation."""
    nav_links = []
    for slug, icon, label in NAV_ITEMS:
        nav_links.append(
            html.A(
                [html.Span(icon, className="nav-icon"), html.Span(label)],
                href=f"#{slug}",
                id=f"nav-{slug}",
                className="nav-link-item",
            )
        )
    
    return html.Div([
        html.Div([
            html.H5("TURBONOMIC", style={"margin": "0"}),
            html.Small("Resource Management", style={"fontSize": "0.72rem"}),
        ], className="sidebar-header"),
        html.Div([
            html.Div("NAVIGATION", className="nav-section-label"),
            *nav_links,
        ], style={"padding": "10px 0"}),
    ], id="sidebar")


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="auth-store", storage_type="session"),
    
    # Login page
    html.Div(id="login-page", children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H3("IBM Turbonomic", style={"color": "#0072c3", "marginBottom": "10px"}),
                        html.P("Resource Management Dashboard", style={"color": "#7a9abf"}),
                        html.Hr(style={"borderColor": "#1e2a45"}),
                        
                        dbc.Input(id="login-host", placeholder="Turbonomic Host (e.g., turbonomic.example.com)", 
                                 type="text", className="mb-3"),
                        dbc.Input(id="login-username", placeholder="Username", type="text", className="mb-3"),
                        dbc.Input(id="login-password", placeholder="Password", type="password", className="mb-3"),
                        dbc.Checklist(
                            options=[{"label": " Verify SSL Certificate", "value": "verify"}],
                            value=[],
                            id="login-ssl",
                            className="mb-3",
                            style={"color": "#c8d8ee"}
                        ),
                        dbc.Button("Connect", id="btn-login", color="primary", className="w-100"),
                        html.Div(id="login-feedback", className="mt-3"),
                    ], style={
                        "backgroundColor": "#161b2e",
                        "padding": "40px",
                        "borderRadius": "10px",
                        "border": "1px solid #1e2a45"
                    })
                ], md=6)
            ], justify="center", style={"minHeight": "100vh"}, align="center")
        ], fluid=True)
    ], style={"display": "block"}),
    
    # Main dashboard
    html.Div(id="main-dashboard", children=[
        create_sidebar(),
        html.Div(id="main-content", children=[
            html.Div(id="page-content"),
        ])
    ], style={"display": "none"}),
])

# ============================================================================
# AUTHENTICATION CALLBACK
# ============================================================================

@app.callback(
    Output("auth-store", "data"),
    Output("login-feedback", "children"),
    Output("login-page", "style"),
    Output("main-dashboard", "style"),
    Input("btn-login", "n_clicks"),
    State("login-host", "value"),
    State("login-username", "value"),
    State("login-password", "value"),
    State("login-ssl", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, host, username, password, ssl_check):
    """Handle login and authentication."""
    if not all([host, username, password]):
        return no_update, dbc.Alert("Please fill in all fields.", color="warning"), no_update, no_update
    
    try:
        verify_ssl = "verify" in (ssl_check or [])
        client = TurbonomicClient(host, username, password, verify_ssl)
        
        session_data = {
            "authenticated": True,
            "client_params": {
                "host": host,
                "username": username,
                "password": password,
                "verify_ssl": verify_ssl
            }
        }
        
        return (
            session_data,
            dbc.Alert("Connected successfully!", color="success"),
            {"display": "none"},
            {"display": "block"}
        )
    except Exception as exc:
        log.error("Login failed: %s", exc)
        return no_update, dbc.Alert(f"Connection failed: {exc}", color="danger"), no_update, no_update


# ============================================================================
# NAVIGATION CALLBACK
# ============================================================================

@app.callback(
    Output("page-content", "children"),
    Input("url", "hash"),
    State("auth-store", "data")
)
def display_page(hash_value, auth_data):
    """Route to appropriate page based on URL hash."""
    if not auth_data or not auth_data.get("authenticated"):
        return html.Div()
    
    page = hash_value.lstrip("#") if hash_value else "overview"
    
    # Create interval components for data loading
    intervals = {
        "overview": dcc.Interval(id="overview-interval", interval=60000, n_intervals=0),
        "actions": dcc.Interval(id="actions-interval", interval=30000, n_intervals=0),
        "entities": dcc.Interval(id="entities-interval", interval=60000, n_intervals=0),
        "app-stats": dcc.Interval(id="app-stats-interval", interval=1000, n_intervals=0, max_intervals=1),
        "targets": dcc.Interval(id="targets-interval", interval=60000, n_intervals=0),
        "groups": dcc.Interval(id="groups-interval", interval=60000, n_intervals=0),
        "clusters": dcc.Interval(id="clusters-interval", interval=60000, n_intervals=0),
        "policies": dcc.Interval(id="policies-interval", interval=60000, n_intervals=0),
    }
    
    stores = {
        "overview": dcc.Store(id="overview-store"),
        "actions": dcc.Store(id="actions-store"),
        "entities": dcc.Store(id="entities-store"),
        "app-stats": dcc.Store(id="app-stats-store"),
        "targets": dcc.Store(id="targets-store"),
        "groups": dcc.Store(id="groups-store"),
        "clusters": dcc.Store(id="clusters-store"),
        "policies": dcc.Store(id="policies-store"),
    }
    
    return html.Div([
        intervals.get(page, html.Div()),
        stores.get(page, html.Div()),
        html.Div(id=f"{page}-content"),
    ])


# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

@app.callback(
    Output("overview-store", "data"),
    Input("overview-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_overview_data(n, auth_data):
    """Load data for Overview tab."""
    try:
        client = get_client(auth_data)
        
        entities = client.get_entities(limit=1000)
        actions = client.get_pending_actions(limit=500)
        targets = client.get_targets()
        
        return {
            "entities": entities,
            "actions": actions,
            "targets": targets,
            "timestamp": time.time()
        }
    except Exception as exc:
        log.error("Failed to load overview data: %s", exc)
        return {"error": str(exc)}


@app.callback(
    Output("overview-content", "children"),
    Input("overview-store", "data")
)
def render_overview(data):
    """Render Overview tab with metrics and charts."""
    if not data or "error" in data:
        return dbc.Alert("Failed to load overview data.", color="danger")
    
    entities = data.get("entities", [])
    actions = data.get("actions", [])
    targets = data.get("targets", [])
    
    # Process data
    entity_df = pd.DataFrame([{
        "Type": e.get("className", "Unknown"),
        "State": e.get("state", "UNKNOWN"),
        "Environment": e.get("environmentType", "Unknown")
    } for e in entities]) if entities else pd.DataFrame()
    
    action_df = pd.DataFrame([{
        "type": a.get("actionType", "Unknown"),
        "severity": a.get("risk", {}).get("severity", "NORMAL") if isinstance(a.get("risk"), dict) else "NORMAL"
    } for a in actions]) if actions else pd.DataFrame()
    
    target_df = pd.DataFrame([{
        "status": t.get("status", "Unknown")
    } for t in targets]) if targets else pd.DataFrame()
    
    # Metric cards
    metrics_row = dbc.Row([
        dbc.Col(html.Div([
            html.Div("🖥️", style={"fontSize": "2rem", "marginBottom": "8px"}),
            html.Div(str(len(entities)), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#0072c3"}),
            html.Div("TOTAL ENTITIES", style={"fontSize": "0.7rem", "color": "#7a9abf", "letterSpacing": "0.05em"}),
        ], className="metric-card"), md=3),
        
        dbc.Col(html.Div([
            html.Div("⚡", style={"fontSize": "2rem", "marginBottom": "8px"}),
            html.Div(str(len(actions)), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#f1620a"}),
            html.Div("PENDING ACTIONS", style={"fontSize": "0.7rem", "color": "#7a9abf", "letterSpacing": "0.05em"}),
        ], className="metric-card"), md=3),
        
        dbc.Col(html.Div([
            html.Div("🎯", style={"fontSize": "2rem", "marginBottom": "8px"}),
            html.Div(str(len(targets)), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#6929c4"}),
            html.Div("TARGETS", style={"fontSize": "0.7rem", "color": "#7a9abf", "letterSpacing": "0.05em"}),
        ], className="metric-card"), md=3),
        
        dbc.Col(html.Div([
            html.Div("💰", style={"fontSize": "2rem", "marginBottom": "8px"}),
            html.Div("N/A", style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#198038"}),
            html.Div("POTENTIAL MONTHLY SAVINGS", style={"fontSize": "0.7rem", "color": "#7a9abf", "letterSpacing": "0.05em"}),
        ], className="metric-card"), md=3),
    ], className="mb-4")
    
    # Chart Row 1: Entity Distribution + Actions by Type
    fig_entities = go.Figure()
    fig_actions = go.Figure()
    
    if not entity_df.empty:
        top_entities = dict(sorted(entity_df["Type"].value_counts().items(), key=lambda x: x[1], reverse=True)[:10])
        fig_entities = go.Figure(go.Pie(
            labels=list(top_entities.keys()),
            values=list(top_entities.values()),
            hole=0.6,
            marker_colors=[ENTITY_COLORS.get(k, "#888") for k in top_entities.keys()],
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_entities.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                  title=dict(text="Entity Distribution", font=dict(size=12, color="#e0eeff")))
    
    if not action_df.empty:
        act_counts = action_df["type"].value_counts().reset_index()
        act_counts.columns = ["Action Type", "Count"]
        fig_actions = go.Figure(go.Bar(
            x=act_counts["Action Type"],
            y=act_counts["Count"],
            marker_color=[ACTION_COLORS.get(t, "#888") for t in act_counts["Action Type"]],
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_actions.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                 title=dict(text="Pending Actions by Type", font=dict(size=12, color="#e0eeff")),
                                 xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
    
    charts_row1 = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_entities, config={"displayModeBar": False}), md=6),
        dbc.Col(dcc.Graph(figure=fig_actions, config={"displayModeBar": False}), md=6),
    ], className="mb-4")
    
    # Chart Row 2: Severity Breakdown + Target Health
    fig_severity = go.Figure()
    fig_targets = go.Figure()
    
    if not action_df.empty:
        sev_counts = action_df["severity"].value_counts()
        fig_severity = go.Figure(go.Pie(
            labels=sev_counts.index.tolist(),
            values=sev_counts.values.tolist(),
            hole=0.6,
            marker_colors=[SEVERITY_COLORS.get(k, "#888") for k in sev_counts.index],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} actions<extra></extra>",
        ))
        fig_severity.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                  title=dict(text="Action Severity Breakdown", font=dict(size=12, color="#e0eeff")))
    
    if not target_df.empty:
        status_counts = target_df["status"].value_counts()
        status_colors_map = {"Validated": "#42be65", "Discovered": "#da1e28", "Failed": "#da1e28"}
        fig_targets = go.Figure(go.Bar(
            x=status_counts.index.tolist(),
            y=status_counts.values.tolist(),
            marker_color=[status_colors_map.get(s, "#888") for s in status_counts.index],
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_targets.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                 title=dict(text="Target Health Status", font=dict(size=12, color="#e0eeff")),
                                 xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
    
    charts_row2 = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_severity, config={"displayModeBar": False}), md=6),
        dbc.Col(dcc.Graph(figure=fig_targets, config={"displayModeBar": False}), md=6),
    ], className="mb-4")
    
    # Chart Row 3: Savings Opportunities (Placeholder)
    fig_savings = go.Figure()
    fig_savings.add_annotation(
        text="Savings Opportunities Chart<br>(Implementation Pending)",
        xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="#7a9abf")
    )
    fig_savings.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                             title=dict(text="Top Savings Opportunities", font=dict(size=12, color="#e0eeff")))
    
    charts_row3 = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_savings, config={"displayModeBar": False}), md=12),
    ], className="mb-4")
    
    return html.Div([
        html.Div([
            html.H4("Overview", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P("Resource management dashboard", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        metrics_row,
        charts_row1,
        charts_row2,
        charts_row3
    ])


# ============================================================================
# TAB 2: PENDING ACTIONS
# ============================================================================

@app.callback(
    Output("actions-store", "data"),
    Input("actions-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_actions_data(n, auth_data):
    """Load pending actions data."""
    try:
        client = get_client(auth_data)
        actions = client.get_pending_actions(limit=500)
        
        rows = []
        for a in actions:
            target = a.get("target", {}) or {}
            entity_type = target.get("className", "")
            
            # Extract namespace from OpenShift/Kubernetes cluster
            # Different strategies based on entity type
            namespace = "—"
            
            # For Kubernetes/OpenShift entities, check multiple locations
            # Strategy 1: Direct namespace field (most common for Pods, Containers, WorkloadControllers)
            namespace = target.get("namespace")
            if namespace:
                pass  # Found it
            
            # Strategy 2: From aspects (some entity types)
            elif target.get("aspects"):
                aspects = target.get("aspects", {})
                if isinstance(aspects, dict):
                    namespace = aspects.get("namespace")
            
            # Strategy 3: From environment
            elif target.get("environment"):
                env_data = target.get("environment", {})
                if isinstance(env_data, dict):
                    namespace = env_data.get("namespace")
            
            # Strategy 4: From providers array (for child entities)
            elif target.get("providers"):
                providers = target.get("providers", [])
                if isinstance(providers, list):
                    for provider in providers:
                        if isinstance(provider, dict):
                            prov_ns = provider.get("namespace")
                            if prov_ns:
                                namespace = prov_ns
                                break
            
            # Strategy 5: From consumers array (for parent entities)
            elif target.get("consumers"):
                consumers = target.get("consumers", [])
                if isinstance(consumers, list):
                    for consumer in consumers:
                        if isinstance(consumer, dict):
                            cons_ns = consumer.get("namespace")
                            if cons_ns:
                                namespace = cons_ns
                                break
            
            # Strategy 6: Parse from displayName (last resort)
            # Format is typically: namespace/pod-name
            if not namespace:
                display_name = target.get("displayName", "")
                if "/" in display_name:
                    parts = display_name.split("/")
                    if len(parts) >= 2:
                        # Namespace is the FIRST part (before the slash)
                        potential_ns = parts[0]
                        # Validate it looks like a namespace (lowercase, hyphens, no spaces)
                        if potential_ns and " " not in potential_ns:
                            namespace = potential_ns
            
            # Default to "—" if still not found
            if not namespace:
                namespace = "—"
            
            # Log for debugging (first 10 actions to see more patterns)
            if len(rows) < 10:
                log.info(f"Action {len(rows)+1}: entity={entity_type}, namespace={namespace}, displayName={target.get('displayName', 'N/A')}")
            
            rows.append({
                "UUID": a.get("uuid", "—"),
                "Action Type": a.get("actionType", "Unknown"),
                "Namespace": namespace,
                "Entity": target.get("displayName", "Unknown"),
                "Entity Type": target.get("className", "Unknown"),
                "Description": a.get("details", "No details"),
                "Severity": a.get("risk", {}).get("severity", "NORMAL") if isinstance(a.get("risk"), dict) else "NORMAL",
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load actions: %s", exc)
        return []


@app.callback(
    Output("actions-content", "children"),
    Input("actions-store", "data")
)
def render_actions(data):
    """Render Pending Actions tab."""
    if not data:
        return dbc.Alert("No pending actions found.", color="info")
    
    df = pd.DataFrame(data)
    
    # Charts Row
    fig_type = go.Figure()
    fig_entity = go.Figure()
    fig_severity = go.Figure()
    
    if not df.empty:
        # Action Type Breakdown
        type_counts = df["Action Type"].value_counts()
        fig_type = go.Figure(go.Bar(
            x=type_counts.index.tolist(),
            y=type_counts.values.tolist(),
            marker_color=[ACTION_COLORS.get(t, "#888") for t in type_counts.index],
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_type.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                              title=dict(text="Action Type Breakdown", font=dict(size=12, color="#e0eeff")),
                              xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
        
        # By Entity Type
        entity_counts = df["Entity Type"].value_counts().head(10)
        fig_entity = go.Figure(go.Bar(
            x=entity_counts.values.tolist(),
            y=entity_counts.index.tolist(),
            orientation="h",
            marker_color=[ENTITY_COLORS.get(t, "#4a6fa5") for t in entity_counts.index],
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
        ))
        fig_entity.update_layout(**BASE_LAYOUT, height=280,
                                title=dict(text="By Entity Type", font=dict(size=12, color="#e0eeff")),
                                xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR),
                                margin=dict(l=120, r=10, t=30, b=10))
        
        # Severity Distribution
        sev_counts = df["Severity"].value_counts()
        fig_severity = go.Figure(go.Pie(
            labels=sev_counts.index.tolist(),
            values=sev_counts.values.tolist(),
            hole=0.6,
            marker_colors=[SEVERITY_COLORS.get(k, "#888") for k in sev_counts.index],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} actions<extra></extra>",
        ))
        fig_severity.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                  title=dict(text="Severity Distribution", font=dict(size=12, color="#e0eeff")))
    
    charts_row = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_type, config={"displayModeBar": False}), md=4),
        dbc.Col(dcc.Graph(figure=fig_entity, config={"displayModeBar": False}), md=4),
        dbc.Col(dcc.Graph(figure=fig_severity, config={"displayModeBar": False}), md=4),
    ], className="mb-4")
    
    # Filters Row 1
    filters_row1 = dbc.Row([
        dbc.Col([
            html.Label("Action Type", className="filter-label"),
            dcc.Dropdown(
                id="filter-action-type",
                options=[{"label": t, "value": t} for t in sorted(df["Action Type"].unique())],
                placeholder="All Types",
                multi=True,
                clearable=True,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Namespace", className="filter-label"),
            dcc.Dropdown(
                id="filter-namespace",
                options=[{"label": ns, "value": ns} for ns in sorted(df["Namespace"].unique()) if ns != "—"],
                placeholder="All Namespaces",
                multi=True,
                clearable=True,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Entity Type", className="filter-label"),
            dcc.Dropdown(
                id="filter-entity-type",
                options=[{"label": t, "value": t} for t in sorted(df["Entity Type"].unique())],
                placeholder="All Entity Types",
                multi=True,
                clearable=True,
            ),
        ], md=3),
        dbc.Col([
            html.Label("Severity", className="filter-label"),
            dcc.Dropdown(
                id="filter-severity",
                options=[{"label": s, "value": s} for s in ["CRITICAL", "MAJOR", "MINOR", "NORMAL"]],
                placeholder="All Severities",
                multi=True,
                clearable=True,
            ),
        ], md=3),
    ], className="mb-3")
    
    # Filters Row 2 (Search)
    filters_row2 = dbc.Row([
        dbc.Col([
            html.Label("Search Entity Name", className="filter-label"),
            dbc.Input(id="filter-search", type="text", placeholder="Type to search..."),
        ], md=12),
    ], className="mb-4")
    
    # Actions Table
    table = dash_table.DataTable(
        id="actions-table",
        columns=[
            {"name": "Action Type", "id": "Action Type"},
            {"name": "Namespace", "id": "Namespace"},
            {"name": "Entity", "id": "Entity"},
            {"name": "Description", "id": "Description"},
            {"name": "Severity", "id": "Severity"},
        ],
        data=_df_to_records(df[["Action Type", "Namespace", "Entity", "Description", "Severity"]]),
        page_size=20,
        row_selectable="multi",
        selected_rows=[],
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
        ],
    )
    
    # Execute Button
    execute_section = html.Div([
        dbc.Button("Execute Selected", id="btn-execute-actions", color="primary", className="mt-3"),
        dbc.Toast(
            id="execute-toast",
            header="Action Execution",
            is_open=False,
            dismissable=True,
            icon="success",
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
        ),
        dbc.Modal([
            dbc.ModalHeader("Confirm Action Execution"),
            dbc.ModalBody(id="execute-modal-body"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="btn-execute-cancel", color="secondary"),
                dbc.Button("Execute", id="btn-execute-confirm", color="danger"),
            ]),
        ], id="execute-modal", is_open=False),
    ])
    
    return html.Div([
        html.Div([
            html.H4("Pending Actions", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} recommended actions", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        charts_row,
        filters_row1,
        filters_row2,
        table,
        execute_section
    ])


@app.callback(
    Output("actions-table", "data"),
    Input("filter-action-type", "value"),
    Input("filter-namespace", "value"),
    Input("filter-entity-type", "value"),
    Input("filter-severity", "value"),
    Input("filter-search", "value"),
    State("actions-store", "data"),
    prevent_initial_call=True
)
def filter_actions_table(action_types, namespaces, entity_types, severities, search, stored_data):
    """Filter actions table based on selected filters."""
    df = pd.DataFrame(stored_data)
    
    if action_types:
        df = df[df["Action Type"].isin(action_types)]
    if namespaces:
        df = df[df["Namespace"].isin(namespaces)]
    if entity_types:
        df = df[df["Entity Type"].isin(entity_types)]
    if severities:
        df = df[df["Severity"].isin(severities)]
    if search and search.strip():
        df = df[df["Entity"].str.contains(search.strip(), case=False, na=False)]
    
    return _df_to_records(df[["Action Type", "Entity", "Description", "Severity"]])


@app.callback(
    Output("execute-modal", "is_open"),
    Output("execute-modal-body", "children"),
    Input("btn-execute-actions", "n_clicks"),
    Input("btn-execute-cancel", "n_clicks"),
    State("actions-table", "selected_rows"),
    State("actions-table", "data"),
    prevent_initial_call=True
)
def show_execute_modal(execute_clicks, cancel_clicks, selected_rows, table_data):
    """Show confirmation modal for action execution."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, ""
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-execute-cancel":
        return False, ""
    
    if button_id == "btn-execute-actions":
        if not selected_rows:
            return False, ""
        
        selected_actions = [table_data[i] for i in selected_rows if i < len(table_data)]
        action_list = html.Ul([html.Li(f"{a['Action Type']} - {a['Entity']}") for a in selected_actions])
        
        return True, html.Div([
            html.P(f"You are about to execute {len(selected_actions)} action(s):"),
            action_list,
            html.P("This action cannot be undone. Continue?", style={"color": "#da1e28", "fontWeight": "600"}),
        ])
    
    return False, ""


@app.callback(
    Output("execute-toast", "is_open"),
    Output("execute-toast", "children"),
    Output("execute-toast", "icon"),
    Output("actions-table", "selected_rows"),
    Output("execute-modal", "is_open", allow_duplicate=True),
    Input("btn-execute-confirm", "n_clicks"),
    State("actions-table", "selected_rows"),
    State("actions-store", "data"),
    State("auth-store", "data"),
    prevent_initial_call=True
)
def execute_selected_actions(n_clicks, selected_rows, store_data, auth_data):
    """Execute selected actions with detailed feedback."""
    if not n_clicks or not selected_rows:
        return no_update, no_update, no_update, no_update, no_update
    
    client = get_client(auth_data)
    actions = [store_data[i] for i in selected_rows if i < len(store_data)]
    success, failed, error_details = [], [], []
    
    for action in actions:
        uuid = action.get("UUID", "")
        entity_name = action.get("Entity", "unknown")
        
        if not uuid or uuid == "—":
            failed.append(entity_name)
            error_details.append(f"{entity_name}: Missing UUID")
            continue
        
        try:
            client.execute_action(uuid)
            success.append(entity_name)
        except Exception as exc:
            failed.append(entity_name)
            error_details.append(f"{entity_name}: {type(exc).__name__}")
    
    # Build feedback
    parts = []
    if success:
        parts.append(html.Div([
            html.Strong("✓ Successfully Executed:", style={"color": "#42be65"}),
            html.Ul([html.Li(name) for name in success])
        ]))
    if failed:
        parts.append(html.Div([
            html.Strong("✗ Failed:", style={"color": "#da1e28"}),
            html.Ul([html.Li(detail) for detail in error_details])
        ]))
    
    icon = "success" if not failed else ("danger" if not success else "warning")
    return True, html.Div(parts), icon, [], False


# ============================================================================
# TAB 3: ENTITIES
# ============================================================================

@app.callback(
    Output("entities-store", "data"),
    Input("entities-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_entities_data(n, auth_data):
    """Load entities data."""
    try:
        client = get_client(auth_data)
        entities = client.get_entities(limit=1000)
        
        rows = []
        for e in entities:
            rows.append({
                "Entity": e.get("displayName", "Unknown"),
                "Type": e.get("className", "Unknown"),
                "State": e.get("state", "UNKNOWN"),
                "Environment": e.get("environmentType", "Unknown"),
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load entities: %s", exc)
        return []


@app.callback(
    Output("entities-content", "children"),
    Input("entities-store", "data")
)
def render_entities(data):
    """Render Entities tab."""
    if not data:
        return dbc.Alert("No entities found.", color="info")
    
    df = pd.DataFrame(data)
    
    # Charts Row
    fig_state = go.Figure()
    fig_type = go.Figure()
    fig_env = go.Figure()
    
    if not df.empty:
        # State Distribution
        state_counts = df["State"].value_counts()
        fig_state = go.Figure(go.Bar(
            x=state_counts.index.tolist(),
            y=state_counts.values.tolist(),
            marker_color=[STATE_COLORS.get(s, "#888") for s in state_counts.index],
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_state.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                               title=dict(text="State Distribution", font=dict(size=12, color="#e0eeff")),
                               xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
        
        # Top Entity Types
        type_counts = df["Type"].value_counts().head(10)
        fig_type = go.Figure(go.Bar(
            x=type_counts.values.tolist(),
            y=type_counts.index.tolist(),
            orientation="h",
            marker_color=[ENTITY_COLORS.get(t, "#4a6fa5") for t in type_counts.index],
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
        ))
        fig_type.update_layout(**BASE_LAYOUT, height=280,
                              title=dict(text="Top Entity Types", font=dict(size=12, color="#e0eeff")),
                              xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=10)),
                              margin=dict(l=160, r=10, t=30, b=10))
        
        # By Environment
        env_counts = df["Environment"].value_counts()
        fig_env = go.Figure(go.Pie(
            labels=env_counts.index.tolist(),
            values=env_counts.values.tolist(),
            hole=0.6,
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_env.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                             title=dict(text="By Environment", font=dict(size=12, color="#e0eeff")))
    
    charts_row = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_state, config={"displayModeBar": False}), md=4),
        dbc.Col(dcc.Graph(figure=fig_type, config={"displayModeBar": False}), md=4),
        dbc.Col(dcc.Graph(figure=fig_env, config={"displayModeBar": False}), md=4),
    ], className="mb-4")
    
    # Filters Row
    filters_row = dbc.Row([
        dbc.Col([
            html.Label("Entity Type", className="filter-label"),
            dcc.Dropdown(
                id="filter-entity-type-single",
                options=[{"label": t, "value": t} for t in sorted(df["Type"].unique())],
                placeholder="All Types",
                clearable=True,
            ),
        ], md=4),
        dbc.Col([
            html.Label("State", className="filter-label"),
            dcc.Dropdown(
                id="filter-state",
                options=[{"label": s, "value": s} for s in sorted(df["State"].unique())],
                placeholder="All States",
                clearable=True,
            ),
        ], md=4),
        dbc.Col([
            html.Label("Search Entity Name", className="filter-label"),
            dbc.Input(id="filter-entity-search", type="text", placeholder="Type to search..."),
        ], md=4),
    ], className="mb-4")
    
    # Entity Inventory Table
    table = dash_table.DataTable(
        id="entities-table",
        columns=[{"name": "Entity Name", "id": "Entity"}],
        data=_df_to_records(df[["Entity"]]),
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
        ],
    )
    
    return html.Div([
        html.Div([
            html.H4("Entities", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} entities discovered", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        charts_row,
        filters_row,
        table
    ])


@app.callback(
    Output("entities-table", "data"),
    Input("filter-entity-type-single", "value"),
    Input("filter-state", "value"),
    Input("filter-entity-search", "value"),
    State("entities-store", "data"),
    prevent_initial_call=True
)
def filter_entities_table(entity_type, state, search, stored_data):
    """Filter entity inventory based on selected filters."""
    df = pd.DataFrame(stored_data)
    
    if entity_type:
        df = df[df["Type"] == entity_type]
    if state:
        df = df[df["State"] == state]
    if search and search.strip():
        df = df[df["Entity"].str.contains(search.strip(), case=False, na=False)]
    
    return _df_to_records(df[["Entity"]])


# ============================================================================
# TAB 4: APP STATISTICS (Simplified version)
# ============================================================================

@app.callback(
    Output("app-stats-content", "children"),
    Input("app-stats-interval", "n_intervals"),
    prevent_initial_call=False
)
def render_app_stats_initial(_n):
    """Initial render of App Stats tab with search interface."""
    return html.Div([
        html.Div([
            html.H4("Application Statistics", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P("Search and analyze application performance", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        
        # Search Interface
        dbc.Row([
            dbc.Col([
                html.Label("Application Name", className="filter-label"),
                dbc.Input(
                    id="appstats-search-input",
                    type="text",
                    placeholder="Enter application name (min 2 characters)...",
                    className="custom-input"
                ),
            ], md=8),
            dbc.Col([
                html.Label(" ", className="filter-label", style={"visibility": "hidden"}),
                dbc.Button("Search", id="btn-appstats-search", color="primary", className="w-100"),
            ], md=4),
        ], className="mb-3"),
        
        # Search Status Message
        html.Div(id="appstats-search-status", className="mb-3"),
        
        # Application Dropdown
        dbc.Row([
            dbc.Col([
                html.Label("Select Application", className="filter-label"),
                dcc.Dropdown(
                    id="appstats-app-dropdown",
                    options=[],
                    placeholder="Search for applications first...",
                    clearable=True,
                    className="custom-dropdown"
                ),
            ], md=12),
        ], className="mb-4"),
        
        # Results Container
        html.Div(id="appstats-results-container")
    ])


# ============================================================================

# Application Statistics - Search Callback
@app.callback(
    Output("appstats-app-dropdown", "options"),
    Output("appstats-search-status", "children"),
    Input("btn-appstats-search", "n_clicks"),
    State("appstats-search-input", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True
)
def search_applications_callback(_btn, search_text, auth_data):
    """Search for applications using server-side filtering."""
    if not search_text or len(search_text.strip()) < 2:
        return [], html.Span("⚠️ Type at least 2 characters to search.", 
                            style={"color": "#f1c21b", "fontSize": "0.9rem"})
    
    try:
        client = get_client(auth_data)
        apps = client.search_applications(name_filter=search_text.strip(), limit=500)
    except Exception as exc:
        log.error("Application search failed: %s", exc)
        return [], html.Span(f"❌ Search failed: {exc}", 
                            style={"color": "#da1e28", "fontSize": "0.9rem"})
    
    if not apps:
        return [], html.Span(f"⚠️ No applications found matching '{search_text}'.", 
                            style={"color": "#f1c21b", "fontSize": "0.9rem"})
    
    options = [
        {"label": f"{a.get('displayName', '?')} [{a.get('className', '?')}]",
         "value": a.get("uuid", "")}
        for a in apps if a.get("uuid")
    ]
    
    status_msg = html.Span(f"✓ {len(apps)} application(s) found — select one below.", 
                          style={"color": "#42be65", "fontSize": "0.9rem"})
    return options, status_msg


# Application Statistics - Display Time Range and Load Button
@app.callback(
    Output("appstats-results-container", "children"),
    Input("appstats-app-dropdown", "value"),
    prevent_initial_call=True
)
def display_time_range_selector(_app_uuid):
    """Display time range selector and Load Stats button when app is selected."""
    if not _app_uuid:
        return html.Div()
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Time Range", className="filter-label"),
                dcc.RadioItems(
                    id="appstats-time-range",
                    options=[
                        {"label": "Last 24 Hours", "value": "24h"},
                        {"label": "Last 7 Days", "value": "7d"},
                        {"label": "Last 30 Days", "value": "30d"},
                        {"label": "Last 90 Days", "value": "90d"},
                    ],
                    value="7d",
                    inline=True,
                    style={"color": "#ffffff"},
                    labelStyle={"color": "#ffffff", "marginRight": "20px"}
                ),
            ], md=8),
            dbc.Col([
                html.Label(" ", className="filter-label", style={"visibility": "hidden"}),
                dbc.Button("Load Statistics", id="btn-load-appstats", color="primary", className="w-100"),
            ], md=4),
        ], className="mb-4"),
        
        html.Div(id="appstats-charts-container")
    ])


# Application Statistics - Load and Display Statistics
@app.callback(
    Output("appstats-charts-container", "children", allow_duplicate=True),
    Input("btn-load-appstats", "n_clicks"),
    State("appstats-app-dropdown", "value"),
    State("appstats-time-range", "value"),
    State("auth-store", "data"),
    prevent_initial_call=True
)
def load_app_statistics(_btn, app_uuid, time_range, auth_data):
    """Load and display application statistics with time-series charts."""
    if _btn is None:
        return no_update
    
    if not app_uuid:
        return dbc.Alert("Please select an application first.", color="warning")
    
    try:
        import time
        client = get_client(auth_data)
        
        # Get application details
        app_entity = client.get_entity(app_uuid)
        if not app_entity:
            return dbc.Alert("Application not found.", color="danger")
        
        app_name = app_entity.get("displayName", "Unknown")
        app_class = app_entity.get("className", "BusinessApplication")
        
        # Calculate time range
        end_ms = int(time.time() * 1000)
        time_ranges = {
            "24h": 24 * 3600 * 1000,
            "7d": 7 * 24 * 3600 * 1000,
            "30d": 30 * 24 * 3600 * 1000,
            "90d": 90 * 24 * 3600 * 1000,
        }
        start_ms = end_ms - time_ranges.get(time_range, time_ranges["7d"])
        
        # Get time-series statistics
        commodities = ["ResponseTime", "Transaction"]
        snapshots = client.get_entity_time_series(app_uuid, commodities, start_ms, end_ms)
        
        # Process time-series data
        stat_series = {}
        for snapshot in snapshots:
            ts_ms = snapshot.get("date", 0)
            ts = safe_timestamp_to_datetime(ts_ms)
            
            statistics = snapshot.get("statistics", [])
            for stat in statistics:
                name = stat.get("name", "Unknown")
                units = stat.get("units", "")
                vals = stat.get("values", {}) or {}
                cap = stat.get("capacity", {}) or {}
                
                if name not in stat_series:
                    stat_series[name] = {
                        "dates": [], "avg": [], "max": [], "min": [],
                        "cap_avg": [], "units": units
                    }
                
                stat_series[name]["dates"].append(ts)
                stat_series[name]["avg"].append(vals.get("avg", None))
                stat_series[name]["max"].append(vals.get("max", None))
                stat_series[name]["min"].append(vals.get("min", None))
                stat_series[name]["cap_avg"].append(cap.get("avg", None))
        
        # Get latest values for metric cards
        response_time_val = "N/A"
        transaction_val = "N/A"
        
        if "ResponseTime" in stat_series:
            avgs = [v for v in stat_series["ResponseTime"]["avg"] if v is not None]
            if avgs:
                units = stat_series["ResponseTime"]["units"]
                response_time_val = f"{avgs[-1]:.1f} {units}"
        
        if "Transaction" in stat_series:
            avgs = [v for v in stat_series["Transaction"]["avg"] if v is not None]
            if avgs:
                units = stat_series["Transaction"]["units"]
                transaction_val = f"{avgs[-1]:.1f} {units}"
        
        # Get pending actions count
        try:
            actions = client.get_entity_actions(app_uuid, limit=100)
            pending_count = len(actions)
        except Exception:
            pending_count = 0
        
        # Application Header
        app_header = html.Div([
            html.H5(f"📱 {app_name}", style={"color": "#e0eeff", "marginBottom": "4px"}),
            html.P(f"Type: {app_class}", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="mb-3")
        
        # Metric Cards
        metrics_row = dbc.Row([
            dbc.Col(html.Div([
                html.Div(response_time_val.split()[0] if response_time_val != "N/A" else "N/A",
                        style={"fontSize": "2.2rem", "fontWeight": "700", "color": "#0072c3"}),
                html.Div("ResponseTime", style={"fontSize": "0.75rem", "color": "#7a9abf"}),
            ], className="chart-card", style={"padding": "20px", "textAlign": "center"}), md=4),
            
            dbc.Col(html.Div([
                html.Div(transaction_val.split()[0] if transaction_val != "N/A" else "N/A",
                        style={"fontSize": "2.2rem", "fontWeight": "700", "color": "#198038"}),
                html.Div("Transaction", style={"fontSize": "0.75rem", "color": "#7a9abf"}),
            ], className="chart-card", style={"padding": "20px", "textAlign": "center"}), md=4),
            
            dbc.Col(html.Div([
                html.Div(str(pending_count),
                        style={"fontSize": "2.2rem", "fontWeight": "700", "color": "#f1620a"}),
                html.Div("Pending Actions", style={"fontSize": "0.75rem", "color": "#7a9abf"}),
            ], className="chart-card", style={"padding": "20px", "textAlign": "center"}), md=4),
        ], className="mb-4")
        
        # Create charts
        charts = []
        for commodity in ["Transaction", "ResponseTime"]:
            if commodity not in stat_series:
                continue
            
            series = stat_series[commodity]
            dates = series["dates"]
            avg_vals = series["avg"]
            max_vals = series["max"]
            cap_vals = series["cap_avg"]
            units = series["units"]
            
            fig = go.Figure()
            
            # Average line with area fill
            fig.add_trace(go.Scatter(
                x=dates, y=avg_vals, name="Average", mode="lines",
                line=dict(color="#0072c3", width=3, shape="spline"),
                fill="tozeroy", fillcolor="rgba(0, 114, 195, 0.1)",
                hovertemplate="<b>Average</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.2f} " + units + "<extra></extra>",
            ))
            
            # Maximum line
            if max_vals and len(max_vals) == len(dates):
                fig.add_trace(go.Scatter(
                    x=dates, y=max_vals, name="Maximum", mode="lines",
                    line=dict(color="#da1e28", width=2, dash="dot", shape="spline"),
                    hovertemplate="<b>Maximum</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.2f} " + units + "<extra></extra>",
                ))
            
            # Capacity line
            if cap_vals and len(cap_vals) == len(dates):
                fig.add_trace(go.Scatter(
                    x=dates, y=cap_vals, name="Capacity", mode="lines",
                    line=dict(color="#f1c21b", width=2, dash="dash", shape="spline"),
                    hovertemplate="<b>Capacity</b><br>%{x|%Y-%m-%d %H:%M}<br>%{y:.2f} " + units + "<extra></extra>",
                ))
            
            fig.update_layout(
                **BASE_LAYOUT, height=320, margin=dict(l=60, r=30, t=50, b=40),
                title=dict(text=f"{commodity} ({units})", font=dict(size=13, color="#e0eeff")),
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#161b2e", font_size=12, bordercolor="#0072c3"),
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                xaxis=dict(gridcolor=GRID_COLOR, showgrid=True),
                yaxis=dict(gridcolor=GRID_COLOR, showgrid=True, title=units),
            )
            
            charts.append(dbc.Col(dcc.Graph(figure=fig, config={"displayModeBar": False}), md=6))
        
        charts_row = dbc.Row(charts, className="mb-4") if charts else html.Div()
        
        # ===================================================================
        # GET CURRENT STATISTICS using /stats API
        # ===================================================================
        try:
            # Get statistics for the application itself
            current_stats = client.get_entity_stats(app_uuid)
            log.info(f"Retrieved {len(current_stats)} statistics for app {app_uuid}")
            
            # If application has no statistics, try to get from related VMs
            if not current_stats:
                log.info(f"No direct stats for app, fetching from related VMs...")
                related_entities = client.get_entity_related(app_uuid)
                log.info(f"Found {len(related_entities)} related entities")
                
                # Get statistics from related VMs
                for related in related_entities[:5]:  # Limit to first 5 VMs
                    related_uuid = related.get("uuid")
                    related_class = related.get("className", "")
                    
                    if related_uuid and "VirtualMachine" in related_class:
                        try:
                            vm_stats = client.get_entity_stats(related_uuid)
                            if vm_stats:
                                log.info(f"Retrieved {len(vm_stats)} stats from VM {related_uuid}")
                                # Add source information to each stat
                                for stat in vm_stats:
                                    stat["_source_vm"] = related.get("displayName", "VM")
                                    stat["_source_uuid"] = related_uuid
                                current_stats.extend(vm_stats)
                        except Exception as vm_exc:
                            log.debug(f"Failed to get stats from VM {related_uuid}: {vm_exc}")
                
                if current_stats:
                    log.info(f"Total {len(current_stats)} statistics from related VMs")
                else:
                    log.warning(f"No statistics available from app or related VMs")
                    
        except Exception as exc:
            log.error(f"Failed to get entity stats: {exc}")
            current_stats = []
        
        # Group statistics by category
        cpu_stats = []
        memory_stats = []
        storage_stats = []
        network_stats = []
        other_stats = []
        
        for stat in current_stats:
            name = stat.get("name", "")
            if any(x in name.upper() for x in ["CPU", "VCPU", "PROCESSOR"]):
                cpu_stats.append(stat)
            elif any(x in name.upper() for x in ["MEM", "MEMORY", "VMEM", "BALLOON", "SWAP"]):
                memory_stats.append(stat)
            elif any(x in name.upper() for x in ["STORAGE", "DISK", "IOPS", "LATENCY"]):
                storage_stats.append(stat)
            elif any(x in name.upper() for x in ["NET", "NETWORK", "THROUGHPUT"]):
                network_stats.append(stat)
            else:
                other_stats.append(stat)
        
        # Create statistics section header
        stats_header = html.Div([
            html.Hr(style={"borderColor": "#1e2a45", "margin": "30px 0 20px 0"}),
            html.H5("📊 Current Resource Statistics",
                   style={"color": "#e0eeff", "marginBottom": "20px"}),
        ])
        
        # Helper function to create stat cards
        def create_stat_cards(stats_list, title, color):
            if not stats_list:
                return html.Div()
            
            cards = []
            for stat in stats_list[:6]:  # Limit to 6 stats per category
                name = stat.get("displayName", stat.get("name", "Unknown"))
                
                # Check if this stat came from a related VM
                source_vm = stat.get("_source_vm")
                if source_vm:
                    name = f"{stat.get('name', 'Unknown')} ({source_vm})"
                
                # Shorten display name if too long
                if len(name) > 40:
                    name = name[:37] + "..."
                
                vals = stat.get("values", {}) or {}
                cap = stat.get("capacity", {}) or {}
                units = stat.get("units", "")
                
                value = vals.get("avg", stat.get("value", 0))
                capacity = cap.get("avg", 0)
                
                # Calculate utilization percentage
                utilization = 0
                if capacity and capacity > 0:
                    utilization = (value / capacity) * 100
                
                # Determine color based on utilization
                util_color = "#42be65"  # Green
                if utilization > 80:
                    util_color = "#da1e28"  # Red
                elif utilization > 60:
                    util_color = "#f1c21b"  # Yellow
                
                card = dbc.Col(html.Div([
                    html.Div(name, style={
                        "fontSize": "0.7rem", "color": "#7a9abf",
                        "marginBottom": "8px", "textTransform": "uppercase"
                    }),
                    html.Div([
                        html.Span(f"{value:.1f}" if isinstance(value, (int, float)) else str(value),
                                 style={"fontSize": "1.8rem", "fontWeight": "700", "color": color}),
                        html.Span(f" {units}", style={"fontSize": "0.9rem", "color": "#7a9abf"}),
                    ]),
                    html.Div([
                        html.Span("Capacity: ", style={"fontSize": "0.7rem", "color": "#7a9abf"}),
                        html.Span(f"{capacity:.1f} {units}" if capacity else "N/A",
                                 style={"fontSize": "0.7rem", "color": "#9ab0ce"}),
                    ], style={"marginTop": "4px"}),
                    html.Div([
                        html.Div(style={
                            "width": f"{min(utilization, 100):.0f}%",
                            "height": "4px",
                            "backgroundColor": util_color,
                            "borderRadius": "2px",
                            "marginTop": "8px",
                            "transition": "width 0.3s"
                        })
                    ], style={"backgroundColor": "#1e2a45", "borderRadius": "2px", "height": "4px"}),
                    html.Div(f"{utilization:.1f}% utilized" if capacity else "",
                            style={"fontSize": "0.65rem", "color": "#7a9abf", "marginTop": "4px"}),
                ], className="chart-card", style={"padding": "16px", "height": "100%"}), md=4, className="mb-3")
                
                cards.append(card)
            
            return html.Div([
                html.Div(title, className="chart-section-label",
                        style={"marginTop": "20px", "marginBottom": "12px"}),
                dbc.Row(cards)
            ])
        
        # Create sections for each category
        cpu_section = create_stat_cards(cpu_stats, "CPU & PROCESSOR STATISTICS", "#0072c3")
        memory_section = create_stat_cards(memory_stats, "MEMORY STATISTICS", "#6929c4")
        storage_section = create_stat_cards(storage_stats, "STORAGE & I/O STATISTICS", "#b28600")
        network_section = create_stat_cards(network_stats, "NETWORK STATISTICS", "#198038")
        other_section = create_stat_cards(other_stats, "OTHER STATISTICS", "#f1620a")
        
        # Combine all sections - only show if we have statistics
        if current_stats:
            statistics_section = html.Div([
                stats_header,
                cpu_section,
                memory_section,
                storage_section,
                network_section,
                other_section
            ])
        else:
            # Show informative message if no statistics available
            statistics_section = html.Div([
                html.Hr(style={"borderColor": "#1e2a45", "margin": "30px 0 20px 0"}),
                dbc.Alert([
                    html.H5("📊 Current Resource Statistics", className="alert-heading"),
                    html.P("No detailed statistics available for this application."),
                    html.Hr(),
                    html.P([
                        "This may occur if:",
                        html.Ul([
                            html.Li("The application doesn't have statistics enabled"),
                            html.Li("The Turbonomic version doesn't support the /stats endpoint"),
                            html.Li("The application type doesn't provide detailed metrics"),
                        ])
                    ], className="mb-0"),
                ], color="info", style={"marginTop": "20px"})
            ])
        
        return html.Div([app_header, metrics_row, charts_row, statistics_section])
        
    except Exception as exc:
        log.error("Failed to load app statistics: %s", exc)
        return dbc.Alert(f"Error loading statistics: {exc}", color="danger")

# TAB 5: TARGETS
# ============================================================================

@app.callback(
    Output("targets-store", "data"),
    Input("targets-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_targets_data(n, auth_data):
    """Load targets data."""
    try:
        client = get_client(auth_data)
        targets = client.get_targets()
        
        rows = []
        for t in targets:
            rows.append({
                "Name": t.get("displayName", "—"),
                "Type": safe_get(t, "type", default="—"),
                "Status": t.get("status", "—"),
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load targets: %s", exc)
        return []


@app.callback(
    Output("targets-content", "children"),
    Input("targets-store", "data")
)
def render_targets(data):
    """Render Targets tab."""
    if not data:
        return dbc.Alert("No targets configured.", color="info")
    
    df = pd.DataFrame(data)
    
    # Charts
    fig_status = go.Figure()
    fig_type = go.Figure()
    
    if not df.empty:
        # Status Overview
        status_counts = df["Status"].value_counts()
        status_colors_map = {"Validated": "#42be65", "Discovered": "#da1e28", "Failed": "#da1e28"}
        fig_status = go.Figure(go.Pie(
            labels=status_counts.index.tolist(),
            values=status_counts.values.tolist(),
            hole=0.5,
            marker_colors=[status_colors_map.get(s, "#6f6f6f") for s in status_counts.index],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_status.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                title=dict(text="Target Status", font=dict(size=12, color="#e0eeff")))
        
        # Targets by Type
        type_counts = df["Type"].value_counts().head(10)
        fig_type = go.Figure(go.Bar(
            x=type_counts.values.tolist(),
            y=type_counts.index.tolist(),
            orientation="h",
            marker_color="#0072c3",
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
        ))
        fig_type.update_layout(**BASE_LAYOUT, height=280,
                              title=dict(text="Targets by Type", font=dict(size=12, color="#e0eeff")),
                              xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR),
                              margin=dict(l=120, r=10, t=30, b=10))
    
    charts_row = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_status, config={"displayModeBar": False}), md=6),
        dbc.Col(dcc.Graph(figure=fig_type, config={"displayModeBar": False}), md=6),
    ], className="mb-4")
    
    # Table
    table = dash_table.DataTable(
        data=_df_to_records(df),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
            {"if": {"filter_query": "{Status} = 'Validated'", "column_id": "Status"},
             "color": "#6fdc8c", "fontWeight": "600"},
            {"if": {"filter_query": "{Status} != 'Validated'", "column_id": "Status"},
             "color": "#ff8389", "fontWeight": "600"},
        ],
    )
    
    return html.Div([
        html.Div([
            html.H4("Targets", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} connected targets", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        charts_row,
        table
    ])


# ============================================================================
# TAB 6: GROUPS
# ============================================================================

@app.callback(
    Output("groups-store", "data"),
    Input("groups-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_groups_data(n, auth_data):
    """Load groups data."""
    try:
        client = get_client(auth_data)
        groups = client.get_groups()
        
        rows = []
        for g in groups:
            rows.append({
                "Name": g.get("displayName", "—"),
                "Type": g.get("groupType", "—"),
                "Entity Type": safe_get(g, "entityType", default="—"),
                "Member Count": g.get("memberCount", g.get("entitiesCount", "—")),
                "Origin": g.get("origin", "—"),
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load groups: %s", exc)
        return []


@app.callback(
    Output("groups-content", "children"),
    Input("groups-store", "data")
)
def render_groups(data):
    """Render Groups tab."""
    if not data:
        return dbc.Alert("No groups configured.", color="info")
    
    df = pd.DataFrame(data)
    
    # Charts
    fig_type = go.Figure()
    fig_origin = go.Figure()
    
    if not df.empty:
        # Groups by Type
        type_counts = df["Type"].value_counts()
        fig_type = go.Figure(go.Bar(
            x=type_counts.index.tolist(),
            y=type_counts.values.tolist(),
            marker_color="#0072c3",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_type.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                              title=dict(text="Groups by Type", font=dict(size=12, color="#e0eeff")),
                              xaxis=dict(gridcolor=GRID_COLOR), yaxis=dict(gridcolor=GRID_COLOR))
        
        # Groups by Origin
        origin_counts = df["Origin"].value_counts()
        fig_origin = go.Figure(go.Pie(
            labels=origin_counts.index.tolist(),
            values=origin_counts.values.tolist(),
            hole=0.5,
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_origin.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                title=dict(text="Groups by Origin", font=dict(size=12, color="#e0eeff")))
    
    charts_row = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_type, config={"displayModeBar": False}), md=6),
        dbc.Col(dcc.Graph(figure=fig_origin, config={"displayModeBar": False}), md=6),
    ], className="mb-4")
    
    # Table
    table = dash_table.DataTable(
        data=_df_to_records(df),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
        ],
    )
    
    return html.Div([
        html.Div([
            html.H4("Groups", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} groups configured", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        charts_row,
        table
    ])


# ============================================================================
# TAB 7: KUBERNETES
# ============================================================================

@app.callback(
    Output("clusters-store", "data"),
    Input("clusters-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_clusters_data(n, auth_data):
    """Load Kubernetes clusters data."""
    try:
        client = get_client(auth_data)
        clusters = client.get_clusters()
        
        rows = []
        for c in clusters:
            rows.append({
                "Name": c.get("displayName", "—"),
                "Type": c.get("className", "—"),
                "State": c.get("state", "—"),
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load clusters: %s", exc)
        return []


@app.callback(
    Output("clusters-content", "children"),
    Input("clusters-store", "data")
)
def render_clusters(data):
    """Render Kubernetes tab."""
    if not data:
        return dbc.Alert("No Kubernetes clusters configured.", color="info")
    
    df = pd.DataFrame(data)
    
    # Table
    table = dash_table.DataTable(
        data=_df_to_records(df),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
        ],
    )
    
    return html.Div([
        html.Div([
            html.H4("Kubernetes", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} clusters", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        table
    ])


# ============================================================================
# TAB 8: POLICIES
# ============================================================================

@app.callback(
    Output("policies-store", "data"),
    Input("policies-interval", "n_intervals"),
    State("auth-store", "data")
)
def load_policies_data(n, auth_data):
    """Load policies data."""
    try:
        client = get_client(auth_data)
        policies = client.get_policies()
        
        rows = []
        for p in policies:
            rows.append({
                "Name": p.get("displayName", "—"),
                "Entity Type": safe_get(p, "entityType", default="—"),
                "Type": p.get("policyType", p.get("type", "—")),
                "Enabled": "Yes" if p.get("enabled", False) else "No",
                "Default": "Yes" if p.get("default", False) else "No",
            })
        
        return rows
    except Exception as exc:
        log.error("Failed to load policies: %s", exc)
        return []


@app.callback(
    Output("policies-content", "children"),
    Input("policies-store", "data")
)
def render_policies(data):
    """Render Policies tab."""
    if not data:
        return dbc.Alert("No policies configured.", color="info")
    
    df = pd.DataFrame(data)
    
    # Metrics
    total_policies = len(df)
    enabled_policies = len(df[df["Enabled"] == "Yes"]) if not df.empty else 0
    default_policies = len(df[df["Default"] == "Yes"]) if not df.empty else 0
    
    metrics_row = dbc.Row([
        dbc.Col(html.Div([
            html.Div(str(total_policies), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#0072c3"}),
            html.Div("TOTAL POLICIES", style={"fontSize": "0.7rem", "color": "#7a9abf"}),
        ], className="metric-card", style={"padding": "20px", "textAlign": "center"}), md=4),
        
        dbc.Col(html.Div([
            html.Div(str(enabled_policies), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#42be65"}),
            html.Div("ENABLED", style={"fontSize": "0.7rem", "color": "#7a9abf"}),
        ], className="metric-card", style={"padding": "20px", "textAlign": "center"}), md=4),
        
        dbc.Col(html.Div([
            html.Div(str(default_policies), style={"fontSize": "2.5rem", "fontWeight": "700", "color": "#b28600"}),
            html.Div("DEFAULT POLICIES", style={"fontSize": "0.7rem", "color": "#7a9abf"}),
        ], className="metric-card", style={"padding": "20px", "textAlign": "center"}), md=4),
    ], className="mb-4")
    
    # Chart
    fig_status = go.Figure()
    if not df.empty:
        enabled_counts = df["Enabled"].value_counts()
        fig_status = go.Figure(go.Pie(
            labels=enabled_counts.index.tolist(),
            values=enabled_counts.values.tolist(),
            hole=0.5,
            marker_colors=["#42be65" if label == "Yes" else "#da1e28" for label in enabled_counts.index],
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_status.update_layout(**BASE_LAYOUT, height=280, margin=_DEFAULT_MARGIN,
                                title=dict(text="Policies: Enabled vs Disabled", font=dict(size=12, color="#e0eeff")))
    
    chart_section = dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_status, config={"displayModeBar": False}), md=12),
    ], className="mb-4")
    
    # Table
    table = dash_table.DataTable(
        data=_df_to_records(df),
        columns=[{"name": c, "id": c} for c in df.columns],
        page_size=20,
        filter_action="native",
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={
            "textAlign": "left", "padding": "12px", "backgroundColor": "#1a1f36",
            "color": "#e0e0e0", "border": "1px solid #2d3548",
            "fontFamily": "IBM Plex Sans, sans-serif", "fontSize": "13px",
        },
        style_header={
            "backgroundColor": "#0f1729", "fontWeight": "600", "color": "#ffffff",
            "border": "1px solid #2d3548", "textTransform": "uppercase",
            "fontSize": "11px", "letterSpacing": "0.5px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#161b2e"},
            {"if": {"filter_query": "{Enabled} = 'Yes'", "column_id": "Enabled"},
             "color": "#6fdc8c", "fontWeight": "600"},
            {"if": {"filter_query": "{Enabled} = 'No'", "column_id": "Enabled"},
             "color": "#6f6f6f", "fontWeight": "600"},
        ],
    )
    
    return html.Div([
        html.Div([
            html.H4("Policies", style={"color": "#e0eeff", "fontWeight": "600", "marginBottom": "4px"}),
            html.P(f"{len(df)} policies configured", style={"color": "#7a9abf", "fontSize": "0.85rem"}),
        ], className="page-header"),
        metrics_row,
        chart_section,
        table
    ])


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
