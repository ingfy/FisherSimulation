{
    "world": {
        "structure": {
            "type": "grid",
            "width": 20,
            "height": 20,
            "good_spot_frequency": 0.1,
            "cell_width": 25,
            "cell_height": 25,
            "aquaculture blocking radius": 25
        }
    },
    "fisherman": {
        "num": 25,
        "priorities": {
            "OwnProfits":                    5.0,
            "CommunityWealth":               2.0,
            "WildFishPrice":                 2.0,
            "FishingIndustryExisting":       3.0,
            "NaturalFishHealth":             2.0,
            "AquacultureIndustryExisting":   1.0
        },
        "learning mechanism": {
            "class": {
                "type":     "class",
                "class":    "ga.Evolution"
            },
            "config class": {
                "type":     "class",
                "class":    "ga.EvolutionConfig"
            },
            "phenotype class": {
                "type":     "class",
                "class":    "ga.FishermanVotingNN"
            },
            "genotype class": {
                "type":     "class",
                "class":    "ga.FishermanNNGenotype"
            },
            "elitism":                       3,
            "selection mechanism":           "rank selection",
            "crossover rate":                0.005,
            "mutation rate":                 0.005,
            "genome mutation rate":          0.00005
            
        },
        "voting mechanism class": {
            "type": "class",
            "class": "ga.FishermanVotingNN"
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
            "class":    "ga.FishermanVotingNN"
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
        "voting mechanism class":           "ga.FishermanVotingNN"
    },
    "tourist": {
        "num": 30,
        "priorities": {
            "CommunityWealth":               1.0,
            "FishingIndustryExisting":       2.0,
            "NonintrusiveAquaculture":       2.0  
        },
        "voting mechanism class":           "ga.FishermanVotingNN"
    },
    "government": {
        "num": 1,
        "priorities": {
            "PopulationHappiness":           1.0     
        }
    },
    "municipality": {
        "num": 1,
        "priorities": {
            "PopulationHappiness":           1.0     
        }
    },
    "aquaculture_spawner": {
        "spawn_interval": 20
    }
}