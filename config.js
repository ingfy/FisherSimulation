{
    "world": {
        "structure": {
            "type": "grid",
            "width": 20,
            "height": 20,
            "good_spot_frequency": 0.1,
            "cell_width": 25,
            "cell_height": 25
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
        }
    },
    "aquaculture": {
        "num": 0,
        "priorities": {
            "OwnProfits":                    5.0,
            "SalmonPrice":                   2.0,
            "AquacultureIndustryExisting":   1.0
        }
    },
    "civilian": {
        "num": 100,
        "priorities": {
            "CommunityWealth":               4.0,
            "FishingIndustryExisting":       3.0,
            "AquacultureIndustryExisting":   3.0,
            "NonintrusiveAquaculture":       1.0
        }
    },
    "tourist": {
        "num": 30,
        "priorities": {
            "CommunityWealth":               1.0,
            "FishingIndustryExisting":       2.0,
            "NonintrusiveAquaculture":       2.0  
        }
    },
    "government": {
        "num": 1,
        "priorities": {
            "PopulationHappiness":           1.0     
        }
    },
    "aquaculture_spawner": {
        "spawn_interval": 20
    }
}