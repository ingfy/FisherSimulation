"""
    Data Objects for sending to/from user interface.
    
    The objects are pickable so that they can be sent between processes.
    Therefore they contain no logic except for static factory methods.
"""

import util
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
        self.tourists = tourists
        
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
            object.capital
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
        return c([
            [Slot.from_world_slot(d) if cells is None or d in cells else None
                for d in r] ###TODO::FIIIX
            for r in world_map.get_structure().get_grid()])
        
class Slot(object):
    """ 
    Public members:
        spawning        Boolean
        aquaculture     Boolean
        fisherman       Boolean
        land            Boolean
        blocked         Boolean
    """
    
    def __init__(self, spawning, aquaculture, fisherman, land, blocked):
        self.spawning = spawning
        self.aquaculture = aquaculture
        self.fisherman = fisherman
        self.land = land
        self.blocked = blocked
        
    def __str__(self):
        attributes_text = {
            "Land": self.land,
            "Spawn": self.spawning,
            "Aqltr": self.aquaculture,
            "Fisher": self.fisherman,
            "Blocked": self.blocked
        }
        return "CELL[%s]" % (
            ", ".join(
                ["%s: %s" % (key, "YES" if attributes_text[key] else "NO") 
                    for key in attributes_text])
        )
        
    @classmethod
    def from_world_slot(c, world_slot):
        occupant = world_slot.get_occupant()
        return c(
            world_slot.fish_spawning(),
            occupant is not None and occupant.__class__ is entities.Aquaculture,
            occupant is not None and occupant.__class__ is entities.Fisherman,
            world_slot.is_land(),
            world_slot.is_blocked()
        )
        
class Message(object):
    """Direct object representation of Message
    Attributes:
        sender:     String
        recipient:  String or None
        recipients: List of Strings or None
        contents:   String
        type:       String: "broadcast" or "single"
    """
        
    def __str__(self):
        recipient_line = ("Recipient: %s" % self.recipient) if \
            self.type == "single" else \
            ("Recipients:%s" % util.smart_line_sep(
                self.recipients, ", ", 100, "\n" + " "*12))
        return "Message:\n\t" + '\n\t'.join([
            "Type: %s"      % self.type     ,            
            "Sender: %s"    % self.sender   ,
            recipient_line                  ,
            "Time: %d"      % self.timestamp,
            "Contents: %s"  % self.contents
        ])
        
    @classmethod
    def from_message(c, world_map, msg):
        assert msg.metainfo.type in ["broadcast", "single"], \
            "Unknown message type: %s" % msg.metainfo.type        
        message = c()
        message.sender = msg.metainfo.source.get_id()
        message.type = msg.metainfo.type        
        if message.type == "broadcast":
            message.recipients = [a.get_id() for a in msg.metainfo.targets]
            message.recipient = None
        else:
            message.recipient = msg.metainfo.target
            message.recipients = None
        message.timestamp = msg.metainfo.timestmap
        message.contents = msg.get_str_summary(world_map)
        return message
        
class PhaseReport(object):
    """
    Public members:
        phase       String
        messages    List<String>
        map         Map
        new_round:  Boolean
        data:       A field where non-standard component data can be sent.
                    Used through the phases module.
    """
    
    @classmethod
    def from_step_result(c, result):
        obj = c()
        obj.phase = result.phase.name
        obj.messages = [Message.from_message(result.world_map, m) 
                            for m in result.messages]
        obj.map = Map.from_world_map(
            result.world_map, cells=result.cells_changed)
        obj.new_round = result.phase.name == "COASTPLAN"
        obj.data = result.data
        return obj