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
    
def simulate():
    structure = cfg['world']['structure']
    gs = world.GridStructure(structure['width'], structure['height'])
    fishermen = [entities.Fisherman() for _ in xrange(cfg['fisherman']['num'])]
    gs.populate_evenly([world.Slot(a) for a in fishermen])
    x, y = gs.get_occupant_position(fishermen[0])
    print([str(e) for e in gs.neighborhood(x, y)])


if __name__ == "__main__":
    sys.exit(main())
