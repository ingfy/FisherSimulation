from agent import CommunicatingAgent, PrioritizingAgent

class AgentFactory(object):
    def __init__(self, directory, cfg):
        self._directory = directory
        self._cfg = cfg
        
    def _produce(self, type, cfg_key):
        return type(self._directory, self._cfg[cfg_key]["priorities"])
    
    def fisherman(self):
        return self._produce(Fisherman, "fisherman")
        
    def aquaculture(self):
        return self._produce(Aquaculture, "aquaculture")
        
    def government(self):
        return self._produce(Government, "government")
        
    def tourist(self):
        return self._produce(Tourist, "tourist")
        
    def civilian(self):
        return self._produce(Civilian, "civilian")
        
class ProducedAgent(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, priorities):
        super(ProducedAgent, self).__init__()
        self.register(directory, ProducedAgent)
        for p in priorities:
            self.set_priority(p, priorities[p])

# Fisherman:
#   <list<slot>>    get_knowledge()
#                   add_knowledge(<slot>)
#   <slot>          go_fish(world_map)      Use knowledge to
#                                           decide a fishing
#                                           spot from the map

class Fisherman(ProducedAgent):
    _state = 0
    _slot_knowledge = set([])

    def add_knowledge(self, info):
        self._slot_knowledge.add(info)

    def get_knowledge(self):
        return list(self._slot_knowledge)

    def go_fish(self, world_map):
        return world_map.get_a_slot()

    def __str__(self):
        return self.get_id()

# Signatures:
#   <bool>  handle_complaint(fisherman, coordinates, aquaculture)

class Government(ProducedAgent):
    def handle_complaint(self, fisherman, coordinates, aquaculture):
        pass


# Signatures:
# <coordinates> pursue_spot(self, world_map)

class Aquaculture(ProducedAgent):
    def pursue_spot(self, world_map):
        return (0, 0)


# Signatures:
#

class Tourist(ProducedAgent):
    pass
    
# Signatures:
#

class Civilian(ProducedAgent):
    pass