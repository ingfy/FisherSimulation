"""Defines the concrete entities used in the simulation."""

import random

from FisherSimulation.agent import VotingAgent
from FisherSimulation.agent import PrioritizingAgent
from FisherSimulation.agent import CommunicatingAgent
from FisherSimulation.agent import WorkingAgent
from FisherSimulation import messages
from FisherSimulation import vote
from FisherSimulation import plan
from FisherSimulation import decisions

class AgentFactory(object):
    def __init__(self, directory, cfg):
        self._directory = directory
        self._cfg = cfg

    def fisherman(self, home_cell):
        return Fisherman(self._directory, self._cfg["fisherman"], home_cell)

    def aquaculture(self, home_cell):
        return Aquaculture(self._directory, self._cfg["aquaculture"], home_cell)

    def municipality(self):
        return Municipality(self._directory, self._cfg["municipality"])

    def government(self):
        return Government(self._directory, self._cfg["government"])

    def tourist(self, home_cell, world_map, radius):
        cells = Tourist.calculate_priority_slots(radius, world_map, home_cell)
        return Tourist(self._directory, self._cfg["tourist"], home_cell, cells)

    def civilian(self):
        return self.Civilian(self._directory, self._cfg["civilian"])

class ProducedAgent(VotingAgent, PrioritizingAgent, WorkingAgent):
    """Base class for aquaculture, fisherman, civilian and tourist agents.

    Attributes:
        slot_knowledge:     A dictionary mapping of cell to fishing quality
                            (float).
        decision_mechanism: An object implementing the
                            vote.VotingDecisionMechanism interface.
        capital:            A float representing the amount of money the agent
                            has.
    """

    def __init__(self, directory, cfg):
        super(ProducedAgent, self).__init__()
        self.register(directory, self.__class__, voting=True)
        self.set_priorities(cfg["priorities"])
        self.capital = 0
        self.slot_knowledge = {}
        self.decision_mechanism = None
        self._guess_mean = 0.6
        self._num_max_complaints = cfg.globals["num max complaints"]
        self._guess_stdev = 0.1
        self._plan_message = None

    # Abstract methods
    def work(self):
        raise NotImplementedError()

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

    def hearing(self, world_map):
        votes = self.decide_votes(self._plan_message.plan, world_map)
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

    def decide_votes(self, plan, world_map):
        return self.decision_mechanism.decide_votes(self, plan, world_map,
            self._num_max_complaints)

# AquacultureSpawner

class AquacultureSpawner(object):
    def __init__(self, voting_mechanism_class, config, aquaculture_in_blocked,
            map):
        self.map = map
        self.voting_mechanism_class = voting_mechanism_class
        self._aquaculture_in_blocked = aquaculture_in_blocked
        self.config = config

    def choose_cell(self, plan):
        # Maybe it should choose the best cell based on public information
        sites = plan.aquaculture_sites() if self._aquaculture_in_blocked \
            else [c for c in plan.aquaculture_sites() if not c.is_blocked()]
        try:
            return random.choice(sites)
        except IndexError:  # no aquaculture sites left
            return None

    def create(self, factory, cell):
        agent = factory.aquaculture(cell)
        self.voting_mechanism_class.new(agent, self.config, self.map)
        return agent

# Handles the planning
class Municipality(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, cfg):
        super(Municipality, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(cfg["priorities"])
        self.decision_mechanism = None
        self._taxes = {}
        self._cfg = cfg
        self._planning_mechanism = cfg["planning mechanism class"](cfg)
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
        self._plan = self._planning_mechanism.create_plan(
            world_map, self._plan, complaints
        )

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

class License(object):
    pass

# Signatures:
#   <>  handle_complaint(fisherman, cell, aquaculture)

# Handles complaints to the plan
class Government(CommunicatingAgent, PrioritizingAgent):
    def __init__(self, directory, cfg):
        self._complaints = {}
        super(Government, self).__init__()
        self.register(directory, self.__class__)
        self.set_priorities(cfg["priorities"])
        self._decision_mechanism = cfg["decision mechanism class"](cfg)
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
        self._decision_mechanism.round_reset()

    def vote(self, message):
        for v in message.votes:
            cell = v.cell
            if v.value == vote.DISAPPROVE:
                if not cell in self._complaints:
                    self._complaints[cell] = plan.Complaint(v)
                else:
                    self._complaints[cell].add(v)

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

    def voting_decision(self):
        self._complaints = self._decision_mechanism.decision(self._complaints)
        return plan.Decision.REVIEW if len(self.get_approved_complaints()) > 1 \
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
    def __init__(self, directory, cfg, home_cell):
        ProducedAgent.__init__(self, directory, cfg)
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

    def __init__(self, directory, cfg, home):
        ProducedAgent.__init__(self, directory, cfg)
        self.home = home
        self.slot_knowledge[home] = home.get_fish_quantity()
        self._work_efficiency = cfg["work efficiency"]
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

    def pay_taxes(self):
        municipality = self.get_directory().get_municipality()
        municipality.collect_tax(self, self.capital * self._taxation)

# Signatures:
#

class Tourist(ProducedAgent):
    """Tourist implementation.

    Attributes:
        priority_slots: A list of cells that the agent would prefer to not have
                        aquaculture built on.
    """
    def __init__(self, directory, cfg, home_cell, prioritized_slots):
        ProducedAgent.__init__(self, directory, cfg)
        self.home = home_cell
        self.priority_slots = prioritized_slots

    def work(self):
        pass

    @staticmethod
    def calculate_priority_slots(care_radius, world_map, home_cell):
        return world_map.get_radius_from(home_cell, care_radius)


# Signatures:
#

class Civilian(ProducedAgent):
    def __init__(self, directory, cfg):
        ProducedAgent.__init__(self, directory, cfg)

    def work(self):
        pass