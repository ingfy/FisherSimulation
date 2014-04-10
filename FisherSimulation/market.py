"""Market module includes state and behavior for the market, where agents
sell their harvest."""

class Market(object):
    """Market for buying and selling fish."""

    def __init__(self):
        self._prices = {
            "wild fish":    1.0,
            "farmed fish":  1.0
        }

    def get_wild_fish_price(self):
        """Returns the current price of wild fish."""
        return self._prices["wild fish"]

    def get_farmed_fish_price(self):
        """Returns the current price of farmed fish."""
        return self._prices["farmed fish"]
