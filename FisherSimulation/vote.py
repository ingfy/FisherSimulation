import decisions

APPROVE = object()
DISAPPROVE = object()

class Vote(object):
    """Object containing vote and the cell it regards.
    
    Attributes:
        value:  Either APPROVE or DISAPPROVE
        cell:   A world.Slot instance
    """
    
    def __init__(self, cell, value):
        assert value in [APPROVE, DISAPPROVE], "Invalid vote value."
        self.value = value
        self.cell = cell
        
    @classmethod
    def complaint(c, cell):
        return c(cell, DISAPPROVE)
        
    def is_complaint(self):
        return self.value == DISAPPROVE        

# Concrete

class AlwaysApprove(decisions.VotingDecisionMechanism):
    def decide_votes(self, agent, coastal_plan, world_map, max_complaints):
        return []
        
    @classmethod
    def new(c, agent, config, world):
        agent.add_voting_mechanism(c())