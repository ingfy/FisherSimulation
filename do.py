import messages

## Objects to be sent through interface
## Are *Pickable* for multiprocessing
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
    def __init__(self, phase, messages, world_map):
        self.phase = phase.name
        self.messages = [Message.from_message(world_map, m) for m in messages]