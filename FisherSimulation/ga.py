import nn
import math
import numpy
import priority
import agent
import entities
import random
import itertools
import vote

class LearningMechanism(object):
    def __init__(self, agents):
        self.agents = agents
        
    def learn(self):
        raise NotImplementedException()
        
class EvolutionarySelectionPhenotype(object):
    def __init__(self, phenotype, fitness):
        self.phenotype = phenotype
        self.fitness = fitness
        
class Evolution(LearningMechanism):
    def __init__(self, agents, cfg):
        LearningMechanism.__init__(self, agents)
        config = EvolutionConfig.from_dict(cfg)
        self._phenotype = config.phenotype
        self._genotype = config.genotype
        self._elitism = config.elitism
        self.selection_mechanism = config.selection_mechanism
        self._crossover_rate = config.crossover_rate
        self._mutation_rate = config.mutation_rate
        self._genome_mutation_rate = config.genome_mutation_rate
        
    def learn(self, fitnesses):
        
        # sorted
        fitnesses = [(a.decision_mechanism, fitnesses[a], a) for a in sorted(
                fitnesses.iterkeys(), key=lambda k: fitnesses[k]
        ) if a in self.agents] 
            # returns an ordered list of (phenotype, fitness, agent) tuples
        
            
        
        # keep elites
        elites, rest = fitnesses[:self._elitism], fitnesses[self._elitism:]
            # elites are left untouched
        selected = self.selection_mechanism(
            [EvolutionarySelectionPhenotype(p, f) for p, f, __ in rest], 
            len(rest)
        ) # select n best non-elites
        
        # Mutate
        genotypes = [p.phenotype.genotype for p in selected]
        
        ## crossover
        for (a, b) in itertools.combinations(range(len(genotypes)), 2):
            genotypes[a], genotypes[b] = self._genotype.crossover(
                genotypes[a], genotypes[b], self._crossover_rate
            )
            
        ## mutation        
        for g in genotypes:
            g.mutate(self._mutation_rate, self._genome_mutation_rate) 
          
        # Create new phenotypes
        new_phenotypes = [self._phenotype.from_genotype(g) for g in genotypes]
        
        # Distribute new phenotypes to non-elite agents
        for (__, ___, a), p in zip(rest, new_phenotypes):
            a.decision_mechanism = p
    
    @staticmethod
    def rank_selection(sorted_phenotypes, num):
        """Linear rank selection.
        Based on roulette wheel. Rank all elements by
        fitness value. Assign 1 ``lottery ticket'' to the lowest ranking member,
        2 to the second and so on up to N tickets for the best member. Randomly
        select based on the weighed probabilities described by the lottery 
        tickets.
        
        Arguments:
            sorted_phenotypes:  TODO
            num:                TODO
            
        Returns:
            TODO
        """
        
        wheel = {}
        sum = 0
        total = 0
        for n in xrange(len(sorted_phenotypes)):
            wheel[sorted_phenotypes[-n]] = n + sum
            sum += n
            total += n + sum
        selected = [None] * num
        for i in xrange(num):
            r = random.random() * total        
            for p in wheel:
                if r > wheel[p]:
                    selected[i] = p
        return selected
        
class EvolutionConfig(object):
    SELECTION_MECHANISMS = {
        "rank": Evolution.rank_selection,
        "rank selection": Evolution.rank_selection,
        "default": Evolution.rank_selection
    }
    
    @classmethod
    def from_dict(c, dict):
        obj = c()
        obj.phenotype = dict["phenotype class"]
        obj.genotype = dict["genotype class"]
        obj.elitism = int(dict["elitism"])
        obj.selection_mechanism = EvolutionConfig.SELECTION_MECHANISMS.get(
            dict["selection mechanism"], 
            EvolutionConfig.SELECTION_MECHANISMS["default"]
        )
        obj.crossover_rate = float(dict["crossover rate"])
        obj.mutation_rate = float(dict["mutation rate"])
        obj.genome_mutation_rate = float(dict["genome mutation rate"])
        return obj

class Phenotype(object):
    def __init__(self, genotype):
        self.genotype = genotype
    
    @classmethod
    def from_genotype(c, genotype):
        return c(genotype)        
        
    def fitness(self):
        raise NotImplementedException()
    
class Genotype(object):
    length = 0

    def __init__(self, genome):
        self.genome = genome
    
    @classmethod
    def random(c):
        return c(
            ["0" if random.random() > 0.5 else "1" for __ in xrange(c.length)]
        )
        
    def mutate(self, mutation_rate, genome_mutation_rate):
        if random.random() < mutation_rate:
            point = int(random.random() * len(self.genome))
            self.genome[point] = "0" if self.genome[point] == "1" else "1"
        
    def __len__(self):
        return self.length
        
    @classmethod
    def crossover(c, first, second, crossover_rate):
        assert len(first) == len(second), "Lengths are not the same."
        point = int(random.random() * len(first))
        return (
            c(first.genome[:point] + second.genome[point:]),
            c(second.genome[:point] + first.genome[point:])
        ) if random.random() < crossover_rate else (first, second)
        
# Abstract Decision Making Mechanism class        
class DecisionMechanism(object):
    def set_input_values(self, inputs):
        raise NotImplementedException()
        
    def process(self):
        raise NotImplementedException()
        
    def get_output_values(self):
        raise NotImplementedException()
            
# Concrete decision making

class FishermanVotingRules(vote.VotingDecisionMechanism, Phenotype):
    data_name = "fisherman"
    
    DIST_PROB = "Distance Probability"
    COMPLAIN_10 = "Always complain 10"
    APPROVE_ALL = "Never complain"
    
    
    def __init__(self, genotype):
        Phenotype.__init__(self, genotype)
        self.rule = genotype.to_rule()
        
        # Rules:
        # - distance proportional probabilistic decision        
        # - always complain 10 random        
        # - never complain
        
    
    def _dist_prob(self, agent, coastal_plan, world_map, num_max_complaints):
        vote_strength = {}
        for cell in coastal_plan.aquaculture_sites():
            norm_distance = world_map.get_cell_distance(agent.home, cell) / \
                world_map.get_max_distance()
            value = random.random() * norm_distance
            complain = value > 0.5
            if complain:
                vote_strength[vote.Vote.complaint(cell)] = value
                
        return sorted(
            vote_strength.iterkeys(),
            key=lambda e: vote_strength[e],
            reverse=True
        )[:num_max_complaints]
        
    def _complain_10(self, agent, coastal_plan, world_map, num_max_complaints):
        return [vote.Vote.complaint(c) for c in
            random.sample(coastal_plan, num_max_complaints)]
    
    def _approve_all(self, agent, coastal_plan, world_map, num_max_complaints):
        return []
        
    rule_to_method = {
        DIST_PROB: _dist_prob,
        COMPLAIN_10: _complain_10,
        APPROVE_ALL: _approve_all
    }
        
    def decide_votes(self, agent, coastal_plan, world_map, num_max_complaints):
        return self.rule_to_method[self.rule](
            self, agent, coastal_plan, world_map, num_max_complaints
        )
        
    @classmethod
    def new(c, agent, config, world):
        agent.add_voting_mechanism(c(FishermanRulesGenotype.random()))
        
class FishermanRulesGenotype(Genotype):
    length = 3
    
    def to_rule(self):
        return {
            0: FishermanVotingRules.DIST_PROB,
            1: FishermanVotingRules.COMPLAIN_10,
            2: FishermanVotingRules.APPROVE_ALL,
            3: FishermanVotingRules.DIST_PROB
        }[int("".join(self.genome), 2) / 2]

            
class FishermanVotingNN(vote.VotingDecisionMechanism, Phenotype):
    data_name = "fisherman"

    inputs = [
            "distance", 
            "home conditions", 
            "targeted conditions"]
    hiddens = ["A", "B", "C", "D", "E", "F"]
    outputs = ["vote"]

    def __init__(self, genotype):
        Phenotype.__init__(self, genotype)        
        self.connections = [
            # All inputs to all hidden neurons
            (a, b) for a in self.inputs for b in self.hiddens       
        ] + [
            # All hidden neurons to all output neurons
            (a, b) for a in self.hiddens for b in self.outputs
        ] + [
            # All hidden neurons to themselves
            (a, a) for a in self.hiddens
        ] + [
            # Bias node to hidden layer nodes
            ("bias", a) for a in self.hiddens
        ]
        self.edges = zip(self.connections, self.genotype.to_number_list())
        self.network = nn.LabeledNeuralNetwork(
            FishermanVotingNN.inputs, 
            FishermanVotingNN.outputs, 
            FishermanVotingNN.hiddens, 
            self.edges
        )
        
    def decide_votes(self, agent, coastal_plan, world_map, num_max_complaints):
        vote_strength = {}
        for cell in coastal_plan.aquaculture_sites():
            home = agent.home
            distance = world_map.get_cell_distance(home, cell) / \
                world_map.get_max_distance()
            cond = agent.slot_knowledge[cell] if \
                cell in agent.slot_knowledge else 0.0
            values = {
                "distance":             distance,
                "home conditions":      agent.slot_knowledge[home],
                "targeted conditions":  cond
            }
            self.network.set_input_values(values)
            self.network.update()
            output = self.network.get_output_values()
            complain = output["vote"] > 0.5
            if complain:
                vote_strength[vote.Vote.complaint(cell)] = output["vote"]                
        
        return sorted(
            vote_strength.iterkeys(),
            key=lambda e: vote_strength[e],
            reverse=True
        )[:num_max_complaints]
        
    @classmethod
    def new(c, agent, config, world):
        agent.add_voting_mechanism(
            c.from_genotype(FishermanNNGenotype.random())
        )
        
    
class FishermanNNGenotype(Genotype):
    phenotype_class = FishermanVotingNN
    precision = 8  # bits per 1
    weight_range = (-1, 1)
    length = (
        # Input to hidden layer
        len(phenotype_class.inputs)  * len(phenotype_class.hiddens) +
        # Hidden layer to outputs
        len(phenotype_class.hiddens) * len(phenotype_class.outputs) +
        # Recurrent hidden layer-connections
        len(phenotype_class.hiddens) +
        # Bias node to hidden layer nodes
        len(phenotype_class.hiddens)
    ) * (weight_range[1] - weight_range[0]) * precision
    
    def to_number_list(self):
        def sep(str, acc):
            if len(str) < self.precision: return acc
            return sep(str[self.precision:], acc + [str[:self.precision]])
        return [self.weight_range[0] + int(''.join(e), 2) / 2.0 ** self.precision * (self.weight_range[1] - self.weight_range[0]) for e in sep(self.genome, [])]