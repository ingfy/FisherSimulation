import json

cfg_json_filename = 'config.js'

def load(varargs = None):
    with open(cfg_json_filename, 'r') as f:
        return json.load(f)
		
	