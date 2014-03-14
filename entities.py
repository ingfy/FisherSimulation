from agent import VotingAgent, PrioritizingAgent, CommunicatingAgent
import messages
import vote
import random
import nn
import ga

class AgentFactory(object):
    def __init__(self, directory, cfg):
        self._directory = directory
        self._cfg = cfg
        
    def _produce(self, type, cfg_key):
        return type(self._directory, self._cfg[cfg_key]["priorities"])
        
    def _produce_home(self, type, cfg_key, home):
        return type(self._directory, self._cfg[cfg_key]["priorities"], home)
    
    def fisherman(self, home_cell):
        return self._produce_home(Fisherman, "fisherman", home_cell)
        
    def aquaculture(self, home_cell):
        return self._produce_home(Aquaculture, "aquaculture", home_cell)
        
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
        return world_map.get_random_cell(lambda c: not c.is_blocked())
        
    def craete(self, factory, cell):
        return factory.aquaculture(cell)        

# Fisherman:
#   <list<slot>>    get_knowledge()
#                   add_knowledge(<slot>)
#   <slot>          go_fish(world_map)      Use knowledge to
#                                           decide a fishing
#                                           spot from the map

class Fisherman(ProducedAgent):
    def __init__(self, directory, priorities, home_cell, decision_mechanism=None):
        ProducedAgent.__init__(self, directory, priorities)
        self._state = 0
        self._slot_knowledge = set([home_cell])
        self._area_threatened = None
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
        
    def vote_call_notification(self, message):
        self._areas_threatened.add(message.target_message.cell)
        complain = self.decide_complain(message.target_mesasge)
        self.send_message(
            self.directory.get_government(),
            messages.VoteResponse.reply_to(
                message, 
                self.get_directory(),
                vote.DONT_BUILD if complain else vote.BUILD)
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
    def __init__(self, directory, priorities, decision_mechanism=None):
        self._complaints = {}
        super(Government, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        self._decision_mechanism = decision_mechanism
        self._target_message = None
        self._broadcast_location_mode = "immediately"
        
    def target_notification(self, message):
        self._target_message = message
        
    def new_vote_round(self):
        self._votes = {}
        
    def vote(self, message):
        self._votes[message.metainfo.sender] = message.vote
        
        # Broadcast the vote
        self.broadcast_message(
            messages.VoteResponseInform.reply_to(message, self.get_directory())
        )
        
        # If all votes have been cast, make the decision
        #all_voters = self.get_directory().get_all_agents(exclude = self)
        #if set(all_voters) == set(self._votes.keys()):
            self.voting_decision()
        
    def voting_decision(self):
        all_voters = self.get_directory().get_all_agents(exclude = self)
        assert set(all_voters) == set(self._votes.keys()),
            "Unexpected number of votes. Ensure that all votes are cast."
        pass
        
    def call_vote(self):
        """
        Send call for vote to all agents
        """
        self.broadcast_message(
            messages.VoteCall.reply_to(
                self._target_message, 
                self.get_directory()
            )
        )


class Aquaculture(ProducedAgent):
     def __init__(self, directory, priorities, home, decision_mechanism=None):
        ProducedAgent.__init__(self, directory, priorities)
        self._home = home
        self.decision_mechanism = decision_mechanism
        self._area_threatened = None
        
     def vote_call_notification(self, message):
        self._areas_threatened.add(message.target_message.cell)
        complain = self.decide_vote(message.target_mesasge)
        self.send_message(
            self.directory.get_government(),
            messages.VoteResponse.reply_to(
                message, 
                self.get_directory(),
                vote.DONT_BUILD if complain else vote.BUILD)
        )
        
    def notify_government(self):
        government = self.get_directory().get_government()
        agent.send_message(messages.TargetArea(self._home), government)

# Signatures:
#

class Tourist(ProducedAgent):
    pass
    
# Signatures:
#

class Civilian(ProducedAgent):
    pass