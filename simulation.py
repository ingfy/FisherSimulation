import config
import entities
import world 
import sys
import agent
import directory
import time
import threading

## Simulation MAIN module ##
class Simulation():
    def __init__(self):
        threading.Thread.__init__(self)
        self._cfg = None
        self._want_abort = False
    
    def setup_config(self, cfg = None):
        self._cfg = config.load(varargs = None)
        
    def reset(self):
        self._directory = None
        self._map = None
        self._aquaculture_spawner = None
        
    def get_map(self):
        return self._map
        
    def initialize(self):
        assert self._cfg is not None, "Configuration not initiated. Run setup_config()"        
        self._directory = directory.Directory()
        self._agent_factory = entities.AgentFactory(self._directory, self._cfg)
        cfg_struct = self._cfg['world']['structure']
        gs = world.GridStructure(
            cfg_struct['width'], 
            cfg_struct['height'], 
            (cfg_struct['cell_width'], cfg_struct['cell_height']), 
            cfg_struct['good_spot_frequency']
        )
        self._map = world.Map(gs)
        self._map.populate_fishermen(self._agent_factory, self._cfg['fisherman']['num'])
        self._aquaculture_spawner = entities.AquacultureSpawner()
        self._steps = Steps(self)
        #self._map.get_structure().get_grid()[10][10].build_aquaculture(self._agent_factory.aquaculture())
        
    def abort(self):
        self._steps.abort()        
            
    def new_round(self):
        pass
        
    def start(self):
        self._steps.start()
        
class Steps(threading.Thread):
    threading.Thread.__init__(self)
    def __init__(self, simulation):
        self._simulation = simulation
        self._current_step = self.start
        self._want_abort = False
        
    def abort(self):
        self._want_abort = True
        
    def run(self):
        while not self._want_abort:
            self.round()
        
    def round(self):
        self.spawn_aquaculture_agent()
        self.vote()
        allow = self.government_decision()
        self.fishing()
        if allow:
            self.build_aquaculture()
        self.fishing()
        self.learning()
        
    def spawn_aquaculture_agent(self):
        self._current_step = self.spawn_aquaculture_agent
        
    def vote(self):
        self._current_step = self.vote
        
    def government_decision(self):
        self._current_step = self.government_decision
        return True
   
    def fishing(self):
        self._current_step = self.fishing
        
    def build_aquaculture(self):
        self._current_step = self.build_aquaculture
        
    def learning(self):
        self._current_step = self.learning
        
    
def main():
    s = Simulation()
    s.setup_config()
    s.initialize()
    s.start()
    s.join()
    return 0

if __name__ == "__main__":
    sys.exit(main())
