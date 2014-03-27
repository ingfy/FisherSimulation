"""
    Data Objects for sending to/from user interface.
    
    The objects are pickable so that they can be sent between processes.
    Therefore they contain no logic except for static factory methods.
"""

import messages
import entities

## Objects to be sent through interface
## Are *Pickable* for multiprocessing
## Contains minimal logic

class Simulation(object):
    """Complete information about the simulation.
    
    Attributes:
        map:                The world map
        fishermen:          A list of fisherman agent objects        
        aquaculture_agents: A list of aquaculture agent objects
        civilians:          A list of civilians
        tourists:           A list of tourists
    """
    
    def __init__(self, map, fishermen, aquaculture_agents, civilians, tourists):
        self.map = map
        self.fishermen = fishermen
        self.aquaculture_agents = aquaculture_agents
        self.civilians = civilians
        self.tourists = touristss
        
    @classmethod
    def from_simulation_info(c, info):
        fishermen = info.directory.get_agents(type = entities.Fisherman)
        aquacultures = info.directory.get_agents(type = entities.Aquaculture)
        civilians = info.directory.get_agents(type = entities.Civilian)
        tourists = info.directory.get_agents(type = entities.Tourist)
        return c(
            Map.from_world_map(info.map),
            [Fisherman.from_object(f) for f in fishermen],
            [Aquaculture.from_object(a) for a in aquacultures],
            [Civilian.from_object(c) for c in civilians],
            [Tourist.from_object(t) for t in tourists]
        )
        
class WorkingAgent(object):
    """Working agents have names and capital.
    
    Attributes:
        name:       Unique identifier string
        capital:    Float representation of capital
    """
    def __init__(self, name, capital):
        self.name = name
        self.capital = capital
        
    @classmethod
    def from_object(c, object):
        return c(
            object.get_id(),
            object.get_capital()
        )
        
class Fisherman(WorkingAgent):
    pass
    
class Civilian(WorkingAgent):
    pass
    
class Tourist(WorkingAgent):
    pass
    
class Aquaculture(WorkingAgent):
    pass
        
class Map(object):
    """A structured container for all the cells in the world.
    
    Attributes:
        grid:   A two-dimensional list of cells
    """
    
    def __init__(self, grid):
        self.grid = grid
        
    @classmethod
    def from_world_map(c, world_map, cells=None):
        s = world_map.get_structure()
        return c([
            [Slot.from_world_slot(c) if cells is None or c in cells else None
                for c in r] 
            for r in s.get_grid()]
        )
        
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
        
class Message(object):
    """
    Public members:
        sender      String
        recipient   String
        contents    String
    """
    
    def __init__(self, sender, recipient, timestamp, contents):
        self.sender = sender
        self.recipient = recipient
        self.contents = contents
        self.timestamp = timestamp
        
    @classmethod
    def from_message(c, world_map, msg):
        return c(
            msg.metainfo.source, 
            msg.metainfo.target, 
            msg.metainfo.timestamp,
            msg.get_str_summary(world_map)
        )
        
class PhaseReport(object):
    """
    Public members:
        phase       String
        messages    List<String>
        map         Map
    """
    
    def __init__(self, phase, messages, map):
        self.phase = phase.name
        self.messages = messages
        self.map = map
        
    @classmethod
    def from_step_result(c, result):
        return c(
            result.phase,
            [Message.from_message(result.world_map, m) 
                for m in result.messages_sent],
            Map.from_world_map(result.world_map, cells=result.cells_changed)
        )