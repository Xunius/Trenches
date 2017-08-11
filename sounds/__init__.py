import pygame
import os
import random
import threading


#----Files--------------------------
PATH=os.path.dirname(os.path.realpath(__file__))

MAIN_FILE='wav_main.ogg'
RIFLE_FILES=['wav_rifle_1.wav',\
        'wav_rifle_3.wav',\
        'wav_rifle_4.wav',\
        'wav_rifle_5.wav',\
        'wav_rifle_6.wav',\
        'wav_rifle_7.wav'\
        ]

SNIPER_FILES=['wav_sniper_1.wav',\
        'wav_sniper_2.wav',\
        'wav_sniper_3.wav',\
        'wav_sniper_4.wav'\
        ]

GRENADE_FILES=['wav_grenade_1.wav',\
        'wav_grenade_2.wav',\
        'wav_grenade_3.wav',\
        'wav_grenade_4.wav'\
        ]

LAUNCHER_FILES=['wav_launcher_1.wav',\
        'wav_launcher_2.wav',\
        'wav_launcher_3.wav',\
        'wav_launcher_4.ogg'\
        ]


MACHINEGUN_FILES=['wav_machinegun_1.wav',\
       'wav_machinegun_2.wav',\
       'wav_machinegun_3.wav',\
       'wav_machinegun_4.wav'\
       ]


ARTILLERY_FILES=['wav_artillery_1.wav',\
        'wav_artillery_2.wav',\
        'wav_artillery_3.wav'\
        ]

BACKGROUND_FILES=['wav_background_1.wav',\
        'wav_background_2.wav',\
        'wav_background_3.wav',\
        'wav_background_4.ogg',\
        'wav_background_5.ogg',\
        'wav_background_6.ogg',\
        'wav_background_7.ogg'\
        ]

GAMEOVER_FILE='wav_gameover.ogg'

BACKGROUND_MUSIC_FILES=[
        'wav_fightmood_1.ogg',\
        'wav_fightmood_2.ogg',\
        'wav_fightmood_3.ogg'\
        ]


#----Load waves--------------------------
class SoundManager(object):
    all_sounds={'rifle':[],\
            'machinegun':[],\
            'sniper':[],\
            'launcher':[],\
            'grenade':[],\
            'mortar':[],\
            'artillery':[],\
            'background_fire':[],\
            'gameover':[]\
            }
    bgm_files=[]
    main_file=None

    def __init__(self):

        if len(self.all_sounds['background_fire'])==0:
            for ii in BACKGROUND_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['background_fire'].append(soundii)

        if len(self.all_sounds['rifle'])==0:
            for ii in RIFLE_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['rifle'].append(soundii)

        if len(self.all_sounds['machinegun'])==0:
            for ii in MACHINEGUN_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['machinegun'].append(soundii)

        if len(self.all_sounds['sniper'])==0:
            for ii in SNIPER_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['sniper'].append(soundii)

        if len(self.all_sounds['launcher'])==0:
            for ii in LAUNCHER_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['launcher'].append(soundii)

        if len(self.all_sounds['grenade'])==0:
            for ii in GRENADE_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['grenade'].append(soundii)

        if len(self.all_sounds['artillery'])==0:
            for ii in ARTILLERY_FILES:
                soundii=pygame.mixer.Sound(os.path.join(PATH,ii))
                self.all_sounds['artillery'].append(soundii)

        #----Use same library for mortar as grenade-----------------
        if len(self.all_sounds['mortar'])==0:
            self.all_sounds['mortar']=self.all_sounds['grenade']

        #----Background music--------------------------
        if len(self.bgm_files)==0:
            for ii in BACKGROUND_MUSIC_FILES:
                self.bgm_files.append(os.path.join(PATH,ii))
        
        #---main-Background music--------------------------
        if self.main_file is None:
            self.main_file=os.path.join(PATH,MAIN_FILE)

    def loadMusic(self,key='battle'):
        if key=='battle':
            self.bgm=pygame.mixer.music.load(random.choice(self.bgm_files))
        elif key=='main':
            self.bgm=pygame.mixer.music.load(self.main_file)


    def pickRandom(self,type_name):
        return random.choice(self.all_sounds[type_name])

class SoundThread(threading.Thread):
    def __init__(self,queue,lock,global_volume,screen_width):
        threading.Thread.__init__(self)
        self.queue=queue
        self.lock=lock
        self.global_volume=global_volume
        self.screen_width=screen_width
        self.stop=False

    def run(self):
        while True and not self.stop:
            self.lock.acquire()
            if not self.queue.empty():
                data=self.queue.get()
                channel=data[0].play()
                if channel is not None:
                    volumes=self.stereoVolume(data[1])
                    channel.set_volume(*volumes)
                self.queue.task_done()
                self.lock.release()
            else:
                self.lock.release()
            pygame.time.wait(30)


    def stereoVolume(self,x):

        right_volume=float(x/self.screen_width)
        left_volume=(1.0-right_volume)*self.global_volume
        right_volume*=self.global_volume

        return (left_volume,right_volume)

class MusicThread(threading.Thread):
    def __init__(self,pause,lock):
        threading.Thread.__init__(self)

        #self.music_func=music_func
        self.pause=pause
        self.lock=lock

    def run(self):
        if not self.pause:
            pygame.mixer.music.play(loops=-1)
            #self.music_func()

sound_manager=SoundManager()


        





        

        




    


    
