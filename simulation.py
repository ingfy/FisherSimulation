import config
import entities
import world 
import sys
import agent
import phases
import directory
import time
import multiprocessing

class SimulationInfo(object):
    def __init__(self, map, cfg, directory, aquaculture_spawner):
        self.map = map
        self.cfg = cfg
        self.directory = directory
        self.agent_factory = agent_factory
        self.aquaculture_spawner = aquaculture_spawner

## Simulation MAIN module ##
class Simulation(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self._cfg = None
        self._want_abort = False
        self._round = Round(self)
    
    def setup_config(self, cfg = None):
        self._cfg = config.load(varargs = None)
        
    def reset(self):
        self._directory = None
        self._map = None
        self._aquaculture_spawner = None
        
    def get_map(self):
        return self._map
        
    def initialize(self):
        assert self._cfg is not None, 
            "Configuration not initiated. Run setup_config()"        
        directory = directory.Directory()
        agent_factory = entities.AgentFactory(self._directory, self._cfg)
        
        # Create government and municipality,
        # which are automatically registered
        # to the directory by their 
        # constructors
        agent_factory.government()
        agent_factory.municipality()
        
        cfg_struct = self._cfg['world']['structure']
        gs = world.GridStructure(
            cfg_struct['width'], 
            cfg_struct['height'], 
            (cfg_struct['cell_width'], cfg_struct['cell_height']), 
            cfg_struct['good_spot_frequency']
        )
        map = world.Map(gs)
        map.populate_fishermen(
            self._agent_factory, 
            self._cfg['fisherman']['num']
        )
        aquaculture_spawner = entities.AquacultureSpawner()
        self._round = phases.Round(SimulationInfo(
            map, 
            self._cfg, 
            directory, 
            agent_factory, 
            aquaculture_spawner
        ))
    
    def step(self):
        result = self._round.next()
        return do.PhaseReport.from_step_result(result)
   
    def run_rounds(self, rounds):
        while not self._want_abort and self._round.rounds() < rounds:
            self._round.next()
        if not self._want_abort:
            self.wait()
        
    def run_steps(self, steps):
        while not self._want_abort and steps > 0:
            self._round.next()
            steps -= 1
        if not self._want_abort:
            self.wait()
            
    def run_inf(self):
        while not self._want_abort:
            self._round.next()
        
    def abort(self):
        self._want_abort = True
                    
    def run(self):
        self.wait()
    
def main():
    s = Simulation()
    s.setup_config()
    s.initialize()
    s.start()
    s.join()
    return 0

if __name__ == "__main__":
    sys.exit(main())