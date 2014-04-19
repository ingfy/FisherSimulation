{
    "global": {
        "num_max_complaints": 10,
        "max_hearing_rounds": 3
    },
    "world": {
        "structure": {
            "type": "grid",
            "width": 15,
            "height": 15,
            "good_spot_frequency": 0.1,
            "cell_width": 25,
            "cell_height": 25,
            "aquaculture blocking radius": 25
        }        
    },
    "interface": {
        "print messages":                   "False"
    },
    "fisherman": {
        "num": 20,
        "priorities": {
            "OwnProfits":                    10.0,
            "CommunityWealth":               2.0,
            "WildFishPrice":                 2.0,
            "FishingIndustryExisting":       3.0,
            "NaturalFishHealth":             2.0,
            "AquacultureIndustryExisting":   1.0
        },
        "learning mechanism": {
            "class": {
                "type":     "class",
                "class":    "FisherSimulation.ga.Evolution"
            },
            "config class": {
                "type":     "class",
                "class":    "FisherSimulation.ga.EvolutionConfig"
            },
            "phenotype class": {
                "type":     "class",
                "class":    "FisherSimulation.ga.FishermanVotingNN"
            },
            "genotype class": {
                "type":     "class",
                "class":    "FisherSimulation.ga.FishermanNNGenotype"
            },
            "elitism":                       3,
            "selection mechanism":           "rank selection",
            "crossover rate":                0.005,
            "mutation rate":                 0.005,
            "genome mutation rate":          0.00005
            
        },
        "voting mechanism class": {
            "type": "class",
            "class": "FisherSimulation.ga.FishermanVotingNN"
        }
    },
    "aquaculture": {
        "num": 0,
        "priorities": {
            "OwnProfits":                    5.0,
            "SalmonPrice":                   2.0,
            "AquacultureIndustryExisting":   1.0
        },
        "voting mechanism class": {
            "type":     "class",
            "class":    "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "civilian": {
        "num": 100,
        "priorities": {
            "CommunityWealth":               4.0,
            "FishingIndustryExisting":       3.0,
            "AquacultureIndustryExisting":   3.0,
            "NonintrusiveAquaculture":       1.0
        },
        "voting mechanism class":           {
            "type": "class",
            "class": "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "tourist": {
        "num": 30,
        "priorities": {
            "CommunityWealth":               1.0,
            "FishingIndustryExisting":       2.0,
            "NonintrusiveAquaculture":       2.0  
        },
        "voting mechanism class":           {
            "type": "class",
            "class": "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "government": {
        "num": 1,
        "priorities": {
        }
    },
    "municipality": {
        "num": 1,
        "priorities": {
        }
    },
    "aquaculture_spawner": {
        "spawn_interval": 20
    }
}