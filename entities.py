from agent import CommunicatingAgent, PrioritizingAgent

# Fisherman:
#   <list<slot>>    get_knowledge()
#                   add_knowledge(<slot>)
#   <slot>          go_fish(world_map)      Use knowledge to
#                                           decide a fishing
#                                           spot from the map

class Fisherman(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, priorities=None):
        super(Fisherman, self).__init__()
        self._state = 0
        self._slot_knowledge = set([])
        if not priorities is None:
            for p, v in priorities:
                self.set_priority(p, v)

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

class Government(CommunicatingAgent, PrioritizingAgent):
    def handle_complaint(self, fisherman, coordinates, aquaculture):
        pass


# Signatures:
# <coordinates> pursue_spot(self, world_map)

class Aquaculture(CommunicatingAgent, PrioritizingAgent):
    def __init__(self):
        pass

    def pursue_spot(self, world_map):
        return (0, 0)

