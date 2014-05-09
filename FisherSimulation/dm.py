"""Concrete decision mechanism (dm) implementations."""

from FisherSimulation import decisions

import random
from FisherSimulation import plan

class ApproveProbability(decisions.GovernmentDecision):
    """Approves complaints one by one according to a configurable probability.
       Implements the GovernmentDecision interface in the decisions package.
    """

    def __init__(self, cfg):
        self._probability = cfg["complaint approval probability"]
        self._max_rounds = cfg.globals["max hearing rounds"]
        self._round_count = 1

    def round_reset(self):
        self._round_count = 1

    def decision(self, complaints):
        if self._round_count >= self._max_rounds:
            return complaints   # Approve none

        self._round_count += 1

        for cell in complaints:
            for vote in complaints[cell].votes:
                if random.random() < self._probability:
                    complaints[cell].approve()

        return complaints

class ComplaintApproveMoreThanOne(decisions.GovernmentDecision):
    def __init__(self, cfg):
        self._max_hearing_rounds = cfg.globals["max hearing rounds"]
        self._hearing_count = 0

    def round_reset(self):
        self._hearing_count = 0

    def decision(self, complaints):
        if self._hearing_count >= self._max_hearing_rounds:
            return complaints

        self._hearing_count += 1
        for cell in complaints:
            approve = complaints[cell].count() > 1
            if approve:
                complaints[cell].approve()

        return complaints

class EverythingAquaculture(decisions.PlanningMechanism):
    def __init__(self, cfg):
        self._aquaculture_in_blocked = cfg.globals["aquaculture in blocked"]

    def _check_cell(self, cell):
        if self._aquaculture_in_blocked:
            return not cell.has_aquaculture()
        return not cell.is_blocked()

    def create_plan(self, world_map, coastplan=None, complaints=None):
        if coastplan is None:
            # If new plan, add all possible cells as aquaculture sites

            # TODO:
            #  Maybe divide into different kinds of areas first,
            #  maybe only 50% of the map for aquaculture.
            coastplan = plan.CoastalPlan({
                c: plan.AQUACULTURE_SITE
                    for c in world_map.get_all_cells()
                        if self._check_cell(c)
            })

        # Convert all cells that have approved complaints to
        # reserved zones.
        if not complaints is None:
            for c in complaints:
                if c.approved:
                    coastplan[c.cell] = plan.RESERVED_ZONE

        return coastplan