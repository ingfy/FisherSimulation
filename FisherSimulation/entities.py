from agent import VotingAgent, PrioritizingAgent, CommunicatingAgent, WorkingAgent
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
        

class ProducedAgent(VotingAgent, PrioritizingAgent, WorkingAgent):
    """Base class for aquaculture, fisherman, civilian and tourist agents.
    
    Attributes:
        slot_knowledge:     A dictionary mapping of cell to fishing quality 
                            (float).
        threats:            A list of cells that are threatened by aquaculture.
        decision_mechanism: An object implementing the 
                            vote.VotingDecisionMechanism interface.
        capital:            A float representing the amount of money the agent
                            has.
    """
    
    def __init__(self, directory, priorities):
        super(ProducedAgent, self).__init__()
        self.register(directory, self.__class__, voting=True)
        self.set_priorities(priorities)
        self.capital = 0
        self.slot_knowledge = {}
        self.threats = []
        self.decision_mechanism = None
        self._guess_mean = 0.6
        self._guess_stdev = 0.1
        self._plan_message = None
    
    # Abstract methods
    def work(self):
        raise NotImplementedException()

    # Concrete methods
    def round_reset(self):
        self.capital = 0        
        
    def add_voting_mechanism(self, mechanism):
        self.decision_mechanism = mechanism        
        
    def plan_hearing_notification(self, message):
        self._plan_message = message
        
    def estimate_cell_quality(self, cell):
        return random.gauss(self._guess_mean, self._guess_stdev)
        
    def vote_response_inform_notification(self, message):
        for v in [c for c in message.reply_to.votes if c.is_complaint()]:
            cell = v.cell
            if not cell in self.slot_knowledge:
                self.slot_knowledge[cell] = self.estimate_cell_quality(cell)
        
    def hearing(self, world_map, num_max_complaints):        
        votes = self.decide_votes(self._plan_message.plan, world_map, 
            num_max_complaints)
        gov = self.get_directory().get_government()
        self.send_message(
            gov,
            messages.VoteResponse(
                messages.MetaInfo(self, gov),
                self._plan_message,
                votes
            )
        )
        return votes
        
    def decide_votes(self, plan, world_map, num_max_complaints):
        return self.decision_mechanism.decide_votes(self, plan, world_map, 
            num_max_complaints)    
        
        
# AquacultureSpawner

class AquacultureSpawner(object):
    def __init__(self, voting_mechanism_class, config, map):
        self.map = map
        self.voting_mechanism_class = voting_mechanism_class
        self.config = config
    
    def choose_cell(self, plan):
        # Maybe it should choose the best cell based on public information
        try:
            return random.choice(plan.aquaculture_sites())
        except IndexError:  # no aquaculture sites left
            return None
        
    def create(self, factory, cell):
        agent = factory.aquaculture(cell)
        self.voting_mechanism_class.new(agent, self.config, self.map)
        return agent

        
# Handles the planning
class Municipality(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, priorities, decision_mechanism=None):
        super(Municipality, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(priorities)
        self.decision_mechanism = decision_mechanism     
        self._taxes = {}
        self.capital = 0.0
        self._plan = None
        
    def round_reset(self):
        self.capital = 0.0
        self._plan = None
    
    def collect_tax(self, sender, amount):
        self.send_message(sender, messages.Inform(
            messages.MetaInfo(self, sender),
            "Tax received %02.2f from %s" % (amount, sender.get_id())
        ))
        self.capital += amount
        if not sender in self._taxes:
            self._taxes[sender] = []
        self._taxes[sender].append(amount)
            
    def distribute_taxes(self):
        benefit_agents = self.get_directory().get_agents(
            predicate=lambda a: a.is_community_member()
        )
        for a in benefit_agents:
            amount = self.capital / len(benefit_agents)
            self.capital -= amount
            a.give(amount)
            self.send_message(a, messages.Inform(
                messages.MetaInfo(self, a),
                "Tax benefit %02.2f to %s" % (amount, a.get_id())
            ))
    
    def coastal_planning(self, world_map, complaints=None):
        self.create_plan(world_map, complaints)
        self.distribute_plan()
        return self._plan
        
    def create_plan(self, world_map, complaints=None):
        if self._plan is None:
            # If new plan, add all possible cells as aquaculture sites
            
            # TODO:
            #  Maybe divide into different kinds of areas first,
            #  maybe only 50% of the map for aquaculture.
            self._plan = plan.CoastalPlan({
                c: plan.AQUACULTURE_SITE
                    for c in world_map.get_all_cells()
                        if not c.has_aquaculture()
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
        recipients = self.get_directory().get_agents(only_voters=True)
        self.broadcast_message(
            messages.PlanHearing(
                messages.BroadcastMetaInfo(self, recipients),
                self._plan
            )
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
        self._decision_mechanism = \
            decision_mechanism or ComplaintApproveMoreThanOne()
        self._licenses = []
        self.hearing_count = 0
        self.max_hearing_count = 3
        
    def distribute_licenses(self):
        num_licenses = 5
        self._licenses = [License() for _ in xrange(num_licenses)]
        return self._licenses
        
    def new_vote_round(self):
        self._complaints = {}
            
    def round_reset(self):
        self.new_vote_round()
        self.hearing_count = 0
        
    def vote(self, message):
        for v in message.votes:
            cell = v.cell
            if v.value == vote.DISAPPROVE:
                if not cell in self._complaints:
                    self._complaints[cell] = plan.Complaint(cell)
                else:
                    self._complaints[cell].add()
            
        # Broadcast the votes
        broadcast_recipients = self.get_directory().get_agents(
            only_voters=True
        )
        self.broadcast_message(
            messages.VoteResponseInform(
                messages.BroadcastMetaInfo(self, broadcast_recipients),
                message
            )
        )
        
    def voting_decision(self, max_hearing_rounds):
        if self.hearing_count >= max_hearing_rounds:
            return plan.Decision.APPROVE
            
        self.hearing_count += 1
        all_voters = self.get_directory().get_agents(exclude = self)
        for cell in self._complaints:
            self._decision_mechanism.set_input_values({
                "num_votes": self._complaints[cell].num
            })
            self._decision_mechanism.process()
            self._complaints[cell].approved = \
                self._decision_mechanism.get_output_values()["approve"] > 0.5
        
        return plan.Decision.REVIEW \
            if len(self.get_approved_complaints()) > 0 \
            else plan.Decision.APPROVE

    def get_approved_complaints(self):
        return [self._complaints[s] for s in 
            self._complaints if self._complaints[s].approved]

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
    """The specific implementation of a Fisherman.
    
    Attributes:
        home:   A cell where the agent prioritizes to work.
    """
    def __init__(self, directory, priorities, home_cell):
        ProducedAgent.__init__(self, directory, priorities)
        self.home = home_cell
        self.first_home = self.home #TODO:DELETE
        self.home.populate(self)
        self._fishing_efficiency = 1.0
        self.slot_knowledge[home_cell] = home_cell.get_fishing_efficiency()
        
    def find_fishing_spot(self, world):
        sorted_known = sorted(
            self.slot_knowledge.iterkeys(),
            key = lambda k: self.slot_knowledge[k] or 0,
            reverse=True
        )
        
        #print self.first_home in sorted_known
        #print self.slot_knowledge[self.first_home]
        #print [(c,self.slot_knowledge[c]) for c in sorted_known]
        
        all_cells = world.get_all_cells()
        shuffled_world = random.sample(all_cells, len(all_cells))
        
        cell = next(
            (cell for cell in sorted_known if not cell.is_blocked()), 
            None
        )
        
        if cell is None or self.slot_knowledge[cell] < 0.5: # base value
            # If we have no knowledge of any unblocked cells, OR
            # every cell has a known output lower than 0.5, try a different
            # cell in the world.
            cell = next(
                (cell for cell in shuffled_world if not cell.is_blocked()), 
                None
            )
        
        if not cell is None:
            # change home
            # if not occupied
            self.home.remove(self)
            cell.populate(self)
            self.home = cell
    
    def work(self):    
        # run through market?
        output = self.home.get_fishing_efficiency() * self._fishing_efficiency        
        
        # quantity updated
        self.slot_knowledge[self.home] = self.home.get_fishing_efficiency()
        
        self.capital += output
        

class Aquaculture(ProducedAgent):
    """Aquaculture agent implementation.
    
    Attributes:
        home:   A cell where the agent is located.
    """

    def __init__(self, directory, priorities, home, decision_mechanism=None):
        ProducedAgent.__init__(self, directory, priorities)
        self.home = home
        self.slot_knowledge[home] = home.get_fish_quantity()
        self._work_efficiency = 10
        self._taxation = 0.1
        # broadcast arrival
        self.broadcast_message(
            messages.AquacultureSpawned(
                messages.BroadcastMetaInfo(
                    self,
                    self.get_directory().get_agents(
                        predicate=lambda e: e is not self
                    )
                ),
                self.home
            )
        )
         
    def work(self):
        self.capital += self._work_efficiency
        
    def build(self):
        self._home.build_aquaculture(self)        
        
    def pay_taxes(self):
        municipality = self.get_directory().get_municipality()
        municipality.collect_tax(self, self.capital * self._taxation)
        
    def notify_government(self):
        government = self.get_directory().get_government()
        agent.send_message(messages.TargetArea(self._home), government)

# Signatures:
#

class Tourist(ProducedAgent):
    """Tourist implementation.
    
    Attributes:
        priority_slots: A list of cells that the agent would prefer to not have
                        aquaculture built on.
    """
    def __init__(self, directory, priorities, home_cell, world_map, radius):
        ProducedAgent.__init__(self, directory, priorities)
        self.priority_slots = Tourist.calculate_priority_slots(
            radius, world_map, home_cell
        )

    def work(self):
        pass
       
    def decide_votes(self, plan):
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
        
    def decide_votes(self, plan):
        return vote.BUILD