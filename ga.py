import nn
import math
import priority
import agent
import entities
import random
import itertools

class LearningMechanism(object):
    def __init__(self, agents):
        self._agents = agents
        
    def selection_mechanism(self):
        raise NotImplementedException()
        
    def learn(self):
        raise NotImplementedException()
        
class EvolutionarySelectionPhenotype(object):
    def __init__(self, phenotype, fitness):
        self.phenotype = phenotype
        self.fitness = fitness
        
class EvolutionConfig(object):
    SELECTION_MECHANISMS = {
        "rank": Evolution.rank_selection,
        "rank selection": Evolution.rank_selection,
        "default": Evolution.rank_selection
    }
    def __init__(self, elitism, selection_mechanism, crossover_rate, 
            mutation_rate):
        self.elitism = elitism
        self.selection_mechanism = selection_mechanism
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
    @classmethid
    def from_dict(c, dict):
        elitism = int(dict["elitism"])
        selection_mechanism = EvolutionConfig.SELECTION_MECHANISMS.get(
            dict["selection mechanism"], 
            EvolutionConfig.SELECTION_MECHANISMS["default"]
        )
        crossover_rate = float(dict["crossover rate"])
        mutation_rate = float(dict["mutation rate"])
        return c(
            elitism,
            selection_mechanism,
            crossover_rate,
            mutation_rate
        )
        
class Evolution(LearningMechanism):
    def __init__(self, phenotype, genotype, agents, config):
        self.LearningMechanism(agents)
        self._phenotype = phenotype
        self._genotype = genotype
        self._elitism = config.elitism
        self.selection_mechanism = config.selection_mechanism
        self._crossover_rate = config.crossover_rate
        self._mutation_rate = config.mutation_rate
        
    def learn(self, simulation_info):
        dir = simulation_info.directory
        all_agents = dir.get_agents()
        fishermen = dir.get_agents(type = entities.Fisherman)
        community_members = 
            dir.get_agents(type = entities.Fisherman) +
            dir.get_agents(type = entities.Aquaculture) +
            dir.get_agents(type = entities.Civilian) +
            dir.get_agents(type = entities.Tourist)
        market = simulation_info.market
        world_map = simulation_info.map
        aquaculture_agent = dir.get_agents(type = entities.Aquaculture)
        fitnesses = {
            agent: agent.get_priorities_satisfaction(
                priority.Influences(
                    agent, all_agents, market, community_members, fishermen, 
                    world_map, aquaculture_agents
                )
            ) for agent in self._agents
        }
        
        # sorted
        fitnesses = [(a.decision_mechanism, f, a) for a, f in sorted(
            fitnesses.iterkeys(), key=lambda k: fitnesses[k]
        )] # returns an ordered list of (phenotype, fitness, agent) tuples
        
        # keep elites
        elites, rest = fitnesses[:self._elitism], fitnesses[self._elitism:]
            # elites are left untouched
        selected = self.selection_mechanism(
            [EvolutionarySelectionPhenotype(p, f) for p, f, __ in rest], 
            len(rest)
        ) # select n best non-elites
        
        # Mutate
        genotypes = [p.genotype for p in selected]
        
        ## crossover
        for (a, b) in itertools.combinations(range(len(genotypes)), 2):
            genotypes[a], genotypes[b] = self._genotype.crossover(
                genotypes[a], genotypes[b], self._crossover_rate
            )
            
        ## mutation
        genotypes = [g.mutate(self._mutation_rate) for g in genotypes]
          
        # Create new phenotypes
        new_phenotypes = [self._phenotype.from_genotype(g) for g in genotypes]
        
        # Distribute new phenotypes to non-elite agents
        for (__, ___, a), p in zip(rest, new_phenotypes):
            a.decision_mechanism = p
        
        
    """
    Linear rank selection. Based on roulette wheel. Rank all elements by
    fitness value. Assign 1 ``lottery ticket'' to the lowest ranking member,
    2 to the second and so on up to N tickets for the best member. Randomly
    select based on the weighed probabilities described by the lottery 
    tickets.
    """
    @staticmethod
    def rank_selection(self, sorted_phenotypes, num):
        wheel = {}
        sum = 0
        total = 0
        for n in xrange(len(sorted_phenotypes)):
            wheel[sorted_phenotypes[-p]] = n + sum
            sum += n
            total += n + sum
        selected = [None] * num
        for i in xrange(num):
            r = random.random() * total        
            for p in wheel:
                if r > wheel[p]:
                    selected[i] = p
        return selected
            

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
            "".join(
                ["0" if random.random() > 0.5 else "1" for __ in xrange(c.length)]
            )
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
        ) if random.random() < rate else (first, second)
        
# Abstract Decision Making Mechanism class        
class DecisionMechanism(object):
    def set_input_values(self, inputs):
        raise NotImplementedException()
        
    def process(self):
        raise NotImplementedException()
        
    def get_output_values(self):
        raise NotImplementedException()
            

class FishermanNN(Phenotype, DecisionMechanism):
    inputs = [
            "distance", 
            "home conditions", 
            "targeted conditions"]
    hiddens = ["A", "B", "C", "D", "E", "F"]
    outputs = ["vote"]

    def __init__(self, genotype):
        self.genotype = genotype        
        self.connctions = [
            # All inputs to all hidden neurons
            (a, b) for a in self.inputs for b in self.hiddens       
        ] + [
            # All hidden neurons to all output neurons
            (a, b) for a in self.hiddens for b in self.outputs
        ] + [
            # All hidden neurons to themselves
            (a, a) for a in self.hiddens
        ]
        self.edges = zip(self.connections, 
            [float(e) / 2**NNGenotype.precision for e in 
                self.genome.to_number_list()])
        self.network = nn.LabeledNeuralNetwork(inputs, outputs, hiddens, edges)
        
    def set_input_values(self, inputs):
        self.network.set_input_values(inputs):
        
    def process(self):
        self.network.update()
        
    def get_output_values(self):
        self.network.get_output_values()
            
    
class FishermanNNGenotype(Genotype):
    phenotype_class = FishermanNN
    precision = 8  # bits per 1
    length = (
        len(phenotype_class.inputs)  * len(phenotype_class.hiddens) +
        len(phenotype_class.hiddens) * len(phenotype_class.outputs) +
        len(phenotype_class.hiddens)
    ) * (weight_range[1] - weight_range[0]) * weight_precision
    
    def to_number_list(self):
        def sep(str, acc):
            if len(str) < self.precision: return acc
            return sep(str[self.precision:], acc + [str[:self.precision]])
        return [int(e, 2) for e in sep(self.genome, [])]        