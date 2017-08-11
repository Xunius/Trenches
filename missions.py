import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP, MOUSEBUTTONDOWN
import levels
import sys


from Trenches import SCREEN_SIZE, SCREEN_DEPTH




def loadLevels():
    '''Get level info pack'''
    return levels.getAllLevels()


def loadLevel(level_num):

    #----Load level--------------------------
    level_str='level'+'%0*d' %(2,level_num)
    command='import levels.'+level_str+' as current_level'
    exec(command)
    level_info=current_level.LevelInfo()


    return level_info



def missions(screen,music_volume=0.5,effect_volume=0.5):
    #----Init--------------------------
    #pygame.init()
    #screen=initScreen(SCREEN_SIZE,SCREEN_FLAG,SCREEN_DEPTH)

    #----These has to be imported after pygame.init() and screen initialization-
    import ui
    import startlevel

    #----Create mission screen--------------------------
    level_pack=loadLevels()
    mission_screen=ui.createMissionScreen(level_pack)

    #----Main loop--------------------------
    clock=pygame.time.Clock()
    pygame.mouse.set_visible(True)
    GO=False
    
    while True:
        time_passed=clock.tick(30)

        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()

            if event.type==mission_screen.event_num:
                if mission_screen.button_pressed=='go':
                    GO=True
                elif mission_screen.button_pressed=='backtomain':
                    return 'backtomain'

            if event.type==MOUSEBUTTONDOWN:
                pressed_mouse=event.button
                mouse_pos=event.pos

                if  pressed_mouse==1:
                    mission_screen.clickActions(('mouse_down',1,mouse_pos),time_passed)

            if event.type==MOUSEBUTTONUP:
                released_mouse=event.button
                mouse_pos=event.pos

                if released_mouse==1:
                    mission_screen.clickActions(('mouse_up',1,mouse_pos),time_passed)

        if not GO:
            mission_screen.draw(screen,time_passed)
            mission_screen.updateTip(time_passed)
            pygame.display.flip()

        if GO:
            level_num=mission_screen.select_index+1

            while True:
                level_info=loadLevel(level_num)
                difficulty=mission_screen.difficulty

                #----Start level--------------------------
                choice=startlevel.startLevel(screen,SCREEN_SIZE,SCREEN_DEPTH,\
                        level_info,difficulty=difficulty,\
                        music_volume=music_volume,effect_volume=effect_volume,\
                        fullscreen=False)
                if choice=='backtomain':
                    GO=False
                    break
                elif choice=='go':
                    if level_num<len(level_pack):
                        mission_screen.select_index+=1
                        mission_screen.updateLevelInfo()
                    GO=False
                    break
                elif choice=='retry':
                    continue

if __name__=='__main__':
    missions()
