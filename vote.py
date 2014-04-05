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

class VotingDecisionMechanism(object):
    """Interface for voting decisions."""
    
    def decide_votes(self, agent, coastal_plan, world_map):
        """Decide whether to complain or not for each vote.
        
        Arguments:
            agent:          The agent deciding the vote
            coastal_plan:   A plan.CoastalPlan instance
            
        Returns:
            A list of Vote instances with APPROVE or DISAPPROVE values for cells 
            with planned aquaculture in the plan.
        """
        raise NotImplementedException()
        
    @classmethod
    def new(c, agent, config, world):
        """Add an instance of this mechanism to the given agent.        
        
        Agents have a method:
            add_voting_mechanism(mechanism)
        
        Arguments:
            agents: A list of agents to add the mechanism to
            config: The configuration object for the given agent,
                    for example cfg['fishermen'] if agents are fishermen.
            world:  The world instance
        """
        raise NotImplementedException()