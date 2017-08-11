'''Define troop type specs
'''
import objects

images=objects.object_images



RIFLE={'image':images['riflesoldier'][0],\
        'image_info':images['riflesoldier'][1],\
        'ammo':20,\
        'speed':100,\
        'life':100\
        }
        
MACHINEGUN={'image':images['machinegunsoldier'][0],\
        'image_info':images['machinegunsoldier'][1],\
        'ammo':20,\
        'speed':90,\
        'life':100\
        }
        
GRENADE={'image':images['grenadesoldier'][0],\
        'image_info':images['grenadesoldier'][1],\
        'ammo':5,\
        'speed':100,\
        'life':100\
        }

SNIPER={'image':images['snipersoldier'][0],\
        'image_info':images['snipersoldier'][1],\
        'ammo':5,\
        'speed':100,\
        'life':100\
        }
MORTAR={'image':images['mortarsoldier'][0],\
        'image_info':images['mortarsoldier'][1],\
        'ammo':5,\
        'speed':70,\
        'life':100\
        }
ARTILLERY={'image':images['artillerysoldier'][0],\
        'image_info':images['artillerysoldier'][1],\
        'ammo':5,\
        'speed':60,\
        'life':100\
        }
FLAMER={'image':images['riflesoldier'][0],\
        'image_info':images['riflesoldier'][1],\
        'ammo':100,\
        'speed':80,\
        'life':100\
        }
MEDI={'image':images['medisoldier'][0],\
        'image_info':images['medisoldier'][1],\
        'ammo':100,\
        'speed':120,\
        'life':100\
        }

TROOP_DICT={'rifle':RIFLE,\
        'machinegun':MACHINEGUN,\
        'grenade':GRENADE,\
        'sniper':SNIPER,\
        'mortar':MORTAR,\
        'artillery':ARTILLERY,\
        'flamer':FLAMER,\
        'medi':MEDI\
        }
