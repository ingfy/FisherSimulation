import random

def convert_edge_tuples(edges, label_to_neuron, neurons):
    out = {a: {b: 0.0 for b in neurons} for a in neurons}
    for (label_a, label_b), value in edges:
        neuron_a, neuron_b = (label_to_neuron[e] for e in (label_a, label_b))
        if not neuron_a in out:
            out[neuron_a] = {}
        out[neuron_a][neuron_b] = value
    return out

class LabeledNeuralNetwork(object):

    # Connectivity: (a, b, val)
    def __init__(self, inputs, outputs, hiddens, edges):
        assert len(inputs) > 0, "No input neurons"
        assert len(outputs) > 0, "No output neurons"
        n = inputs + outputs + hiddens
        assert len(n) == len(set(n)), "Duplicate labels."
        self.inputs = {label: Neuron(0.0, Neuron.INPUT) for label in inputs}
        self.outputs = {label: Neuron(0.0, Neuron.OUTPUT) for label in outputs}
        self.hiddens = {label: Neuron(0.0, Neuron.HIDDEN) for label in hiddens}
        connectivity_valid, err = self.validate_edges(edges)
        assert connectivity_valid, "Invalid edges. " + err
        self.edges = convert_edge_tuples(edges, {
            label: neuron for (label, neuron) 
                          in zip(self.labels(), self.neurons())
        }, self.neurons())
        
    def labels(self):
        return [e for l in [self.inputs, self.hiddens, self.outputs] 
            for e in l.keys()]
    
    def neurons(self):
        return [e for l in [self.inputs, self.hiddens, self.outputs] 
            for e in l.values()]            
        
    def validate_edges(self, edges):
        # Check that all labels in connectivity have a match
        n = self.labels()
        marked = {l: False for l in n}
        for (a, b), v in edges:
            for e in [a, b]:
                if not e in n:
                    return False, "%s is not a label." % e
                marked[e] = True
        for l in marked:
            if not marked[l]:
                return False, "%s is isolated." % l
        return True, None
        
    def set_input_values(self, values = {}):
        for l in values:
            assert isinstance(values[l], float), "Values have to be floats."
            self.inputs[l].value = values[l]
            
    def get_output_values(self):
        return {label: self.outputs[label].value for label in self.outputs}
        
    def get_output(self, label):
        return self.outputs[label].value
        
    def update(self):
        for n in self.neurons():
            n.value = sum([m.value * self.edges[n][m] for m in self.neurons()])
        
        
class Neuron(object):
    HIDDEN = 0
    INPUT = 1
    OUTPUT = 2

    def __init__(self, v, type):
        self.value = v
        self.type = type