import entities
import world
import priorityutil
import do
import priority
import simulation

class Interface(object):
    def __init__(self):
        self._s = simulation.Simulation()

    def get_map(self):
        return do.Map.from_world_map(self._s.get_map())
        
    def abort(self):
        self._s.abort()
        
    def setup_config(self, cfg=None):
        self._s.setup_config()

    def start_simulation(self):
        self._s.initialize()
        self._s.start()