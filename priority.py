import numpy

class Influences(object):
    def __init__(self, 
            agent = None, 
            all_agents = None, 
            market = None, 
            fishermen = None, 
            world_map = None, 
            aquaculture_agents = None):
        self.agent = agent
        self.all_agents = all_agents
        self.market = market
        self.fishermen = fishermen
        self.world_map = world_map
        self.aquaculture_agents = aquaculture_agents

class Priority(object):
    # <dobule> calculate_value(...) should be implemented for all subclasses
    
    def __init__(self, name):
        self._name = name
        
class OwnProfits(Priority):
    def __init__(self):
        super(OwnProfits, self).__init__("Own Profits")
        
    # Assume agent has methods:
    #   get_capital()
    def calculate_value(self, influences):
        return influences.agent.get_capital()
        
class CommunityWealth(Priority):
    def __init__(self):
        super(CommunityWealth, self).__init__("Community Wealth")
        
    # Assume agent has methods:
    #   get_capital()
    #   is_community_member()
    # Return the average capital of all agents that count as
    # community members.
    def calculate_value(self, influences):
        members = [a for a in influences.all_agents if a.is_community_member()]
        return sum([m.get_capital() for m in members])/len(members)
        
class SalmonPrice(Priority):
    def __init__(self):
        super(SalmonPrice, self).__init__("Salmon Price")

    # Assume market has methods:
    #   get_salmon_price()
    def calculate_value(self, influences):
        return influences.market.get_salmon_price()
        
class WildFishPrice(Priority):
    def __init__(self):
        super(WildFishPrice, self).__init__("Wild Fish Price")

    # Assume market has methods:
    #   get_wild_fish_price()
    def calculate_value(self, influences):
        return influences.market.get_wild_fish_price()

class FishingIndustryExisting(Priority):
    def __init__(self):
        super(FishingIndustryExisting, self).__init__("Fishing Industry Existing")
        
    # Assume fisherman has methods:
    #   is_fishing()    False if agent has changed occupation, True if still fishing.
    # Check if fishermen are still fishing or have quit to move on to other things.
    # Return fraction of (original) fishermen that are still fishing.
    def calculate_value(self, influences):
        return sum([1.0 if f.is_fishing() else 0.0 for f in influences.fishermen])/len(influences.hermen)
        
class NaturalFishHealth(Priority):
    def __init__(self):
        super(NaturalFishHealth, self).__init__("Natural Fish Health")
       
    # Assume world map Slot has methods:
    #   get_fish_status()   Fraction of fish health between 0.0 and 1.0
    # Assume that world_map has methods:
    #   get_slots()         Returns an iterable of all the slots
    # Retursn the average health of every slot on the map
    def calculate_value(self, influences):
        slots = influences.world_map.get_slots()
        return sum([s.get_fish_status() for s in slots])/len(slots)

class AquacultureIndustryExisting(Priority):
    def __init__(self):
        super(AquacultureIndustryExisting, self).__init__("Aquaculture Industry Existing")
    
    # Count the number of aquaculture companinies.
    def calculate_value(self, influences):
        return len(influences.aquaculture_agents)
        
class NonintrusiveAquaculture(Priority):
    def __init__(self):
        super(NonintrusiveAquaculture, self).__init__("Non-intrusive Aquaculture")

    # Assume world map Slot has methods:
    #   has_aquaculture()   True if there is an aquaculture establishment occupying the
    #                       slot.
    # Assume agent has methods:
    #   get_priority_slots()    Returns a list of world map slots that the agent cares 
    #   about being "clean" of aquaculture establishments.
    def calculate_value(self, influences):
        slots = influences.agent.get_priority_slots()
        return sum([0 if s.has_aquaculture() else 1 for s in slots])/len(slots)
        
class PopulationHappiness(Priority):
    def __init__(self):
        super(PopulationHappiness, self).__init__("Population Happiness")
        
    # Assume agent has methods:
    #   get_priorities_satisfaction()
    # Calculate the median happiness of agents
    def calculate_value(self, influences):
        return numpy.median([a.get_priorities_satisfaction() for a in influences.agents])