class Map:
    def __init_(self):
        self.structure = None
    
    def set_structure(self, structure):
        self.structure = structure

    def get_a_slot(self):
        return self.structure.get_a_slot()

# Slot
#   get_occupant():         returns fisherman if there is one there
#   populate(agent):        sets the fisherman to the given agent
#   build_aquaculture():    blocks the slot and kicks out the fisherman
#   good_fishing():         indicates if the current slot is a good fishing spot
# Assume that all occupants can be converted to strings

class Slot:
    def __init__(self, occupant=None):
        self._occupant = occupant
        self._spawning = False
        self._blocked = False

    def get_occupant(self):
        return self._occupant

    def is_blocked(self):
        return self._blocked
    
    def good_fishing(self):
        return self.fish_spawning()

    def fish_spawning(self):
        return not self._blocked and self._spawning

    def populate(self, agent):
        self._occupant = agent

    def build_aquaculture(self):
        self._occupant = None
        self._blocked = True

    def __str__(self):
        surround = "s{%s}" if self._spawning else "s[%s]"
        return surround % (str(self._occupant) if self._occupant is not None else " ")

# General Structure doc:
#   populate_evenly(agents) :   Assumes that the structure has at
#                               least as many slots as the number
#                               of agents passed
#   __init__(width, height) :   Defines the structure size
#   size()                  :   Returns the size
#   neighborhood(x, y)      :   Gets all the agents that neigh-
#                               bors the given cell. Type of
#                               neighborhood decided by struct.
class GridStructure:
    def __init__(self, width, height, neighborhood_type="von_neumann"):
        self._slots = [[None for _ in xrange(width)] for _ in xrange(height)]
        self.set_neighborhood_type(neighborhood_type)
            
    def set_neighborhood_type(self, neighborhood_type):
        try:
            self.neighborhood = {
                "von_neumann":    self.neighborhood_von_neumann,
                "moore":          self.neighborhood_moore
            }[neighborhood_type]
        except NameError:
            raise Exception("Undefined neighborhood type")

    def get_a_slot(self):
        return self._slots[0][0]
        
    def coordinates_list(self):
        # flatten the grid
        return [(x, y) for y in xrange(0, len(self._slots)) for x in xrange(0, len(self._slots[y]))]

    def populate_evenly(self, agents):
        # Exception on next when out of bounds
        iter_agents = iter(agents)
        num = len(agents)
        for x, y in self.coordinates_list():
            self._slots[x][y] = next(iter_agents)

    def size(self):
        # Assume all rows have the same amount of cells, 
        # since that's the structure we're working with
        return (len(self._slots), len(self._slots[0]))

    def in_bounds(self, x, y):
        w, h = self.size()
        return w > x >= 0 and h > y >= 0

    def get_occupant_position(self, occupant):
        for x in xrange(len(self._slots)):
            for y in xrange(len(self._slots[x])):
                if occupant is self._slots[x][y].get_occupant(): 
                    return (x, y)
        return None

    def neighborhood_moore(self, x, y):
        d = [(1,1),(1,0),(1,-1),(0,1),(0,-1),(-1,1),(-1,0),(-1,-1)]
        return self.get_positions_if_valid([(x + X, y + Y) for (X,Y) in d])

    def neighborhood_von_neumann(self, x, y):
        d = [(1,0),(0,1),(-1,0),(0,-1)]
        return self.get_positions_if_valid([(x + X, y + Y) for (X,Y) in d])
    
    def get_positions_if_valid(self, positions):
        valid_positions = filter(lambda (x,y): self.in_bounds(x,y), positions)
        return [self._slots[x][y] for (x,y) in valid_positions]

