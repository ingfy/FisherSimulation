import config
import entities
import world 
import sys
import agent

##      Globals     ##
cfg = None

## Simulation MAIN module ##

def setup_config():
    ## handle varargs
    global cfg
    cfg = config.load(varargs = None)

def main():
    setup_config()
    simulate()
    return 0    
    
class MissingConfigurationException(Exception): pass
    
def simulate(callback=None):
    if cfg is None:
        raise MissingConfigurationException("Configuration not instantiated. Run setup_config()")
    structure = cfg['world']['structure']
    gs = world.GridStructure(structure['width'], structure['height'])
    fishermen = [entities.Fisherman() for _ in xrange(cfg['fisherman']['num'])]
    gs.populate_evenly([world.Slot(a) for a in fishermen])
    x, y = gs.get_occupant_position(fishermen[0])

if __name__ == "__main__":
    sys.exit(main())
