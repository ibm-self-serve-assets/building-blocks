"""
Automated Hardcoded Secret Detection and Vault Migration
A Python Dash application with IBM Carbon Design System
"""

import os
import re
import json
from typing import Dict, List, Tuple
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from vault_client import VaultClient
from secret_patterns import SECRET_PATTERNS, get_severity

# Load environment variables
load_dotenv()

# Initialize Dash app with IBM Carbon Design System styling
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap",
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ],
    suppress_callback_exceptions=True
)

# Custom CSS for enhanced Carbon styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            .carbon-header {
                background: linear-gradient(135deg, #0f62fe 0%, #0043ce 100%);
                padding: 2rem 0;
                margin-bottom: 2rem;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            .carbon-card {
                border: none;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                border-radius: 0;
                transition: box-shadow 0.2s ease;
            }
            .carbon-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .carbon-button {
                border-radius: 0;
                font-weight: 500;
                letter-spacing: 0.16px;
                transition: all 0.2s ease;
            }
            .carbon-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .carbon-table {
                border-collapse: separate;
                border-spacing: 0;
            }
            .carbon-table thead th {
                position: sticky;
                top: 0;
                z-index: 10;
            }
            .carbon-badge {
                display: inline-flex;
                align-items: center;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.32px;
            }
            .loading-spinner {
                border: 3px solid #f4f4f4;
                border-top: 3px solid #0f62fe;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            @keyframes pulse {
                0%, 100% {
                    transform: scale(1);
                    opacity: 1;
                }
                50% {
                    transform: scale(1.05);
                    opacity: 0.9;
                }
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .carbon-header {
                animation: fadeIn 0.6s ease-out;
            }
            .stat-card {
                background: white;
                padding: 1.5rem;
                border-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .code-editor {
                font-family: 'IBM Plex Mono', monospace;
                background-color: #262626;
                color: #f4f4f4;
                border: 1px solid #393939;
                border-radius: 4px;
                padding: 16px;
            }
            .code-editor::placeholder {
                color: #8d8d8d;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# IBM Carbon Design System color palette
CARBON_COLORS = {
    'ui_01': '#ffffff',
    'ui_02': '#f4f4f4',
    'ui_03': '#e0e0e0',
    'ui_04': '#8d8d8d',
    'ui_05': '#161616',
    'text_01': '#161616',
    'text_02': '#525252',
    'text_03': '#a8a8a8',
    'text_04': '#ffffff',
    'interactive_01': '#0f62fe',
    'interactive_02': '#393939',
    'interactive_03': '#0f62fe',
    'interactive_04': '#0f62fe',
    'danger': '#da1e28',
    'success': '#24a148',
    'warning': '#f1c21b',
    'info': '#0043ce',
}

# Initialize Vault client
vault_client = VaultClient(
    vault_addr=os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
    vault_token=os.getenv('VAULT_TOKEN', '')
)

# App layout
app.layout = html.Div([
    # Enhanced Premium Carbon Header with IBM Design
    html.Div([
        dbc.Container([
            # Top badge
            html.Div([
                html.Span("🛡️ ENTERPRISE SECURITY", style={
                    'backgroundColor': 'rgba(255,255,255,0.2)',
                    'color': 'white',
                    'padding': '6px 16px',
                    'borderRadius': '20px',
                    'fontSize': '0.75rem',
                    'fontWeight': '600',
                    'letterSpacing': '1px',
                    'display': 'inline-block',
                    'marginBottom': '1.5rem',
                    'border': '1px solid rgba(255,255,255,0.3)'
                })
            ], className="text-center"),
            
            # Main title with icon
            html.Div([
                html.Div([
                    html.Span("🔐", style={
                        'fontSize': '3.5rem',
                        'marginRight': '1rem',
                        'display': 'inline-block',
                        'animation': 'pulse 2s ease-in-out infinite'
                    }),
                    html.Span("Automated Secret Detection", style={
                        'display': 'block',
                        'fontFamily': 'IBM Plex Sans, sans-serif',
                        'fontWeight': '700',
                        'color': 'white',
                        'fontSize': '2.75rem',
                        'lineHeight': '1.2',
                        'textShadow': '0 2px 4px rgba(0,0,0,0.2)'
                    })
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '0.5rem'}),
                html.H2(
                    "& Vault Migration Platform",
                    className="text-center",
                    style={
                        'fontFamily': 'IBM Plex Sans, sans-serif',
                        'fontWeight': '300',
                        'color': 'rgba(255,255,255,0.95)',
                        'fontSize': '1.75rem',
                        'marginBottom': '1.5rem',
                        'letterSpacing': '0.5px'
                    }
                )
            ]),
            
            # Description with features
            html.Div([
                html.P(
                    "Scan source code for hardcoded secrets, encrypt with Vault Transit (AES256-GCM96), and migrate to secure storage",
                    className="text-center",
                    style={
                        'fontFamily': 'IBM Plex Sans, sans-serif',
                        'color': 'rgba(255,255,255,0.9)',
                        'fontSize': '1.15rem',
                        'marginBottom': '1.5rem',
                        'maxWidth': '800px',
                        'margin': '0 auto 1.5rem auto',
                        'lineHeight': '1.6'
                    }
                ),
                # Feature badges
                html.Div([
                    html.Span("✓ 40+ Secret Types", style={
                        'backgroundColor': 'rgba(255,255,255,0.15)',
                        'color': 'white',
                        'padding': '8px 16px',
                        'borderRadius': '20px',
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'margin': '0 8px 8px 0',
                        'display': 'inline-block',
                        'border': '1px solid rgba(255,255,255,0.25)'
                    }),
                    html.Span("✓ Transit Encryption", style={
                        'backgroundColor': 'rgba(255,255,255,0.15)',
                        'color': 'white',
                        'padding': '8px 16px',
                        'borderRadius': '20px',
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'margin': '0 8px 8px 0',
                        'display': 'inline-block',
                        'border': '1px solid rgba(255,255,255,0.25)'
                    })
                ], className="text-center", style={'marginBottom': '0'})
            ])
        ], style={'padding': '3rem 1rem'})
    ], className='carbon-header', style={
        'background': 'linear-gradient(135deg, #0f62fe 0%, #0043ce 50%, #002d9c 100%)',
        'position': 'relative',
        'overflow': 'hidden'
    }),
    
    # Main Container
    dbc.Container([
        # Connection status
        dbc.Row([
            dbc.Col([
                html.Div(id='connection-status', className='mb-4')
            ])
        ]),

        # Main content
        dbc.Row([
            dbc.Col([
                # Code input section
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H5("📝 Source Code Input",
                                style={
                                    'fontFamily': 'IBM Plex Sans, sans-serif',
                                    'marginBottom': '0',
                                    'fontWeight': '600'
                                }
                            ),
                            html.P("Paste your code below to scan for hardcoded secrets",
                                style={
                                    'fontFamily': 'IBM Plex Sans, sans-serif',
                                    'fontSize': '0.875rem',
                                    'color': CARBON_COLORS['text_02'],
                                    'marginBottom': '0',
                                    'marginTop': '0.25rem'
                                }
                            )
                        ])
                    ], style={'backgroundColor': CARBON_COLORS['ui_01'], 'borderBottom': f'1px solid {CARBON_COLORS["ui_03"]}'}),
                    dbc.CardBody([
                        dcc.Textarea(
                            id='code-input',
                            placeholder='# Paste your source code here...\n\n# Example:\nAWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"\nAWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\ndb_password = "MySecretPassword123!"\n\n# The scanner will detect 40+ types of secrets',
                            className='code-editor',
                            style={
                                'width': '100%',
                                'height': '320px',
                                'fontFamily': 'IBM Plex Mono, monospace',
                                'fontSize': '14px',
                                'lineHeight': '1.6',
                                'backgroundColor': '#262626',
                                'color': '#f4f4f4',
                                'border': f'1px solid {CARBON_COLORS["ui_03"]}',
                                'borderRadius': '4px',
                                'padding': '16px',
                                'resize': 'vertical'
                            }
                        ),
                        html.Div([
                            dbc.Button([
                                html.Span("🔍 ", style={'marginRight': '8px'}),
                                "Scan for Secrets"
                            ],
                                id='scan-button',
                                color="primary",
                                size="lg",
                                className="carbon-button",
                                style={
                                    'fontFamily': 'IBM Plex Sans, sans-serif',
                                    'backgroundColor': CARBON_COLORS['interactive_01'],
                                    'border': 'none',
                                    'fontWeight': '500',
                                    'padding': '12px 32px',
                                    'fontSize': '1rem'
                                }
                            ),
                            html.Span(
                                "Detects 40+ secret types including AWS, GCP, Azure, GitHub, and more",
                                style={
                                    'fontFamily': 'IBM Plex Sans, sans-serif',
                                    'fontSize': '0.875rem',
                                    'color': CARBON_COLORS['text_02'],
                                    'marginLeft': '1rem',
                                    'display': 'inline-block',
                                    'verticalAlign': 'middle'
                                }
                            )
                        ], className='mt-3')
                    ])
                ], className='mb-4 carbon-card'),

                # Loading indicator
                html.Div(id='loading-indicator', style={'display': 'none'}),

                # Results section
                html.Div(id='scan-results'),

                # Migrated code section
                html.Div(id='migrated-code-section')
            ])
        ])
    ], fluid=True, style={'fontFamily': 'IBM Plex Sans, sans-serif', 'paddingBottom': '3rem'})
])


@app.callback(
    Output('connection-status', 'children'),
    Input('scan-button', 'n_clicks'),
    prevent_initial_call=False
)
def check_vault_connection(n_clicks):
    """Check Vault connection status with enhanced Carbon styling and masked address"""
    def mask_vault_addr(addr):
        """Mask the Vault address for security"""
        if not addr:
            return "***"
        # Extract protocol and host
        if '://' in addr:
            protocol, rest = addr.split('://', 1)
            if ':' in rest:
                host, port = rest.rsplit(':', 1)
                # Mask the host but show protocol and port
                return f"{protocol}://***:{port}"
            else:
                return f"{protocol}://***"
        return "***"
    
    masked_addr = mask_vault_addr(vault_client.vault_addr)
    
    if vault_client.is_connected():
        return html.Div([
            dbc.Alert([
                html.Div([
                    html.Span("✓", style={
                        'fontSize': '1.5rem',
                        'marginRight': '12px',
                        'fontWeight': 'bold',
                        'color': CARBON_COLORS['success']
                    }),
                    html.Div([
                        html.Strong("Connected to Vault", style={'display': 'block', 'marginBottom': '4px'}),
                        html.Span(f"Successfully connected to {masked_addr}",
                            style={'fontSize': '0.875rem', 'opacity': '0.9'})
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ],
                color="success",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'border': 'none',
                    'borderLeft': f'4px solid {CARBON_COLORS["success"]}',
                    'borderRadius': '4px',
                    'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
                }
            )
        ])
    else:
        return html.Div([
            dbc.Alert([
                html.Div([
                    html.Span("⚠", style={
                        'fontSize': '1.5rem',
                        'marginRight': '12px',
                        'fontWeight': 'bold',
                        'color': CARBON_COLORS['danger']
                    }),
                    html.Div([
                        html.Strong("Cannot Connect to Vault", style={'display': 'block', 'marginBottom': '4px'}),
                        html.Span(f"Failed to connect to {masked_addr}. Please verify VAULT_ADDR and VAULT_TOKEN.",
                            style={'fontSize': '0.875rem', 'opacity': '0.9'})
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ],
                color="danger",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'border': 'none',
                    'borderLeft': f'4px solid {CARBON_COLORS["danger"]}',
                    'borderRadius': '4px',
                    'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
                }
            )
        ])


@app.callback(
    [
        Output('scan-results', 'children'),
        Output('migrated-code-section', 'children'),
        Output('loading-indicator', 'style')
    ],
    Input('scan-button', 'n_clicks'),
    State('code-input', 'value'),
    prevent_initial_call=True
)
def scan_and_migrate(n_clicks, code_input):
    """Scan code for secrets and migrate to Vault with enhanced UI feedback"""
    if not code_input:
        return (
            dbc.Alert([
                html.Div([
                    html.Span("ℹ️", style={'fontSize': '1.5rem', 'marginRight': '12px'}),
                    html.Span("Please enter some code to scan.", style={'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ],
                color="warning",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'borderLeft': f'4px solid {CARBON_COLORS["warning"]}',
                    'borderRadius': '4px'
                }
            ),
            None,
            {'display': 'none'}
        )

    if not vault_client.is_connected():
        return (
            dbc.Alert([
                html.Div([
                    html.Span("❌", style={'fontSize': '1.5rem', 'marginRight': '12px'}),
                    html.Span("Cannot connect to Vault. Please check your configuration.", style={'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ],
                color="danger",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'borderLeft': f'4px solid {CARBON_COLORS["danger"]}',
                    'borderRadius': '4px'
                }
            ),
            None,
            {'display': 'none'}
        )

    # Scan for secrets
    findings = scan_code_for_secrets(code_input)

    if not findings:
        return (
            dbc.Alert([
                html.Div([
                    html.Span("✓", style={'fontSize': '1.5rem', 'marginRight': '12px', 'color': CARBON_COLORS['success']}),
                    html.Div([
                        html.Strong("No Secrets Detected", style={'display': 'block', 'marginBottom': '4px'}),
                        html.Span("Your code appears to be clean! No hardcoded secrets were found.",
                            style={'fontSize': '0.875rem', 'opacity': '0.9'})
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ],
                color="info",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'borderLeft': f'4px solid {CARBON_COLORS["info"]}',
                    'borderRadius': '4px',
                    'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
                }
            ),
            None,
            {'display': 'none'}
        )

    # Migrate secrets to Vault
    migration_results = migrate_secrets_to_vault(findings)

    # Generate updated code
    updated_code = generate_updated_code(code_input, findings)

    # Create results display
    results_card = create_results_card(findings, migration_results)
    migrated_code_card = create_migrated_code_card(updated_code)

    return results_card, migrated_code_card, {'display': 'none'}


def scan_code_for_secrets(code: str) -> List[Dict]:
    """Scan code for hardcoded secrets using pattern matching"""
    findings = []
    lines = code.split('\n')

    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern_info in SECRET_PATTERNS.items():
            matches = re.finditer(pattern_info['pattern'], line, re.IGNORECASE)
            for match in matches:
                secret_value = match.group(0)
                findings.append({
                    'line': line_num,
                    'column': match.start() + 1,
                    'type': pattern_name,
                    'value': secret_value,
                    'severity': get_severity(pattern_name),
                    'description': pattern_info['description'],
                    'line_content': line.strip()
                })

    # Deduplicate findings
    unique_findings = []
    seen = set()
    for finding in findings:
        key = f"{finding['type']}::{finding['value']}"
        if key not in seen:
            seen.add(key)
            unique_findings.append(finding)

    return unique_findings


def migrate_secrets_to_vault(findings: List[Dict]) -> List[Dict]:
    """Migrate detected secrets to Vault with Transit encryption"""
    results = []

    # Ensure Transit engine is enabled
    vault_client.enable_transit_engine()

    # Ensure Transit key exists
    vault_client.create_transit_key('secret-scanner-key')

    for idx, finding in enumerate(findings):
        secret_type = finding['type']
        secret_value = finding['value']
        vault_path = f"scanner/secrets/{secret_type}_{idx}"

        # Determine if this secret type should be encrypted
        encrypt_types = [
            'generic_password', 'database_url', 'jdbc_url',
            'aws_secret_key', 'azure_client_secret',
            'vault_token', 'vault_root_token',
            'generic_secret', 'jwt_token'
        ]

        should_encrypt = any(encrypt_type in secret_type for encrypt_type in encrypt_types)

        if should_encrypt:
            # Encrypt with Transit
            encrypted_value = vault_client.transit_encrypt('secret-scanner-key', secret_value)
            if encrypted_value:
                # Store encrypted value in KV
                success = vault_client.kv_write_secret(
                    vault_path,
                    {
                        'value': encrypted_value,
                        'type': secret_type,
                        'severity': finding['severity'],
                        'encrypted': True,
                        'encryption_key': 'secret-scanner-key'
                    }
                )
                results.append({
                    'path': vault_path,
                    'type': secret_type,
                    'encrypted': True,
                    'success': success
                })
            else:
                results.append({
                    'path': vault_path,
                    'type': secret_type,
                    'encrypted': False,
                    'success': False,
                    'error': 'Encryption failed'
                })
        else:
            # Store plaintext in KV
            success = vault_client.kv_write_secret(
                vault_path,
                {
                    'value': secret_value,
                    'type': secret_type,
                    'severity': finding['severity'],
                    'encrypted': False
                }
            )
            results.append({
                'path': vault_path,
                'type': secret_type,
                'encrypted': False,
                'success': success
            })

    return results


def generate_updated_code(original_code: str, findings: List[Dict]) -> str:
    """Generate updated code with Vault references"""
    lines = original_code.split('\n')
    updated_lines = lines.copy()

    # Sort findings by line number in reverse to avoid offset issues
    sorted_findings = sorted(findings, key=lambda x: x['line'], reverse=True)

    # Replace secrets with Vault references
    for idx, finding in enumerate(sorted_findings):
        line_num = finding['line'] - 1
        if line_num < len(updated_lines):
            original_line = updated_lines[line_num]
            secret_value = finding['value']
            vault_path = f"scanner/secrets/{finding['type']}_{idx}"

            # Replace the secret with a Vault reference comment
            updated_line = original_line.replace(
                secret_value,
                f'get_secret_from_vault("{vault_path}")'
            )
            updated_lines[line_num] = updated_line

    # Add Vault client initialization at the beginning
    vault_init_code = '''
# Vault client initialization
import hvac
import os

def get_vault_client():
    """Initialize Vault client"""
    client = hvac.Client(
        url=os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200'),
        token=os.getenv('VAULT_TOKEN')
    )
    return client

def get_secret_from_vault(path):
    """Retrieve and decrypt secret from Vault"""
    client = get_vault_client()
    
    # Read secret from KV
    secret_response = client.secrets.kv.v2.read_secret_version(path=path)
    secret_data = secret_response['data']['data']
    
    # Check if encrypted
    if secret_data.get('encrypted'):
        # Decrypt with Transit
        encrypted_value = secret_data['value']
        decrypt_response = client.secrets.transit.decrypt_data(
            name=secret_data['encryption_key'],
            ciphertext=encrypted_value
        )
        import base64
        decrypted_value = base64.b64decode(decrypt_response['data']['plaintext']).decode('utf-8')
        return decrypted_value
    else:
        return secret_data['value']

'''

    updated_code = vault_init_code + '\n'.join(updated_lines)
    return updated_code


def create_results_card(findings: List[Dict], migration_results: List[Dict]) -> dbc.Card:
    """Create results display card with enhanced IBM Carbon Design"""
    # Create findings table with improved styling
    findings_rows = []
    for idx, finding in enumerate(findings):
        severity_color = {
            'critical': CARBON_COLORS['danger'],
            'high': '#ff832b',
            'medium': CARBON_COLORS['warning'],
            'low': CARBON_COLORS['success']
        }.get(finding['severity'], CARBON_COLORS['text_02'])
        
        severity_icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(finding['severity'], '⚪')

        findings_rows.append(
            html.Tr([
                html.Td(str(idx + 1), style={'fontWeight': '600', 'color': CARBON_COLORS['text_02']}),
                html.Td(str(finding['line']), style={'fontFamily': 'IBM Plex Mono, monospace', 'fontWeight': '500'}),
                html.Td(finding['type'].replace('_', ' ').title(), style={'fontWeight': '500'}),
                html.Td(
                    html.Span([
                        html.Span(severity_icon, style={'marginRight': '6px'}),
                        finding['severity'].upper()
                    ],
                        className='carbon-badge',
                        style={
                            'backgroundColor': severity_color,
                            'color': 'white',
                            'padding': '6px 12px',
                            'borderRadius': '12px',
                            'fontSize': '11px',
                            'fontWeight': '600',
                            'letterSpacing': '0.5px',
                            'display': 'inline-flex',
                            'alignItems': 'center'
                        }
                    )
                ),
                html.Td(
                    f"{finding['value'][:4]}...{finding['value'][-4:]}" if len(finding['value']) > 8 else finding['value'],
                    style={
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '12px',
                        'backgroundColor': '#f4f4f4',
                        'padding': '4px 8px',
                        'borderRadius': '4px'
                    }
                ),
                html.Td(finding['description'], style={'fontSize': '13px', 'color': CARBON_COLORS['text_02']})
            ], style={'borderBottom': f'1px solid {CARBON_COLORS["ui_03"]}'})
        )

    findings_table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("#", style={'width': '60px'}),
                    html.Th("Line", style={'width': '80px'}),
                    html.Th("Pattern Type", style={'width': '180px'}),
                    html.Th("Severity", style={'width': '140px'}),
                    html.Th("Value Preview", style={'width': '150px'}),
                    html.Th("Description")
                ]),
                style={
                    'backgroundColor': CARBON_COLORS['ui_05'],
                    'color': CARBON_COLORS['text_04'],
                    'fontWeight': '600',
                    'fontSize': '13px',
                    'letterSpacing': '0.32px'
                }
            ),
            html.Tbody(findings_rows)
        ],
        bordered=False,
        hover=True,
        responsive=True,
        className='carbon-table',
        style={
            'fontFamily': 'IBM Plex Sans, sans-serif',
            'fontSize': '14px',
            'marginBottom': '0'
        }
    )

    # Create migration results table with enhanced styling
    migration_rows = []
    for idx, result in enumerate(migration_results):
        encryption_badge = html.Span(
            "🔐 Transit (AES256)" if result['encrypted'] else "📝 Plaintext",
            className='carbon-badge',
            style={
                'backgroundColor': '#0f62fe' if result['encrypted'] else CARBON_COLORS['ui_04'],
                'color': 'white' if result['encrypted'] else CARBON_COLORS['text_01'],
                'padding': '6px 12px',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'letterSpacing': '0.5px',
                'display': 'inline-flex',
                'alignItems': 'center'
            }
        )

        status_badge = html.Span(
            "✓ Success" if result['success'] else "✗ Failed",
            className='carbon-badge',
            style={
                'backgroundColor': CARBON_COLORS['success'] if result['success'] else CARBON_COLORS['danger'],
                'color': 'white',
                'padding': '6px 12px',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'letterSpacing': '0.5px',
                'display': 'inline-flex',
                'alignItems': 'center'
            }
        )

        migration_rows.append(
            html.Tr([
                html.Td(str(idx + 1), style={'fontWeight': '600', 'color': CARBON_COLORS['text_02']}),
                html.Td(result['path'], style={
                    'fontFamily': 'IBM Plex Mono, monospace',
                    'fontSize': '12px',
                    'backgroundColor': '#f4f4f4',
                    'padding': '4px 8px',
                    'borderRadius': '4px'
                }),
                html.Td(result['type'].replace('_', ' ').title(), style={'fontWeight': '500'}),
                html.Td(encryption_badge),
                html.Td(status_badge)
            ], style={'borderBottom': f'1px solid {CARBON_COLORS["ui_03"]}'})
        )

    migration_table = dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("#", style={'width': '60px'}),
                    html.Th("Vault Path", style={'width': '300px'}),
                    html.Th("Pattern Type", style={'width': '180px'}),
                    html.Th("Encryption", style={'width': '180px'}),
                    html.Th("Status", style={'width': '120px'})
                ]),
                style={
                    'backgroundColor': CARBON_COLORS['ui_05'],
                    'color': CARBON_COLORS['text_04'],
                    'fontWeight': '600',
                    'fontSize': '13px',
                    'letterSpacing': '0.32px'
                }
            ),
            html.Tbody(migration_rows)
        ],
        bordered=False,
        hover=True,
        responsive=True,
        className='carbon-table',
        style={
            'fontFamily': 'IBM Plex Sans, sans-serif',
            'fontSize': '14px',
            'marginBottom': '0'
        }
    )

    # Enhanced summary statistics with Carbon styling
    total_secrets = len(findings)
    encrypted_count = sum(1 for r in migration_results if r['encrypted'])
    plaintext_count = total_secrets - encrypted_count
    success_count = sum(1 for r in migration_results if r['success'])

    summary = dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("📊", style={'fontSize': '2rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    html.H2(str(total_secrets), style={
                        'color': CARBON_COLORS['interactive_01'],
                        'fontWeight': '700',
                        'fontSize': '2.5rem',
                        'marginBottom': '0.25rem'
                    }),
                    html.P("Total Secrets", style={
                        'color': CARBON_COLORS['text_02'],
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'marginBottom': '0'
                    })
                ])
            ], className="stat-card text-center")
        ], width=3),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("🔐", style={'fontSize': '2rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    html.H2(str(encrypted_count), style={
                        'color': CARBON_COLORS['info'],
                        'fontWeight': '700',
                        'fontSize': '2.5rem',
                        'marginBottom': '0.25rem'
                    }),
                    html.P("Encrypted (Transit)", style={
                        'color': CARBON_COLORS['text_02'],
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'marginBottom': '0'
                    })
                ])
            ], className="stat-card text-center")
        ], width=3),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("📝", style={'fontSize': '2rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    html.H2(str(plaintext_count), style={
                        'color': CARBON_COLORS['warning'],
                        'fontWeight': '700',
                        'fontSize': '2.5rem',
                        'marginBottom': '0.25rem'
                    }),
                    html.P("Plaintext (KV)", style={
                        'color': CARBON_COLORS['text_02'],
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'marginBottom': '0'
                    })
                ])
            ], className="stat-card text-center")
        ], width=3),
        dbc.Col([
            html.Div([
                html.Div([
                    html.Span("✅", style={'fontSize': '2rem', 'marginBottom': '0.5rem', 'display': 'block'}),
                    html.H2(str(success_count), style={
                        'color': CARBON_COLORS['success'],
                        'fontWeight': '700',
                        'fontSize': '2.5rem',
                        'marginBottom': '0.25rem'
                    }),
                    html.P("Successfully Migrated", style={
                        'color': CARBON_COLORS['text_02'],
                        'fontSize': '0.875rem',
                        'fontWeight': '500',
                        'marginBottom': '0'
                    })
                ])
            ], className="stat-card text-center")
        ], width=3)
    ], className="mb-4")

    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H4("📋 Scan Results", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'marginBottom': '0',
                    'fontWeight': '600',
                    'display': 'inline-block'
                }),
                html.Span(f"{len(findings)} secrets detected and migrated", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontSize': '0.875rem',
                    'color': CARBON_COLORS['text_02'],
                    'marginLeft': '1rem',
                    'verticalAlign': 'middle'
                })
            ])
        ], style={
            'backgroundColor': CARBON_COLORS['ui_01'],
            'borderBottom': f'3px solid {CARBON_COLORS["interactive_01"]}'
        }),
        dbc.CardBody([
            summary,
            html.Hr(style={'borderColor': CARBON_COLORS['ui_03'], 'margin': '2rem 0'}),
            html.Div([
                html.H5("🔍 Pattern Detection Results", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontWeight': '600',
                    'marginBottom': '1rem'
                }),
                html.P("Detected hardcoded secrets in your source code", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontSize': '0.875rem',
                    'color': CARBON_COLORS['text_02'],
                    'marginBottom': '1rem'
                })
            ]),
            findings_table,
            html.Hr(style={'borderColor': CARBON_COLORS['ui_03'], 'margin': '2rem 0'}),
            html.Div([
                html.H5("🔐 Vault Storage Results", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontWeight': '600',
                    'marginBottom': '1rem'
                }),
                html.P("Secrets have been securely stored in HashiCorp Vault", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontSize': '0.875rem',
                    'color': CARBON_COLORS['text_02'],
                    'marginBottom': '1rem'
                })
            ]),
            migration_table
        ])
    ], className='mb-4 carbon-card')


def create_migrated_code_card(updated_code: str) -> dbc.Card:
    """Create migrated code display card with enhanced Carbon styling"""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H4("💻 Updated Code with Vault Integration", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'marginBottom': '0',
                    'fontWeight': '600',
                    'display': 'inline-block'
                }),
                html.Span("Production-ready code", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontSize': '0.875rem',
                    'color': CARBON_COLORS['text_02'],
                    'marginLeft': '1rem',
                    'verticalAlign': 'middle'
                })
            ])
        ], style={
            'backgroundColor': CARBON_COLORS['ui_01'],
            'borderBottom': f'3px solid {CARBON_COLORS["success"]}'
        }),
        dbc.CardBody([
            dbc.Alert([
                html.Div([
                    html.Span("ℹ️", style={'fontSize': '1.5rem', 'marginRight': '12px'}),
                    html.Div([
                        html.Strong("Ready to Deploy", style={'display': 'block', 'marginBottom': '4px'}),
                        html.Span(
                            "The code below has been refactored to retrieve secrets from Vault. "
                            "Set VAULT_ADDR and VAULT_TOKEN environment variables before running.",
                            style={'fontSize': '0.875rem', 'opacity': '0.9'}
                        )
                    ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
                ], style={'display': 'flex', 'alignItems': 'flex-start'})
            ],
                color="info",
                style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'borderLeft': f'4px solid {CARBON_COLORS["info"]}',
                    'borderRadius': '4px',
                    'marginBottom': '1.5rem'
                }
            ),
            html.Div([
                html.Label("Refactored Source Code", style={
                    'fontFamily': 'IBM Plex Sans, sans-serif',
                    'fontWeight': '600',
                    'fontSize': '0.875rem',
                    'color': CARBON_COLORS['text_02'],
                    'marginBottom': '0.5rem',
                    'display': 'block',
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.32px'
                }),
                dcc.Textarea(
                    value=updated_code,
                    className='code-editor',
                    style={
                        'width': '100%',
                        'height': '450px',
                        'fontFamily': 'IBM Plex Mono, monospace',
                        'fontSize': '13px',
                        'lineHeight': '1.6',
                        'backgroundColor': '#262626',
                        'color': '#f4f4f4',
                        'border': f'2px solid {CARBON_COLORS["ui_03"]}',
                        'borderRadius': '4px',
                        'padding': '16px',
                        'resize': 'vertical'
                    },
                    readOnly=True
                )
            ]),
            html.Div([
                dbc.Button([
                    html.Span("📋 ", style={'marginRight': '8px'}),
                    "Copy to Clipboard"
                ],
                    id='copy-button',
                    color="secondary",
                    size="lg",
                    className="carbon-button",
                    style={
                        'fontFamily': 'IBM Plex Sans, sans-serif',
                        'fontWeight': '500',
                        'padding': '12px 32px',
                        'marginTop': '1rem'
                    }
                ),
                html.Div([
                    html.P([
                        html.Strong("Next Steps:", style={'display': 'block', 'marginBottom': '0.5rem'}),
                        html.Span("1. Copy the code above", style={'display': 'block'}),
                        html.Span("2. Set environment variables: VAULT_ADDR and VAULT_TOKEN", style={'display': 'block'}),
                        html.Span("3. Install hvac: pip install hvac", style={'display': 'block'}),
                        html.Span("4. Run your application with secure secret management", style={'display': 'block'})
                    ], style={
                        'fontFamily': 'IBM Plex Sans, sans-serif',
                        'fontSize': '0.875rem',
                        'color': CARBON_COLORS['text_02'],
                        'backgroundColor': CARBON_COLORS['ui_02'],
                        'padding': '1rem',
                        'borderRadius': '4px',
                        'marginTop': '1rem',
                        'borderLeft': f'4px solid {CARBON_COLORS["success"]}'
                    })
                ])
            ])
        ])
    ], className='carbon-card')


if __name__ == '__main__':
    port = int(os.getenv('DASH_PORT', 8050))
    debug = os.getenv('DASH_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)

# Made with Bob
