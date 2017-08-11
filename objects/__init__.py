'''Load images for various game objects and icons
'''
from generals import interpName
import pygame
import os
import generals

PATH=os.path.dirname(os.path.realpath(__file__))

IMAGE_FILES={
    'EXPLODE1_FILE'     : 'ani_explode1_1x160x9x160.png',
    'EXPLODE2_FILE'     : 'ani_explode2_1x150x7x150.png',
    'EXPLODE3_FILE'     : 'ani_explode3_1x170x7x170.png',
    'GRENADE_FILE'      : 'ani_grenade_1x20x8x20.png',

    'RIFLESOLDIER_FILE'      : 'image_riflesoldier_1x40x4x40.png',
    'MACHINEGUNSOLDIER_FILE' : 'image_machinegunsoldier_1x40x4x40.png',
    'GRENADESOLDIER_FILE'    : 'image_grenadesoldier_1x40x5x40.png',
    'MORTARSOLDIER_FILE'     : 'image_mortarsoldier_1x40x5x40.png',
    'SNIPERSOLDIER_FILE'     : 'image_snipersoldier_1x40x4x40.png',
    'ARTILLERYSOLDIER_FILE'  : 'image_artillerysoldier_1x40x2x40.png',
    'MEDISOLDIER_FILE'      : 'image_medisoldier_1x40x4x40.png',

    'GREENCIRCLE_FILE'  : 'image_greencircle_1x140x6x140.png',
    'INSIGNIA_FILE'     : 'image_insignia_1x20x6x12.png',
    'MORTARSHELL_FILE'  : 'image_mortarshell_1x10x1x30.png',
    'BOXEDGE_FILE'      : 'image_boxedge_1x40x2x40.png',
    'BLINK_FILE'        : 'ani_blink_1x30x3x30.png',
    'RIFLEBULLET_FILE'  : 'image_riflebullet_1x3x1x10.png',
    'SNIPERBULLET_FILE' : 'image_sniperbullet_1x5x1x20.png',
    'EXCLAMATION_FILE'  : 'image_exclamation_1x15x1x15.png',
    'BLOOD_FILE'        : 'ani_blood_1x30x2x30.png',
    'HEAL_FILE'         : 'ani_heal_1x40x3x40.png',
    'AMMOBOX_FILE'      : 'image_ammobox_1x40x1x40.png'
}

NEED_SCALING=[
    'INSIGNIA_FILE',
    'MORTARSHELL_FILE',
    'BLINK_FILE',
    'EXCLAMATION_FILE',
    'BLOOD_FILE',
    ]



def LoadImages():

    images={}
    for kk,vv in IMAGE_FILES.items():
        img=pygame.image.load(os.path.join(PATH,vv)).convert_alpha()
        img_info=interpName(vv)
        if kk in NEED_SCALING:
            img=generals.scaleImage(img,img_info)
        images[kk.split('_')[0].lower()]=[img,img_info]

    return images


object_images=LoadImages()
