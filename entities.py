from agent import VotingAgent, PrioritizingAgent, CommunicatingAgent
import messages
import vote
import random
import nn
import plan
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
        
class ProducedAgent(VotingAgent, PrioritizingAgent, WorkingAgent):
    def __init__(self, directory, priorities):
        super(ProducedAgent, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        self._capital = 0
        
    def round_reset(self):
        self._capital = 0
        
# AquacultureSpawner

class AquacultureSpawner(object):
    def __init__(self):
        pass
        
    def choose_cell(self, world_map):
        return world_map.get_random_cell(predicate=lambda c: not c.is_blocked())
        
    def craete(self, factory, cell):
        return factory.aquaculture(cell)
        

        
# Handles the planning
class Municipality(CommunicatingAgent, PrioritizingAgent)
    pass
    
    def coastal_planning(self, world_map, previous_plan=None, complaints=None):
        plan = self.create_plan(world_map, previous_plan, complaints)
        self.distribute_plan(plan)
        
    def create_plan(self, world_map, plan=None, complaints=None):
        if plan is None:
            # If new plan, add all possible cells as aquaculture sites
            
            # TODO:
            #  Maybe divide into different kinds of areas first,
            #  maybe only 50% of the map for aquaculture.
            
            plan = {
                c: plan.AQUACULTURE
                    for c in world_map.get_all_cells()
                    if not c.is_blocked()
            }
        
        # Convert all cells that have approved complaints to
        # reserved zones.
        if not complaints is None:
            for c in complaints:
                if c.approved:
                    plan[c.cell] = plan.RESERVED_ZONE
                    
        return plan


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
        self._taxes = {}
        self._capital = 0.0
        
    def target_notification(self, message):
        self._target_message = message
        
    def new_vote_round(self):
        self._votes = {}
        
    def collect_tax(sender, amount):
        self.send_message(sender, messages.Inform(
            "Tax received %02.2f from %s" % (amount, sender.get_id())
        )
        self._capital += amount
        if sender in self._taxes:
            self._taxes[sender] += amount
        else:
            self._taxes[sender] = amount
            
    def distribute_taxes(self):
        benefit_agents = self._directory.get_agents(
            predicate=lambda a: a.is_community_member()
        )
        for a in benefit_agents:
            amount = self._capital / len(benefit_agents)
            a.give(amount)
            self.send_message(a, messages.Inform(
                "Tax benefit %02.2f to %s" % (amount, a.get_id())
            )
            
    def round_reset(self):
        self._capital = 0.0
        
    def vote(self, message):
        self._votes[message.metainfo.sender] = message.vote
        
        # Broadcast the vote
        self.broadcast_message(
            messages.VoteResponseInform.reply_to(message, self.get_directory())
        )
        
        # If all votes have been cast, make the decision
        #all_voters = self.get_directory().get_all_agents(exclude = self)
        if set(all_voters) == set(self._votes.keys()):
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

##
## NON-GOVERNMENT AGENTS: VOTERS, PRODUCEDAGENTS
##        
        
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
        self._slot_knowledge = {
            home_cell: home_cell.get_fish_quantity()
        }
        self._area_threatened = []
        self._home = home_cell
        self._fishing_efficiency = 1.0
        self.decision_mechanism = decision_mechanism or ga.FishermanNN(
            ga.FishermanNNGenotype.random()
        )
        
    def work(self):
        # find best slot
        best_cell = max(
            self._slot_knowledge.iterkeys(),
            key=lambda k: self._slot_knowledge[k] or 0
        )
        
        output = best_cell.get_fish_quantity() * self._fishing_efficiency
        
        # run output through market
        self._capital += output
        
        
    def vote_response_inform_notification(self, message):
        cell = message.vote_response.vote_call.target_message.cell
        if not cell in self._slot_knowledge:
            self._slot_knowledge[cell] = None

    def go_fish(self, world_map):
        return world_map.get_a_slot()
        
    def decide_vote(self, target_message):
        # complaint decision
        # returns vote.BUILD or vote.DONT_BUILD
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
        return vote.DONT_BUILD if
            self.decision_mechanism.get_output_values()["vote"] > 0.5
            else vote.BUILD  

class Aquaculture(ProducedAgent):
     def __init__(self, directory, priorities, home, decision_mechanism=None):
        ProducedAgent.__init__(self, directory, priorities)
        self._home = home
        self.decision_mechanism = decision_mechanism
        self._area_threatened = []
        self._capital = 0
        self._work_efficiency = 10
        self._taxation = 0.1
         
    def work(self):
        self._capital += self._work_efficiency
        
    def build(self):
        self._home.build_aquaculture(self)
        
    def get_location(self):
        return self._home
        
    def pay_taxes(self):
        government = self.directory.get_government()
        government.collect_tax(self, self._capital * self._taxation)
        
    def decide_vote(self, target_message):
        # complaint decision
        # returns vote.BUILD or vote.DONT_BUILD
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
        return vote.DONT_BUILD if
            self.decision_mechanism.get_output_values()["vote"] > 0.5
            else vote.BUILD
        
    def notify_government(self):
        government = self.get_directory().get_government()
        agent.send_message(messages.TargetArea(self._home), government)

# Signatures:
#

class Tourist(ProducedAgent):
    def work(self):
        pass
       
    def decide_vote(self, target_message):
       return vote.DONT_BUILD
    
# Signatures:
#

class Civilian(ProducedAgent):
    def work(self):
        pass
        
    def decide_vote(self, target_message):
        return vote.BUILD