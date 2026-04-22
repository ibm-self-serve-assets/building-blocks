"""
Applications Insights Tab
Displays application analytics with multi-level drill-down:
- Application overview with analytics
- Application-specific CVE details
- Build artifact tracking
- Artifact-specific CVE analysis
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
    Create the Applications insights tab layout
    
    Returns:
        Dash HTML component
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Applications Insights Dashboard", className="mb-4"),
                html.P("Comprehensive application portfolio analysis with vulnerability tracking", className="text-muted")
            ])
        ]),
        
        # Load button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Load Applications",
                    id="load-apps-btn",
                    color="primary",
                    className="mb-3"
                )
            ])
        ]),
        
        # Loading spinner
        dcc.Loading(
            id="loading-apps",
            type="default",
            children=[
                # Overview section with analytics
                html.Div(id="app-overview-section"),
                
                # Applications table
                html.Div(id="app-table-container", className="mt-4"),
                
                # Hidden div to store selected app name
                html.Div(id="selected-app-name", style={'display': 'none'}),
                
                # Application details section
                html.Div(id="app-details-section", className="mt-4"),
                
                # Artifact CVE section
                html.Div(id="artifact-cve-section", className="mt-4")
            ]
        )
    ], fluid=True)


def create_overview_charts(df):
    """
    Create overview analytics charts for all applications
    
    Args:
        df: Applications DataFrame
        
    Returns:
        Dash HTML component with overview analytics
    """
    if df.empty:
        return html.Div()
    
    # Calculate statistics
    total_apps = len(df)
    total_vulns = df['Vulnerabilities'].sum()
    apps_with_artifacts = len(df[df['Has Artifacts'] == 'Yes'])
    avg_vulns = df['Vulnerabilities'].mean()
    
    # Statistics cards
    stats_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(total_apps, className="card-title"),
                    html.P("Total Applications", className="card-text text-muted")
                ])
            ], color="primary", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(total_vulns, className="card-title text-danger"),
                    html.P("Total Vulnerabilities", className="card-text text-muted")
                ])
            ], color="danger", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(apps_with_artifacts, className="card-title text-info"),
                    html.P("Apps with Artifacts", className="card-text text-muted")
                ])
            ], color="info", outline=True)
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{avg_vulns:.1f}", className="card-title text-warning"),
                    html.P("Avg Vulnerabilities", className="card-text text-muted")
                ])
            ], color="warning", outline=True)
        ], md=3)
    ], className="mb-4")
    
    # 1. Application Status Distribution (Pie Chart)
    status_counts = df['Status'].value_counts()
    status_fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=0.4,
        textinfo='label+value+percent',
        textposition='auto'
    )])
    status_fig.update_layout(
        title="Application Status Distribution",
        height=400
    )
    
    # 2. Vulnerability Distribution Across Applications (Bar Chart)
    vuln_ranges = ['0', '1-5', '6-10', '11-20', '20+']
    vuln_counts = [
        len(df[df['Vulnerabilities'] == 0]),
        len(df[(df['Vulnerabilities'] >= 1) & (df['Vulnerabilities'] <= 5)]),
        len(df[(df['Vulnerabilities'] >= 6) & (df['Vulnerabilities'] <= 10)]),
        len(df[(df['Vulnerabilities'] >= 11) & (df['Vulnerabilities'] <= 20)]),
        len(df[df['Vulnerabilities'] > 20])
    ]
    
    vuln_dist_fig = go.Figure(data=[go.Bar(
        x=vuln_ranges,
        y=vuln_counts,
        marker=dict(color='#007bff'),
        text=vuln_counts,
        textposition='auto'
    )])
    vuln_dist_fig.update_layout(
        title="Vulnerability Distribution Across Applications",
        xaxis_title="Vulnerability Count Range",
        yaxis_title="Number of Applications",
        height=400
    )
    
    # 3. Applications with/without Build Artifacts (Grouped Bar Chart)
    artifact_stats = df.groupby('Has Artifacts').agg({
        'Name': 'count',
        'Vulnerabilities': 'mean'
    }).reset_index()
    
    artifact_fig = go.Figure(data=[
        go.Bar(
            name='App Count',
            x=artifact_stats['Has Artifacts'],
            y=artifact_stats['Name'],
            marker=dict(color='#17a2b8'),
            text=artifact_stats['Name'],
            textposition='auto'
        ),
        go.Bar(
            name='Avg Vulnerabilities',
            x=artifact_stats['Has Artifacts'],
            y=artifact_stats['Vulnerabilities'],
            marker=dict(color='#ffc107'),
            text=[f"{v:.1f}" for v in artifact_stats['Vulnerabilities']],
            textposition='auto'
        )
    ])
    artifact_fig.update_layout(
        title="Applications with/without Build Artifacts",
        xaxis_title="Has Build Artifacts",
        yaxis_title="Count / Average",
        height=400,
        barmode='group'
    )
    
    # 4. Top 10 Applications by Vulnerability Count (Horizontal Bar Chart)
    top_apps = df.nlargest(10, 'Vulnerabilities')[['Name', 'Vulnerabilities']]
    
    # Color gradient based on vulnerability count
    max_vuln = top_apps['Vulnerabilities'].max()
    # Handle case when max_vuln is 0 or NaN to avoid division by zero
    if max_vuln > 0:
        colors = [f'rgba(220, 53, 69, {0.3 + 0.7 * (v / max_vuln)})' for v in top_apps['Vulnerabilities']]
    else:
        colors = ['rgba(220, 53, 69, 0.5)'] * len(top_apps)
    
    top_apps_fig = go.Figure(data=[go.Bar(
        x=top_apps['Vulnerabilities'],
        y=top_apps['Name'],
        orientation='h',
        marker=dict(color=colors),
        text=top_apps['Vulnerabilities'],
        textposition='auto'
    )])
    top_apps_fig.update_layout(
        title="Top 10 Applications by Vulnerability Count",
        xaxis_title="Vulnerability Count",
        yaxis_title="Application Name",
        height=500,
        yaxis=dict(autorange='reversed')
    )
    
    # Layout charts in responsive grid
    charts = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=status_fig)
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=vuln_dist_fig)
        ], md=6)
    ])
    
    charts_row2 = dbc.Row([
        dbc.Col([
            dcc.Graph(figure=artifact_fig)
        ], md=6),
        dbc.Col([
            dcc.Graph(figure=top_apps_fig)
        ], md=6)
    ], className="mt-3")
    
    return html.Div([
        html.H3("Application Portfolio Overview", className="mb-3"),
        stats_cards,
        charts,
        charts_row2
    ])


def create_app_table(df):
    """
    Create interactive data table for applications
    
    Args:
        df: Applications DataFrame
        
    Returns:
        Dash HTML component with data table
    """
    if df.empty:
        return dbc.Alert("No application data available", color="info")
    
    table = dash_table.DataTable(
        id='app-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=20,
        page_action='native',
        sort_action='native',
        sort_mode='multi',
        filter_action='native',
        row_selectable='single',
        selected_rows=[],
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
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            },
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'rgba(0, 123, 255, 0.2)',
                'border': '1px solid rgb(0, 123, 255)'
            }
        ]
    )
    
    return dbc.Card([
        dbc.CardHeader(html.H4("Applications List")),
        dbc.CardBody([
            html.P("Click on any application row to view detailed vulnerability analysis", className="text-muted mb-3"),
            table
        ])
    ])


def create_cve_charts(df_cves, app_name):
    """
    Create CVE analytics charts for application or artifact
    
    Args:
        df_cves: CVE DataFrame
        app_name: Application or artifact name for title
        
    Returns:
        Dash HTML component with CVE charts
    """
    if df_cves.empty:
        return html.Div()
    
    severity_dist = DataProcessor.get_severity_distribution(df_cves)
    
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
        title=f"CVE Severity Distribution - {app_name}",
        height=400
    )
    
    # 2. Risk Score Distribution Histogram
    risk_fig = go.Figure(data=[go.Histogram(
        x=df_cves['Risk Score'],
        nbinsx=20,
        marker=dict(color='#007bff', opacity=0.7)
    )])
    risk_fig.update_layout(
        title="Risk Score Distribution",
        xaxis_title="Risk Score",
        yaxis_title="Number of CVEs",
        height=400,
        xaxis=dict(range=[0, 10])
    )
    
    # 3. Top 10 Highest Risk CVEs
    top_cves = df_cves.nlargest(10, 'Risk Score')[['CVE ID', 'Risk Score', 'Severity']]
    top_fig = go.Figure(data=[go.Bar(
        x=top_cves['Risk Score'],
        y=top_cves['CVE ID'],
        orientation='h',
        marker=dict(
            color=[DataProcessor.get_severity_color(s) for s in top_cves['Severity']]
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
    priority_dist = DataProcessor.get_priority_distribution(df_cves)
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


def create_cve_table(df_cves):
    """
    Create CVE details table with severity-based styling
    
    Args:
        df_cves: CVE DataFrame
        
    Returns:
        Dash HTML component with CVE table
    """
    if df_cves.empty:
        return dbc.Alert("No CVE data available for this application", color="info")
    
    # Apply severity-based styling
    style_data_conditional = []
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        color = DataProcessor.get_severity_color(severity)
        bg_color = color if severity == 'CRITICAL' else f"{color}33"
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
        id='app-cve-table',
        columns=[{"name": col, "id": col} for col in df_cves.columns],
        data=df_cves.to_dict('records'),
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
        style_data_conditional=style_data_conditional
    )
    
    return table


def create_artifact_table(df_artifacts):
    """
    Create build artifacts table with row selection
    
    Args:
        df_artifacts: Build artifacts DataFrame
        
    Returns:
        Dash HTML component with artifacts table
    """
    if df_artifacts.empty:
        return dbc.Alert("No build artifacts found for this application", color="info")
    
    table = dash_table.DataTable(
        id='artifact-table',
        columns=[{"name": col, "id": col} for col in df_artifacts.columns],
        data=df_artifacts.to_dict('records'),
        page_size=10,
        page_action='native',
        sort_action='native',
        row_selectable='single',
        selected_rows=[],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'minWidth': '100px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        style_header={
            'backgroundColor': '#28a745',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'state': 'selected'},
                'backgroundColor': 'rgba(40, 167, 69, 0.2)',
                'border': '1px solid rgb(40, 167, 69)'
            }
        ]
    )
    
    return html.Div([
        html.P("Click on any artifact to view its CVE details", className="text-muted mb-3"),
        table
    ])


def register_callbacks(app, api_client):
    """
    Register callbacks for Applications tab
    
    Args:
        app: Dash application instance
        api_client: ConcertAPIClient instance
    """
    
    @app.callback(
        [Output('app-overview-section', 'children'),
         Output('app-table-container', 'children')],
        [Input('load-apps-btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def load_applications(n_clicks):
        """Load and display applications with overview analytics"""
        try:
            logger.info("Loading applications...")
            
            # Fetch applications from API
            apps = api_client.get_applications()
            
            if not apps:
                return (
                    dbc.Alert("No applications found", color="warning"),
                    html.Div()
                )
            
            # Process data
            df = DataProcessor.process_applications(apps)
            
            # Create overview and table
            overview = create_overview_charts(df)
            table = create_app_table(df)
            
            logger.info(f"Successfully loaded {len(df)} applications")
            return overview, table
            
        except Exception as e:
            logger.error(f"Error loading applications: {str(e)}")
            error_alert = dbc.Alert(
                f"Error loading application data: {str(e)}",
                color="danger"
            )
            return error_alert, html.Div()
    
    @app.callback(
        [Output('app-details-section', 'children'),
         Output('selected-app-name', 'children')],
        [Input('app-table', 'selected_rows')],
        [State('app-table', 'data')],
        prevent_initial_call=True
    )
    def display_app_details(selected_rows, table_data):
        """Display application CVE details and build artifacts"""
        if not selected_rows or not table_data:
            return html.Div(), ""
        
        try:
            # Get selected application
            app_data = table_data[selected_rows[0]]
            app_name = app_data['Name']
            
            logger.info(f"Loading details for application: {app_name}")
            
            # Fetch application vulnerabilities
            vulns = api_client.get_application_vulnerabilities(app_name)
            df_cves = DataProcessor.process_cves(vulns)
            
            # Calculate statistics
            total_cves = len(df_cves)
            severity_dist = DataProcessor.get_severity_distribution(df_cves)
            critical_count = severity_dist.get('CRITICAL', 0)
            high_count = severity_dist.get('HIGH', 0)
            avg_risk = df_cves['Risk Score'].mean() if not df_cves.empty else 0
            
            # Statistics cards
            stats_cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(total_cves, className="card-title"),
                            html.P("Total CVEs", className="card-text text-muted")
                        ])
                    ], color="primary", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(critical_count, className="card-title text-danger"),
                            html.P("Critical", className="card-text text-muted")
                        ])
                    ], color="danger", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(high_count, className="card-title text-warning"),
                            html.P("High", className="card-text text-muted")
                        ])
                    ], color="warning", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(f"{avg_risk:.2f}", className="card-title"),
                            html.P("Avg Risk Score", className="card-text text-muted")
                        ])
                    ], color="info", outline=True)
                ], md=3)
            ], className="mb-3")
            
            # Create CVE visualizations
            cve_charts = create_cve_charts(df_cves, app_name)
            cve_table = create_cve_table(df_cves)
            
            # Fetch build artifacts
            artifacts = api_client.get_build_artifacts(app_name)
            df_artifacts = DataProcessor.process_build_artifacts(artifacts)
            artifact_table = create_artifact_table(df_artifacts)
            
            details = dbc.Card([
                dbc.CardHeader(html.H3(f"Application Details: {app_name}")),
                dbc.CardBody([
                    html.H4("Vulnerability Overview", className="mb-3"),
                    stats_cards,
                    cve_charts,
                    html.Hr(),
                    html.H4("CVE Details", className="mb-3"),
                    cve_table,
                    html.Hr(),
                    html.H4("Build Artifacts", className="mb-3 mt-4"),
                    artifact_table
                ])
            ])
            
            return details, app_name
            
        except Exception as e:
            logger.error(f"Error loading application details: {str(e)}")
            error_alert = dbc.Alert(
                f"Error loading application details: {str(e)}",
                color="danger"
            )
            return error_alert, ""
    
    @app.callback(
        Output('artifact-cve-section', 'children'),
        [Input('artifact-table', 'selected_rows')],
        [State('artifact-table', 'data'),
         State('selected-app-name', 'children')],
        prevent_initial_call=True
    )
    def display_artifact_cves(selected_rows, artifact_data, app_name):
        """Display CVE details for selected build artifact"""
        if not selected_rows or not artifact_data or not app_name:
            return html.Div()
        
        try:
            # Get selected artifact
            artifact = artifact_data[selected_rows[0]]
            artifact_id = artifact['ID']
            artifact_name = artifact['Name']
            
            logger.info(f"Loading CVEs for artifact: {artifact_name} (ID: {artifact_id})")
            
            # Fetch artifact CVEs
            cves = api_client.get_build_artifact_cves(app_name, artifact_id)
            
            if not cves:
                return dbc.Alert(
                    f"No CVEs found for artifact: {artifact_name}",
                    color="info"
                )
            
            df_cves = DataProcessor.process_cves(cves)
            
            # Calculate statistics
            total_cves = len(df_cves)
            severity_dist = DataProcessor.get_severity_distribution(df_cves)
            critical_count = severity_dist.get('CRITICAL', 0)
            high_count = severity_dist.get('HIGH', 0)
            avg_risk = df_cves['Risk Score'].mean()
            
            # Statistics cards
            stats_cards = dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(total_cves, className="card-title"),
                            html.P("Total CVEs", className="card-text text-muted")
                        ])
                    ], color="primary", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(critical_count, className="card-title text-danger"),
                            html.P("Critical", className="card-text text-muted")
                        ])
                    ], color="danger", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(high_count, className="card-title text-warning"),
                            html.P("High", className="card-text text-muted")
                        ])
                    ], color="warning", outline=True)
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5(f"{avg_risk:.2f}", className="card-title"),
                            html.P("Avg Risk Score", className="card-text text-muted")
                        ])
                    ], color="info", outline=True)
                ], md=3)
            ], className="mb-3")
            
            # Create visualizations
            cve_charts = create_cve_charts(df_cves, artifact_name)
            cve_table = create_cve_table(df_cves)
            
            artifact_details = dbc.Card([
                dbc.CardHeader(html.H4(f"Artifact CVE Details: {artifact_name}")),
                dbc.CardBody([
                    stats_cards,
                    cve_charts,
                    html.Hr(),
                    html.H5("CVE Details", className="mb-3"),
                    cve_table
                ])
            ], className="mt-4")
            
            return artifact_details
            
        except Exception as e:
            logger.error(f"Error loading artifact CVEs: {str(e)}")
            return dbc.Alert(
                f"Error loading artifact CVE data: {str(e)}",
                color="danger"
            )

# Made with Bob
