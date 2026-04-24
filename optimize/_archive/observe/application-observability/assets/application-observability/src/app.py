"""
Main Dash Application

Instana Observability Dashboard for monitoring application health and performance.
"""

from dash import Dash, html, Input, Output, State
import dash_bootstrap_components as dbc

from src.config import Config
from src.utils.logger import setup_logger
from src.integrations.instana_integration import InstanaClient, aggregate_metrics
from src.components.dashboard import create_dashboard_layout, create_dashboard_content


# Initialize logger
logger = setup_logger(__name__, Config.LOG_LEVEL)

# Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="Instana Observability Dashboard"
)

# Set server for deployment
server = app.server

# Create layout
app.layout = create_dashboard_layout(Config.INSTANA_APPLICATION_NAME)


@app.callback(
    Output('dashboard-content', 'children'),
    Input('refresh-button', 'n_clicks'),
    prevent_initial_call=False
)
def update_dashboard(n_clicks):
    """
    Update dashboard content with latest data from Instana.
    
    Args:
        n_clicks: Number of times refresh button was clicked
        
    Returns:
        html.Div: Updated dashboard content
    """
    try:
        logger.info(f"Updating dashboard for application: {Config.INSTANA_APPLICATION_NAME}")
        
        # Initialize Instana client
        client = InstanaClient()
        
        # Fetch all data
        data = client.fetch_all_data(Config.INSTANA_APPLICATION_NAME)
        
        # Check for errors
        if "error" in data:
            logger.error(f"Error fetching data: {data['error']}")
            return dbc.Alert([
                html.H4("⚠️ Unable to Load Data", className="alert-heading"),
                html.P(data['error']),
                html.Hr(),
                html.P([
                    "Please check:",
                    html.Ul([
                        html.Li("Your Instana credentials in .env file"),
                        html.Li(f"Application name '{Config.INSTANA_APPLICATION_NAME}' exists in Instana"),
                        html.Li("Network connectivity to Instana API"),
                        html.Li("API token has correct permissions")
                    ])
                ], className="mb-0")
            ], color="danger", className="m-4")
        
        # Aggregate metrics
        metrics = aggregate_metrics(data)
        
        # Create dashboard content
        content = create_dashboard_content(data, metrics)
        
        logger.info("Dashboard updated successfully")
        return content
        
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}", exc_info=True)
        return dbc.Alert([
            html.H4("❌ Error", className="alert-heading"),
            html.P(f"An unexpected error occurred: {str(e)}"),
            html.Hr(),
            html.P("Please check the application logs for more details.", className="mb-0")
        ], color="danger", className="m-4")


def main():
    """Main entry point for the application."""
    logger.info("=" * 60)
    logger.info("Starting Instana Observability Dashboard")
    logger.info("=" * 60)
    logger.info(f"Application: {Config.INSTANA_APPLICATION_NAME}")
    logger.info(f"Instana URL: {Config.INSTANA_BASE_URL}")
    logger.info(f"Server: http://{Config.APP_HOST}:{Config.APP_PORT}")
    logger.info(f"Debug Mode: {Config.DEBUG_MODE}")
    logger.info("=" * 60)
    
    try:
        app.run_server(
            host=Config.APP_HOST,
            port=Config.APP_PORT,
            debug=Config.DEBUG_MODE
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

# Made with Bob
