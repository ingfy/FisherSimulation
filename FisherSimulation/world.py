"""
The world module contains implementations for elements regarding the geography 
and contents of the world. This includes structure, and contents of map cells.
"""

import random
import math
import entities

class Map(object):
    """
    The map is the top-level entity, and it contains a structure which controls 
    positioning. It defines many methods for accessing information stored in the 
    structure, and for manipulating it.
    """

    def __init__(self, structure):
        self.set_structure(structure)
    
    def set_structure(self, structure):
        self._structure = structure
        
    def get_structure(self):
        return self._structure
        
    def get_max_distance(self):
        return self._structure.get_distance(
            (0, 0), tuple([e - 1 for e in self._structure.get_size()])
        )
        
    def get_random_cell(self, predicate = None):
        return random.choice(self.get_all_cells(predicate))
        
    def get_all_cells(self, predicate=None):
        cells = self._structure.get_all_slots()
        return cells if predicate is None else filter(predicate, cells)
        
    def populate_fishermen(self, factory, num):
        slots = self._structure.get_all_slots()
        random.shuffle(slots)
        good = [s for s in slots if s.fish_spawning()]
        bad  = [s for s in slots if not s.fish_spawning()]
        
        assert num <= len(good) + len(bad), \
            "%d fishermen, but map only contains %d slots" % (num, len(slots))
        
        for s in (good + bad)[:num]:
            s.populate(factory.fisherman(s))
            
    def get_cell_distance(self, a, b):
        return self._structure.get_cell_distance(a, b)
            
    def build_aquaculture(self, agent, cell):
        radius = self._structure.get_aquaculture_blocking(cell)
        damage = self._structure.get_aquaculture_damage(cell)
        for b in radius:
            if not b == cell:
                b.block()

        for c in damage:
            c.inflict_damage(damage[c])                
                
        cell.build_aquaculture(agent)
        
        return radius + damage.keys()
        
    def get_radius_from(self, cell, r):
        return self.get_radius(r, self._structure.get_cell_position(cell))
        
    def get_radius(self, r, pos):
        return self._structure.get_radius(r, pos)
        
# Slot
#   get_occupant():         returns fisherman if there is one there
#   populate(agent):        sets the fisherman to the given agent
#   build_aquaculture():    blocks the slot and kicks out the fisherman
#   fish_spawning():        indicates if the current slot is a good fishing spot
# Assume that all occupants can be converted to strings

class Slot(object):
    def __init__(self, occupants=None):
        self._occupants = occupants or []
        self._spawning = False
        self._blocked = False
        self._land = False
        self._has_aquaculture = False
        self._fish_quantity = 0.5

    def get_occupants(self):
        return self._occupants

    def is_blocked(self):
        return self._blocked
        
    def is_land(self):
        return self._land
        
    def inflict_damage(self, damage):
        """Inflicts damage on the cell's resource.
        
        Arguments:
            damage  A floating-point number between 0 and 1 representing the
                    proportional damage to be inflicted.
        """
        self._fish_quantity -= self._fish_quantity * damage
        
    def has_aquaculture(self):
        """Checks if the cell has aquaculture built on it.
        
        Returns: True or False.
        """
        return self._has_aquaculture
        
    def set_land(self):
        self._land = True
        
    def get_position(self, world_map):
        """Finds the position of this cell in the world map.
        
        Parameters:
            world_map:  A Map object
            
        Returns:
            A tuple of integers (x, y) representing the location in coordinate 
            form.
        """
        return world_map.get_structure().get_cell_position(self)
        
    def set_fish_spawning(self):
        self._spawning = True
        self._fish_quantity = 1.0
        
    def get_fish_quantity(self):
        return self._fish_quantity
        
    def get_fishing_efficiency(self):
        """Calculates the fishing output of this slot.
        
        Fishing output is shared evenly among all occupants.
        
        Returns a floating-point number.
        """
        return self._fish_quantity / len(self._occupants)

    def fish_spawning(self):
        return self._spawning
        
    def block(self):
        self._blocked = True

    def populate(self, agent):
        if not agent in self._occupants:
            self._occupants.append(agent)
        
    def remove(self, agent):
        if agent in self._occupants:
            self._occupants.remove(agent)

    def build_aquaculture(self, agent):
        self._has_aquaculture = True
        self._occupants = [agent]
        self._blocked = True
        
class MapStructure(object):
    """Interface showing methods that need to be implemented for a
    map structure."""
    
    @classmethod
    def create(cls, cfg, good_spot_frequency):
        """Creates the map structure. May be overridden, or the implementing
        subclass can have a constructor that takes the same arguments as this
        function.
        
        Parameters:
            cfg                 The configuration object for the structure
            good_spot_frequency A floating-point number representing the
                                probability of any one spot being good. Between
                                0 and 1.
                                
        Returns:
            An instance of the implementing class.
        """
        
        return cls(cfg, good_spot_frequency)
    
    def get_cell_distance(self, a, b):
        """Finds the distance in meters between two given cells.
        
        Paraeters:
            a   A Slot instance
            b   Another Slot instance
            
        Returns:
            A floating-point number representing the distance.
        """
        
        raise NotImplementedError()

    def get_distance(self, pos_a, pos_b):
        """Finds the distance in meters between two given positions.
        
        Paraeters:
            pos_a   A duple of two integers representing the first position
            pos_b   Another duple for the second position
            
        Returns:
            A floating-point number representing the distance.
        """
        
        raise NotImplementedError()

    def get_size(self): 
        """Gives the size of the structure.
        
        Returns:
            A duple of integers: (width, height).
        """
        
        raise NotImplementedError()

    def get_all_slots(self):
        """Gives a list of all the Slot instances in the structure.
        
        Returns:
            A list of Slot instances.
        """
        
        raise NotImplementedError()

    def get_aquaculture_blocking(self, cell):
        """Gets all the cells that will or would be blocked by aquaculture
        expansion in the given cell.
        
        The aquaculture blocking radius is given by the "aquaculture blocking
        radius" field in cfg.globals.
        
        Attributes:
            cell    The Slot where the aquaculture is being built
            
        Returns:
            A list of Slot instances.
        """
    
        raise NotImplementedError()

    def get_aquaculture_damage(self, cell):
        """Gets the cells damaged by aquaculture expansion in the given cell,
        and the amount of damage sustained to them.
        
        The aquaculture damage proportion is given by the "aquaculture damage 
        proportion" field in cfg.globals.
        
        The aquaculture damage radius is given by the "aquaculture damage 
        radius" field in cfg.globals.
        
        Attributes:
            cell    The Slot where aquaculture is being built.
            
        Returns:
            A dictionary mapping cells to a floating-point number between 0 and 
            1, representing the amount of damage, where 1 is completely 
            destroyed and 0 is untouched.
        """
    
        raise NotImplementedError()

    def get_cell_position(self, cell):
        """Gets the position of the given cell.
        
        Parameters:
            cell    A Slot instance
            
        Returns:
            A duple of integers representing the coordinate position of the 
            cell.
        """
    
        raise NotImplementedError()

    def get_radius(self, r, pos):
        """Gets all cells within the given radius of the given position.
        
        Paraeters:
            r   An integer representing the radius in meters.
            pos A duple of integers representing the coordinates of the 
                position.
                
        Returns:
            A list of all Slot instances within the radius.
        """
    
        raise NotImplementedError()
        
# Abstract Structure class
class AbstractStructure(MapStructure):
    def __init__(self, cfg):
        self._aquaculture_blocking_radius = \
            cfg.globals["aquaculture blocking radius"]
        self._aquaculture_damage_radius = \
            cfg.globals["aquaculture damage radius"]
        self._aquaculture_damage_proportion = \
            cfg.globals["aquaculture damage proportion"]
        
    def initialize_slots(self, width, height):
        raise NotImplementedError       
            
    def get_position(self, fun):
        for (x, y) in self.get_coordinates_list():
            if fun(x, y):
                return (x, y)
        return None
            
    def get_cell_position(self, cell):
        return self.get_position(lambda x, y: cell is self.slots[x][y])
        
    def get_occupant_position(self, occupant):
        return self.get_position(
            lambda x, y: occupant is self.slots[x][y].get_occupant()
        )
    
    def get_cell_distance(self, a, b):
        return self.get_distance(
            self.get_cell_position(a), 
            self.get_cell_position(b)
        )
        
    def get_occupants_distance(self, a, b):
        return self.get_distance(
            self.get_occupant_position(a),
            self.get_occupant_position(b)
        )
        
    def get_aquaculture_damage(self, cell):
        pos = self.get_cell_position(cell)
        cells = self.get_radius(self._aquaculture_damage_radius, pos)
        prop = self._aquaculture_damage_proportion
        max = self._aquaculture_damage_radius
        distances = {
            c: self.get_distance(pos, self.get_cell_position(c)) for c in cells
        }
        damage = {
            c: float(prop) * (max - distances[c]) / max for c in distances if 
                distances[c] <= self._aquaculture_damage_radius
        }
        damage[cell] = float(prop)
        return damage

    def get_aquaculture_blocking(self, cell):
        pos = self.get_cell_position(cell)
        return self.get_radius(self._aquaculture_blocking_radius, pos)
            
    def get_coordinates_list(self):
        """ Returns a list of all the coordinates in the structure """
        return [(x, y) for y in xrange(0, len(self.slots)) for x in 
            xrange(0, len(self.slots[y]))]
            
    def get_distance(self, (a_x, a_y), (b_x, b_y)):
        """Returns a floating-point number representing the distance in meter
           between the two positions."""
        raise NotImplementedError()
            
    def get_grid(self):
        """ Returns all slots as grid corresponding to real-world layout. """
        return self.slots

    def get_radius(self, r, pos):
        """ Returns all slots in a radius of r meters. """
        raise NotImplementedError()
        
    def get_size(self):
        """ Return size in (width, height) format. """
        return (len(self.slots), len(self.slots[0]))
        
    def get_all_slots(self):
        """ Return a list of all the slots """
        return [self.slots[x][y] for (x, y) in self.get_coordinates_list()]
        
    def get_positions_if_valid(self, positions):
        valid_positions = [(x, y) for (x, y) in positions if self.in_bounds(x, y)]
        return [self.slots[x][y] for (x, y) in valid_positions]
        
    def _get_at_offsets(self, o, x, y):
        """ Return a list of slots at the given offsets <o> from the point (x, y) """
        raise NotImplementedError
        
    def in_bounds(self, x, y):
        raise NotImplementedError
        
    def size(self):
        raise NotImplementedError

# FishingStructure to hold general method for initializing good fishing spots
class FishingStructure(AbstractStructure):
    def __init__(self, cfg, good_spot_frequency):
        AbstractStructure.__init__(self, cfg)
        self.cell_size = (cfg["cell width"], cfg["cell height"])
        self.initialize_slots(cfg["width"], cfg["height"])
        self.initialize_fishing_spots(good_spot_frequency)
        
    def initialize_slots(self, width, height):
        self.slots = [[Slot() for _ in xrange(width)] for _ in xrange(height)]

    def initialize_fishing_spots(self, good_spot_frequency):
        slots = self.get_all_slots()
        num_slots = len(slots)
        num_good_spots = good_spot_frequency * num_slots
        for s in random.sample(slots, int(num_good_spots)):
            s.set_fish_spawning()        

class GridStructure(FishingStructure):
    def in_bounds(self, x, y):
        w, h = self.get_size()
        return w > x >= 0 and h > y >= 0
        
    def get_distance(self, (a_x, a_y), (b_x, b_y)):
        cell_x, cell_y = self.cell_size
        return math.sqrt(
            ((b_x - a_x) * cell_x) ** 2 + 
            ((b_y - a_y) * cell_y) ** 2
        )
        
    def get_radius(self, r, (x, y)):
        sx, sy = self.cell_size
        offsets = [e for subl in [
            [(  0, yy), (  0, -yy), 
             ( xx, 0),  ( xx,  yy), ( xx, -yy),
             (-xx, 0),  (-xx,  yy), (-xx, -yy)] for 
                xx in xrange(1, r/sx + 1) for 
                yy in xrange(1, r/sy + 1)] for e in subl]  
        return self._get_at_offsets(offsets, x, y)
            
    def _get_at_offsets(self, o, x, y):
        return self.get_positions_if_valid([(x + X, y + Y) for (X, Y) in o])

# TorusStructure represents a kind of grid structure that wraps around both
# horizontally and vertically. That means the neighborhood and radius
# methods are different from GridStructure.
class TorusStructure(FishingStructure):
    def in_bounds(self, x, y):
        w, h = self.get_size()
        return w > x >= 0 and h > y >= 0

    def _absolute(self, x, y):
        w, h = self.get_size()
        return (x % w, y % h)
        
    def get_distance(self, (a_x, a_y), (b_x, b_y)):
        cell_x, cell_y = self.cell_size
        w, h = self.get_size()
        offsets = ((-w, -h), (-w, 0), (-w, h),
                   (0, -h),  (0, 0),  (0, h), 
                   (w, -h),  (w, 0),  (w, h))
        return min(math.sqrt(
            ((a_x - b_x + dx) * cell_x) ** 2 + 
            ((a_y - b_y + dy) * cell_y) ** 2
        ) for (dx, dy) in offsets)
    
    def get_radius(self, r, (x, y)):
        sx, sy = self.cell_size
        # In each direction
        offsets = [e for subl in [
            [(  0, yy), (  0, -yy), 
             ( xx, 0),  ( xx,  yy), ( xx, -yy),
             (-xx, 0),  (-xx,  yy), (-xx, -yy)] for 
                xx in xrange(1, r/sx + 1) for 
                yy in xrange(1, r/sy + 1)] for e in subl]        
        return self._get_at_offsets(offsets, x, y)
            
    def _get_at_offsets(self, o, x, y):
        return [self.slots[X][Y] for (X, Y) in
            [self._absolute(x + xx, y + yy) for (xx, yy) in o]]