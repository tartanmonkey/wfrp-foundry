# career lists by context
tavern_clientele = ["Lawyer", "Physician", "Scholar", "Agitator", "Artisan", "Townsman", "Servant", "Bailiff", "Hunter", "Merchant", "Miner", "Villager", "Coachman", "Entertainer", "Messenger", "Pedlar", "Huffer", "Boatman", "Smuggler", "Stevedore", "Bawd", "Charlatan", "Racketeer", "Thief", "Protagonist", "Soldier"]
tavern_seedy_clientele = ["Agitator", "Artisan", "Townsman", "Servant", "Coachman", "Entertainer", "Messenger", "Pedlar", "Smuggler", "Stevedore", "Bawd", "Charlatan", "Racketeer", "Thief", "Protagonist", "Watchman", "Beggar", "Rat Catcher", "Grave Robber", "Outlaw", "Pit Fighter"]
town_folk = ["Townsman", "Villager", "Artisan", "Stevedore", "Boatman", "Servant"]
dock_gang = ["Stevedore", "Racketeer", "Protagonist", "Smuggler"]
guardian_band = ["Servant", "Hunter", "Villager", "Pedlar", "Stevedore", "Bawd", "Outlaw", "Soldier"]
bandit_gang = ["Hunter", "Soldier", "Outlaw", "Outlaw", "Villager", "Protagonist"]

# note members can also have a "magic" key
# level will randomize if 2 vals not equal, using 2nd as 'highest'
groups = {
    "card game": [{"number": (2, 5), "career": tavern_clientele, "level": (1, 2), "details": ["Default", "Captain", "None", "Motivated", "Quirky", "Conflict"]}],
    "river patrol": [
        {"number": (1, 1), "career": ["Riverwarden"], "level": (3, 3), "details": ["Captain"]},
        {"number": (3, 5), "career": ["Riverwarden"], "level": (2, 2), "details": ["Default", "None", "Motivated", "Quirky", "Conflict", "Basic"]},
        {"number": (1, 5), "career": ["Riverwarden"], "level": (1, 1), "details": ["Default", "None", "Motivated", "Quirky", "5e", "Basic"]}
    ],
    "tavern": [{"number": (3, 8), "career": tavern_clientele, "level": (1, 2), "details": ["Default", "Captain", "None", "Motivated", "Quirky", "5e", "Basic"]}],
    "seedy tavern": [{"number": (5, 12), "career": tavern_seedy_clientele, "level": (1, 2), "details": ["Default", "Captain", "None", "Motivated", "Quirky", "5e", "Basic"]}],
    "dock gang": [
            {"number": (1, 1), "career": ["Racketeer"], "level": (2, 3), "details": ["Motivated", "Basic"]},
            {"number": (2, 3), "career": dock_gang, "level": (2, 2), "details": ["None", "Basic"]},
            {"number": (1, 2), "career": dock_gang, "level": (1, 1), "details": ["None"]}
        ],
    "pit fight": [
                {"number": (2, 4), "career": ["Pit Fighter"], "level": (1, 3), "details": ["Default", "None", "Motivated", "Quirky", "Conflict", "Basic"]}
            ],
    "guardian band": [
            {"number": (1, 1), "career": ["Agitator", "Priest", "Soldier", "Entertainer"], "level": (2, 3), "details": ["Motivated", "Basic"]},
            {"number": (2, 6), "career": guardian_band, "level": (1, 2), "details": ["Default", "None", "Quirky", "Basic"]}
        ],
    "soldier squad": [
        {"number": (1, 1), "career": ["Soldier"], "level": (2, 3), "details": ["Captain"]},
        {"number": (3, 5), "career": ["Soldier"], "level": (2, 2), "details": ["Default", "None", "Motivated", "Quirky", "Conflict", "Basic"]},
        {"number": (1, 5), "career": ["Soldier"], "level": (1, 1), "details": ["Default", "None", "Quirky", "Basic"]}
    ],
    "caravan guards": [
            {"number": (1, 1), "career": ["Guard"], "level": (2, 3), "details": ["Captain"]},
            {"number": (3, 3), "career": ["Guard"], "level": (1, 2), "details": ["Default", "None", "Motivated", "Quirky", "Conflict", "Basic"]},
        ],
    "fist fight": [
                    {"number": (2, 5), "career": ["Pit Fighter", "Villager", "Stevedore", "Soldier", "Protagonist"], "level": (1, 3), "details": ["Default", "None", "Motivated", "Quirky", "Conflict", "Basic"]}
                ],
    "bandit gang": [
            {"number": (1, 1), "career": ["Outlaw"], "level": (2, 3), "details": ["Motivated", "Basic"]},
            {"number": (2, 6), "career": bandit_gang, "level": (1, 2), "details": ["Default", "None", "Quirky", "Basic"]}
        ]
}