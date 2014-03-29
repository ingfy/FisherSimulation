import config
import entities
import world 
import sys
import agent
import market
import phases
import directory
import do
import time
import ga
import multiprocessing

class SimulationInfo(object):
    def __init__(self, map, cfg, directory, market, agent_factory, 
            aquaculture_spawner, learning_mechanisms):
        self.map = map
        self.cfg = cfg
        self.directory = directory
        self.market = market
        self.agent_factory = agent_factory
        self.aquaculture_spawner = aquaculture_spawner
        self.learning_mechanisms = learning_mechanisms
        

## Simulation MAIN module ##
class Simulation(object):
    def __init__(self):
        self._cfg = None
        self._round = None
    
    def setup_config(self, cfg = None):
        self._cfg = config.load(varargs = None)
        
    def initialize(self):
        assert not self._cfg is None, \
            "Configuration not initiated. Run setup_config()"        
            
        dir = directory.Directory()
        agent_factory = entities.AgentFactory(dir, self._cfg)
        
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
            agent_factory, 
            self._cfg['fisherman']['num']
        )
        aquaculture_spawner = entities.AquacultureSpawner()
        
        # Learning mechanisms
        ## Fishermen
        fisherman_learning = ga.Evolution(
            ga.FishermanNNGenotype,
            ga.FishermanNN,
            dir.get_agents(type = entities.Fisherman),
            ga.EvolutionConfig.from_dict(self._cfg['fisherman']['evolution'])
        )
        
        info = SimulationInfo(
            map, 
            self._cfg, 
            dir, 
            market.Market(),
            agent_factory, 
            aquaculture_spawner,
            {
                entities.Fisherman: fisherman_learning
            }
        )
                
        self._round = phases.Round(info)
        
        return do.Simulation.from_simulation_info(info)
    
    def step(self):
        result = self._round.next()
        return do.PhaseReport.from_step_result(result)
    
def main():
    s = Simulation()
    s.setup_config()
    map = s.initialize()
    result1 = s.step()
    result2 = s.step()
    result3 = s.step()
    result4 = s.step()
    result5 = s.step()
    return 0

if __name__ == "__main__":
    sys.exit(main())