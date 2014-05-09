"""decisions.py

Contains abstract interfaces for decision mechanisms used by agents in entities.
"""

class VotingDecisionMechanism(object):
    """Interface for voting decisions."""

    def decide_votes(self, agent, coastal_plan, world_map, max_complaints):
        """Decide whether to complain or not for each vote.

        Arguments:
            agent:          The agent deciding the vote
            coastal_plan:   A plan.CoastalPlan instance

        Returns:
            A list of vote.Vote instances with APPROVE or DISAPPROVE values for
            cells with planned aquaculture in the plan.

            There is a maximum number of complaints allowed, so they have to
            be prioritized.
        """

        raise NotImplementedError()

    @classmethod
    def new(cls, agent, config, world):
        """Add an instance of this mechanism to the given agent.

        Agents have a method:
            add_voting_mechanism(mechanism)

        Arguments:
            agents: A list of agents to add the mechanism to
            config: The configuration object for the given agent,
                    for example cfg['fishermen'] if agents are fishermen.
            world:  The world instance
        """

        raise NotImplementedError()

class GovernmentDecision(object):
    """Interface for government decisions.
    
    The constructor of a GovernmentDecision takes a configuration object
    which is the whole configuration object for the agent type (Government).
    """

    def round_reset(self):
        """Round reset called when before a new round is started."""

        raise NotImplementedError()

    def decision(self, complaints):
        """The decision function is called on the set of all complaints from a
        single hearing round.

        Arguments:
            complaints  A dictionary of world.Slot instances mapped to
                        plan.Complaint objects.
        Returns:
            The dictionary of complaints, with approved flags set or not.
        """

        raise NotImplementedError()

class PlanningMechanism(object):
    """Interface form planning mechanisms for the municipality.
    
    The constructor for PlanningMechanism takes a configuration object
    which is the same as for the parent object (Municipality).
    """
    
    def create_plan(self, world_map, coastplan=None, complaints=None):
        """The create_plan method is called in each CoastalPlanning phase.

        Arguments:
            world_map   A world.Map instance
            coastplan   The previous plan, a plan.CoastalPlan instance.
            complaints  A list of plan.Complaint objects to review the plan
                        based on, it is None if there was no previous plan.

        Returns:
            A plan.CoastalPlan instance.
        """

        raise NotImplementedError()
