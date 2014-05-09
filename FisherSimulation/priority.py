"""
Agent's motivations are driven by their priorities, which are implemented as 
calculable entities. Priorities are calculated by picking attributes in a common 
object for influences.
"""

import numpy

class Influences(object):
    """
    All influences that can have an impact on an agent's priorities are included 
    in this class. It has field for the agent, all agents, community member 
    agents, the market, fishermen, the world map and aquaculture agents.
    """
    
    def __init__(self, 
            agent = None, 
            all_agents = None, 
            market = None, 
            community_members = None,
            fishermen = None,             
            world_map = None, 
            aquaculture_agents = None):
        self.agent = agent
        self.all_agents = all_agents
        self.community_members = community_members
        self.market = market
        self.fishermen = fishermen
        self.world_map = world_map
        self.aquaculture_agents = aquaculture_agents
        
    def copy_for(self, agent):
        return Influences(
            agent,
            self.all_agents,
            self.market,
            self.community_members,
            self.fishermen,
            self.world_map,
            self.aquaculture_agents
        )

class Priority(object):
    """
    A single priority is implemented by giving a calculating function to this 
    class.
    """

    # <dobule> calculate_value(...) should be implemented for all instances
    
    def __init__(self, name, calculate_value):
        self.name = name
        self.calculate_value = calculate_value
        
def OwnProfits_value(influences):
    return influences.agent.capital

def WildFishPrice_value(influences):
    return influences.market.get_wild_fish_price()
    
def SalmonPrice_value(influences):
    return influences.market.get_farmed_fish_price()

def CommunityWealth_value(influences):
    members = [a for a in influences.community_members]
    return float(sum([m.capital for m in members]))/len(members)
        
def FishingIndustryExisting_value(influences):
    return float(
        sum([f.capital for f in influences.fishermen])
        )/len(influences.fishermen)
        
def NaturalFishHealth_value(influences):
    slots = influences.world_map.get_all_cells()
    return sum([s.get_fish_quantity() for s in slots])/len(slots)
    
def AquacultureIndustryExisting_value(influences):
    return 1.0 if len(influences.aquaculture_agents) > 0 else 0.0
    
def NonintrusiveAquaculture_value(infleucnes):
    slots = influences.agent.get_priority_slots()
    return sum([0 if s.has_aquaculture() else 1 for s in slots])/len(slots)

# Exported real priorities
OwnProfits = Priority("Own Profits", OwnProfits_value)
WildFishPrice = Priority("Wild Fish Price", WildFishPrice_value)
SalmonPrice = Priority("Salmon Price", SalmonPrice_value)
CommunityWealth = Priority("Community Wealth", CommunityWealth_value)
FishingIndustryExisting = Priority("Fishing Industry Existing", FishingIndustryExisting_value)
NaturalFishHealth = Priority("Natural Fish Health", NaturalFishHealth_value)
AquacultureIndustryExisting = Priority("Aquaculture Industry Existing", AquacultureIndustryExisting_value)
NonintrusiveAquaculture = Priority("Nonintrusive Aquaculture", NonintrusiveAquaculture_value)