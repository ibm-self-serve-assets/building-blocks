"""
Dashboard Component Module

Provides the main dashboard layout and visualization functions for Instana observability.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Any

from src.utils.helpers import format_number, get_health_status


def create_dashboard_layout(app_name: str) -> html.Div:
    """
    Create the main dashboard layout.
    
    Args:
        app_name: Application name to display
        
    Returns:
        html.Div: Dashboard layout
    """
    return html.Div([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1(
                    "Application Observability Dashboard",
                    className="text-center mt-4 mb-2"
                ),
                html.H5(
                    f"Monitoring: {app_name}",
                    className="text-center text-muted mb-4"
                )
            ])
        ]),
        
        # Refresh button
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "🔄 Refresh Data",
                    id="refresh-button",
                    color="primary",
                    className="mb-3"
                )
            ], width={"size": 2, "offset": 10})
        ]),
        
        # Loading spinner and content
        dcc.Loading(
            id="loading",
            type="default",
            children=html.Div(id="dashboard-content")
        ),
        
        # Footer
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.P(
                    "Powered by IBM Instana",
                    className="text-center text-muted"
                )
            ])
        ])
    ], className="container-fluid")


def create_summary_cards(metrics: Dict[str, Any]) -> dbc.Row:
    """
    Create summary metric cards.
    
    Args:
        metrics: Aggregated metrics dictionary
        
    Returns:
        dbc.Row: Row of summary cards
    """
    health_score = metrics.get('avg_health_score', 0)
    status_label, status_color = get_health_status(health_score)
    
    cards = [
        {
            "title": "Services",
            "value": str(metrics.get('total_services', 0)),
            "icon": "🔧",
            "color": "primary"
        },
        {
            "title": "Total Calls",
            "value": format_number(metrics.get('total_calls', 0), 0),
            "icon": "📞",
            "color": "info"
        },
        {
            "title": "Avg Error Rate",
            "value": f"{metrics.get('avg_error_rate', 0):.2f}%",
            "icon": "⚠️",
            "color": "warning" if metrics.get('avg_error_rate', 0) > 5 else "success"
        },
        {
            "title": "Avg Latency",
            "value": f"{metrics.get('avg_latency', 0):.0f}ms",
            "icon": "⏱️",
            "color": "warning" if metrics.get('avg_latency', 0) > 500 else "success"
        },
        {
            "title": "Health Score",
            "value": f"{health_score:.0f}/100",
            "icon": "💚" if health_score >= 80 else "💛" if health_score >= 60 else "🧡" if health_score >= 40 else "❤️",
            "color": "success" if health_score >= 80 else "warning" if health_score >= 60 else "danger"
        }
    ]
    
    card_components = []
    for card in cards:
        card_components.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(card["title"], className="card-subtitle mb-2 text-muted"),
                        html.H3([
                            html.Span(card["icon"], className="me-2"),
                            card["value"]
                        ], className="card-title")
                    ])
                ], color=card["color"], outline=True, className="mb-3")
            ], width=12, md=6, lg=2)
        )
    
    return dbc.Row(card_components, className="mb-4")


def create_service_health_chart(df: pd.DataFrame) -> dcc.Graph:
    """
    Create service health bar chart.
    
    Args:
        df: Service health DataFrame
        
    Returns:
        dcc.Graph: Plotly bar chart
    """
    if df.empty:
        return dcc.Graph(
            figure={
                "data": [],
                "layout": {
                    "title": "No service data available",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False}
                }
            }
        )
    
    # Sort by calls and take top 10
    df_top = df.nlargest(10, 'calls')
    
    # Create color scale based on health score
    colors = df_top['health_score'].apply(
        lambda x: '#24a148' if x >= 80 else '#f1c21b' if x >= 60 else '#ff832b' if x >= 40 else '#da1e28'
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_top['service_name'],
            y=df_top['calls'],
            marker_color=colors,
            text=df_top['calls'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         'Calls: %{y}<br>' +
                         'Health Score: %{customdata[0]:.1f}<br>' +
                         'Error Rate: %{customdata[1]:.2f}%<br>' +
                         'Latency: %{customdata[2]:.0f}ms<br>' +
                         '<extra></extra>',
            customdata=df_top[['health_score', 'error_rate', 'latency']].values
        )
    ])
    
    fig.update_layout(
        title="Service Call Volume (Top 10)",
        xaxis_title="Service",
        yaxis_title="Number of Calls",
        hovermode='closest',
        height=400,
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig)


def create_error_rate_chart(df: pd.DataFrame) -> dcc.Graph:
    """
    Create error rate bar chart.
    
    Args:
        df: Service health DataFrame
        
    Returns:
        dcc.Graph: Plotly bar chart
    """
    if df.empty:
        return dcc.Graph(
            figure={
                "data": [],
                "layout": {
                    "title": "No error data available",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False}
                }
            }
        )
    
    # Filter services with errors and sort
    df_errors = df[df['error_rate'] > 0].nlargest(10, 'error_rate')
    
    if df_errors.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No errors detected - All services healthy! 🎉",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="green")
        )
        fig.update_layout(
            title="Error Rates by Service",
            height=400,
            template="plotly_white"
        )
        return dcc.Graph(figure=fig)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_errors['service_name'],
            y=df_errors['error_rate'],
            marker_color='#da1e28',
            text=df_errors['error_rate'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         'Error Rate: %{y:.2f}%<br>' +
                         'Errors: %{customdata[0]}<br>' +
                         'Total Calls: %{customdata[1]}<br>' +
                         '<extra></extra>',
            customdata=df_errors[['errors', 'calls']].values
        )
    ])
    
    fig.update_layout(
        title="Error Rates by Service (Top 10)",
        xaxis_title="Service",
        yaxis_title="Error Rate (%)",
        hovermode='closest',
        height=400,
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig)


def create_latency_chart(df: pd.DataFrame) -> dcc.Graph:
    """
    Create latency bar chart.
    
    Args:
        df: Service health DataFrame
        
    Returns:
        dcc.Graph: Plotly bar chart
    """
    if df.empty:
        return dcc.Graph(
            figure={
                "data": [],
                "layout": {
                    "title": "No latency data available",
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False}
                }
            }
        )
    
    # Sort by latency and take top 10
    df_latency = df.nlargest(10, 'latency')
    
    # Color based on latency thresholds
    colors = df_latency['latency'].apply(
        lambda x: '#24a148' if x < 100 else '#f1c21b' if x < 500 else '#ff832b' if x < 1000 else '#da1e28'
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_latency['service_name'],
            y=df_latency['latency'],
            marker_color=colors,
            text=df_latency['latency'].apply(lambda x: f"{x:.0f}ms"),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>' +
                         'Latency: %{y:.0f}ms<br>' +
                         'Calls: %{customdata[0]}<br>' +
                         '<extra></extra>',
            customdata=df_latency[['calls']].values
        )
    ])
    
    fig.update_layout(
        title="Average Latency by Service (Top 10)",
        xaxis_title="Service",
        yaxis_title="Latency (ms)",
        hovermode='closest',
        height=400,
        template="plotly_white"
    )
    
    return dcc.Graph(figure=fig)


def create_service_table(df: pd.DataFrame) -> dbc.Table:
    """
    Create service details table.
    
    Args:
        df: Service health DataFrame
        
    Returns:
        dbc.Table: Bootstrap table component
    """
    if df.empty:
        return html.Div("No service data available", className="text-muted text-center p-4")
    
    # Sort by health score (lowest first to highlight issues)
    df_sorted = df.sort_values('health_score', ascending=True)
    
    # Create table rows
    rows = []
    for _, row in df_sorted.iterrows():
        status_label, status_color = get_health_status(row['health_score'])
        
        rows.append(
            html.Tr([
                html.Td(row['service_name']),
                html.Td(format_number(row['calls'], 0)),
                html.Td(f"{row['error_rate']:.2f}%", 
                       style={"color": "#da1e28" if row['error_rate'] > 5 else "#24a148"}),
                html.Td(f"{row['latency']:.0f}ms",
                       style={"color": "#da1e28" if row['latency'] > 1000 else "#f1c21b" if row['latency'] > 500 else "#24a148"}),
                html.Td([
                    dbc.Badge(
                        f"{row['health_score']:.0f} - {status_label}",
                        color="success" if row['health_score'] >= 80 else "warning" if row['health_score'] >= 60 else "danger",
                        className="me-1"
                    )
                ])
            ])
        )
    
    table = dbc.Table([
        html.Thead(
            html.Tr([
                html.Th("Service Name"),
                html.Th("Calls"),
                html.Th("Error Rate"),
                html.Th("Avg Latency"),
                html.Th("Health Score")
            ])
        ),
        html.Tbody(rows)
    ], bordered=True, hover=True, responsive=True, striped=True)
    
    return table


def create_dashboard_content(data: Dict, metrics: Dict) -> html.Div:
    """
    Create complete dashboard content.
    
    Args:
        data: Raw data from Instana
        metrics: Aggregated metrics
        
    Returns:
        html.Div: Complete dashboard content
    """
    from src.integrations.instana_integration import process_service_health
    
    # Process service health data
    df = process_service_health(data.get('services', []), data.get('trace_data', {}))
    
    return html.Div([
        # Summary cards
        create_summary_cards(metrics),
        
        # Service health chart
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        create_service_health_chart(df)
                    ])
                ], className="mb-4")
            ], width=12)
        ]),
        
        # Error rate and latency charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        create_error_rate_chart(df)
                    ])
                ], className="mb-4")
            ], width=12, lg=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        create_latency_chart(df)
                    ])
                ], className="mb-4")
            ], width=12, lg=6)
        ]),
        
        # Service details table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Service Details")),
                    dbc.CardBody([
                        create_service_table(df)
                    ])
                ], className="mb-4")
            ], width=12)
        ])
    ])

# Made with Bob
