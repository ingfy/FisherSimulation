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
        
    def municipality(self):
        # TODO: municipality needs to have its own priorities
        return self._produce(Municipality, "government")
        
    def government(self):
        return self._produce(Government, "government")
        
    def tourist(self):
        return self._produce(Tourist, "tourist")
        
    def civilian(self):
        return self._produce(Civilian, "civilian")
        
# Base for all the non-government, non municipality agents:
#  Fishermen, aquaculture owners, civilians and tourists
class ProducedAgent(VotingAgent, PrioritizingAgent, WorkingAgent):
    def __init__(self, directory, priorities):
        super(ProducedAgent, self).__init__()
        self.register(directory, self.__class__, voting=True)
        self.set_priorities(priorities)
        self._capital = 0
        self.threats = []
        
    def get_capital(self):
        return self._capital
        
    def target_notification(self, message):
        self.threats.add(message)        
        
    def hearing(self):
        for target_message in self._threats:
            vote = self.decide_vote(target_message)
            self.send_message(
                self.get_directory().get_government(),
                messages.VoteResponse.reply_to(
                    target_message, 
                    self.get_directory()                    
                    vote
                )
            )
        
    def round_reset(self):
        self._capital = 0
        
# AquacultureSpawner

class AquacultureSpawner(object):
        
    def choose_cell(self, plan):
        # Maybe it should choose the best cell based on public information
        return random.choice(plan.aquaculture_sites())
        
    def create(self, factory, cell):
        return factory.aquaculture(cell)

        
# Handles the planning
class Municipality(CommunicatingAgent, PrioritizingAgent)
    def __init__(self, directory, priorities, decision_mechanism=None):
        super(Municipality, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        self._decision_mechanism = decision_mechanism     
        self._taxes = {}
        self._capital = 0.0
        self._plan = plan
        
    def round_reset(self):
        self._capital = 0.0
    
    def collect_tax(sender, amount):
        self.send_message(sender, messages.Inform(
            "Tax received %02.2f from %s" % (amount, sender.get_id())
        )
        self._capital += amount
        if not sender in self._taxes:
            self._taxes[sender] = []
        self._taxes[sender].add(amount)
            
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
    
    def coastal_planning(self, world_map, complaints=None):
        self.create_plan(world_map, complaints)
        self.distribute_plan()
        
    def create_plan(self, world_map, complaints=None):
        if self._plan is None:
            # If new plan, add all possible cells as aquaculture sites
            
            # TODO:
            #  Maybe divide into different kinds of areas first,
            #  maybe only 50% of the map for aquaculture.
            
            self._plan = plan.CoastalPlan({
                c: plan.AQUACULTURE_SITE
                    for c in world_map.get_all_cells()
                    if not c.is_blocked()
            })
        
        # Convert all cells that have approved complaints to
        # reserved zones.
        if not complaints is None:
            for c in complaints:
                if c.approved:
                    self._plan[c.cell] = plan.RESERVED_ZONE
                    
    def get_plan(self):
        return self._plan
        
    def distribute_plan(self):
        # Send a message to all interested parties
        for a in self.get_directory().get_agents(voting_only=True):
            for cell in self._plan:
                if self._plan[cell] == plan.AQUACULTURE_SITE:
                    self.send_message(a, messages.TargetArea(
                        messages.MetaInfo(
                            self, a, self.get_directory().get_timestamp()
                        ),
                        cell
                    )

class ComplaintApproveMoreThanOne(object):
    def set_input_values(self, values):
        assert "num_votes" in values, "Expected number of votes <num_votes>."
        self._num_votes = values["num_votes"]
        
    def process(self):
        # If more than one vote, approve complaint
        self._approved = 1 if self._num_votes > 1 else 0
        
    def get_output_values(self):
        return {"approve": self._approved}
        
class License(object):
    pass

# Signatures:
#   <>  handle_complaint(fisherman, cell, aquaculture)

# Handles complaints to the plan
class Government(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, priorities, decision_mechanism=None):
        self._complaints = {}
        super(Government, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        self._decision_mechanism = decision_mechanism or
            ComplaintApproveMoreThanOne()
        self._licenses = []
        
    def distribute_licenses(self):
        num_licenses = 5
        self._licenses = [License() for _ in xrange(num_licenses)]
        return self._licenses
        
    def new_vote_round(self):
        self._complaints = {}
            
    def round_reset(self):
        self.new_vote_round()
        
    def vote(self, message):
        cell = message.get_cell()
        if message.vote == vote.DISAPPROVE:
            complaint = plan.Complaint(cell)
            if not cell in self._complaints:
                self._complaints[cell] = complaint
            else:
                self._complaints[cell].add()
        
        # Broadcast the vote
        self.broadcast_message(
            messages.VoteResponseInform.reply_to(message, self.get_directory())
        )        
        
    def voting_decision(self):
        all_voters = self.get_directory().get_all_agents(exclude = self)
        assert set(all_voters) == set(self._votes.keys()),
            "Unexpected number of votes. Ensure that all votes are cast."
        for cell in self._complaints:
            self._decision_mechanism.set_input_values({
                "num_votes": self._complaints[cell].num
            })
            self._decision_mechanism.process()
            self._complaints[cell].approved = 
                self._decision_mechanism.get_output_values()["approve"] > 0.5
        
        return plan.Decision.REVIEW 
            if len(self.get_approved_complaints()) > 0
            else plan.Decision.APPROVE

    def get_approved_complaints(self):
        return [c for c in self._complaints if c.approved]
        
    def call_vote(self):
        # Outdated maybe
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
    def __init__(self, directory, priorities, home_cell, world_map, radius):
        ProducedAgent.__init__(self, directory, priorities)
        self._priority_slots = Tourist.calculate_priority_slots(
            radius, world_map, home_cell
        )
        
    def get_priority_slots(self):
        return self._priority_slots

    def work(self):
        pass
       
    def decide_vote(self, target_message):
       return vote.DONT_BUILD
       
    @staticmethod
    def calculate_priority_slots(care_radius, world_map, home_cell):
        return world_map.get_radius_from(home_cell, care_radius)
        
    
# Signatures:
#

class Civilian(ProducedAgent):
    def __init__(self, directory, priorities):
        ProducedAgent.__init__(self, directory, priorities)

    def work(self):
        pass
        
    def decide_vote(self, target_message):
        return vote.BUILD