{
    "global": {
        "num max complaints":     10,
        "max hearing rounds":     3,
        "aquaculture in blocked": false
    },
    "world": {
        "structure": {
            "class": {
                "type":  "class",
                "class": "FisherSimulation.world.GridStructure"
            },
            "width":                       15,
            "height":                      15,
            "cell width":                  25,
            "cell height":                 25,
            "aquaculture blocking radius": 25,
            "neighbourhood type":          "von_neumann"
        },
        "good spot frequency": 0.1
    },
    "interface": {
        "print messages": true
    },
    "fisherman": {
        "num":        20,
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
                "type":  "class",
                "class": "FisherSimulation.ga.Evolution"
            },
            "phenotype class": {
                "type":  "class",
                "class": "FisherSimulation.ga.FishermanVotingRules"
            },
            "genotype class": {
                "type":  "class",
                "class": "FisherSimulation.ga.FishermanRulesGenotype"
            },
            "elitism":              3,
            "selection mechanism":  "rank selection",
            "crossover rate":       0.005,
            "mutation rate":        0.005,
            "genome mutation rate": 0.00005
            
        },
        "voting mechanism class": {
            "type":  "class",
            "class": "FisherSimulation.ga.FishermanVotingRules"
        }
    },
    "aquaculture": {
        "priorities": {},
        "voting mechanism class": {
            "type":  "class",
            "class": "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "civilian": {
        "num":        0,
        "priorities": {},
        "voting mechanism class": {
            "type": "class",
            "class": "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "tourist": {
        "num":        0,
        "priorities": {},
        "voting mechanism class": {
            "type": "class",
            "class": "FisherSimulation.vote.AlwaysApprove"
        }
    },
    "government": {
        "priorities": {}
    },
    "municipality": {
        "priorities": {}
    }
}