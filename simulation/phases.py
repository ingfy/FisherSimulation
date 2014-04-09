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
import numpy

class Round(object):
    def __init__(self, info):
        self.info = info
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
        result = self._current_step.action(self._round_counter)
        self._current_step = self._current_step.next()
        if self._current_step is None:
            self.new_round()
        return result 

    def new_round(self):
        self.info.logger.write_round_statistics(
            self._round_counter, 
            self.info.map, 
            self.info.directory.get_agents(type = entities.Aquaculture)
        )
        self._round_counter += 1
        self._current_step = self._start
        # reset
        for a in self.info.directory.get_agents(): a.round_reset()        
        
    def current(self):
        return self._current_step.name
       
    def rounds(self):
        return self._round_counter
        
class StepResult(object):
    def __init__(self, phase, messages_sent, cells_changed, world_map, data):
        self.phase = phase
        self.messages_sent = messages_sent
        self.cells_changed = cells_changed
        self.world_map = world_map
        self.data = data
        
    @classmethod
    def cells_changed(c, phase, cells_changed, world_map, data):
        return c(phase, [], cells_changed, world_map, data)
        
    @classmethod
    def no_cells_changed(c, phase, world_map, data):
        return c(phase, [], [], world_map, data)

## Abstract Step classes ##

class Step(object):
    def __init__(self, info, next, name):
        self.info = info
        self._next = next
        self.name = name

    def do(self, round):
        raise NotImplementedException()

    def next(self):
        return self._next

    def action(self, round):
        self.info.directory.start_recording()
        result = self.do(round)
        result.messages = self.info.directory.stop_recording()
        return result

class DecisionStep(Step):
    def __init__(self, info, next_table, name):
        Step.__init__(self, info, None, name)
        self.set_next_table(next_table)
        self._decision_value = None

    def set_next_table(self, next_table):
        self._next_table = next_table

    def action(self, round):
        self.info.directory.start_recording()
        (result, decision) = self.do(round)
        self.decide(decision)
        result.messages = self.info.directory.stop_recording()
        return result

    def decide(self, value):
        self._decision_value = value

    def next(self):
        return self._next_table[self._decision_value]


## Concrete Step Implementations ##

class CoastalPlanning(Step):
    def do(self, round):
        for a in self.info.directory.get_agents():
            self.info.logger.vote_fitness_relation(round, a)
        municipality = self.info.directory.get_municipality()
        municipality.coastal_planning(
            self.info.map,
            self.info.directory.get_government().get_approved_complaints()
        )
        return StepResult.no_cells_changed(self, self.info.map, {})
    
class Hearing(Step):
    def do(self, round):
        data_dict = {}
        self.info.directory.get_government().new_vote_round()
        for agent in self.info.directory.get_voting_agents():
            votes = agent.hearing(
                self.info.map, 
                self.info.cfg['global']['num_max_complaints']
            )
            self.info.logger.add_vote(round, agent, 
                len([v for v in votes if v.is_complaint()]))
        return StepResult.no_cells_changed(self, self.info.map, data_dict)
        
class GovernmentDecision(DecisionStep):
   def do(self, round):
        government = self.info.directory.get_government()
        decision = government.voting_decision(
            self.info.cfg["global"]["max_hearing_rounds"]
        )
        return (
            StepResult.no_cells_changed(self, self.info.map, {}), decision
        )

class Fishing(Step):
    def do(self, round):
        # Agents do profit activities
        government = self.info.directory.get_government()
        
        working_agents = \
            self.info.directory.get_agents(type = entities.Fisherman) + \
            self.info.directory.get_agents(type = entities.Aquaculture)
            
        fishermen = self.info.directory.get_agents(type = entities.Fisherman)
        
        affected_cells = []
        
        for f in fishermen:
            old_home = f.home
            f.find_fishing_spot(self.info.map)
            if old_home != f.home:
                affected_cells.extend([f.home, old_home])
        
        for a in working_agents: 
            a.work()
        
        # (Local) Aquaculture companies pay some of their revenue to locals
        # through taxation
        for a in self.info.directory.get_agents(type = entities.Aquaculture):
            a.pay_taxes()
        
        return StepResult.cells_changed(self, affected_cells, self.info.map, {})
        
class Building(Step):
    def do(self, round):
        government = self.info.directory.get_government()
        municipality = self.info.directory.get_municipality()
        licenses = government.distribute_licenses()
        spawner = self.info.aquaculture_spawner
        plan = municipality.get_plan()
        blocking_radius = 25
        affected_cells = []
        for license in licenses:
            location = spawner.choose_cell(plan)
            if not location is None:
                agent = spawner.create(
                    self.info.agent_factory,
                    location
                )
                affected_cells.append(location)
                affected_cells.extend(self.info.map.build_aquaculture(
                    agent, 
                    location
                ))
        return StepResult.cells_changed(self, affected_cells, self.info.map, {})
        
class Learning(Step):
    def do(self, round):
        data_dict = {"average fitness": {}}
        
        dir = self.info.directory
        all_agents = dir.get_agents()
        fishermen = dir.get_agents(type = entities.Fisherman)
        community_members = \
            dir.get_agents(type = entities.Fisherman) + \
            dir.get_agents(type = entities.Aquaculture) + \
            dir.get_agents(type = entities.Civilian)# + \
            #dir.get_agents(type = entities.Tourist)
        market = self.info.market
        world_map = self.info.map
        aquaculture_agents = dir.get_agents(type = entities.Aquaculture)
        fitnesses = {
            agent: agent.get_priorities_satisfaction(
                priority.Influences(
                    agent, all_agents, market, community_members, fishermen, 
                    world_map, aquaculture_agents
                )
            ) for agent in self.info.directory.get_agents()
        }
        
        # record average fitness
        for t, l in [(entities.Fisherman, "fisherman")]:
            data_dict["average fitness"][l] = numpy.mean(
                [fitnesses[a] for a in fitnesses if a.__class__ == t]
            )
            
        # log fitness
        for agent in fitnesses:
            self.info.logger.add_fitness(round, agent, fitnesses[agent])
    
        for group in self.info.learning_mechanisms:
            self.info.learning_mechanisms[group].learn(fitnesses)
        
        return StepResult.no_cells_changed(self, self.info.map, data_dict)