import yaml
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), '../config/service_rules.yaml')

def load_rules():
    with open(RULES_PATH, 'r') as f:
        return yaml.safe_load(f)

def check_necessity(pii_list, service_type):
    rules = load_rules()
    service_rules = rules.get(service_type, {})
    required = service_rules.get('required', [])
    exceptions = service_rules.get('exceptions', [])
    result = []
    for pii in pii_list:
        needed = pii['type'] in required and pii['type'] not in exceptions
        result.append({'type': pii['type'], 'value': pii['value'], 'needed': needed})
    return result
