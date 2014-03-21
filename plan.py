class CoastalPlan(object):
    pass
    
class PlanEntity(object):
    def __init__(self, description=None):
        self.description = description
        
    def __str__(self):
        if self.description is None:
            return "Plan Entity"
        return self.description
    
AQUACULTURE = PlanEntity(
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