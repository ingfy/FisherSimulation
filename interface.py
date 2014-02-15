import main
import entities
import world
import priorityutil
import priority

class Abstract(object):
    def map_changed(map):
        raise NotImplementedError
        
    
