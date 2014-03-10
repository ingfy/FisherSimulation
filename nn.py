import random


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
        self.edges = edges
    
    def neurons(self):
        return self.inputs + self.hiddens + self.outputs
        
    def validate_edges(self, edges):
        # Check that all labels in connectivity have a match
        n = self.neurons()
        for a, b, v in edges:
            for e in [a, b]:
                if not e in n:
                    return False, "%s is not a label." % e
        return True, None
        
    def set_input_values(self, values = {})
        for l in labeled_values:
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