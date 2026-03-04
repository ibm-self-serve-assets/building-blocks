"""
IBM Concert Insights Dashboard
Main application entry point with multi-tab navigation
"""

import logging
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Import configuration and setup logging
from config import validate_config, HOST, PORT, DEBUG_MODE, logger

# Import API client
from api.concert_api import ConcertAPIClient

# Import tab modules
from ui import cves_tab, applications_tab, certificates_tab

# Validate configuration before starting
try:
    validate_config()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration validation failed: {str(e)}")
    logger.error("Please check your .env file and ensure all required variables are set")
    raise

# Initialize Dash app with Bootstrap theme
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="IBM Concert Insights Dashboard"
)

# Initialize API client
api_client = ConcertAPIClient()
logger.info("API client initialized")

# App layout with navigation tabs
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("IBM Concert Insights Dashboard", className="text-primary mb-2"),
                html.P(
                    "Comprehensive vulnerability management, application monitoring, and certificate lifecycle tracking",
                    className="text-muted lead"
                )
            ], className="text-center my-4")
        ])
    ]),
    
    html.Hr(),
    
    # Navigation tabs
    dbc.Tabs(
        id="main-tabs",
        active_tab="cves-tab",
        children=[
            dbc.Tab(
                label="🔒 CVE Insights",
                tab_id="cves-tab",
                label_style={"cursor": "pointer"}
            ),
            dbc.Tab(
                label="📱 Applications",
                tab_id="apps-tab",
                label_style={"cursor": "pointer"}
            ),
            dbc.Tab(
                label="🔐 Certificates",
                tab_id="certs-tab",
                label_style={"cursor": "pointer"}
            )
        ],
        className="mb-4"
    ),
    
    # Tab content
    html.Div(id="tab-content"),
    
    # Footer
    html.Hr(className="mt-5"),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.P([
                    "IBM Concert Insights Dashboard | ",
                    html.A("Documentation", href="#", className="text-primary"),
                    " | ",
                    html.A("API Reference", href="#", className="text-primary")
                ], className="text-center text-muted small")
            ])
        ])
    ], className="mb-4")
], fluid=True)


# Callback to render tab content
@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "active_tab")
)
def render_tab_content(active_tab):
    """
    Render content based on selected tab
    
    Args:
        active_tab: ID of the active tab
        
    Returns:
        Tab content layout
    """
    if active_tab == "cves-tab":
        return cves_tab.create_layout()
    elif active_tab == "apps-tab":
        return applications_tab.create_layout()
    elif active_tab == "certs-tab":
        return certificates_tab.create_layout()
    
    return html.Div("Select a tab to view insights")


# Register callbacks for each tab
logger.info("Registering tab callbacks...")
cves_tab.register_callbacks(app, api_client)
applications_tab.register_callbacks(app, api_client)
certificates_tab.register_callbacks(app, api_client)
logger.info("All callbacks registered successfully")


# Run the application
if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting IBM Concert Insights Dashboard")
    logger.info("=" * 80)
    logger.info(f"Host: {HOST}")
    logger.info(f"Port: {PORT}")
    logger.info(f"Debug Mode: {DEBUG_MODE}")
    logger.info("=" * 80)
    
    try:
        app.run_server(
            host=HOST,
            port=PORT,
            debug=DEBUG_MODE
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

# Made with Bob
