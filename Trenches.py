'''
TRENCHES

The game TRENCHES is a tower defence game with some modified flavours added to
the game play, most notably, unlike in conventional tower defence games where
incoming enemies are unable to attack and destroy the defending units, the
players defences are at constant risk, like real soldiers in battle field
trenches.

Another major change to the game play is defending units are not strictly
static: once a soldier runs out of ammo, he will move to a nearby ammobox
and reload; should a army doctor finds a wounded fellow, he will come over
and heal the wound. After reload, soldier will return back to his original
slot, and army doctor will just stay where he is, until next medic care
call is issued.

Consistent with most tower defence games, the goal of the game is to eliminate
threats to the protected target (HQ in this case), by placing defencing units
along the path of incoming attacks. Valid locations for defence deployment
are inside the trenches (hence comes the title). Incoming enemies will come
from one or multiple directions. If certain number of enemies pass across
your defence lines, the mission is failed.

Defence units the play can deploy include:
    - Rifle men,
    - Machinegun men,
    - Grenadiers,
    - Mortars,
    - Artilleries,
    - Snipers,
    - Medics, to heal wounded soldiers,
    - Ammoboxes, to provide ammo to all other units except Medics.

Enemy team may have all above units except Medics and Ammoboxes.

Some tips/features:
    - Firing accuracy will drop when wounded, so will moving speed.
    - Certain chance the enemy's firing will miss, thus mimicking the effect
      of enjoying extra cover provided by the trenches.
    - Explosive weapons have areal damage.
    - The in-game intel-bar shows intels about incoming attacks, as well as
      some shouts from your men.
    - Some other tips are shown in the game.


Required python modules:

    - pygame (mine is 1.9.3).
    - numpy


The game has got its basic shape: a working game play, a set of GUI, some
option settings, and a relatively easy level design system to facilitate
quick level designs. However, there are still some features that I haven't
got the time to fully implement, like map-scrolling to allow for larger maps,
a grid-system that allows for units of different sizes, the ability to
control movement and firing of defencing units, weathers, more units,
and of cause better graphics.

I may come back to implement some of these, but I kind of prefer leaving it
for now and starting to learn a more powerful game engine, perhaps Unity.
So if anyone find this game interesting and would like to mod it, please
go ahead, and I'd appreciate it if you could also share with me your own
re-creations.

Author: Guangzhi XU (xugzhi1987@gmail.com, guangzhi.xu@outlook.com)



'''
import pygame
#from pygame.locals import *
from pygame.locals import DOUBLEBUF, QUIT, MOUSEBUTTONUP,\
        MOUSEBUTTONDOWN, FULLSCREEN
import sys,os
try:
    import numpy
except:
    raise Exception("module <numpy> not found.")
    pygame.quit()
    sys.exit()

    

SCREEN_SIZE=(800,600)
#SCREEN_FLAG=DOUBLEBUF | FULLSCREEN
SCREEN_FLAG=DOUBLEBUF
SCREEN_DEPTH=32
GLOBAL_MUSIC_VOLUME=0.2
GLOBAL_EFFECT_VOLUME=0.2
__version__='v1.1'


if getattr(sys,'frozen',False):
    os.chdir(sys._MEIPASS)


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


if __name__=='__main__':

    #----Init--------------------------
    pygame.init()
    screen=initScreen(SCREEN_SIZE,SCREEN_FLAG,SCREEN_DEPTH)

    #----These has to be imported after pygame.init() and screen initialization-
    import ui
    import missions
    import sounds

    #----Create main screen--------------------------
    main_screen=ui.createMainScreen()

    #----Create credit screen--------------------------
    credit_screen=ui.createCreditScreen()

    #----Main loop--------------------------
    clock=pygame.time.Clock()
    pygame.mouse.set_visible(True)
    START=False
    CREDIT=False
    
    #----Music thread--------------------------
    music_thread=sounds.MusicThread(False,None)
    sounds.sound_manager.loadMusic('main')
    music_thread.start()
    pygame.mixer.music.set_volume(GLOBAL_MUSIC_VOLUME)

    while True:
        time_passed=clock.tick(30)

        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()

            if event.type==main_screen.event_num:
                if main_screen.button_pressed=='start':
                    START=True
                elif main_screen.button_pressed=='credit':
                    CREDIT=True
                elif main_screen.button_pressed=='exit':
                    pygame.quit()
                    sys.exit()

            if event.type==MOUSEBUTTONDOWN:
                pressed_mouse=event.button
                mouse_pos=event.pos
                if  pressed_mouse==1:
                    if not CREDIT:
                        main_screen.buttonAction(('mouse_down',1,mouse_pos))
                    if CREDIT:
                        choice=credit_screen.buttonAction(('mouse_down',1,mouse_pos))
                        if choice=='backtomain':
                            CREDIT=False

            if event.type==MOUSEBUTTONUP:
                released_mouse=event.button
                mouse_pos=event.pos

                if released_mouse==1:
                    if not CREDIT:
                        main_screen.buttonAction(('mouse_up',1,mouse_pos))
                    if CREDIT:
                        choice=credit_screen.buttonAction(('mouse_up',1,mouse_pos))
                        if choice=='backtomain':
                            CREDIT=False

        if not START and not CREDIT:
            #music_thread.pause=False
            main_screen.draw(screen)
            pygame.display.flip()

        if START:
            #music_thread.pause=True
            choice=missions.missions(screen,GLOBAL_MUSIC_VOLUME,GLOBAL_EFFECT_VOLUME)
            if choice=='backtomain':
		sounds.sound_manager.loadMusic('main')
	        #music_thread.start()
		pygame.mixer.music.play()
                START=False
        if CREDIT:
            credit_screen.draw(screen)
            pygame.display.flip()




