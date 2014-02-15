import priority
import inspect
import sys
		
def _is_priority(c):
    for e in inspect.getmro(c):
        if e == priority.Priority: return True
    return False    
    
priority_types = inspect.getmembers(priority, lambda e: inspect.isclass(e) and _is_priority(e))
string_to_class = {n : c for (n, c) in priority_types}

class NonexistingPriorityException(Exception): pass

def from_string(str):
    try:
        return string_to_class[str]
    except KeyError:
        # TODO: log
        raise NonexistingPriorityException("No such priority: %s" % str)