import json, sys
from pathlib import Path

state_file = Path(__file__).parent.parent / 'infra' / 'terraform' / 'terraform.tfstate'
state = json.loads(state_file.read_text())

listed = set()
for res in state.get('resources', []):
    for inst in res.get('instances', []):
        idx = inst.get('index_key')
        addr = f'{res["type"]}.{res["name"]}["{idx}"]' if idx else f'{res["type"]}.{res["name"]}'
        listed.add(addr)

admin   = next((r for r in state['resources'] if r['type']=='confluent_api_key' and r['name']=='admin_kafka'), None)
cluster = next((r for r in state['resources'] if r['type']=='confluent_kafka_cluster'), None)
env_r   = next((r for r in state['resources'] if r['type']=='confluent_environment'), None)

print('Topics in state:', [a for a in sorted(listed) if 'kafka_topic' in a])
print('admin_kafka in state:', admin is not None)
if admin:
    attrs = admin['instances'][0]['attributes']
    print('  admin key id:', attrs.get('id'))
    print('  admin secret present:', bool(attrs.get('secret')))
if cluster:
    attrs = cluster['instances'][0]['attributes']
    print('cluster id:', attrs.get('id'))
    print('cluster rest_endpoint:', attrs.get('rest_endpoint'))
if env_r:
    print('env id:', env_r['instances'][0]['attributes'].get('id'))
