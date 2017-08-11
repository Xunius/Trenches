'''Run game level.

The main function startLevel() is called from missions.py, and this script
can also be run as standalone for debugging main game play.
'''

#----------------------Import----------------------
import pygame
from pygame.locals import QUIT, FULLSCREEN, HWSURFACE, DOUBLEBUF
from pygame.locals import KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from generals import window2Grid, prepareEndingText
import sys
import intel
import threading
import Queue


#---------------------Globals---------------------
from Trenches import SCREEN_SIZE, SCREEN_FLAG, SCREEN_DEPTH, __version__
TOP_PANEL_WIDTH=40
TOPLEFT=(0,TOP_PANEL_WIDTH)
GRID_SIZE=(40,40)

GOD_MOD=False
FRIEND_DAMAGE=False



        

#--------Initiate pygame and return screen.--------
def initScreen(screen_size,screen_flag,screen_depth,verbose=True):
    '''Initiate pygame and return screen.

    screen_size,screen_flag,screen_depth
    '''

    pygame.mixer.pre_init(44100,16,2,4096)
    pygame.mixer.set_num_channels(50)
    screen=pygame.display.set_mode(screen_size,screen_flag,screen_depth)
    pygame.display.set_caption('TRENCHES %s' %__version__)
    return screen




def startLevel(screen,screen_size,screen_depth,level_info,\
        difficulty,music_volume,effect_volume,fullscreen):

    #----These has to be imported after pygame.init() and
    # screen initialization-
    import game_class
    import ui
    import sounds

    #----Globals--------------------------
    top_panel_width=TOP_PANEL_WIDTH
    topleft=TOPLEFT
    grid_size=GRID_SIZE

    #----Create scene--------------------------
    scene=game_class.GameScene(level_info,screen,\
            effect_volume=effect_volume,difficulty=difficulty,\
            player_name='player',friend_damage=FRIEND_DAMAGE)

    #----Create window elements--------------------------
    menu_button=ui.createMenuButton()
    scroll_bar=ui.createScrollMenu(scene,level_info)
    intel_bar=ui.createIntelBar()
    money_bar=ui.createMoneyBar()
    hq_bar=ui.createHqBar()

    #----Create pause screen--------------------------
    pause_screen=ui.createPauseScreen()

    #----Create option screen--------------------------
    option_screen=ui.createOptionScreen()

    #----Create enemy spawn--------------------------
    enemy_spawn=game_class.EnemySpawn(scene)

    #----Create barrack--------------------------
    barrack=game_class.Barrack(scene)

    #----Intel centre--------------------------
    intel_center=intel.IntelCenter(scene,enemy_spawn)
    scene.addIntelCenter(intel_center)

    #----Create gameover box--------------------------
    gameover_box=ui.createGameOver()
    
    #----Create thread lock--------------------------
    thread_lock=threading.Lock()
    scene.thread_lock=thread_lock

    '''
    soldier_lock=threading.Lock()
    scene.soldier_lock=soldier_lock
    '''

    #----Create music/sound threads--------------------------
    sound_queue=Queue.Queue()
    scene.sound_queue=sound_queue

    sound_threads=[]
    for ii in range(6):
        sound_threadii=sounds.SoundThread(sound_queue,thread_lock,\
                effect_volume,screen_size[0])
        sound_threadii.setDaemon(True)
        sound_threads.append(sound_threadii)
        sound_threadii.start()

    #----Create soldier queue and threads--------------------------
    '''
    soldier_queue=Queue.Queue()
    scene.soldier_queue=soldier_queue
    
    soldier_threads=[]
    for ii in range(10):
        threadii=game_class.SoldierThread(soldier_queue,soldier_lock,\
                scene.surface)
        threadii.setDaemon(True)
        soldier_threads.append(threadii)
        threadii.start()
    '''


    #----Main loop--------------------------
    clock=pygame.time.Clock()
    pygame.mouse.set_visible(True)
    WIN=False
    PAUSED=False
    GAME_OVER=False
    GOT_END_TEXT=False
    OPTION=False

    music_thread=sounds.MusicThread(PAUSED,thread_lock)
    sounds.sound_manager.loadMusic('battle')
    music_thread.start()
    pygame.mixer.music.set_volume(music_volume)

    picked_up_troop=None
    FPS=30
    
    while True:
        '''
        if len(scene.all_troops)>15:
            FPS=20
        elif len(scene.all_troops)<=15 and len(scene.all_troops)>10:
            FPS=15
        '''
        time_passed=clock.tick(FPS)

        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()

            if event.type==menu_button.PAUSE_EVENT:
                PAUSED=True
            if event.type==pause_screen.event_num:
                buttonii=pause_screen.button_pressed
                if buttonii=='resume':
                    PAUSED=False
                    pygame.mixer.music.unpause()
                elif buttonii=='option':
                    PAUSED=True
                    OPTION=True
                elif buttonii=='tomain':
                    for ii in sound_threads:
                        ii.stop=True
                    '''
                    for ii in soldier_threads:
                        ii.stop=True
                    '''
                    return 'backtomain'
                elif buttonii=='exit':
                    pygame.quit()
                    sys.exit()
            
            if event.type==option_screen.event_num:
                music_volume=option_screen.music_volume
                scene.effect_volume=option_screen.effect_volume
                pygame.mixer.music.set_volume(music_volume)
                if option_screen.fullscreen:
                    screen=pygame.display.set_mode(screen_size,\
                            FULLSCREEN|HWSURFACE|DOUBLEBUF,\
                            screen_depth)
                    scene.surface=screen
                else:
                    screen=pygame.display.set_mode(screen_size,DOUBLEBUF,\
                            screen_depth)
                    scene.surface=screen

                OPTION=False
                PAUSED=True

            if event.type==KEYDOWN:
                if event.key == K_ESCAPE:
                    PAUSED=True

            if event.type==MOUSEBUTTONDOWN:
                pressed_mouse=event.button
                mouse_pos=event.pos

                if  pressed_mouse==1:
                    if PAUSED and OPTION==False:
                        pause_screen.buttonAction(('mouse_down',1,mouse_pos))
                    elif PAUSED and OPTION:
                        option_screen.buttonAction(('mouse_down',1,mouse_pos))
                    elif GAME_OVER:
                        choice=gameover_box.buttonAction(('mouse_down',1,mouse_pos))
                        if choice is not None:
                            return choice
                    else:
                        scroll_bar.buttonAction(('mouse_down',1,mouse_pos),time_passed)
                        menu_button.actions(('mouse_down',1,mouse_pos))
                        scene.drawUnitCircle(('mouse_down',1,mouse_pos))

                        if picked_up_troop is not None:
                            #----Add defence--------------------------
                            slot=window2Grid(mouse_pos,grid_size,topleft)
                            if slot in scene.spots['defence']:
                                barrack.addTroop(slot,picked_up_troop)
                                picked_up_troop=None
                            else:
                                picked_up_troop=None

                            barrack.resetCursor()

            if event.type==MOUSEBUTTONUP:
                released_mouse=event.button
                mouse_pos=event.pos
                if released_mouse==1:
                    if PAUSED and OPTION==False:
                        pause_screen.buttonAction(('mouse_up',1,mouse_pos))
                    elif PAUSED and OPTION:
                        option_screen.buttonAction(('mouse_up',1,mouse_pos))
                    elif GAME_OVER:
                        choice=gameover_box.buttonAction(('mouse_up',1,mouse_pos))
                        if choice is not None:
                            for ii in sound_threads:
                                ii.stop=True
                            '''
                            for ii in soldier_threads:
                                ii.stop=True
                            '''
                            return choice
                    else:
                        menu_button.actions(('mouse_up',1,mouse_pos))
                        picked_up_troop=scroll_bar.buttonAction(('mouse_up',1,\
                                mouse_pos),time_passed)

                        barrack.replaceCursor(picked_up_troop)
                    
        if PAUSED:
            pygame.mixer.music.pause()
            if OPTION:
                option_screen.draw(screen)
            else:
                pause_screen.draw(screen)
            pygame.display.flip()

            continue

        if GAME_OVER:

            pygame.mouse.set_visible(True)
            
            #----Send game over info to intel center------------------
            scene.globalTimer()

            if not GOT_END_TEXT:
                intel_center.time_table={}
                intel_text=' '
                over_intel=intel.Intel(text=intel_text,intel_type='over',\
                        priority=1,start=scene.global_time_passed,\
                        time=30)
                intel_center.addNewIntel(over_intel)
                ending_text=prepareEndingText(scene,WIN)
                intel_bar.rolling_speed=0.1
                intel_bar.updateText(ending_text)
                GOT_END_TEXT=True

            intel_bar.draw(time_passed,screen)
            gameover_box.chooseButton(WIN)
            gameover_box.draw(screen)


        if not GAME_OVER:
            menu_button.draw(screen)
            scroll_bar.draw(screen)

            #----Intel bar--------------------------
            intel_center.update()
            intel_bar.updateByIntel(intel_center.active_intel)
            intel_bar.draw(time_passed,screen)

            #----Money bar--------------------------
            money_bar.update(scene.money,screen)
            hq_bar.update(scene.hq_life,screen)

            enemy_spawn.spawnAtRandom(time_passed)
            
            screen.blit(level_info.background_image,(0,0+top_panel_width))
            scene.removeDead()
            GAME_OVER=scene.updateHQ(time_passed)

            scene.globalTimer()
            scene.playBackgroundShot()
            scene.layeredDraw(time_passed,screen)
            #soldier_queue.join()
            scene.drawAllBullets(time_passed,screen)
            sound_queue.join()
            scene.drawAnimations(time_passed,screen)
            scene.drawMarkers(time_passed,screen)
            scene.drawAmmoBoxs(screen)

            if picked_up_troop is not None:
                barrack.drawCircleAndSlot(pygame.mouse.get_pos())

            #----Detect victory--------------------------
            WIN=enemy_spawn.isVictory()
            if WIN:
                GAME_OVER=True
                pygame.mixer.music.stop()

        pygame.display.flip()


#-----------------------main-----------------------
if __name__=='__main__':
    #print 'use mission.py'

    #----Init--------------------------
    #pygame.init()
    screen=initScreen(SCREEN_SIZE,SCREEN_FLAG,SCREEN_DEPTH)



    #----Load level--------------------------
    LEVEL=4
    level_str='level'+'%0*d' %(2,LEVEL)
    command='import levels.'+level_str+' as current_level'
    exec(command)
    level_info=current_level.LevelInfo()

    #----Start level--------------------------
    choice=startLevel(screen,SCREEN_SIZE,SCREEN_DEPTH,\
            level_info,difficulty='Low',\
            music_volume=0.5,effect_volume=0.5,\
            fullscreen=False)



