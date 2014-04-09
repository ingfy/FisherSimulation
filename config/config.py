import json
import lib.priority as priority
import inspect
import sys
import importlib

cfg_json_filename = 'config/config.js'
agent_types = ['fisherman', 'aquaculture', 'tourist', 'government', 
    'municipality', 'civilian']
voting_agents = ['fisherman', 'aquaculture', 'tourist', 'civilian']

def load(varargs = None, filename = cfg_json_filename):
    with open(filename, 'r') as f:
        return process_config(json.load(f))
        
def process_config(cfg):
    cfg = convert_priorities(cfg)
    cfg = convert_classes(cfg)
    return cfg
    
def convert_classes(cfg):
    if isinstance(cfg, dict):
        if "type" in cfg and cfg["type"] == "class":       
            return import_class(cfg["class"])
        else:
            for key in cfg:
                cfg[key] = convert_classes(cfg[key])
    return cfg
    
def import_class(full_classname):
    class_name = full_classname.split('.')
    m = importlib.import_module('.'.join(class_name[:-1]))
    return getattr(m, class_name[-1])

def convert_priorities(cfg):
    for agent_type in agent_types:
        cfg[agent_type]['priorities'] = \
            conv_p_dict(cfg[agent_type]['priorities'])
    return cfg
		
def conv_p_dict(pd):
    return {priority_from_string(k): pd[k] for k in pd}
    
priority_types = inspect.getmembers(
    priority, lambda e: isinstance(e, priority.Priority)
)
string_to_obj = {n : c for (n, c) in priority_types}

def priority_from_string(str):
    assert str in string_to_obj, "Priority %s doesn't exist" % str
    return string_to_obj[str]