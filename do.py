"""
    do.py
    Data Objects for sending to/from user interface
"""

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
    def from_world_map(c, world_map cells=None):
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
    def __init__(self, phase, messages, map):
        self.phase = phase.name
        self.messages = messages
        self.map = map
        
    @classmethod
    def from_step_result(c, result, world_map):
        return c(
            result.phase,
            [Message.from_message(world_map, m) for m in result.messages_sent],
            Map.from_world_map(world_map, cells=result.cells_changed)
        )