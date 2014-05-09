"""
The plan module contains classes that simplify dealing with the coastal 
plan.
"""

class CoastalPlan(dict):
    """
    This class subclasses the standard Python dictionary, and is used to map 
    cells to plan entities.
    """
    
    def __init__(self, dictionary):
        for key in dictionary:
            dict.__setitem__(self, key, dictionary[key])
            
    def _of_type(self, type):
        return [cell for cell in self if self[cell] == type]
            
    def aquaculture_sites(self):
        return self._of_type(AQUACULTURE_SITE)
        
    def reserved_zones(self):
        return self._of_type(RESERVED_ZONE)
    
class PlanEntity(object):
    """
    Items in the coastal plan are plan entities, and these have a description. 
    There are two entities implemented.
    """

    def __init__(self, description=None):
        self.description = description  
        
    def __str__(self):
        if self.description is None:
            return "Plan Entity"
        return self.description
    
AQUACULTURE_SITE = PlanEntity(
    """
    **AQUACULTURE SITE**
    The aquaculture site represents a place that has been approved for 
    industrial aquaculture development. Once a site has been approved and the
    plan has been finalized, an aquaculture company with a license may 
    establish there without inference from other parties (like fishermen).
    """
)
RESERVED_ZONE = PlanEntity(
    """
    **RESERVED ZONE**
    A "Reserved Zone" is an area that has been reserved from industrial 
    development, and is open for fishing.
    """
)
    
class Complaint(object):
    """
    A complaint is an entity that gathers negative votes about a certain cell. 
    It has an approved-flag for the government to set.
    """

    def __init__(self, vote):
        self.cell = vote.cell
        self.approved = False
        self.votes = [vote]
        
    def approve(self):
        self.approved = True
        
    def count(self):
        return len(self.votes)
        
    def add(self, vote):
        assert vote.cell is self.cell, "Complaint is not about the same cell!"
        self.votes.append(vote)
        
class Decision(object):
    """
    The decision class is used as a name space for the overall plan decisions 
    the government can make: approve, or review.
    """

    APPROVE = object()
    REVIEW  = object()