import entities
import world
import priorityutil
import priority
import simulation

class Interface(object):
    def __init__(self):
        self._s = simulation.Simulation()

    def get_map(self):
        return Map.from_world_map(self._s.get_map())
        
    def abort(self):
        self._s.abort()
        
    def setup_config(self, cfg=None):
        self._s.setup_config()

    def start_simulation(self):
        self._s.initialize()
        self._s.start()
        
## Objects to be sent through interface
## Contains minimal logic
        
class Map(object):
    """
    Public members:
        grid    Array<Slot>[][]
    """
    def __init__(self, grid):
        self.grid = grid
        
    @classmethod
    def from_world_map(c, world_map):
        s = world_map.get_structure()
        return c([[Slot.from_world_slot(c) for c in r] for r in s.get_grid()])
        
class Slot(object):
    """ 
    Public members:
        spawning        Boolean
        aquaculture     Boolean
        fisherman       Boolean
        land            Boolean
    """
    def __init__(self, spawning, aquaculture, fisherman, land):
        self.spawning = spawning
        self.aquaculture = aquaculture
        self.fisherman = fisherman
        self.land = land
        
    @classmethod
    def from_world_slot(c, world_slot):
        occupant = world_slot.get_occupant()
        return c(
            world_slot.fish_spawning(),
            occupant is not None and occupant.__class__ is entities.Aquaculture,
            occupant is not None and occupant.__class__ is entities.Fisherman,
            world_slot.is_land()
        )