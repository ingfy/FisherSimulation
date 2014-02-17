import config
import entities
import world 
import sys
import agent
import directory
import time
import threading

## Simulation MAIN module ##
class Simulation(threading.Thread):
    _cfg = None
    _want_abort = False
    
    def __init__(self):
        threading.Thread.__init__(self)
    
    def setup_config(self, cfg = None):
        self._cfg = config.load(varargs = None)
        
    def reset(self):
        self._directory = None
        self._map = None
        
    def get_map(self):
        return self._map
        
    def initialize(self):
        if self._cfg is None:
            raise MissingConfigurationException("Configuration not instantiated. Run setup_config()")
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
        
    def abort(self):
        self._want_abort = True
        
    def loop(self):
        while not self._want_abort:
            time.sleep(0.1)
            
        
    def run(self):
        print [str(s) for s in self._map.get_radius(100, (4, 4))]
        self.loop()
        
    
def main():
    s = Simulation()
    s.setup_config()
    s.initialize()
    s.start()
    s.join()
    return 0
    
class MissingConfigurationException(Exception): pass

if __name__ == "__main__":
    sys.exit(main())
