import priority
import inspect
import sys
		
def _is_priority(c):
    for e in inspect.getmro(c):
        if e == priority.Priority: return True
    return False    
    
priority_types = inspect.getmembers(priority, lambda e: inspect.isclass(e) and _is_priority(e))
string_to_class = {n : c for (n, c) in priority_types}

def from_string(str):
    assert str in string_to_class, "Priority %s doesn't exist" % str
    return string_to_class[str]