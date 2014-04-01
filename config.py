import json
import priorityutil
import importlib

cfg_json_filename = 'config.js'
agent_types = ['fisherman', 'aquaculture', 'tourist', 'government', 
    'municipality', 'civilian']
voting_agents = ['fisherman', 'aquaculture', 'tourist', 'civilian']

def load(varargs = None, filename = cfg_json_filename):
    with open(filename, 'r') as f:
        return process_config(json.load(f))
        
def process_config(cfg):
    cfg = convert_voting_mechanisms(cfg)
    cfg = convert_priorities(cfg)
    return cfg
        
def convert_voting_mechanisms(cfg):
    for agent_type in voting_agents:
        cfg[agent_type]['voting mechanism class'] = import_class(
            cfg[agent_type]['voting mechanism class']
        )
    return cfg
    
def import_class(full_classname):
    class_name = full_classname.split('.')
    m = importlib.import_module('.'.join(class_name[:-1]))
    return getattr(m, class_name[-1])        

def convert_priorities(cfg):
    for agent_type in agent_types:
        cfg[agent_type]['priorities'] = conv_p_dict(cfg[agent_type]['priorities'])
    return cfg
		
def conv_p_dict(pd):
    return {priorityutil.from_string(k): pd[k] for k in pd}