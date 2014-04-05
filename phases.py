"""
Implementation of the overall simulation process, divided into steps.

Phases:
    CoastalPlanning
    Hearing
    GovernmentDecision
    Fishing
    Building
    Learning
"""


import vote
import priority
import entities
import plan

class Round(object):
    def __init__(self, info):
        LEARNING = Learning(info, None, "LEARNING")
        FISHING2 = Fishing(info, LEARNING, "FISHING2")
        BUILDING = Building(info, FISHING2, "BUILDING")
        FISHING1 = Fishing(info, BUILDING, "FISHING1")
        GOVDECISION = GovernmentDecision(info, None, "GOVDECISION")
        HEARING = Hearing(info, GOVDECISION, "HEARING")
        COASTPLAN = CoastalPlanning(info, HEARING, "COASTPLAN")
        GOVDECISION.set_next_table({ 
            plan.Decision.APPROVE: FISHING1, 
            plan.Decision.REVIEW: COASTPLAN 
        })
        self._current_step = self._start = COASTPLAN
        self._round_counter = 0
        
    def next(self):
        result = self._current_step.action()
        self._current_step = self._current_step.next()
        if self._current_step is None:
            self._round_counter += 1
            self._current_step = self._start
        return result        
        
    def current(self):
        return self._current_step.name
       
    def rounds(self):
        return self._round_counter
        
class StepResult(object):
    def __init__(self, phase, messages_sent, cells_changed, world_map):
        self.phase = phase
        self.messages_sent = messages_sent
        self.cells_changed = cells_changed
        self.world_map = world_map
        
    @classmethod
    def cells_changed(c, phase, cells_changed, world_map):
        return c(phase, [], cells_changed, world_map)
        
    @classmethod
    def no_cells_changed(c, phase, world_map):
        return c(phase, [], [], world_map)

## Abstract Step classes ##

class Step(object):
    def __init__(self, info, next, name):
        self.info = info
        self._next = next
        self.name = name

    def do(self):
        raise NotImplementedException()

    def next(self):
        return self._next

    def action(self):
        print self
        self.info.directory.start_recording()
        result = self.do()
        result.messages = self.info.directory.stop_recording()
        return result

class DecisionStep(Step):
    def __init__(self, info, next_table, name):
        Step.__init__(self, info, None, name)
        self.set_next_table(next_table)
        self._decision_value = None

    def set_next_table(self, next_table):
        self._next_table = next_table

    def action(self):
        self.info.directory.start_recording()
        (result, decision) = self.do()
        self.decide(decision)
        result.messages = self.info.directory.stop_recording()
        return result

    def decide(self, value):
        self._decision_value = value

    def next(self):
        return self._next_table[self._decision_value]


## Concrete Step Implementations ##

class CoastalPlanning(Step):
    def do(self):
        # first round reset
        for a in self.info.directory.get_agents():
            a.round_reset()
    
        municipality = self.info.directory.get_municipality()
        municipality.coastal_planning(
            self.info.map,
            self.info.directory.get_government().get_approved_complaints()
        )
        return StepResult.no_cells_changed(self, self.info.map)
    
class Hearing(Step):
    def do(self):
        self.info.directory.get_government().new_vote_round()
        for agent in self.info.directory.get_voting_agents():
            agent.hearing(self.info.map)
        return StepResult.no_cells_changed(self, self.info.map)
        
class GovernmentDecision(DecisionStep):
   def do(self):
        government = self.info.directory.get_government()
        decision = government.voting_decision()
        return (
            StepResult.no_cells_changed(self, self.info.map), decision
        )

class Fishing(Step):
    def do(self):
        # Agents do profit activities
        government = self.info.directory.get_government()
        working_agents = self.info.directory.get_agents(exclude = government)
        #for a in working_agents: a.work()
        
        # (Local) Aquaculture companies pay some of their revenue to locals
        # through taxation
        for a in self.info.directory.get_agents(type = entities.Aquaculture):
            a.pay_taxes()
        
        return StepResult.no_cells_changed(self, self.info.map)
        
class Building(Step):
    def do(self):
        government = self.info.directory.get_government()
        municipality = self.info.directory.get_municipality()
        licenses = government.distribute_licenses()
        spawner = self.info.aquaculture_spawner
        plan = municipality.get_plan()
        blocking_radius = 100
        affected_cells = []
        for license in licenses:
            location = spawner.choose_cell(plan)
            agent = spawner.create(
                self.info.agent_factory,
                location
            )            
            affected_cells.append(self.info.map.build_aquaculture(
                agent, 
                location, 
                blocking_radius
            ))
        return StepResult.cells_changed(
            self, affected_cells, self.info.map
        )
        
class Learning(Step):
    def do(self):
        for group in self.info.learning_mechanisms:
            self.info.learning_mechanisms[group].learn(self.info)
        
        return StepResult.no_cells_changed(self, self.info.map)