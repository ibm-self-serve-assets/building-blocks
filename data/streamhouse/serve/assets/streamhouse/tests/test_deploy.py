"""No-network tests for one-command Terraform launcher and schema consistency."""
import base64
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('deploy', ROOT / 'scripts' / 'deploy.py')
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)


def outputs():
    return {key: {'value': value} for key, value in {
        'kafka_bootstrap': 'SASL_SSL://broker.cloud:9092',
        'kafka_app_key': 'test-app-key', 'kafka_app_secret': 'test-app-secret',
        'schema_registry_url': 'https://registry.cloud',
        'schema_registry_key': 'sr-key', 'schema_registry_secret': 'sr-secret',
        'flink_compute_pool_id': 'lfcp-123',
        'mcp_endpoint': 'https://mcp.cloud/mcp',
        'mcp_global_key': 'mcp-key', 'mcp_global_secret': 'mcp-secret',
    }.items()}


class DeploymentTests(unittest.TestCase):
    def test_cloud_credentials_are_not_persisted(self):
        env = deploy.render_env(outputs(), 'VITE_GOOGLE_MAPS_API_KEY=local-public-key\nPORT=4000\n')
        self.assertIn('STREAM_MODE=kafka', env)
        self.assertIn('KAFKA_BOOTSTRAP_SERVERS=broker.cloud:9092', env)
        self.assertIn('SCHEMA_REGISTRY_API_SECRET=sr-secret', env)
        self.assertIn('VITE_GOOGLE_MAPS_API_KEY=local-public-key', env)
        self.assertIn('KAFKA_CONSUME_DERIVED=true', env)
        self.assertNotIn('CONFLUENT_CLOUD_API_KEY=', env)
        self.assertIn('RTCE_MCP_BASIC_TOKEN='+base64.b64encode(b'mcp-key:mcp-secret').decode(),env)

    def test_missing_runtime_creds_fails_closed(self):
        bad = outputs()
        bad['kafka_app_secret'] = {'value': ''}
        with self.assertRaises(RuntimeError):
            deploy.render_env(bad)

    def test_no_rtce_and_flink_settings(self):
        v = outputs()
        v['flink_compute_pool_id'] = {'value': None}
        v['mcp_global_key'] = {'value': None}
        v['mcp_global_secret'] = {'value': None}
        v['mcp_endpoint'] = {'value': None}
        rendered = deploy.render_env(v)
        self.assertIn('KAFKA_CONSUME_DERIVED=false',rendered)
        self.assertIn('RTCE_MCP_BASIC_TOKEN=\n',rendered)

    def test_source_schemas_are_json_schema_and_subjects_match(self):
        paths = sorted((ROOT / 'infra' / 'terraform' / 'schemas').glob('*.json'))
        self.assertEqual(len(paths),6)
        for path in paths:
            obj = json.loads(path.read_text())
            self.assertEqual(obj['type'],'object')
            self.assertTrue(obj['required'])
            self.assertTrue(set(obj['required']).issubset(set(obj['properties'])))
            self.assertTrue(re.match(r'factory-(iot-telemetry|asset-state|maintenance-events)-(key|value).json', path.name))

    def test_terraform_schema_files_match_actual_node_producer(self):
        if not shutil.which('node'):
            self.skipTest('Node unavailable; install Node 20+ before running')
        js = """import {VALUE_SCHEMAS,KEY_SCHEMA} from './server/src/schemas.js';
console.log(JSON.stringify({values:VALUE_SCHEMAS,key:KEY_SCHEMA}));"""
        result = subprocess.run(['node','--input-type=module','-e',js],cwd=ROOT,
                                capture_output=True,text=True,check=True)
        schemas = json.loads(result.stdout)
        for topic, schema in schemas['values'].items():
            for kind, expected in (('value',schema),('key',schemas['key'])):
                got = json.loads((ROOT / 'infra' / 'terraform' / 'schemas' / f'{topic}-{kind}.json').read_text())
                self.assertEqual(got,expected)

    def test_all_terraform_resources_are_present(self):
        code = (ROOT / 'infra' / 'terraform' / 'main.tf').read_text()
        for resource in ('confluent_environment', 'confluent_kafka_cluster',
            'confluent_kafka_topic', 'confluent_api_key', 'confluent_kafka_acl',
            'confluent_schema', 'confluent_flink_compute_pool',
            'confluent_flink_statement', 'confluent_tableflow_topic',
            'confluent_rtce_topic'):
            self.assertIn('resource "'+resource+'"',code)
        self.assertTrue((ROOT / 'infra' / 'terraform' / 'sql' / '05-governed-topic-ctas.sql').exists())


if __name__=='__main__':
    unittest.main()
