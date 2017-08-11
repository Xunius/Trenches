'''Define game world parameters
'''

WEATHER_RANGE_FACTOR={'sunny':1.0,\
        'drizzle':0.95,\
        'rain':0.8,\
        'snow':0.7,\
        'thunder':0.8,\
        'fog':0.6}
WEATHER_SPEED_FACTOR={'sunny':1.0,\
        'drizzle':0.95,\
        'rain':0.8,\
        'snow':0.7,\
        'thunder':1.0,\
        'fog':0.9}
WEATHER_ACCURACY_FACTOR=WEATHER_RANGE_FACTOR

TERRAIN_SPEED_FACTOR={'grass':0.9,\
        'brick':1.0,\
        'snow':0.7,\
        'bush':0.7,\
        'sand':0.9,\
        'rock':0.7,\
        'puddle':0.7,\
        'forest':0.8,\
        'wire':0.4\
        }
TERRAIN_RANGE_FACTOR={'grass':1.0,\
        'brick':1.0,\
        'snow':1.0,\
        'bush':0.8,\
        'sand':1.0,\
        'rock':1.0,\
        'puddle':1.0,\
        'forest':0.8,\
        'wire':0.9\
        }

RANK={'soldier':range(0,6),\
        'private':range(6,11),\
        'private_1st':range(11,21),\
        'corporal':range(21,31),\
        'sergeant':range(31,41),\
        'staff_sergeant':range(41,51),\
        'sergeant_1st':range(51,61)\
        }
RANK_FACTOR={'soldier':1.0,\
        'private':1.05,\
        'private_1st':1.1,\
        'corporal':1.15,\
        'sergeant':1.2,\
        'staff_sergeant':1.25,\
        'sergeant_1st':1.3\
        }


DIFFICULTY_PAUSE_FACTOR={
        'Come on':1+0.3,\
        'Low':1+0.2,\
        'Mid':1,\
        'High':1-0.2,\
        'Are You Sure?':1-0.3\
        }
DIFFICULTY_ENEMY_AMMO_FACTOR={
        'Come on':1-0.4,\
        'Low':1-0.2,\
        'Mid':1,\
        'High':1+0.2,\
        'Are You Sure?':1+0.4\
        }
DIFFICULTY_ENEMY_ACCURACY_FACTOR={
        'Come on':30,\
        'Low':25,\
        'Mid':20,\
        'High':20,\
        'Are You Sure?':20\
        }
DIFFICULTY_PLAYER_ACCURACY_FACTOR={
        'Come on':10,\
        'Low':15,\
        'Mid':20,\
        'High':20,\
        'Are You Sure?':20\
        }
DIFFICULTY_MONEY_REPLENISH_FACTOR={
        'Come on':10,\
        'Low':8,\
        'Mid':5,\
        'High':4,\
        'Are You Sure?':3\
        }

DIFFICULTY_ENEMY_MISS_CHANCE={
        'Come on':45,\
        'Low':40,\
        'Mid':35,\
        'High':30,\
        'Are You Sure?':20\
        }
#----Whether enemy will choose least life soldier as target or not
DIFFICULTY_ENEMY_FOCUS_FIRE={
        'Come on':False,\
        'Low':False,\
        'Mid':False,\
        'High':True,\
        'Are You Sure?':True\
        }
