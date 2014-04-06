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
        
    def get_default_config_filename(self):
        return config.cfg_json_filename
    
    def setup_config(self, filename=None):
        if not filename is None:
            cfg = config.load(varargs=None, filename=filename)
        else:
            cfg = config.load(varargs=None)
        self._cfg = cfg
        
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
        map = world.Map(gs, 
            self._cfg['world']['structure']['aquaculture blocking radius']
        )
        map.populate_fishermen(
            agent_factory, 
            self._cfg['fisherman']['num']
        )
        fishermen = dir.get_agents(type=entities.Fisherman)
        # Add voting mechanism
        for a in fishermen:
            self._cfg['fisherman']['voting mechanism class'].new(
                a,
                self._cfg['fisherman'],
                map
            )
        
        aquaculture_spawner = entities.AquacultureSpawner(
            self._cfg['aquaculture']['voting mechanism class'],
            self._cfg['aquaculture'],
            map
        )
        
        # Learning mechanisms
        
        agent_types_config_name = {
            entities.Fisherman: "fisherman",
            entities.Aquaculture: "aquaculture",
            entities.Civilian: "civilian",
            entities.Tourist: "tourist",
            entities.Government: "government",
            entities.Municipality: "municipality"            
        }
        
        learning_mechanisms = {}
        
        for entity in agent_types_config_name:
            name = agent_types_config_name[entity]
            if "learning mechanism" in self._cfg[name]:
                learning = self._cfg[name]["learning mechanism"]["class"]
                config = self._cfg[name]["learning mechanism"]["config class"]
                learning_mechanisms[entity] = learning(
                    dir.get_agents(type = entity),
                    config.from_dict(self._cfg[name]["learning mechanism"])
                )
        
        ## Fishermen
        # fishermen_learning_class = \
            # self._cfg['fisherman']['learning mechanism']['class']
        # fishermen_learning_config_class = \
            # self._cfg['fisherman']['learning mechanism']['config class']
        # fisherman_learning = fishermen_learning_class(
            # dir.get_agents(type = entities.Fisherman),
            # fishermen_learning_config_class.from_dict(
                # self._cfg['fisherman']['learning mechanism']
            # )
        # )
        
        info = SimulationInfo(
            map, 
            self._cfg, 
            dir, 
            market.Market(),
            agent_factory, 
            aquaculture_spawner,
            learning_mechanisms
        )
                
        self._round = phases.Round(info)
        
        return do.Simulation.from_simulation_info(info)
        
    def get_current_phase(self):
        return self._round.current()
    
    def step(self):
        result = self._round.next()
        report = do.PhaseReport.from_step_result(result)
        #print '\n'.join([str(m) for m in report.messages])
        return report
    
def main():
    s = Simulation()
    s.setup_config()
    map = s.initialize()
    result1 = s.step()
    result2 = s.step()
    result3 = s.step()
    result4 = s.step()
    result5 = s.step()
    result6 = s.step()
    result7 = s.step()
    result8 = s.step()
    return 0

if __name__ == "__main__":
    sys.exit(main())