import vote

class Round(object):
    def __init__(self, info):
        LEARNING = Learning(info, None, "LEARNING")
        FISHING3 = Fishing(info, LEARNING, "FISHING3")
        FISHING2 = Fishing(info, FISHING3, "FISHING2")
        BUILDING = Building(info, FISHING3, "BUILDING")
        FISHING1 = Fishing(info, BUILDING, "FISHING1")
        GOVDECISION = GovernmentDecision(info, 
            { vote.BUILD: FISHING1, vote.DONT_BUILD: FISHING2 }, "GOVDECISION")
        VOTING = Voting(info, GOVDECISION, "VOTING")
        SPAWNING = SpawnAquacultureAgent(info, VOTING, "SPAWNING")
        self._current_step = self._start = Round.spawn = 
            Step(self.spawn_quaculture_agent, vote)
        self._round_counter = 0
        
    def next(self):
        self._current_step = self._current_step.next()
        result = self._current_step.action()
        if self._current_step = self._start:
            self._round_counter += 1
        return result
       
    def rounds(self):
        return self._round_counter
        
class StepResult(object):
    def __init__(self, phase, messages_sent, cells_changed)
        self.phase = phase
        self.messages_sent = messages_sent
        self.cells_changed = cells_changed
        
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
        self._next_table = next_table
        self._decision_value = None
        
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
        
class SpawnAquacultureAgent(Step):
    def action(self):
        # choose a random cell
        cell = self._info.aquaculture_spawner.choose_cell(self._info.map)
        # create agent
        agent = self._info.aquaculture_spawner.create(
            self._info.agent_factory, 
            cell
        )
        # tell the government
        agent.notify_government()
        return StepResult.no_cells_changed(self)
        
class Voting(Step):
    def do(self):
        # government issues call for voting 
        government = self._info.directory.get_government()
        government.new_vote_round()
        government.call_vote()        
        return StepResult(self, [], [])
        
class GovernmentDecision(DecisionStep):
   def do(self):
        decision = government.voting_decision()
        return (StepResult([]), decision)

class Fishing(Step):
    def do(self):
        return StepResult([])
        
class Building(Step):
    def do(self):
        return StepResult([])
        
class Learning(Step):
    def do(self):
        return StepResult([])