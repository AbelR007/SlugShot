
regions = {
    "Wild Western Caverns": {
        "Shane Hideout": ["Kord Zane", "Pronto", "Trixie"],
        "Wild Spores Cavern": ["Pronto"],
        "Dark Spores Cavern": ["Pronto", "Trixie"],
        "Herringbone Cavern": ["Pronto"],
        "Rocklock Cavern": ["Kord Zane"],
    },
}

question_mark = "<:question_mark:976450883049111582>"
items = {
    'fire slug food':
        [20,'<:fire_food:979751145343950888>','Slug food for the Fire Type Slugs'],
    'water slug food': 
        [20,'<:water_food:979751175463247882>','Slug food for the Water Type Slugs'],
    'energy slug food': 
        [20,'<:energy_food:979751168785940481>','Slug food for the Energy Type Slugs'],
    'earth slug food': 
        [20,'<:earth_food:979751165648592956>','Slug food for the Earth Type Slugs'],
    'air slug food': 
        [20,'<:air_food:979751161328439316>','Slug food for the Air Type Slugs'],

    'damage enhancer':
        [2000, question_mark, "Increases damage of a slug by 10%. Efficient for a high damage dealing slug."],
    'defense boost':
        [2000, question_mark, "Increases defense of a slug by 10%. Efficient for defending high damage slugs."],

    'common box':
        [500, question_mark, "Regular Box with chances of slug and unique items."],
    'rare box':
        [1500, question_mark, "Rare Box with higher chances of slugs"],
    'mythic box':
        [3000, question_mark, "Mythic Box with higher chances for unique items than a rare box"],
    'legendary box':
        [10000, question_mark, "Legendary Box with guaranteed chance of slug and many other unique items"],

    # 'common box','rare box','mythical box','legendary box'
}

box_positions = [
    'a1','b1','c1','d1','e1',
    'a2','b2','c2','d2','e2',
    'a3','b3','c3','d3','e3',
    'a4','b4','c4','d4','e4',
    'a5','b5','c5','d5','e5'
]

locations = {
    "Wild Western Caverns": {
        "Shane Hideout": 1,
        "Wild Spores Cavern": 2,
        "Dark Spores Cavern": 3,
        "Herringbone Cavern": 4,
        "Rocklock Cavern": 6,
    },
    "Northern Caverns": {
        "Chillbore Cavern": 1,
        "Northern Cavern": 3,
        "Snowdance Cavern": 6,
    }
}

char_regions = {
    "Wild Western Caverns": {
        "Shane Hideout": ["Kord Zane", "Pronto", "Trixie"],
        "Wild Spores Cavern": ["Pronto"],
        "Dark Spores Cavern": ["Pronto","Trixie"],
        "Herringbone Cavern": ["Pronto"],
        "Rocklock Cavern": ["Kord Zane"],
    },
}

slugs_chance = {
    "Shane Hideout": {
        "common": ['rammstone', 'hop rock'],
        "uncommon": ['armashelt', 'arachnet', ],
        "legendary": ['infurnus'],
    },
    "Wild Spores Cavern": {
        "common": ['flatulorhinkus'],
        "uncommon": ['flaringo'],
        "rare": ['bubbaleone'],
        "super rare": ['frostcrawler'],
        # "mythical": ['thugglet'],
    },
    "Dark Spores Cavern": {
        "common": ['flatulorhinkus'],
        "rare": ['speedstinger'],
        "super rare": ['grenuke', 'frightgeist'],
    },
    "Herringbone Cavern": {
        "uncommon": ['speedstinger'],
        "rare": ['grenuke', 'armashelt'],
    },
    "Rocklock Cavern": {
        "common": ['hop rock'],
        "uncommon": ['arachnet', 'rammstone'],
        "super rare": ['grenuke'],
    }
}
