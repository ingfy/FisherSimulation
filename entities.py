from agent import VotingAgent, PrioritizingAgent, CommunicatingAgent
import messages
import random
import nn
import ga

class AgentFactory(object):
    def __init__(self, directory, cfg):
        self._directory = directory
        self._cfg = cfg
        
    def _produce(self, type, cfg_key):
        return type(self._directory, self._cfg[cfg_key]["priorities"])
    
    def fisherman(self, home_cell):
        return Fisherman(self._directory, self._cfg["fisherman"]["priorities"], home_cell)
        
    def aquaculture(self):
        return self._produce(Aquaculture, "aquaculture")
        
    def government(self):
        return self._produce(Government, "government")
        
    def tourist(self):
        return self._produce(Tourist, "tourist")
        
    def civilian(self):
        return self._produce(Civilian, "civilian")
        
class ProducedAgent(VotingAgent, PrioritizingAgent):
    def __init__(self, directory, priorities):
        super(ProducedAgent, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        
# AquacultureSpawner

class AquacultureSpawner(object):
    def __init__(self):
        pass
        
    def choose_cell(self, world_map):
        cells = world_map.get_structure().get_all_slots()
        return random.choice(cells)

# Fisherman:
#   <list<slot>>    get_knowledge()
#                   add_knowledge(<slot>)
#   <slot>          go_fish(world_map)      Use knowledge to
#                                           decide a fishing
#                                           spot from the map

class Fisherman(ProducedAgent):
    def __init__(self, directory, priorities, home_cell, decision_mechanism = None):
        ProducedAgent.__init__(self, directory, priorities)
        self._state = 0
        self._slot_knowledge = set([home_cell])
        self._areas_threatened = set([])
        self._home = home_cell
        self.decision_mechanism = decision_mechanism or ga.FishermanNN(
            ga.FishermanNNGenotype.random()
        )

    def add_knowledge(self, info):
        self._slot_knowledge.add(info)

    def get_knowledge(self):
        return list(self._slot_knowledge)

    def go_fish(self, world_map):
        return world_map.get_a_slot()
        
    def message_area_targeted(self, sender, msg):
        self._areas_threatened.add(msg.cell)
        if self.decide_complain(msg):
            self.send_message(
                self.directory.get_government(), 
                messages.Complaint(msg.metainfo.reply(), msg)
            )
                
    def decide_complaint(self, target_message):
        # complaint decision
        # returns True if complain, otherwise False
        self.decision_mechanism.set_input_values({
            "distance":             world_map.get_structure()
                                        .get_cell_distance(self._home, 
                                            target_message.cell),
            "home conditions":      self._home.get_fish_quantity(),
            "targeted conditions":  target_message.cell.get_fish_quantity() if 
                                        target_message.cell in 
                                            self._slot_knowledge
                                        else 0.0
        })
        self.decision_mechanism.process()
        return self.decision_mechanism.get_output_values()["vote"] > 0.5        

# Signatures:
#   <>  handle_complaint(fisherman, cell, aquaculture)

class Government(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, priorities):
        self._complaints = {}
        super(Government, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)

    def handle_complaint(self, fisherman, cell, aquaculture):
        if cell in self._complaints:
            if fisherman in self._complaints[cell]:
                # Have received complaints on same cell from same
                # fisherman before.
                pass
            else:
                pass
                # Have received complaints from other fishermen
                # about the same spot
            # Several complaints
        else:
            # First complaint about spot
            self._complaints[cell] = [fisherman]


# Signatures:
# <cell> pursue_spot(self, world_map)

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