import pygame
import os


PATH=os.path.dirname(os.path.realpath(__file__))


BACKGROUND_FILE='image_background_1x600x1x800.png'
MASKMAP_FILE='image_via_map.png'
MINIMAP_FILE='image_minimap_1x600x1x800.png'

WEAPONS_IN_LEVEL=[
        'rifle',\
        'machinegun',\
        'grenade',\
        'mortar',\
        'sniper',\
        'medi',\
        'artillery',\
        'ammo'\
        ]

ENEMY_LIST1=[('rifle',3),('machinegun',3)]
ENEMY_LIST2=[('rifle',3),('machinegun',2),('grenade',2)]
ENEMY_LIST3=[('rifle',5),('machinegun',1),('mortar',2)]
ENEMY_LIST4=[('mortar',2),('sniper',1),('rifle',3)]
ENEMY_GROUPS=[ENEMY_LIST1,ENEMY_LIST2,ENEMY_LIST3,ENEMY_LIST4]
INTRA_GROUP_PAUSE=1500
INTER_GROUP_PAUSE=12000

ENEMY_AMMO_DICT={
        'rifle':10,\
        'machinegun':40,\
        'sniper':4,\
        'grenade':3,\
        'mortar':3,\
        'artillery':3\
        }

#----Should be smaller than weapons.max_weapon_ammo--------------------------
PLAYER_AMMO_DICT={
        'rifle':100,\
        'machinegun':250,\
        'grenade':20,\
        'mortar':20,\
        'artillery':20,\
	'sniper':40,\
	'medi':100,\
	'ammo':300\
        }



WEATHER='sunny'
MONEY=2500
HQ_LIFE=15
LEVEL='06'

LEVEL_TITLE='Challenge'
LEVEL_TEXTS=[\
        "Enhanced by the back-up forces, enemies at gate are barking even louder.",
        'We are faced with a big challenge.',
	' ',\
        'Dispatch army doctors to the trenches.',
	'They will try to save your men.',
	' '\
        ]

class LevelInfo(object):
    def __init__(self):

        self.level=LEVEL
        self.background_file=BACKGROUND_FILE
        self.maskmap_file=MASKMAP_FILE
        self.weapons_in_level=WEAPONS_IN_LEVEL

        self.background_file=os.path.join(PATH,BACKGROUND_FILE)
        self.maskmap_file=os.path.join(PATH,MASKMAP_FILE)
        self.minimap_file=os.path.join(PATH,MINIMAP_FILE)

        self.weapons_in_level=WEAPONS_IN_LEVEL

        #----Background for display--------------------------
        self.background_image=pygame.image.load(self.background_file).convert()

        #----Minimap for display--------------------------
        self.minimap_image=pygame.image.load(self.minimap_file).convert()

        #----Mask image for process--------------------------
        mask_image=pygame.image.load(self.maskmap_file).convert()
        self.mask_image=pygame.surfarray.array3d(mask_image)

        #----Mask image for display--------------------------
        #self.mask_background=pygame.image.load(self.maskmap_file).convert()

        #----Enemy setups--------------------------
        self.enemy_groups=ENEMY_GROUPS
        self.intra_pause=INTRA_GROUP_PAUSE
        self.inter_pause=INTER_GROUP_PAUSE

        #----Start up status--------------------------
        self.money=MONEY
        self.hq_life=HQ_LIFE
        self.weather=WEATHER

        #----Ammo--------------------------
        self.enemy_ammo_dict=ENEMY_AMMO_DICT
        self.player_ammo_dict=PLAYER_AMMO_DICT

        #----Info--------------------------
        self.title=LEVEL_TITLE
        self.texts=LEVEL_TEXTS
        
        



