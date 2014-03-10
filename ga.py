import nn
import math

class Phenotype(object):
    def __init__(self, genotype):
        self.genotype = genotype
    
    @classmethod
    def from_genotype(c, genotype):
        return c(genotype)
        
    def fitness(self):
        pass
    
class Genotype(object):
    length = 0
    mutation_rate = 0.005
    crossover_rate = 0.005

    def __init__(self, genome):
        self.genome = genome
    
    @classmethod
    def random(c):
        return c(
            "".join(["0" if math.random() > 0.5 else "1" for __ in xrange(c.length)])
        )
        
    def mutate(self):
        if math.random() < mutation_rate:
            point = int(math.random() * len(self))
            self.genome[point] = "0" if self.genome[point] == "1" else "1"
        
    def __len__(self):
        return self.length
        
    @classmethod
    def crossover(c, first, second):
        assert len(first) == len(second), "Lengths are not the same."
        point = int(math.random() * len(first))
        return c(first.genome[:point] + second.genome[point:])
        
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
            [float(e) / 2**NNGenotype.precision for e in self.genome.to_number_list()])
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