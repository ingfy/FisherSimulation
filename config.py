import json
import priorityutil

cfg_json_filename = 'config.js'

def load(varargs = None):
    with open(cfg_json_filename, 'r') as f:
        return convert_priorities(json.load(f))

def convert_priorities(cfg):
    for agent_type in ['fisherman', 'aquaculture', 'tourist', 'government', 'civilian']:
        cfg[agent_type]['priorities'] = conv_p_dict(cfg[agent_type]['priorities'])
    return cfg
		
def conv_p_dict(pd):
    return {priorityutil.from_string(k): pd[k] for k in pd}