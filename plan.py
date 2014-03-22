class CoastalPlan(dict):
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
    def __init__(self, cell):
        self.cell = cell
        self.approved = False