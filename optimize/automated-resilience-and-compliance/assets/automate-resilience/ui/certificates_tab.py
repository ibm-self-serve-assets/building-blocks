"""
Certificates Insights Tab
Displays certificate lifecycle management with expiry tracking and analytics
"""

import logging
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)


def create_layout():
    """
    Create the Certificates insights tab layout
    
    Returns:
        Dash HTML component
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Certificates Insights Dashboard", className="mb-4"),
                html.P("Certificate lifecycle management and expiry tracking", className="text-muted")
            ])
        ]),
        
        # Load button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Load Certificates",
                    id="load-certs-btn",
                    color="primary",
                    className="mb-3"
                )
            ])
        ]),
        
        # Loading spinner
        dcc.Loading(
            id="loading-certs",
            type="default",
            children=[
                # Statistics cards
                html.Div(id="cert-stats-cards"),
                
                # Visualization charts
                html.Div(id="cert-charts", className="mt-4"),
                
                # Certificates data table
                html.Div(id="cert-table-container", className="mt-4")
            ]
        )
    ], fluid=True)


def create_stats_cards(df):
    """
    Create statistics cards for certificate overview
    
    Args:
        df: Certificates DataFrame
        
    Returns:
        Dash HTML component with statistics cards
    """
    if df.empty:
        return html.Div()
    
    total_certs = len(df)
    
    # Count by status
    valid_count = len(df[df['Status'] == 'valid'])
    expired_count = len(df[df['Status'] == 'expired'])
    
    # Count expiring soon (within 30 days)
    expiring_soon = 0
    if 'Days to Expiry' in df.columns:
        expiring_soon = len(df[
            (df['Days to Expiry'] != 'N/A') & 
            (df['Days to Expiry'].apply(lambda x: isinstance(x, (int, float)) and 0 < x <= 30))
        ])
    
    # Average days to expiry
    avg_days = 'N/A'
    if 'Days to Expiry' in df.columns:
        valid_days = df[df['Days to Expiry'].apply(lambda x: isinstance(x, (int, float)) and x > 0)]['Days to Expiry']
        if not valid_days.empty:
            avg_days = f"{valid_days.mean():.0f}"
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(total_certs, className="card-title"),
                    html.P("Total Certificates", className="card-text text-muted")
                ])
            ], color="primary", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(valid_count, className="card-title text-success"),
                    html.P("Valid Certificates", className="card-text text-muted")
                ])
            ], color="success", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(expiring_soon, className="card-title text-warning"),
                    html.P("Expiring Soon (30d)", className="card-text text-muted")
                ])
            ], color="warning", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(expired_count, className="card-title text-danger"),
                    html.P("Expired Certificates", className="card-text text-muted")
                ])
            ], color="danger", outline=True)
        ], md=3)
    ], className="mb-4")
    
    return cards


def create_cert_charts(df):
    """
    Create interactive visualization charts for certificate data
    
    Args:
        df: Certificates DataFrame
        
    Returns:
        Dash HTML component with charts
    """
    if df.empty:
        return html.Div()
    
    # 1. Certificate Status Distribution (Pie Chart)
    status_counts = df['Status'].value_counts()
    status_colors = {
        'valid': '#28a745',
        'expired': '#dc3545',
        'revoked': '#6c757d'
    }
    
    status_fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=0.4,
        marker=dict(colors=[status_colors.get(s, '#007bff') for s in status_counts.index]),
        textinfo='label+value+percent',
        textposition='auto'
    )])
    status_fig.update_layout(
        title="Certificate Status Distribution",
        height=400
    )
    
    # 2. Expiry Timeline (Histogram)
    expiry_fig = html.Div()
    if 'Days to Expiry' in df.columns:
        valid_expiry = df[df['Days to Expiry'].apply(lambda x: isinstance(x, (int, float)) and x > 0)]
        
        if not valid_expiry.empty:
            expiry_hist = go.Figure(data=[go.Histogram(
                x=valid_expiry['Days to Expiry'],
                nbinsx=30,
                marker=dict(color='#17a2b8', opacity=0.7),
                name='Days to Expiry'
            )])
            expiry_hist.update_layout(
                title="Certificate Expiry Timeline",
                xaxis_title="Days Until Expiry",
                yaxis_title="Number of Certificates",
                height=400
            )
            expiry_fig = dcc.Graph(figure=expiry_hist)
    
    # 3. Algorithm Distribution (Bar Chart)
    algo_counts = df['Algorithm'].value_counts().head(10)
    algo_fig = go.Figure(data=[go.Bar(
        x=algo_counts.index,
        y=algo_counts.values,
        marker=dict(color='#ffc107'),
        text=algo_counts.values,
        textposition='auto'
    )])
    algo_fig.update_layout(
        title="Top 10 Certificate Algorithms",
        xaxis_title="Algorithm",
        yaxis_title="Number of Certificates",
        height=400,
        xaxis={'tickangle': 45}
    )
    
    # 4. Key Size Distribution (Bar Chart)
    key_counts = df['Key Size'].value_counts()
    key_fig = go.Figure(data=[go.Bar(
        x=key_counts.index,
        y=key_counts.values,
        marker=dict(color='#6f42c1'),
        text=key_counts.values,
        textposition='auto'
    )])
    key_fig.update_layout(
        title="Key Size Distribution",
        xaxis_title="Key Size (bits)",
        yaxis_title="Number of Certificates",
        height=400
    )
    
    # 5. Certificates Expiring Soon (Top 10)
    expiring_soon = df[df['Days to Expiry'].apply(lambda x: isinstance(x, (int, float)) and 0 < x <= 90)]
    expiring_chart = html.Div()
    
    if not expiring_soon.empty:
        top_expiring = expiring_soon.nsmallest(10, 'Days to Expiry')[['Subject', 'Days to Expiry']]
        
        # Color gradient based on urgency
        colors = []
        for days in top_expiring['Days to Expiry']:
            if days <= 7:
                colors.append('#dc3545')  # Red - Critical
            elif days <= 30:
                colors.append('#ffc107')  # Yellow - Warning
            else:
                colors.append('#17a2b8')  # Blue - Info
        
        expiring_bar = go.Figure(data=[go.Bar(
            x=top_expiring['Days to Expiry'],
            y=top_expiring['Subject'],
            orientation='h',
            marker=dict(color=colors),
            text=top_expiring['Days to Expiry'],
            textposition='auto'
        )])
        expiring_bar.update_layout(
            title="Top 10 Certificates Expiring Soon",
            xaxis_title="Days Until Expiry",
            yaxis_title="Certificate Subject",
            height=500,
            yaxis=dict(autorange='reversed')
        )
        expiring_chart = dbc.Col([
            dcc.Graph(figure=expiring_bar)
        ], md=6)
    
    # Layout charts
    charts_row1 = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=status_fig)
        ], md=6),
        dbc.Col([
            expiry_fig if expiry_fig != html.Div() else html.Div()
        ], md=6)
    ])
    
    charts_row2 = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=algo_fig)
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=key_fig)
        ], md=6)
    ], className="mt-3")
    
    charts_row3 = html.Div()
    if expiring_chart != html.Div():
        charts_row3 = dbc.Row([
            expiring_chart,
            dbc.Col([
                dbc.Alert([
                    html.H5("Expiry Alert Levels", className="alert-heading"),
                    html.Hr(),
                    html.P([
                        html.Span("🔴 Critical: ", style={'color': '#dc3545', 'fontWeight': 'bold'}),
                        "≤ 7 days"
                    ]),
                    html.P([
                        html.Span("🟡 Warning: ", style={'color': '#ffc107', 'fontWeight': 'bold'}),
                        "8-30 days"
                    ]),
                    html.P([
                        html.Span("🔵 Info: ", style={'color': '#17a2b8', 'fontWeight': 'bold'}),
                        "31-90 days"
                    ])
                ], color="light")
            ], md=6)
        ], className="mt-3")
    
    return html.Div([charts_row1, charts_row2, charts_row3])


def create_cert_table(df):
    """
    Create interactive data table for certificate details
    
    Args:
        df: Certificates DataFrame
        
    Returns:
        Dash HTML component with data table
    """
    if df.empty:
        return dbc.Alert("No certificate data available", color="info")
    
    # Apply status and expiry-based styling
    style_data_conditional = [
        # Status-based styling
        {
            'if': {
                'filter_query': '{Status} = "valid"',
                'column_id': 'Status'
            },
            'backgroundColor': '#d4edda',
            'color': '#155724',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{Status} = "expired"',
                'column_id': 'Status'
            },
            'backgroundColor': '#f8d7da',
            'color': '#721c24',
            'fontWeight': 'bold'
        },
        # Expiry warning styling
        {
            'if': {
                'filter_query': '{Days to Expiry} <= 7 && {Days to Expiry} > 0',
                'column_id': 'Days to Expiry'
            },
            'backgroundColor': '#f8d7da',
            'color': '#721c24',
            'fontWeight': 'bold'
        },
        {
            'if': {
                'filter_query': '{Days to Expiry} <= 30 && {Days to Expiry} > 7',
                'column_id': 'Days to Expiry'
            },
            'backgroundColor': '#fff3cd',
            'color': '#856404',
            'fontWeight': 'bold'
        }
    ]
    
    table = dash_table.DataTable(
        id='cert-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=20,
        page_action='native',
        sort_action='native',
        sort_mode='multi',
        filter_action='native',
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'minWidth': '100px',
            'maxWidth': '300px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': '#007bff',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=style_data_conditional,
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('records')
        ],
        tooltip_duration=None
    )
    
    return dbc.Card([
        dbc.CardHeader(html.H4("Certificate Details")),
        dbc.CardBody([
            dbc.Alert([
                html.Strong("Color Coding: "),
                "Red = Expired or Expiring ≤7 days | Yellow = Expiring 8-30 days | Green = Valid"
            ], color="info", className="mb-3"),
            table
        ])
    ])


def register_callbacks(app, api_client):
    """
    Register callbacks for Certificates tab
    
    Args:
        app: Dash application instance
        api_client: ConcertAPIClient instance
    """
    
    @app.callback(
        [Output('cert-stats-cards', 'children'),
         Output('cert-charts', 'children'),
         Output('cert-table-container', 'children')],
        [Input('load-certs-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_certificates(n_clicks):
        """Load and display certificate data"""
        try:
            logger.info("Loading certificates...")
            
            # Fetch certificates from API
            certs = api_client.get_certificates()
            
            if not certs:
                return (
                    dbc.Alert("No certificates found", color="warning"),
                    html.Div(),
                    html.Div()
                )
            
            # Process data
            df = DataProcessor.process_certificates(certs)
            
            # Create visualizations
            stats = create_stats_cards(df)
            charts = create_cert_charts(df)
            table = create_cert_table(df)
            
            logger.info(f"Successfully loaded {len(df)} certificates")
            return stats, charts, table
            
        except Exception as e:
            logger.error(f"Error loading certificates: {str(e)}")
            error_alert = dbc.Alert(
                f"Error loading certificate data: {str(e)}",
                color="danger"
            )
            return error_alert, html.Div(), html.Div()

# Made with Bob
