'''Define specs of weapons
'''
import random
import objects
import generals
import sounds


images=objects.object_images
sound_manager=sounds.SoundManager()



RIFLE={'weapon_type':'rifle',\
        'fire_range':230,\
        'damage_range':5,\
        'height':None,\
        'top_damage':10,\
        'fire_rate':500,\
        #'image':RIFLE_IMAGE,\
        'images':generals.splitImage(*images['riflebullet']),\
        #'image':images['bullet'][0],\
        #'image_info':images['bullet'][1],\
        'speed':900,\
        'life':1,\
        'sounds':sound_manager.all_sounds['rifle']\
        }

MACHINEGUN={'weapon_type':'machinegun',\
        'fire_range':230,\
        'damage_range':5,\
        'height':None,\
        'top_damage':5,\
        'fire_rate':50,\
        #'image':RIFLE_IMAGE,\
        'images':generals.splitImage(*images['riflebullet']),\
        #'image':images['bullet'][0],\
        #'image_info':images['bullet'][1],\
        'speed':900,\
        'life':1,\
        'sounds':sound_manager.all_sounds['machinegun']\
        }

SNIPER={'weapon_type':'sniper',\
        'fire_range':450,\
        'damage_range':5,\
        'height':None,\
        'top_damage':70,\
        'fire_rate':1500,\
        #'image':RIFLE_IMAGE,\
        'images':generals.splitImage(*images['sniperbullet']),\
        #'image':images['bullet'][0],\
        #'image_info':images['bullet'][1],\
        'speed':1300,\
        'life':3,\
        'sounds':sound_manager.all_sounds['sniper']\
        }

GRENADE={'weapon_type':'grenade',\
        'fire_range':170,\
        'min_fire_range':60,\
        'damage_range':80,\
        'height':60,\
        'top_damage':50,\
        'fire_rate':1500,\
        #'image':GRENADE_IMAGE,\
        'images':generals.splitImage(*images['grenade']),\
        #'image':images['grenade'][0],\
        #'image_info':images['grenade'][1],\
        'speed':500,\
        'life':1,\
        'launch_sounds':[],\
        'explode_sounds':sound_manager.all_sounds['grenade']\
        }
    
MORTAR={'weapon_type':'mortar',\
        'fire_range':340,\
        'min_fire_range':130,\
        'damage_range':130,\
        'height':320,\
        'top_damage':60,\
        'fire_rate':1700,\
        #'image':GRENADE_IMAGE,\
        'images':generals.splitImage(*images['mortarshell']),\
        #'image':images['mortarshell'][0],\
        #'image_info':images['mortarshell'][1],\
        'speed':1200,\
        'life':1,\
        'launch_sounds':sound_manager.all_sounds['launcher'],\
        'explode_sounds':sound_manager.all_sounds['grenade']\
        }


ARTILLERY={'weapon_type':'artillery',\
        'fire_range':460,\
        'min_fire_range':200,\
        'damage_range':150,\
        'height':500,\
        'top_damage':70,\
        'fire_rate':1800,\
        #'image':GRENADE_IMAGE,\
        'images':generals.splitImage(*images['mortarshell']),\
        #'image':images['mortarshell'][0],\
        #'image_info':images['mortarshell'][1],\
        'speed':1400,\
        'life':1,\
        'launch_sounds':sound_manager.all_sounds['launcher'],\
        'explode_sounds':sound_manager.all_sounds['artillery']\
        }

'''
FLAMER={'weapon_type':'flamer',\
        'fire_range':200,\
        'damage_range':50,\
        'top_damage':40,\
        'fire_rate':300,\
        #'image':GRENADE_IMAGE,\
        'image':images['mortarshell'][0],\
        'image_info':images['flamer'][1],\
        'speed':600,\
        'life':1}
'''
MEDI={'weapon_type':'medi',\
        'fire_range':250,\
        'damage_range':0,\
        'height':None,\
        'top_damage':10,  #Of course this should be added to life\
        'fire_rate':1000,\
        #'image':GRENADE_IMAGE,\
        #'image':images['medi'][0],\
        #'image_info':images['medi'][1],\
        'images':[],\
        'speed':0,\
        'life':1,\
        'sounds':None\
        }
AMMO={'load':300,\
      'life':50,\
      'fire_range':300,\
      'recharge_rate':200,\
      'images':generals.splitImage(*images['ammobox'])\
      }

WEAPON_PRICES={
        'rifle':100,\
        'machinegun':200,\
        'grenade':250,\
        'mortar':300,\
        'sniper':1000,\
        'flamer':700,\
        'medi':300,\
        'ammo':100,\
        'artillery':1000\
        }
MAX_WEAPON_AMMO={
        'rifle':100,\
        'machinegun':250,\
        'grenade':20,\
        'mortar':20,\
        'sniper':40,\
        'medi':100,\
        'ammo':300,\
        'artillery':30\
        }

WEAPON_DICT={'rifle':RIFLE,\
        'machinegun':MACHINEGUN,\
        'grenade':GRENADE,\
        'sniper':SNIPER,\
        'mortar':MORTAR,\
        'artillery':ARTILLERY,\
        #'flamer':FLAMER,\
        'medi':MEDI,\
        'ammo':AMMO\
        }
WEAPON_ACCURACY_FACTOR={'rifle':0.9,\
        'machinegun':0.8,\
        'sniper':0.95,\
        'flamer':0.8,\
        'grenade':0.8,\
        'mortar':0.7,\
        'artillery':0.75\
        }

EXPLOSIONS={
        'explode1':{
            'images':images['explode1'][0],\
            'image_info':images['explode1'][1],\
            'time':1000\
            },\
        'explode2':{
            'images':images['explode2'][0],\
            'image_info':images['explode2'][1],\
            'time':1000\
            },
        'explode3':{
            'images':images['explode3'][0],\
            'image_info':images['explode3'][1],\
            'time':1000\
            }
        }


def getRandomExplosion():

    return EXPLOSIONS[random.choice(EXPLOSIONS.keys())]



