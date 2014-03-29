APPROVE = 0
DISAPPROVE = 1

class Vote(object):
    def __init__(self, cell, value):
        self.value = value
        self.cell = cell

class VotingDecisionMechanism(object):
    """Interface for voting decisions."""
    
    def decide_votes(self, agent, coastal_plan):
        """Decide whether to complain or not for each vote.
        
        Arguments:
            agent:          The agent deciding the vote
            coastal_plan:   A plan.CoastalPlan instance
            
        Returns:
            A list of Vote instances with APPROVE or DISAPPROVE values for cells 
            with planned aquaculture in the plan.
        """
        raise NotImplementedException()