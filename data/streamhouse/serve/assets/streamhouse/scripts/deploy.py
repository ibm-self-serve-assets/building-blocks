#!/usr/bin/env python3
"""Confluent Cloud Factory Pulse setup. Python stdlib; Terraform and Node/npm required.

The administrator key pair is obtained from the terminal or inherited environment;
NEVER written to the app .env or a tfvars file. Generated resource secrets from
Terraform are written to the ignored local .env and inevitably to Terraform state.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / 'infra' / 'terraform'
DOTENV = ROOT / '.env'


def explain(message: str) -> None:
    print(f'\n[Factory Pulse] {message}', flush=True)


def cli_command(program: str) -> str:
    cmd = shutil.which(program)
    if not cmd:
        raise RuntimeError(f'Missing {program}. Install it and rerun. See docs/one-click-terraform.md')
    return cmd


def _read_tfvars(path: Path) -> dict:
    """Parse key = "value" lines from a .tfvars file; returns only credential keys."""
    result = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding='utf8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'^(confluent_cloud_api_key|confluent_cloud_api_secret)\s*=\s*"([^"]*)"', line)
        if m:
            result[m.group(1)] = m.group(2)
    return result


def cloud_credentials(env: dict) -> dict:
    # Priority: shell environment → terraform.tfvars → interactive prompt
    tfvars = _read_tfvars(INFRA / 'terraform.tfvars')
    key = (env.get('CONFLUENT_CLOUD_API_KEY')
           or tfvars.get('confluent_cloud_api_key')
           or input('Confluent Cloud API KEY: ').strip())
    secret = (env.get('CONFLUENT_CLOUD_API_SECRET')
              or tfvars.get('confluent_cloud_api_secret')
              or getpass.getpass('Confluent Cloud API SECRET: '))
    if not key or not secret:
        raise RuntimeError('Both a Confluent Cloud API key AND secret are required.')
    env['CONFLUENT_CLOUD_API_KEY'] = key
    env['CONFLUENT_CLOUD_API_SECRET'] = secret
    return env


TFVARS_FILE = INFRA / 'terraform.tfvars'


def _tfvars_has_var(name: str) -> bool:
    """Return True if terraform.tfvars already declares this variable."""
    if not TFVARS_FILE.exists():
        return False
    return bool(re.search(rf'^\s*{name}\s*=', TFVARS_FILE.read_text(encoding='utf8'), re.M))


def terraform_vars(args, env: dict) -> dict:
    # Only set TF_VAR_* overrides for vars NOT already present in terraform.tfvars.
    # This lets the tfvars file be the single source of truth when fully populated.
    overrides = {
        'deployment_name': args.name,
        'region': args.region,
        'enable_flink': 'false' if args.no_flink else 'true',
        'enable_tableflow': 'false' if args.no_tableflow else 'true',
        'enable_rtce': 'false' if args.no_rtce else 'true',
        'flink_max_cfu': str(args.max_cfu),
    }
    for var, value in overrides.items():
        if not _tfvars_has_var(var):
            env[f'TF_VAR_{var}'] = value
    env['TF_IN_AUTOMATION'] = '1'
    env['TF_INPUT'] = '0'
    return env


def tf_varfile_args() -> list[str]:
    """Return -var-file flag if terraform.tfvars exists."""
    return ['-var-file', str(TFVARS_FILE)] if TFVARS_FILE.exists() else []


def run(command: list[str], env: dict, *, cwd=INFRA, capture=False):
    # Never print environment variables or contents of terraform JSON outputs.
    return subprocess.run(command, cwd=cwd, env=env, text=True, check=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)


def val(outputs: dict, name: str, default=''):
    return outputs.get(name, {}).get('value') or default


def render_env(outputs: dict, previous: str = '') -> str:
    """Preserve site-specific Maps credentials and action webhook, replace managed settings."""
    kafka = str(val(outputs, 'kafka_bootstrap'))
    kafka = re.sub(r'^(?:SASL_SSL|SSL|PLAINTEXT)://', '', kafka, flags=re.I)
    additions = {
        'STREAM_MODE': 'kafka',
        'KAFKA_BOOTSTRAP_SERVERS': kafka,
        'KAFKA_API_KEY': str(val(outputs, 'kafka_app_key')),
        'KAFKA_API_SECRET': str(val(outputs, 'kafka_app_secret')),
        'SCHEMA_REGISTRY_URL': str(val(outputs, 'schema_registry_url')),
        'SCHEMA_REGISTRY_API_KEY': str(val(outputs, 'schema_registry_key')),
        'SCHEMA_REGISTRY_API_SECRET': str(val(outputs, 'schema_registry_secret')),
        'KAFKA_AUTO_CREATE_TOPICS': 'false',
        'KAFKA_CONSUME_DERIVED': 'true' if val(outputs, 'flink_compute_pool_id') else 'false',
        'KAFKA_RISK_TOPIC': 'factory-risk-signals',
        'KAFKA_KPI_TOPIC': 'factory-shift-kpis',
        'RTCE_MCP_ENDPOINT': str(val(outputs, 'mcp_endpoint')),
        'RTCE_MCP_BASIC_TOKEN': '',
    }
    if val(outputs, 'mcp_global_key') and val(outputs, 'mcp_global_secret'):
        pair = f"{val(outputs,'mcp_global_key')}:{val(outputs,'mcp_global_secret')}"
        additions['RTCE_MCP_BASIC_TOKEN'] = base64.b64encode(pair.encode()).decode('ascii')
    if not additions['KAFKA_BOOTSTRAP_SERVERS'] or not additions['KAFKA_API_SECRET'] or not additions['SCHEMA_REGISTRY_API_SECRET']:
        raise RuntimeError('Terraform outputs do not contain the expected application credentials.')
    existing = {}
    for line in previous.splitlines():
        if line.lstrip().startswith('#') or '=' not in line:
            continue
        name, old = line.split('=', 1)
        name = name.strip()
        if re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
            existing[name] = old
    existing.update(additions)
    # Avoid copying credentials to logs, shell history, or README.
    return '# AUTOGENERATED by scripts/deploy.py. DO NOT COMMIT.\n' + '\n'.join(f'{k}={v}' for k, v in existing.items()) + '\n'


def write_private_env(text: str) -> None:
    # tempfile is private by default. Replace only after successful terraform apply.
    fd, name = tempfile.mkstemp(prefix='.factory-pulse-', dir=ROOT, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf8') as file:
            file.write(text)
        if os.name != 'nt':
            os.chmod(name, 0o600)
        os.replace(name, DOTENV)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def output_json(terraform: str, env: dict) -> dict:
    result = run([terraform, 'output', '-json'], env, capture=True)
    return json.loads(result.stdout)


def _state_json() -> dict:
    """Load the local terraform state file as a dict, or empty dict if absent."""
    state_file = INFRA / 'terraform.tfstate'
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding='utf8'))


def _state_resource(state: dict, res_type: str, res_name: str) -> dict | None:
    """Return the first instance attributes for a resource type+name from state."""
    for res in state.get('resources', []):
        if res.get('type') == res_type and res.get('name') == res_name:
            instances = res.get('instances', [])
            if instances:
                return instances[0].get('attributes', {})
    return None


def _state_listed(state: dict) -> set[str]:
    """Return the set of full resource address strings present in state."""
    addresses = set()
    for res in state.get('resources', []):
        module = res.get('module', '')
        prefix = f'{module}.' if module else ''
        for inst in res.get('instances', []):
            index = inst.get('index_key')
            if index is not None:
                addresses.add(f'{prefix}{res["type"]}.{res["name"]}["{index}"]')
            else:
                addresses.add(f'{prefix}{res["type"]}.{res["name"]}')
    return addresses


def import_orphaned_topics(terraform: str, env: dict, varfile: list[str]) -> None:
    """Import source Kafka topics that exist in Confluent Cloud but are missing from state.

    This handles the case where topics were removed from state (e.g. after a 403 error)
    but already exist on the cluster, causing a 400 'already exists' on the next apply.
    """
    state = _state_json()
    listed = _state_listed(state)

    # Get env_id and cluster_id from state
    env_attrs = _state_resource(state, 'confluent_environment', 'demo')
    cluster_attrs = _state_resource(state, 'confluent_kafka_cluster', 'demo')
    admin_key_attrs = _state_resource(state, 'confluent_api_key', 'admin_kafka')

    if not env_attrs or not cluster_attrs:
        explain('Cannot import topics: environment or cluster not in state yet.')
        return

    env_id = env_attrs.get('id')
    cluster_id = cluster_attrs.get('id')
    rest_endpoint = cluster_attrs.get('rest_endpoint')

    # If admin_kafka key is in state, use its credentials for the import REST calls.
    # The provider needs IMPORT_KAFKA_REST_ENDPOINT + credentials via env vars.
    import_env = env.copy()
    import_env['IMPORT_KAFKA_REST_ENDPOINT'] = rest_endpoint or ''
    if admin_key_attrs:
        import_env['IMPORT_KAFKA_API_KEY'] = admin_key_attrs.get('id', '')
        import_env['IMPORT_KAFKA_API_SECRET'] = admin_key_attrs.get('secret', '')

    source_topics = ['factory-iot-telemetry', 'factory-asset-state', 'factory-maintenance-events']
    for topic in source_topics:
        addr = f'confluent_kafka_topic.source["{topic}"]'
        if addr in listed:
            explain(f'  {topic} already in state, skipping import.')
            continue
        # confluent_kafka_topic import ID format: <cluster_id>/<topic_name>
        import_id = f'{cluster_id}/{topic}'
        explain(f'Importing orphaned topic {topic} ({import_id}) into state...')
        try:
            run([terraform, 'import', '-input=false'] + varfile + [addr, import_id], import_env)
            explain(f'  Imported {topic} OK')
        except subprocess.CalledProcessError as exc:
            # Topic doesn't exist on the cluster yet — Terraform will create it on apply.
            explain(f'  Import skipped for {topic} (will be created): {exc}')


def verify_state_permissions() -> None:
    if os.name == 'nt':
        return
    for pattern in ('*.tfstate', '*.tfstate.backup'):
        for f in INFRA.glob(pattern):
            os.chmod(f, 0o600)


def print_status(outputs: dict) -> None:
    # Print IDs only, never API keys/secrets or base64 HTTP auth.
    print('  Environment:', val(outputs, 'environment_id'))
    print('  Kafka cluster:', val(outputs, 'cluster_id'))
    print('  Region:', val(outputs, 'region'))
    print('  Kafka bootstrap:', val(outputs, 'kafka_bootstrap'))
    print('  Flink compute pool:', val(outputs, 'flink_compute_pool_id', '(disabled)'))
    print('  Flink SQL pipelines:', ', '.join(sorted(val(outputs, 'flink_statement_ids', {}).keys())) or '(disabled)')
    print('  Tableflow:', 'enabled' if val(outputs, 'tableflow_enabled') else 'disabled')
    print('  RTCE:', 'enabled' if val(outputs, 'rtce_enabled') else 'disabled')
    print('  RTCE MCP endpoint:', val(outputs, 'mcp_endpoint', '(disabled)'))


def launch_demo() -> None:
    npm = cli_command('npm.cmd' if os.name == 'nt' else 'npm')
    frontend = ROOT / 'frontend'
    if not (frontend / 'node_modules').exists():
        explain('Installing frontend dependencies (npm install)...')
        run([npm, 'install'], os.environ.copy(), cwd=frontend)
    explain('Starting Python backend API on http://localhost:4000 and Vite UI on http://localhost:5173; Ctrl+C stops the app, not Cloud resources.')
    backend = None
    frontend_proc = None
    try:
        backend = subprocess.Popen([sys.executable, 'server/app.py'], cwd=ROOT, env=os.environ.copy())
        frontend_proc = subprocess.Popen([npm, 'run', 'dev'], cwd=frontend, env=os.environ.copy())
        backend.wait()
    except KeyboardInterrupt:
        print('\nStopped local app. Run python scripts/deploy.py destroy when finished to stop Cloud billing.')
    finally:
        for proc in (frontend_proc, backend):
            if proc and proc.poll() is None:
                proc.terminate()


def main() -> int:
    p = argparse.ArgumentParser(description='One-command IBM Factory Pulse demo infrastructure and UI')
    p.add_argument('action', nargs='?', default='up', choices=('up', 'plan', 'retry', 'status', 'destroy', 'run'))
    p.add_argument('--name', default='factory-pulse-demo', help='Display name for a new, isolated Cloud environment')
    p.add_argument('--region', default='us-east-2', help='AWS region; verify feature availability')
    p.add_argument('--max-cfu', type=int, choices=[5, 10, 20, 30, 40, 50], default=5)
    p.add_argument('--no-flink', action='store_true', help='Do not create a Flink pool/statements')
    p.add_argument('--no-tableflow', action='store_true', help='Do not activate Iceberg materialization')
    p.add_argument('--no-rtce', action='store_true', help='Do not activate RTCE/MCP')
    p.add_argument('--yes', action='store_true', help='Approve provider plan automatically (BILLABLE)')
    p.add_argument('--no-launch', action='store_true', help='Provision Cloud but do not start the local UI')
    args = p.parse_args()
    try:
        if args.action == 'run':
            launch_demo()
            return 0
        terraform = cli_command('terraform')
        if args.action == 'status':
            print_status(output_json(terraform, os.environ.copy()))
            return 0
        env = terraform_vars(args, cloud_credentials(os.environ.copy()))
        varfile = tf_varfile_args()

        if args.action == 'retry':
            # Resume a partial apply without the plan→DEPLOY gate.
            # Imports orphaned topics (exist in Cloud but not in state) before applying.
            explain('Resuming incremental apply against existing Terraform state...')
            run([terraform, 'init', '-input=false'], env)
            import_orphaned_topics(terraform, env, varfile)
            run([terraform, 'apply', '-auto-approve', '-input=false'] + varfile, env)
            verify_state_permissions()
            outputs = output_json(terraform, env)
            previous = DOTENV.read_text(encoding='utf8') if DOTENV.exists() else (ROOT / '.env.example').read_text(encoding='utf8')
            write_private_env(render_env(outputs, previous))
            explain('.env updated with live Confluent credentials.')
            print_status(outputs)
            if not args.no_launch:
                launch_demo()
            else:
                print('Start later using: python scripts/deploy.py run')
            return 0

        if args.action in ('up', 'plan'):
            explain('Initializing pinned Confluent Terraform provider...')
            run([terraform, 'init', '-input=false'], env)
            explain('Checking Terraform configuration...')
            run([terraform, 'validate', '-no-color'], env)
            if args.action == 'plan':
                run([terraform, 'plan', '-no-color', '-input=false'] + varfile, env)
                return 0
            plan = INFRA / '.factory-pulse.tfplan'
            try:
                explain('Reviewing billable Confluent Cloud resources...')
                run([terraform, 'plan', '-out', str(plan), '-input=false'] + varfile, env)
                if os.name != 'nt' and plan.exists():
                    os.chmod(plan, 0o600)
                print('\nCAUTION: Standard Kafka, continuously-running Flink SQL, Tableflow, and RTCE can incur charges.')
                if not args.yes:
                    answer = input('Type DEPLOY to approve and provision: ').strip()
                    if answer != 'DEPLOY':
                        print('Cancelled. No resources applied.')
                        return 1
                explain('Applying Terraform plan...')
                run([terraform, 'apply', '-input=false', str(plan)], env)
                verify_state_permissions()
                outputs = output_json(terraform, env)
                previous = DOTENV.read_text(encoding='utf8') if DOTENV.exists() else (ROOT / '.env.example').read_text(encoding='utf8')
                write_private_env(render_env(outputs, previous))
                explain('Cloud infrastructure created. Application .env generated locally and permission-restricted.')
                print_status(outputs)
                if not args.no_launch:
                    launch_demo()
                else:
                    print('Start later using: python scripts/deploy.py run')
                return 0
            finally:
                plan.unlink(missing_ok=True)

        if args.action == 'destroy':
            print('WARNING: Terraform destroy permanently deletes the DEMO environment and data, including Iceberg Tableflow resources.')
            if not args.yes and input('Type DESTROY to confirm: ').strip() != 'DESTROY':
                print('Cancelled.')
                return 1
            run([terraform, 'init', '-input=false'], env)
            run([terraform, 'destroy', '-auto-approve', '-input=false'] + varfile, env)
            verify_state_permissions()
            print('Cloud teardown completed. Local .env and Terraform state remain for auditing; delete securely when appropriate.')
            return 0
    except (RuntimeError, subprocess.CalledProcessError, OSError, ValueError) as ex:
        verify_state_permissions()  # Partial applies can already contain sensitive keys.
        print(f'\n[Factory Pulse] ERROR: {ex}', file=sys.stderr)
        print('No live cloud success is claimed. See docs/one-click-terraform.md for recovery.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
