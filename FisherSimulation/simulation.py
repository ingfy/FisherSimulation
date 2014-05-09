"""Module for initializing and running the simulation."""

from collections import namedtuple

from config import config
from FisherSimulation import entities
from FisherSimulation import world
from FisherSimulation import market
from FisherSimulation import phases
from FisherSimulation import directory
from FisherSimulation import do
from FisherSimulation import log

## Simulation MAIN module ##
class Simulation(object):
    """Master class for setting up and stepping through the simulation."""

    def __init__(self):
        self._cfg = None
        self._round = None

    def setup_config(self, filename=None):
        """Loads the configuration and makes sure it is processed.

        Arguments:
            filename    The relative path (from project directory) of a
                        configuration file.
        """
        if not filename is None:
            cfg = config.load(varargs=None, filename=filename)
        else:
            cfg = config.load(varargs=None)
        self._cfg = cfg

    def initialize(self):
        """Initializes the map and entities in the simulation.

        Returns:
            A SimulationInfo instance from the do module, describing the
            simulation properties.
        """

        assert not self._cfg is None, \
            "Configuration not initiated. Run setup_config()"

        logger = log.Logger.new()

        agent_directory = directory.Directory()
        agent_factory = entities.AgentFactory(agent_directory, self._cfg)

        # Create government and municipality,
        # which are automatically registered
        # to the directory by their
        # constructors
        agent_factory.government()
        agent_factory.municipality()

        structure = self._cfg['world']['structure']['class'](
            self._cfg['world']['structure'],
            self._cfg['world']['good spot frequency']
        )
        worldmap = world.Map(structure)
        worldmap.populate_fishermen(
            agent_factory,
            self._cfg['fisherman']['num']
        )
        fishermen = agent_directory.get_agents(type=entities.Fisherman)
        # Add voting mechanism
        for fisher in fishermen:
            self._cfg['fisherman']['voting mechanism class'].new(
                fisher,
                self._cfg['fisherman'],
                worldmap
            )

        aquaculture_spawner = entities.AquacultureSpawner(
            self._cfg['aquaculture']['voting mechanism class'],
            self._cfg['aquaculture'],
            self._cfg["global"]["aquaculture in blocked"],
            worldmap
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
                mechanism_config = self._cfg[name]["learning mechanism"]
                learning_mechanisms[entity] = learning(
                    agent_directory.get_agents(type=entity),
                    mechanism_config
                )

        simulation_info = namedtuple("SimulationInfo", [
            "map",
            "cfg",
            "directory",
            "market",
            "agent_factory",
            "aquaculture_spawner",
            "learning_mechanisms",
            "logger"
        ])

        info = simulation_info(
            worldmap,
            self._cfg,
            agent_directory,
            market.Market(),
            agent_factory,
            aquaculture_spawner,
            learning_mechanisms,
            logger
        )

        self._round = phases.Round(info)

        return do.Simulation.from_simulation_info(info, self._cfg)

    def get_current_phase(self):
        """Returns the current phase of the simulation."""
        return self._round.current()

    def step(self):
        """Processes one step of the simulation.
        Returns:
            A do.PhaseReport instance describing the results of the phase.
        """
        result = self._round.next()
        phase = self.get_current_phase()
        return do.PhaseReport.from_step_result(result, phase)
