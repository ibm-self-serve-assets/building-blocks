"""
CVE Insights Tab
Displays comprehensive CVE analytics with interactive visualizations
"""

import logging
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor

logger = logging.getLogger(__name__)


def create_layout():
    """
    Create the CVE insights tab layout
    
    Returns:
        Dash HTML component
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("CVE Insights Dashboard", className="mb-4"),
                html.P("Comprehensive vulnerability analysis and insights", className="text-muted")
            ])
        ]),
        
        # Load button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Load CVE Data",
                    id="load-cves-btn",
                    color="primary",
                    className="mb-3"
                )
            ])
        ]),
        
        # Loading spinner
        dcc.Loading(
            id="loading-cves",
            type="default",
            children=[
                # Statistics cards
                html.Div(id="cve-stats-cards"),
                
                # Visualization charts
                html.Div(id="cve-charts", className="mt-4"),
                
                # CVE data table
                html.Div(id="cve-table-container", className="mt-4")
            ]
        )
    ], fluid=True)


def create_stats_cards(df):
    """
    Create statistics cards for CVE overview
    
    Args:
        df: CVE DataFrame
        
    Returns:
        Dash HTML component with statistics cards
    """
    if df.empty:
        return html.Div()
    
    total_cves = len(df)
    severity_dist = DataProcessor.get_severity_distribution(df)
    critical_count = severity_dist.get('CRITICAL', 0)
    high_count = severity_dist.get('HIGH', 0)
    avg_risk_score = df['Risk Score'].mean() if 'Risk Score' in df.columns else 0
    
    cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(total_cves, className="card-title"),
                    html.P("Total CVEs", className="card-text text-muted")
                ])
            ], color="primary", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(critical_count, className="card-title text-danger"),
                    html.P("Critical CVEs", className="card-text text-muted")
                ])
            ], color="danger", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(high_count, className="card-title text-warning"),
                    html.P("High Severity CVEs", className="card-text text-muted")
                ])
            ], color="warning", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_risk_score:.2f}", className="card-title"),
                    html.P("Average Risk Score", className="card-text text-muted")
                ])
            ], color="info", outline=True)
        ], md=3)
    ], className="mb-4")
    
    return cards


def create_cve_charts(df):
    """
    Create interactive visualization charts for CVE data
    
    Args:
        df: CVE DataFrame
        
    Returns:
        Dash HTML component with charts
    """
    if df.empty:
        return html.Div()
    
    severity_dist = DataProcessor.get_severity_distribution(df)
    
    # 1. Severity Distribution Pie Chart
    severity_fig = go.Figure(data=[go.Pie(
        labels=list(severity_dist.keys()),
        values=list(severity_dist.values()),
        hole=0.4,
        marker=dict(colors=[
            DataProcessor.get_severity_color(s) for s in severity_dist.keys()
        ]),
        textinfo='label+value+percent',
        textposition='auto'
    )])
    severity_fig.update_layout(
        title="CVE Severity Distribution",
        height=400,
        showlegend=True
    )
    
    # 2. Risk Score Distribution Histogram
    risk_fig = go.Figure(data=[go.Histogram(
        x=df['Risk Score'],
        nbinsx=20,
        marker=dict(color='#007bff', opacity=0.7),
        name='Risk Score'
    )])
    risk_fig.update_layout(
        title="Risk Score Distribution",
        xaxis_title="Risk Score",
        yaxis_title="Number of CVEs",
        height=400,
        xaxis=dict(range=[0, 10])
    )
    
    # 3. Top 10 Highest Risk CVEs
    top_cves = df.nlargest(10, 'Risk Score')[['CVE ID', 'Risk Score', 'Severity']]
    top_fig = go.Figure(data=[go.Bar(
        x=top_cves['Risk Score'],
        y=top_cves['CVE ID'],
        orientation='h',
        marker=dict(
            color=[DataProcessor.get_severity_color(s) for s in top_cves['Severity']],
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=top_cves['Risk Score'],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Risk Score: %{x}<br>Severity: %{customdata}<extra></extra>',
        customdata=top_cves['Severity']
    )])
    top_fig.update_layout(
        title="Top 10 Highest Risk CVEs",
        xaxis_title="Risk Score",
        yaxis_title="CVE ID",
        height=500,
        yaxis=dict(autorange='reversed')
    )
    
    # 4. Priority Distribution (if available)
    priority_dist = DataProcessor.get_priority_distribution(df)
    priority_chart = html.Div()
    
    if priority_dist:
        priority_fig = go.Figure(data=[go.Bar(
            x=list(priority_dist.keys()),
            y=list(priority_dist.values()),
            marker=dict(color='#28a745'),
            text=list(priority_dist.values()),
            textposition='auto'
        )])
        priority_fig.update_layout(
            title="Priority Distribution",
            xaxis_title="Priority",
            yaxis_title="Number of CVEs",
            height=400
        )
        priority_chart = dbc.Col([
            dcc.Graph(figure=priority_fig)
        ], md=6)
    
    charts = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=severity_fig)
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=risk_fig)
        ], md=6)
    ]) 
    
    charts_row2 = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=top_fig)
        ], md=6 if priority_dist else 12),
        priority_chart
    ], className="mt-3")
    
    return html.Div([charts, charts_row2])


def create_cve_table(df):
    """
    Create interactive data table for CVE details
    
    Args:
        df: CVE DataFrame
        
    Returns:
        Dash HTML component with data table
    """
    if df.empty:
        return dbc.Alert("No CVE data available", color="info")
    
    # Apply severity-based styling
    style_data_conditional = []
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        color = DataProcessor.get_severity_color(severity)
        bg_color = color if severity == 'CRITICAL' else f"{color}33"  # Add transparency
        text_color = 'white' if severity == 'CRITICAL' else 'black'
        
        style_data_conditional.append({
            'if': {
                'filter_query': f'{{Severity}} = "{severity}"',
                'column_id': 'Severity'
            },
            'backgroundColor': bg_color,
            'color': text_color,
            'fontWeight': 'bold'
        })
    
    table = dash_table.DataTable(
        id='cve-table',
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
        dbc.CardHeader(html.H4("CVE Details")),
        dbc.CardBody([table])
    ])


def register_callbacks(app, api_client):
    """
    Register callbacks for CVE tab
    
    Args:
        app: Dash application instance
        api_client: ConcertAPIClient instance
    """
    
    @app.callback(
        [Output('cve-stats-cards', 'children'),
         Output('cve-charts', 'children'),
         Output('cve-table-container', 'children')],
        [Input('load-cves-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_cves(n_clicks):
        """Load and display CVE data"""
        try:
            logger.info("Loading CVE data...")
            
            # Fetch CVEs from API
            cves = api_client.get_cves()
            
            if not cves:
                return (
                    dbc.Alert("No CVEs found", color="warning"),
                    html.Div(),
                    html.Div()
                )
            
            # Process data
            df = DataProcessor.process_cves(cves)
            
            # Create visualizations
            stats = create_stats_cards(df)
            charts = create_cve_charts(df)
            table = create_cve_table(df)
            
            logger.info(f"Successfully loaded {len(df)} CVEs")
            return stats, charts, table
            
        except Exception as e:
            logger.error(f"Error loading CVEs: {str(e)}")
            error_alert = dbc.Alert(
                f"Error loading CVE data: {str(e)}",
                color="danger"
            )
            return error_alert, html.Div(), html.Div()

# Made with Bob
