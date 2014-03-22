import vote
import priority
import entities

class Round(object):
    def __init__(self, info):
        LEARNING = Learning(info, None, "LEARNING")
        FISHING2 = Fishing(info, LEARNING, "FISHING2")
        BUILDING = Building(info, FISHING2, "BUILDING")
        FISHING1 = Fishing(info, BUILDING, "FISHING1")
        GOVDECISION = GovernmentDecision(info, None, "GOVDECISION")
        HEARING = Hearing(info, GOVDECISION, "HEARING")
        COASTPLAN = CoastalPlanning(info, Hearing, "SPAWNING")
        GOVDECISION.set_next_table({ 
            plan.Decision.APPROVE: FISHING1, 
            vote.Decision.REVIEW: COASTPLAN 
        })
        self._current_step = self._start = SPAWNING
        self._round_counter = 0
        
    def next(self):
        self._current_step = self._current_step.next()
        if self._current_step is None:
            self._round_counter += 1
            self._current_step = self._start
        result = self._current_step.action()
        return result
       
    def rounds(self):
        return self._round_counter
        
class StepResult(object):
    def __init__(self, phase, messages_sent, cells_changed)
        self.phase = phase
        self.messages_sent = messages_sent
        self.cells_changed = cells_changed
        
    @classmethod
    def cells_changed(c, phase, cells_changed):
        return c(phase, [], cells_changed)
        
    @classmethod
    def no_cells_changed(c, phase):
        return c(phase, [], [])
        
class Step(object):
    def __init__(self, info, next, name):
        self._info = info
        self._next = next
        self.name = name
        
    def action(self):
        raise NotImplementedException()
        
    def next(self):
        return self._next
        
    def action(self):
        self._info.directory.start_recording()
        result = self.do()
        result.messages = self._info.directory.start_recording()
        return result
        
class DecisionStep(Step):
    def __init__(self, info, next_table, name):
        self.Step(info, None, name)
        self.set_next_table(next_table)
        self._decision_value = None
        
    def set_next_table(self, next_table):
        self._next_table = next_table
        
    def action(self):
        self._info.directory.start_recording()
        (decision, result) = self.do()
        self.decide(decision)
        result.messages = self._info.directory.start_recording()
        return result
        
    def decide(self, value):
        self._decision_value = value
        
    def next(self):
        return self._next_table[self._decision_value]
        
class CoastalPlanning(Step):
    def do(self):
        municipality = self._info.directory.get_municipality()
        municipality.coastal_planning(
            self._info.directory.get_government().get_approved_complaints()
        )        
        return StepResult.no_cells_changed(self)
    
class Hearing(Step):
    def do(self):
        self._info.directory.get_government().new_vote_round()
        for agent in self._info.directory.get_voting_agents():
            agent.hearing()
        return StepResult.no_cells_changed(self)
        
class GovernmentDecision(DecisionStep):
   def do(self):
        government = self._info.directory.get_government()
        decision = government.voting_decision()
        return (StepResult.no_cells_changed(self), decision)

class Fishing(Step):
    def do(self):
        # Agents do profit activities
        government = self._info.directory.get_government()
        working_agents = self._info.directory.get_agents(exclude = government)
        #for a in working_agents: a.work()
        
        # (Local) Aquaculture companies pay some of their revenue to locals
        # through taxation
        for a in self._info.directory.get_agents(type = entities.Aquaculture):
            a.pay_taxes()
        
        return StepResult.no_cells_changed(self)
        
class Building(Step):
    def do(self):
        location = self._info.spawned_agent.get_location()
        agent = self._info.spawned_agent
        blocking_radius = 100
        affected_cells = self._info.map.build_aquaculture(
            agent, 
            location, 
            blocking_radius
        )
        return StepResult.cells_changed(phase, affected_cells)
        
class Learning(Step):
    def do(self):
        influences = priority.Influences()
        return StepResult([])