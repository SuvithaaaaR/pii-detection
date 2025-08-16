import yaml
import os

RULES_PATH = os.path.join(os.path.dirname(__file__), '../config/service_rules.yaml')

def load_rules():
    with open(RULES_PATH, 'r') as f:
        return yaml.safe_load(f)

def check_necessity(pii_list, service_type):
    rules = load_rules()
    required = rules.get(service_type, [])
    result = []
    for pii in pii_list:
        needed = pii['type'] in required
        result.append({'type': pii['type'], 'value': pii['value'], 'needed': needed})
    return result
