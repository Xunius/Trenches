'''Classes for multiple objects in game.
'''
import pygame
from pygame.locals import Rect
import random
import threading
import numpy
from startlevel import GRID_SIZE
from startlevel import SCREEN_SIZE
from startlevel import TOPLEFT
from startlevel import GOD_MOD
import copy

import generals
import objects
import prepromask
import statemachine
import weapons
import sounds
import troops
import readnames
import intel
import parameters
import testbezier
import cus_font
import pathfinder_class2

E_FONT=cus_font.E_FONT_PATH8





class Animation():

    def __init__(self,world,images,image_info,pos_center,loop,\
            time=None,rate=None,layer=1):

        self.world=world
        self.image_info=image_info
        self.images=generals.splitImage(images,image_info)

        self.pos_center=generals.Vector2(pos_center)
        self.loop=loop   #positive integer
        self.layer=layer

        self.image_index=0
        self.image=self.images[self.image_index]

        self.size=self.image.get_size()
        self.surface=self.world.surface
        
        if time is not None and rate is None:
            self.rate=float(time)/image_info[1]/image_info[3]
            self.time=time   #in milliseconds
        elif time is None and rate is not None:
            self.rate=rate
            self.time=rate*image_info[1]*image_info[3]
        else:
            raise()

        self.passed_time=0
        self.world.addAnimation(self)

    @property
    def topleft(self):
        return generals.center2Topleft(center=self.pos_center,size=self.size)

    @property
    def rect(self):
        return Rect(self.topleft[0],self.topleft[1],self.size[0],\
                self.size[1])

    def draw(self,time_passed,surface=None):

        if self.loop>0:

            self.passed_time+=time_passed
            self.image_index=int(self.passed_time/self.rate)%\
                    (self.image_info[1]*self.image_info[3])

            self.image=self.images[self.image_index]
        
            if surface is None:
                self.surface.blit(self.image,self.topleft)
            else:
                surface.blit(self.image,self.topleft)

            if self.passed_time>=self.time:
                self.passed_time=0
                self.loop-=1


class GameObject(pygame.sprite.Sprite):

    def __init__(self,world,topleft,image,speed,\
            life,layer=0,heading=(1,0)):
        pygame.sprite.Sprite.__init__(self)

        self.world=world
        self.topleft=generals.Vector2(*topleft)
        self.image=image
        self.speed=speed
        self.life=max(0,life)
        self.layer=layer
        self.surface=self.world.surface
        self.size=self.image.get_size()
        self.heading=generals.Vector2(heading)

        self.pos_center=generals.topleft2Center(topleft=self.topleft,size=self.size)
        self.destination=generals.Vector2(0,0)


    @property
    def rect(self):
        return Rect(self.topleft[0],self.topleft[1],self.size[0],\
                self.size[1])

    def moveTo(self,time_passed):
        '''<time_passed>: in milliseconds.
        '''

        if self.speed!=0 and self.pos_center != self.destination:

            move_vector=self.destination-self.pos_center
            move_length=move_vector.get_length()
            self.heading=move_vector.get_normalized()
            actual_move_length=min(move_length,time_passed/1000.*self.speed)
            self.pos_center+=actual_move_length*self.heading
            self.topleft=generals.center2Topleft(center=self.pos_center,size=self.size)


    def rotate(self):
        '''Any degree rotate. Starting from 0 vector(1,0).
        positive angle is conti-clockwise.
        Note that the size of the image surface will change, so necessary
        to locate using the center of surface and rotate and redefine the 
        size of the surface and the topleft position.
        '''
        theta=numpy.arctan2(-self.heading[1],self.heading[0])/numpy.pi*180.
        self.image=pygame.transform.rotate(self.image,theta)

        #----Relocate the topleft by pos_center--------------------------
        self.size=self.image.get_size()
        self.topleft=generals.center2Topleft(center=self.pos_center,size=self.size)


    def action(self,time_passed):
        pass

    def draw(self,surface=None):
        if self.life>0:
            if surface is None:
                self.surface.blit(self.image,self.topleft)
            else:
                surface.blit(self.image,self.topleft)


class AmmoBox(GameObject):
    '''Ammo box to replenish soldiers weapon ammo'''
    def __init__(self,load,recharge_rate,fire_range,world,topleft,images,speed,\
            life=50,layer=0,heading=(1,0)):

        try:
            self.image=images[0]
        except:
            self.image=images

        GameObject.__init__(self,world,topleft,self.image,speed,\
                life,layer=0,heading=(1,0))
        self.load=load
        self.team=1
        self.supply_range=fire_range
        self.recharge_rate=recharge_rate

        self.ammo_bar=StatusBar(self.topleft+(5,0),self.size[0]-10,\
                weapons.MAX_WEAPON_AMMO['ammo'],\
                self.load,(0,0,0),(50,50,240))


    def draw(self,surface):

        self.ammo_bar.update(self.load,self.topleft)
        self.ammo_bar.draw(surface)

        GameObject.draw(self,surface)


class Soldier(GameObject):

    images=[]

    def __init__(self,team,name,rank,weapon,ammo,image_info,\
            world,topleft,image,speed,life,layer):

        GameObject.__init__(self,world,topleft,image,speed,life,layer)

        self.team=team
        self.name=name
        self.rank=rank
        self.weapon=weapon
        self.ammo=ammo
        self.armor='normal'
        self.armor_type=None

        self.image_info=image_info
        self.image_index=0

        if len(self.images)==0:
            self.images=generals.splitImage(image,image_info)
            # make a copy for rotation
            self.images_ori=[ii.copy() for ii in self.images]

        self.image=self.images[self.image_index]
        self.size=self.image.get_size()

        self.rate=100   #Rate for animation
        #self.rate=500   #Rate for animation
        self.passed_time=0  #Used to change animation frame
        self.path_list=None

        self.ismoving=False
        self.kill=0
        self.slot=None

        self._speed=speed
        self.isclick=False
        self.heading=random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        self.heading=generals.Vector2(self.heading)

        #----Status bars--------------------------
        self.ammo_bar=None
        self.hp_bar_length=self.size[0]-10
        self.hp_bar_vert_shift=0.5*self.size[1]+6
        self.hp_bar=StatusBar(self.pos_center-(0.5*self.hp_bar_length,
            self.hp_bar_vert_shift), self.hp_bar_length,self.life,\
                self.life,(255,0,0),(0,255,0))

        #----Insignia--------------------------
        self.insignia=Insignia(self)

        #----State machine--------------------------
        if self.team==2:
            marching_state=statemachine.MarchingState(self)
            firing_state=statemachine.FiringState(self)
            self.brain=statemachine.StateMachine(marching_state)
            self.brain.addState(firing_state)
        elif self.team==1:
            defencing_state=statemachine.DefencingState(self)
            standby_state=statemachine.StandByState(self)
            moveto_ammo_state=statemachine.MoveToAmmoState(self)
            recharge_ammo_state=statemachine.RechargeAmmoState(self)
            return_to_slot_state=statemachine.ReturnToSlotState(self)

            self.brain=statemachine.StateMachine(standby_state)
            self.brain.addState(defencing_state)
            self.brain.addState(moveto_ammo_state)
            self.brain.addState(recharge_ammo_state)
            self.brain.addState(return_to_slot_state)


    @property
    def pos_center(self):
        return generals.topleft2Center(topleft=self.topleft,size=self.size)

    @pos_center.setter
    def pos_center(self,value):
        self._pos_center=value


    @property
    def speed(self):
        return self._speed*parameters.WEATHER_SPEED_FACTOR[self.world.weather]*\
                max(0.5,self.life/100.)*parameters.RANK_FACTOR[self.rank]

    @speed.setter
    def speed(self,value):
        self._speed=value

    def getWeapon(self,weapon):
        self.weapon=weapon
        self.ammo_bar=StatusBar(self.pos_center-(0.5*self.hp_bar_length,
            self.hp_bar_vert_shift-3),self.hp_bar_length,\
                weapons.MAX_WEAPON_AMMO[weapon.weapon_type],\
                self.ammo,(0,0,0),(50,50,240))

    def upgradeRank(self):
        for ii in parameters.RANK.keys():
            if self.kill in parameters.RANK[ii]:
                if self.rank!=ii:
                    #----Send promotion intel to intel center------------------
                    intel_text=self.rank.capitalize()+' '+self.name+\
                            ' is promoted to '+ii+'.'
                    promo_intel=intel.Intel(text=intel_text,intel_type='promote',\
                            priority=2,start=self.world.global_time_passed,\
                            time=3000)
                    self.world.intel_center.addNewIntel(promo_intel)
                    self.rank=ii

                    #----enlarge fire range circle when upgrade--------------------------
                    self.weapon.updateRangeCircle()

                    #----Add blink animation--------------------------
                    ani=Animation(self.world,images=objects.object_images['blink'][0],\
                            image_info=objects.object_images['blink'][1],\
                            pos_center=self.pos_center+self.insignia.shift+(5,10),\
                            loop=1,time=1100)
                    self.world.addAnimation(ani)
                    break

    def rotate(self):

        pos_center=self.pos_center
        theta=numpy.arctan2(-self.heading[1],self.heading[0])/numpy.pi*180
        if abs(theta)>0:
            self.image=self.images_ori[self.image_index].copy()
            self.image=pygame.transform.rotate(self.image,theta)

            self.heading=generals.Vector2(*self.heading).normalize()
            self.size=self.image.get_size()
            self.topleft=generals.center2Topleft(center=pos_center,size=self.size)


    #------Move along a list of coordinate pairs.----------
    def moveAlongPath(self,time_passed,verbose=True):
        '''Move along a list of coordinate pairs.
        '''

        end=generals.grid2Window(self.path_list[-1],GRID_SIZE,TOPLEFT)

        if self.topleft==end:
            self.ismoving=False    #used to toggle animation if True
            return 

        #----Next grid point to move to--------------------------
        destination=generals.grid2Window(self.path_list[0],GRID_SIZE,TOPLEFT)
        if self.topleft==destination:

            #----If the current destination is the last grid box in path_list-----
            if len(self.path_list)==1:
                destination=generals.grid2Window(self.path_list[0],GRID_SIZE,TOPLEFT)
                self.topleft=destination
                self.ismoving=False
                return
            else:
                #----Remove the current destination and set to the next one in path_list
                del self.path_list[0]
                destination=generals.grid2Window(self.path_list[0],GRID_SIZE,TOPLEFT)

        move_vector=destination-self.topleft
        move_length=move_vector.get_length()
        self.heading=move_vector.get_normalized()
        actual_move_length=min(move_length,time_passed/1000.*self.speed)
        self.topleft+=actual_move_length*self.heading

        self.ismoving=True

    

    def update(self,time_passed,surface=None):
        #----Send medi shout to intel center------------------
        if self.team==1 and self.life<=30:
            intel_text=self.rank.capitalize()+' '+self.name+\
                    ': MEDI CARE!!!!'
            shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                    priority=3,start=self.world.global_time_passed,\
                    time=3000)
            self.world.intel_center.addNewIntel(shout_intel)

        #----Send ammo shout to intel center------------------
        if self.team==1 and self.ammo<=3:
            intel_text=self.rank.capitalize()+' '+self.name+\
                    ': I am running out of AMMO !!!!'
            shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                    priority=3,start=self.world.global_time_passed,\
                    time=3000)
            self.world.intel_center.addNewIntel(shout_intel)

        #self.upgradeRank()  #move to bullet damge part
        self.weapon.update()
        self.brain.think(time_passed)
        self.draw(time_passed,surface)


    def draw(self,time_passed,surface=None):

        if self.ismoving:
            self.passed_time+=time_passed
            self.image_index=(self.passed_time/self.rate)%\
                    (self.image_info[1]*self.image_info[3])
                    #(self.image_info[1]*self.image_info[3]-1)+1
            if self.image_index==1 and self.passed_time>=self.rate*10:
                self.passed_time=0
        else:
            self.image_index=0

        self.image=self.images[self.image_index]

        #----Rotate according to heading--------------------------
        self.rotate()
        
        if surface is None:
            GameObject.draw(self)
        else:
            GameObject.draw(self,surface)

        #----Draw status--------------------------
        if self.ammo_bar is not None:
            self.ammo_bar.update(self.ammo,self.pos_center-(0.5*self.hp_bar_length,
            self.hp_bar_vert_shift-3))
            self.ammo_bar.draw(surface)
        self.hp_bar.update(self.life,self.pos_center-(0.5*self.hp_bar_length,
            self.hp_bar_vert_shift))
        self.hp_bar.draw(surface)

        #----Draw insignia--------------------------
        self.insignia.draw(surface)

        #----Draw range circle --------------------------
        self.drawCircle(surface)


    def searchEnemey(self):
        '''Search an radius and return an enemy in range.
        '''

        if self.weapon.weapon_type in ['grenade','mortar','artillery']:
            enemies=self.world.searchArea('enemy_bomb',self.id,\
                    self.weapon.fire_range,self.weapon.min_fire_range)
        else:
            enemies=self.world.searchArea('enemy',self.id,self.weapon.fire_range)

        if len(enemies)>0:
            if self.team==2 and parameters.DIFFICULTY_ENEMY_FOCUS_FIRE[\
                    self.world.difficulty]==False:
                return random.choice(enemies)
            else:
                life=[ii.life for ii in enemies]
                index=numpy.argsort(life)
                #----Return the enemy with the lowest life------------
                return enemies[index[0]]
        else:
            return None

    def fireAtWill(self,time_passed):
        '''Return <fired>: boolean, actually fired or not.
        When soldier has no ammo left or weapon not cooled down, weapon.fireAt()
        could result in not doing fire.
        '''

        target=self.searchEnemey()
        if target is not None:
            self.heading=(target.pos_center-self.pos_center).normalize()
            #self.heading=self.heading.normalize()
            fired=self.weapon.fireAt(target,time_passed)

        else:
            fired=False

        return fired

    def isOver(self,point):
        '''Check wether mouse is over soldier
        '''
        in_x=point[0]>=self.topleft[0] and\
                point[0]<=self.topleft[0]+self.size[0]
        in_y=point[1]>=self.topleft[1] and\
                point[1]<=self.topleft[1]+self.size[1]

        return in_x and in_y


    def drawCircle(self,surface):
        if self.weapon is not None and self.isclick:
            topleft=self.pos_center-generals.Vector2(self.weapon.fire_range,\
                    self.weapon.fire_range)
            surface.blit(self.weapon.range_circle_copy,topleft)


    def click(self,mouse_event):
        '''
        <mouse_event>:(mouse_event_type,button,point):
            <mouse_event_type>: 'mouse_down' or 'mouse_up'.
            <button>: button number, 1 for left, 2 for mid, 3 for right.
            <point>: mouse position
        '''

        mouse_event_type,button,point=mouse_event

        if self.isOver(point) and mouse_event_type=='mouse_down':
            self.isclick=True
            return True
        elif self.isOver(point)==False and mouse_event_type=='mouse_down':
            self.isclick=False
            return False

    def searchAmmo(self):
        if len(self.world.ammoboxs)==0:
            return None

        self.path_finder.start=self.slot
        viable_ammos=[]
        dists=[]
        for ii in self.world.ammoboxs.values():
            self.path_finder.end=ii.slot
            self.path_finder.findPath()
            distii=(self.pos_center-ii.pos_center).get_length()
            if self.path_finder.path is not None and distii\
                    <=ii.supply_range:
                viable_ammos.append(ii)
                dists.append(distii)

        if len(viable_ammos)==0:
            return None
        else:
            index=numpy.argsort(dists)
            return viable_ammos[index[0]]

    def reload(self,time_passed):
        # <load> is the num of ammo recharged during time <time_passed>,
        # subject to that it doesn't overshoot max ammo of weapon type,
        # subject to that it doesn't overdraw from ammo box.
        load=int(time_passed/1000.*weapons.AMMO['recharge_rate'])
        load=min(load,\
                weapons.MAX_WEAPON_AMMO[self.weapon.weapon_type]-self.ammo,\
                self.target_ammo.load)
        self.ammo+=load
        self.target_ammo.load-=load


class MediDoctor(Soldier):

    def __init__(self,team,name,rank,weapon,ammo,image_info,\
            world,topleft,image,speed,life,layer):

        Soldier.__init__(self,team,name,rank,weapon,ammo,image_info,\
            world,topleft,image,speed,life,layer)

        self.wound=None
        self.last_fire_time=self.world.global_time_passed

        #----Set transparent--------------------------
        self.images2=[ii.copy() for ii in self.images]
        self.images=self.images2

        #----State machine--------------------------
        standby_state=statemachine.MediStandByState(self)
        moveto_state=statemachine.MoveToWoundState(self)
        healing_state=statemachine.HealingState(self)
        moveto_ammo_state=statemachine.MoveToAmmoState(self)
        recharge_ammo_state=statemachine.RechargeAmmoState(self)
        return_to_slot_state=statemachine.ReturnToSlotState(self)

        self.brain=statemachine.StateMachine(standby_state)
        self.brain.addState(moveto_state)
        self.brain.addState(healing_state)
        self.brain.addState(moveto_ammo_state)
        self.brain.addState(recharge_ammo_state)
        self.brain.addState(return_to_slot_state)

    def searchWound(self):
        if self.ammo<=0:
            return None

        allies=self.world.searchArea('allies',self.id,self.weapon.fire_range)
        if len(allies)>0:
            life=[ii.life for ii in allies]
            if numpy.min(life)==100:
                return None
            index=numpy.argsort(life).tolist()
            self.path_finder.start=self.slot

            #----Return the soldier with the lowest life and viable------------
	    for ii in index:
                if allies[ii].life==100:
                    continue
		#----Check path--------------------------
                # NOTE: topleft of soldier will change due to rotation,
                # don't use self.path_finder.end=generals.window2Grid(
                # allies[ii].topleft,GRID_SIZE,TOPLEFT)
		self.path_finder.end=allies[ii].slot
		self.path_finder.findPath()
		if self.path_finder.path is not None:
		    return allies[ii]
	        else:
		    continue
	    return None
        else:
            return None

        
    def heal(self,time_passed):

        #-----------------Cool down passed-----------------
        if self.world.global_time_passed-self.last_fire_time>=self.weapon.fire_rate:
            if self.wound is not None:
                self.wound.life+=min(self.weapon.top_damage,100-self.wound.life)
                self.ammo-=1
                fired=True
                self.last_fire_time=self.world.global_time_passed

                #----Add healing animation--------------------------
                ani=Animation(self.world,pos_center=self.wound.pos_center,\
                        loop=1,rate=None,layer=1,\
                        images=objects.object_images['heal'][0],\
                        image_info=objects.object_images['heal'][1],\
                        time=1000)
                self.world.addAnimation(ani)
            else:
                fired=False
        else:
            fired=False

        return fired


class Weapon():
    '''Note that topleft of weapon should be the pos_center attribute of the
    soldier
    '''
    circles,info=objects.object_images['greencircle']
    range_circle=generals.splitImage(circles,info)[-1]

    def __init__(self,weapon_type,fire_range,height,\
            damage_range,top_damage,fire_rate,images,speed,life,sounds,\
            world,pos_center,carrier):

        self.weapon_type=weapon_type
        self._fire_range=fire_range
        self.height=height
        self.damage_range=damage_range
        self.top_damage=top_damage
        self._fire_rate=fire_rate
        self.images=images
        self.speed=speed
        self.life=life
        self.sounds=sounds

        self.world=world
        self.carrier=carrier

        self.weather=self.world.weather
        self.friend_damage=self.world.friend_damage

        #----Store the time when it last fired, \
        # used to calcuate cool down time -------------
        self.last_fire_time=self.world.global_time_passed
        self.pos_center=self.carrier.pos_center

        self.passed_time=0

        #----Fire range circle--------------------------
        range_circle_size=int(2*self.fire_range)
        self.range_circle_copy=self.range_circle.copy() #circle surface that is blit in drawCircle()
        self.range_circle_copy=pygame.transform.scale(self.range_circle_copy,\
                (range_circle_size,range_circle_size))
        
        # images could be one single image for gun bullets,
        # and a series for grenade. Even if there is only one surface,
        # it was put in a list as [image,]
        try:
            self.image=self.images[0]
        except:
            self.image=images

    @property
    def fire_range(self):
        return self.weaponFactor('range')
    @property
    def fire_rate(self):
        return self.weaponFactor('rate')

 
    #------Modify weapon properties----------
    def weaponFactor(self,keyword):
        '''Modify weapon properties according to world settings
        '''
        if keyword=='range':
            return self._fire_range*parameters.WEATHER_RANGE_FACTOR[self.weather]*\
                    parameters.RANK_FACTOR[self.carrier.rank]
        elif keyword=='rate':
            return self._fire_rate*max(0.5,self.carrier.life/100.)*\
                parameters.RANK_FACTOR[self.carrier.rank]

    def machinegunFireAt(self,target,time_passed):
        '''Give machinegun different firing mechanism
        '''

        self.passed_time+=time_passed
        if self.passed_time>=500:
            fired=False
        else:
            bullet=GunBullet(self.weapon_type,self.fire_range,\
                    self.damage_range,self.height,self.top_damage,self.friend_damage,\
                    target,self.carrier,\
                    self.world,self.pos_center,\
                    self.image,self.speed,self.life)

            self.world.addBullet(bullet)
            self.carrier.ammo-=1
            self.playFiringSound()

            self.last_fire_time=self.world.global_time_passed
            fired=True

        if self.passed_time>1500:
            self.passed_time=0

        return fired


    def fireAt(self,target,time_passed):

        #----Weapon has cooled down, ready to fire--------------------------
        if self.world.global_time_passed-self.last_fire_time>=self.fire_rate:

            if self.weapon_type == 'machinegun':
                fired=self.machinegunFireAt(target,time_passed)
                return fired

            elif self.weapon_type in ['rifle',\
                    'sniper','flamer']:

                # Note that self.image, which is one single surface is passed.
                bullet=GunBullet(self.weapon_type,self.fire_range,\
                        self.damage_range,self.height,self.top_damage,self.friend_damage,\
                        target,self.carrier,\
                        self.world,self.pos_center,\
                        self.image,self.speed,self.life)

                # Note that self.images, which is a list of surfaces, is passed.
            elif self.weapon_type in ['grenade','mortar','artillery']:
                bullet=ShellBullet(self.weapon_type,self.fire_range,\
                        self.damage_range,self.height,self.top_damage,self.friend_damage,\
                        target,self.carrier,\
                        self.world,self.pos_center,\
                        self.images,self.speed,self.life)

            self.world.addBullet(bullet)
            self.carrier.ammo-=1
            self.playFiringSound()

            self.last_fire_time=self.world.global_time_passed
            fired=True
        else:
            fired=False

        return fired


    def playFiringSound(self):
        if len(self.sounds)>0:
            firing_sound=random.choice(self.sounds)
            self.world.thread_lock.acquire()
            self.world.sound_queue.put((firing_sound,self.pos_center[0]))
            self.world.thread_lock.release()


    def update(self):
        self.pos_center=self.carrier.pos_center
        self.topleft=self.pos_center

    def updateRangeCircle(self):
        #----Update range circle size--------------------------
        range_circle_size=int(2*self.fire_range)
        self.range_circle_copy=pygame.transform.scale(self.range_circle_copy,\
                (range_circle_size,range_circle_size))


class BombWeapon(Weapon):

    def __init__(self,weapon_type,fire_range,min_fire_range,height,\
            damage_range,top_damage,fire_rate,images,speed,life,launch_sounds,\
            explode_sounds,\
            world,pos_center,carrier):

        self.min_fire_range=min_fire_range
        self.explode_sounds=explode_sounds

        Weapon.__init__(self,weapon_type,fire_range,height,\
            damage_range,top_damage,fire_rate,images,speed,life,launch_sounds,\
            world,pos_center,carrier)

        #----Fire range circle--------------------------
        #self.range_circle_copy=self.range_circle.copy()
        self.min_range_circle=self.range_circle.copy()
        self.min_range_circle=pygame.transform.scale(self.min_range_circle,\
                (self.min_fire_range*2,self.min_fire_range*2))

        min_topleft=(int(self.fire_range-self.min_fire_range),\
            int(self.fire_range-self.min_fire_range))
        generals.chopCenter(self.range_circle_copy,self.min_range_circle,min_topleft)

    def update(self):
        self.pos_center=self.carrier.pos_center
        self.topleft=self.pos_center

    def updateRangeCircle(self):
        #----Update range circle size--------------------------
        range_circle_size=int(2*self.fire_range)
        #----Get a copy from the original circle--------------------------
        self.range_circle_copy=self.range_circle.copy()
        self.range_circle_copy=pygame.transform.scale(self.range_circle_copy,\
                (range_circle_size,range_circle_size))
        min_topleft=(int(self.fire_range-self.min_fire_range),\
            int(self.fire_range-self.min_fire_range))
        generals.chopCenter(self.range_circle_copy,self.min_range_circle,min_topleft)

    def fireAt(self,target,time_passed):

        #----Weapon has cooled down, ready to fire--------------------------
        if self.world.global_time_passed-self.last_fire_time>=self.fire_rate:

            if self.weapon_type in ['grenade','mortar','artillery']:
                bullet=ShellBullet(self.weapon_type,self.fire_range,\
                        self.damage_range,self.height,self.top_damage,self.friend_damage,\
                        target,self.carrier,self.explode_sounds,\
                        self.world,self.pos_center,\
                        self.images,self.speed,self.life)

            self.world.addBullet(bullet)
            self.carrier.ammo-=1
            self.playFiringSound()

            self.last_fire_time=self.world.global_time_passed
            fired=True
        else:
            fired=False

        return fired


class Bullet(GameObject):

    def __init__(self,weapon_type,fire_range,damage_range,height,top_damage,\
            friend_damage,target,carrier,\
            world,topleft,image,speed,life,layer=1,heading=(1,0)):

        GameObject.__init__(self,world,topleft,image,speed,\
                life,layer,heading)

        self.weapon_type=weapon_type
        self.fire_range=fire_range
        self.damage_range=damage_range #for explosive weapons
        self.height=height   #Flying height, for parabolic movement
        self.top_damage=top_damage  #Highest damage posible
        self.friend_damage=friend_damage
        self.target=target
        self.carrier=carrier
        #self.image_info=image_info
        self.team=carrier.team
        
        #----Register enemies that have taken damage, to avoid double hits-------
        self.units_in_path_regi=[]

        #self.setDestination()

    def setDestination(self):
        pass

    def randomOffset(self):
        '''Add a random offset to the hit point.
        '''

        delta_x=random.randint(0,40)*(1-weapons.WEAPON_ACCURACY_FACTOR[self.weapon_type])*\
                (1./parameters.WEATHER_ACCURACY_FACTOR[self.world.weather])*\
                (1.1-self.carrier.life/100.)/parameters.RANK_FACTOR[self.carrier.rank]
        delta_y=random.randint(0,40)*(1-weapons.WEAPON_ACCURACY_FACTOR[self.weapon_type])*\
                (1./parameters.WEATHER_ACCURACY_FACTOR[self.world.weather])*\
                (1.1-self.carrier.life/100.)/parameters.RANK_FACTOR[self.carrier.rank]

        #----Scale random offset by difficulty level--------------------------
        if self.carrier.team==1:
            scale=parameters.DIFFICULTY_PLAYER_ACCURACY_FACTOR[self.world.difficulty]
        elif self.carrier.team==2:
            scale=parameters.DIFFICULTY_ENEMY_ACCURACY_FACTOR[self.world.difficulty]

        shift=generals.Vector2(delta_x*scale,delta_y*scale)
        self.destination+=shift
        #print 'random shift of',self.carrier.id,shift

    def smartAiming(self):
        '''Try to adjust bullet destination by predicting target's
        next move.
        '''
        delta_t=(self.target.pos_center-self.pos_center).get_length()/self.speed
        shift=self.target.heading*self.target.speed*delta_t
        self.destination+=shift
        #print 'smart shift of',self.carrier.id,shift
        

    def makeDamage(self):
        pass


class GunBullet(Bullet):

    def __init__(self,weapon_type,fire_range,damage_range,height,top_damage,\
            friend_damage,target,carrier,\
            world,pos_center,image,speed,life):

        self.pos_center=pos_center
        self.size=image.get_size()
        self.topleft=generals.center2Topleft(center=self.pos_center,size=self.size)

        Bullet.__init__(self,weapon_type,fire_range,damage_range,height,top_damage,\
            friend_damage,target,carrier,\
            world,self.topleft,image,speed,life)

        #----Register enemies that have taken damage, to avoid double hits-------
        self.units_in_path_regi=[]

        self.setDestination()

    def setDestination(self):

        #----Straight-line-moving type of weapons--------------------------
        if self.weapon_type in ['machinegun','rifle',\
                'sniper','flamer']:

            vector2target=self.target.pos_center-self.pos_center
            heading=vector2target.normalize()
            #set destination to the farest point along the shooting line, so
            # that penetrating of the bullet could be possible to simulate. 
            self.destination=heading*self.fire_range+self.pos_center

            #----Rotate bullet image to face to target-------------------
            theta=numpy.arctan2(-heading[1],heading[0])/numpy.pi*180.
            self.image=pygame.transform.rotate(self.image,theta)

            #----Relocate the topleft by pos_center--------------------------
            self.size=self.image.get_size()
            self.topleft=generals.center2Topleft(center=self.pos_center,size=self.size)

        self.smartAiming()
        self.randomOffset()

    def makeDamage(self):

        if self.friend_damage:
            units_in_path=self.world.all_troops.values()
        else:
            if self.team==1:
                units_in_path=self.world.team2.values()
            elif self.team==2:
                units_in_path=self.world.team1.values()

        #----Use sprite group to detect collision--------------------------
        group=pygame.sprite.Group(*units_in_path)

        #----Straight-line-moving type of weapons--------------------------
        if self.weapon_type in ['machinegun','rifle',\
                'sniper','flamer']:

            hit_target=pygame.sprite.spritecollideany(self,group)

            if hit_target is not None:
                if hit_target not in self.units_in_path_regi:

                    if GOD_MOD and hit_target.team==1:
                        pass
                    else:
                        #----Certain chance for the enemy to miss------
                        if self.team==2:
                            chance=parameters.DIFFICULTY_ENEMY_MISS_CHANCE[\
                                    self.world.difficulty]
                            if random.randint(0,100)<=chance:
                                miss_marker=StaticMarker(self.world,\
                                        self.topleft,image=None,text='miss',time=700,\
                                        font_size=20,color=(255,50,50))
                                self.world.addMarker(miss_marker)
                                return

                        hit_target.life-=self.top_damage
                        #----Count kill--------------------------
                        if hit_target.life<=0:
                            self.carrier.kill+=1
                            self.carrier.upgradeRank()

                        self.life-=1
                        #----Add the target hit to this register list to avoid double hits-
                        self.units_in_path_regi.append(hit_target)

            if (self.pos_center-self.destination).get_length()<=0.1:
                #----Disappear when get to fire range--------------------------
                self.life=0


class ShellBullet(Bullet):

    def __init__(self,weapon_type,fire_range,damage_range,height,top_damage,\
            friend_damage,target,carrier,explode_sounds,\
            world,pos_center,images,speed,life,layer=1,heading=(1,0)):

        #-Get a single image 1st to pass to Bullet.__init__(), which will
        # pass that to Gameobject.__init__(), where size is obtained from
        # image.
        self.images=images
        self.image=self.images[0]
        self.size=self.image.get_size()
        self.topleft=generals.center2Topleft(center=pos_center,size=self.size)
        self.explode_sounds=explode_sounds

        Bullet.__init__(self,weapon_type,fire_range,damage_range,height,top_damage,\
            friend_damage,target,carrier,\
            world,self.topleft,self.image,speed,life,layer=1,heading=(1,0))

        self.image_index=0
        self.passed_time=0
        self.rate=100    #rate for swiching frames
        self.ismoving=True

        self.setDestination()
        self.getMovePath()

    def getMovePath(self):
        '''Get a list of corrdinates to simulate a parabolic curve.
        '''
        steps=2+int((abs(self.destination[0]-self.pos_center[0])+\
                abs(self.destination[1]-self.pos_center[1]))/13.)
        path_list=testbezier.getParabol(start=self.pos_center,end=self.destination,\
                height=self.height,steps=steps)
        self.path_list=path_list
        

    def setDestination(self):

        #----Parabolic-curve-moving type of weapons--------------------------
        if self.weapon_type in ['grenade','mortar','artillery']:
            self.destination=self.world.all_troops[self.target.id].pos_center

        self.smartAiming()
        self.randomOffset()

    def makeDamage(self):

        #----Parabolic-curve-moving type of weapons--------------------------
        if self.weapon_type in ['grenade','mortar','artillery']:

            if (self.pos_center-self.destination).get_length()<=0.1:

                if self.friend_damage:
                    targets=self.world.searchArea('bullet_all',self.id,self.damage_range)
                else:
                    targets=self.world.searchArea('bullet_enemy',self.id,self.damage_range)

                if len(targets)!=0:
                    for ii in targets:
                        ii.life-=self.top_damage*(ii.pos_center-self.pos_center).\
                                get_length()/self.damage_range
                        #----Count kill--------------------------
                        if ii.life<=0:
                            self.carrier.kill+=1
                            self.carrier.upgradeRank()

                #----Add animation here--------------------------
                ani=Animation(self.world,pos_center=self.pos_center,\
                        loop=1,rate=None,layer=1,**weapons.getRandomExplosion())
                self.world.addAnimation(ani)
                self.life-=1

                self.playExplodeSound()

    def playExplodeSound(self):
        explode_sound=random.choice(self.explode_sounds)
        self.world.thread_lock.acquire()
        self.world.sound_queue.put((explode_sound,self.pos_center[0]))
        self.world.thread_lock.release()
        


    #------Move along a list of coordinate pairs.----------
    def moveTo(self,time_passed):
        '''Move along a list of coordinate pairs.

        '''
        #if self.topleft==self.path_list[-1]:
        if self.pos_center==self.path_list[-1]:
            self.ismoving=False    #used to toggle animation if True
            return 

        #----Next point to move to--------------------------
        destination=self.path_list[0]
        if self.pos_center==destination:

            #----If the current destination is the last grid box in path_list-----
            if len(self.path_list)==1:
                destination=self.path_list[0]
                self.pos_center=destination
                self.ismoving=False
                return
            else:
                #----Remove the current destination and set to the next one in path_list
                del self.path_list[0]
                destination=self.path_list[0]

        move_vector=destination-self.pos_center
        move_length=move_vector.get_length()
        self.heading=move_vector.get_normalized()
        actual_move_length=min(move_length,time_passed/1000.*self.speed)
        self.pos_center+=actual_move_length*self.heading
        self.topleft=generals.center2Topleft(center=self.pos_center,size=self.size)

        self.ismoving=True

        self.selectFrame(time_passed)


    def selectFrame(self,time_passed):
        '''Designed for grenades to rotate in air.
        '''

        if len(self.images)==1:
            self.image=self.images[0]
            return
        else:
            if self.ismoving:
                self.passed_time+=time_passed
                self.image_index=(self.passed_time/self.rate)%len(self.images)
                if self.image_index==0 and self.passed_time>=self.rate:
                    self.passed_time=0
            else:
                self.image_index=0

            self.image=self.images[self.image_index]


    def draw(self,surface=None):
        #----Rotate according to heading--------------------------
        if self.weapon_type in ['mortar','artillery']:
            self.rotate()
        
        if surface is None:
            GameObject.draw(self)
        else:
            GameObject.draw(self,surface)


class StatusBar():
    shift=-generals.Vector2(0,2)
    def __init__(self,topleft,length,max_value,value,color_max,color_value):

        #----Shift from the topleft of the soldier rect--------------------------
        #self.topleft=topleft+self.shift
        self.topleft=topleft
        self.length=length
        self.max_value=max_value
        self.value=value
        self.color_max=color_max   #Back ground color
        self.color_value=color_value  

        self.max_box=pygame.surface.Surface((self.length,3))
        self.max_box.fill(color_max)

    def draw(self,surface):

        width=int((float(self.value)/self.max_value)*self.length)
        width=max(0,width)
        value_box=pygame.surface.Surface((width,3))
        value_box.fill(self.color_value)
        surface.blit(self.max_box,self.topleft)
        surface.blit(value_box,self.topleft)

    def update(self,value,topleft):
        self.topleft=topleft+self.shift
        self.value=value

        
class Insignia(object):
    images=[]
    shift=generals.Vector2(8,0)   #shift from center of soldier
    rank_dict={\
            'soldier':None,\
        'private':0,\
        'private_1st':1,\
        'corporal':2,\
        'sergeant':3,\
        'staff_sergeant':4,\
        'sergeant_1st':5\
        }

    def __init__(self,carrier):

        self.carrier=carrier
        if len(self.images)==0:
            self.images=generals.splitImage(*objects.object_images['insignia'])

    @property
    def rank(self):
        return self.carrier.rank
    @property
    def topleft(self):
        return self.carrier.pos_center+self.shift
    @property
    def image_index(self):
        return self.rank_dict[self.rank]

    def draw(self,surface):
        if self.image_index is not None:
            self.image=self.images[self.image_index]
            surface.blit(self.image,self.topleft)


class StaticMarker(object):
    def __init__(self,world,topleft,image=None,text=None,time=1000,\
            font_size=10,color=(255,255,255)):

        self.world=world
        self.topleft=topleft
        self.image=image
        self.text=text
        self.time=time
        self.font_size=font_size
        self.color=color
        self.alive=True
        self.passed_time=0

        if text is not None:
            #----Font--------------------------
	    self.font=pygame.font.Font(E_FONT,self.font_size)
            self.image=self.font.render(self.text,True,self.color)
            self.size=self.image.get_size()

        self.size=self.image.get_size()
        #self.topleft=center2Topleft(center=self.pos_center,size=self.size)
        self.pos_center=generals.topleft2Center(topleft=self.topleft,size=self.size)


    def draw(self,time_passed,surface):
        self.passed_time+=time_passed
        if self.passed_time>=self.time:
            self.alive=False
            return
        else:
            surface.blit(self.image,self.topleft)


class GameScene():
    def __init__(self,level_info,surface,effect_volume,\
            difficulty='Mid',player_name='player',\
            friend_damage=False):
        
        self.level_info=level_info
        self.background=level_info.background_image
        self.mask_map=level_info.mask_image
        self.weather=level_info.weather
        self.level=level_info.level
        self.hq_life=level_info.hq_life
        self.money=level_info.money

        self.surface=surface
        self.difficulty=difficulty
        self.player_name=player_name
        self.friend_damage=friend_damage

        self.team1={}
        self.team2={}
        self.all_troops={}
        self.soldier_queue=None

        self.team1_count=0
        self.team2_count=0
        self.all_count=0

        self.bullets={}
        self.bullet_count=0

        self.animations={}
        self.animation_count=0

        self.markers={}
        self.marker_count=0

        self.preProcessMaskMap()

        self.clock=pygame.time.Clock()
        self.clock.tick(30)
        self.global_time_passed=0
        self.all_names={1:[],2:[]}
        self.dead_names={1:[],2:[]}

        self.ammoboxs={}
        self.ammobox_count=0

        self.effect_volume=effect_volume
        self.GAME_OVER_EVENT=None
        self.sound_queue=None



    def addIntelCenter(self,intel_center):
        self.intel_center=intel_center


    def replenishMoney(self,time_passed):
        #----Replenish every n seconds of time----------
        if (self.global_time_passed/1000)%20==0:
            add_money=parameters.DIFFICULTY_MONEY_REPLENISH_FACTOR[self.difficulty]*\
                    (1+random.uniform(0,0.5))
            self.money+=int(add_money)

    def preProcessMaskMap(self):
        '''Preprocess level mask map to get way points and paths
        '''
        via_map=prepromask.regrid(self.mask_map,GRID_SIZE)
        self.spots=prepromask.readSpots(via_map)
        self.via_map=prepromask.viaimage2Viamap(via_map)
        self.player_via_map=prepromask.viaimage2Viamap(via_map,\
                block_value=prepromask.COLOR_CODES['viable'])
        
    def addBullet(self,bullet):
        self.bullets[self.bullet_count]=bullet
        bullet.id=self.bullet_count
        self.bullet_count+=1

    def addAmmoBox(self,ammobox):
        self.ammoboxs[self.ammobox_count]=ammobox
        ammobox.id=self.ammobox_count
        self.ammobox_count+=1

    def addTroop(self,soldier):
        self.all_troops[self.all_count]=soldier
        soldier.id=self.all_count
        self.all_count+=1

        if soldier.team==1:
            self.team1[self.team1_count]=soldier
            self.team1_count+=1
        elif soldier.team==2:
            self.team2[self.team2_count]=soldier
            self.team2_count+=1

    def addAnimation(self,ani):
        self.animations[self.animation_count]=ani
        ani.id=self.animation_count
        self.animation_count+=1

    def addMarker(self,marker):
        self.markers[self.marker_count]=marker
        marker.id=self.marker_count
        self.marker_count+=1


    def searchArea(self,search_type,id,radius,min_radius=0):

        search_list=[]
        if len(self.all_troops)==0:
            return []

        if search_type=='enemy':

            center=self.all_troops[id].pos_center

            for ii in self.all_troops.values():
                if ii.team==self.all_troops[id].team:
                    continue
                if (ii.pos_center-center).get_length()<=radius:
                    search_list.append(ii)

        elif search_type=='enemy_bomb':

            center=self.all_troops[id].pos_center

            for ii in self.all_troops.values():
                if ii.team==self.all_troops[id].team:
                    continue
                if (ii.pos_center-center).get_length()<=radius and\
                        (ii.pos_center-center).get_length()>=min_radius:
                    search_list.append(ii)

        elif search_type=='bullet_enemy':
            center=self.bullets[id].pos_center
            for ii in self.all_troops.values():
                if ii.team==self.bullets[id].team:
                    continue
                if (ii.pos_center-center).get_length()<=radius:
                    search_list.append(ii)

        elif search_type=='bullet_all':
            center=self.bullets[id].pos_center
            for ii in self.all_troops.values():
                if (ii.pos_center-center).get_length()<=radius:
                    search_list.append(ii)

        elif search_type=='allies':
            center=self.all_troops[id].pos_center

            for ii in self.all_troops.values():
                if ii.team!=self.all_troops[id].team:
                    continue
                if ii.id==id:
                    continue
                if (ii.pos_center-center).get_length()<=radius:
                    search_list.append(ii)

        return search_list




    def drawAll(self,time_passed):
        for ii in self.all_troops.values():
            ii.draw(time_passed)

    def drawAnimations(self,time_passed,surface=None):
        for ii in self.animations.values():
            if ii.loop>0:
                ii.draw(time_passed,surface)

    def drawMarkers(self,time_passed,surface=None):
        for ii in self.markers.values():
            if ii.alive:
                ii.draw(time_passed,surface)

    def drawAmmoBoxs(self,surface=None):
        for ii in self.ammoboxs.values():
            if ii.load>0 and ii.life>0:
                ii.draw(surface)

    def globalTimer(self):
        self.global_time_passed+=self.clock.get_time()
        self.clock.tick(30)

    def layeredDraw(self,time_passed,surface):
        #layers=[ii.layer for ii in self.all_troops.values()]
        #index=numpy.argsort(layers)

        '''
        self.soldier_lock.acquire()
        for ii in index:
            self.soldier_queue.put(self.all_troops.values()[ii])
        self.soldier_lock.release()
        '''
        for ii in self.all_troops.values():
            ii.update(time_passed,surface)
        '''
        for ii in self.soldier_threads.values():
            ii.join()
        '''

    def drawAllBullets(self,time_passed,surface=None):
        for ii in self.bullets.values():
            ii.moveTo(time_passed)
            ii.makeDamage()
            ii.draw(surface)

    def removeDead(self):
        for kk,vv in self.bullets.items():
            if vv.life<=0:
                del self.bullets[kk]

        for kk,vv in self.animations.items():
            if vv.loop<=0:
                del self.animations[kk]

        for kk,vv in self.markers.items():
            if vv.alive==False:
                del self.markers[kk]

        for kk,vv in self.ammoboxs.items():
            if vv.load<=0 or vv.life<=0:
                del self.ammoboxs[kk]

        for kk,vv in self.all_troops.items():
            # TODO: show the dead frame for a while before removing
            if vv.life<=0:
                del self.all_troops[kk]

        for kk,vv in self.team1.items():
            if vv.life<=0:
                # Put dead solider's slot back to avaiable list
                self.spots['defence'].append(vv.slot) 

                #----Send dead info to intel center------------------
                intel_text=vv.rank.capitalize()+' '+vv.name+' died.'
                death_intel=intel.Intel(text=intel_text,intel_type='dead',\
                        priority=2,start=self.global_time_passed,\
                        time=3000)
                self.intel_center.addNewIntel(death_intel)

                #----Get name--------------------------
                self.dead_names[1].append(vv.name)
                del self.team1[kk]


        for kk,vv in self.team2.items():
            if vv.life<=0:
                #----Get name--------------------------
                self.dead_names[2].append(vv.name)
                del self.team2[kk]


    def updateHQ(self,time_passed):

        self.replenishMoney(time_passed)

        #----Attack HQ--------------------------
        for kk,vv in self.team2.items():
            if generals.window2Grid(vv.pos_center,GRID_SIZE,TOPLEFT) in\
                    self.spots['hq']:
                self.hq_life-=1

                #----Send hq attack intel to intel center------------------
                intel_text='HQ under attack!!!!'
                hq_intel=intel.Intel(text=intel_text,intel_type='hq',\
                        priority=2,start=self.global_time_passed,\
                        time=3000)
                self.intel_center.addNewIntel(hq_intel)
                #print 'remove enemy after attacking hq',vv.id
                del self.all_troops[vv.id]
                del self.team2[kk]

        if self.money<=100:
            #----Send money shortage intel to intel center------------------
            intel_text='We are running out of money...'
            money_intel=intel.Intel(text=intel_text,intel_type='money',\
                    priority=4,start=self.global_time_passed,\
                    time=3000)
            self.intel_center.addNewIntel(money_intel)

        if self.hq_life<=0:
            return True


    def playBackgroundShot(self):
        if self.hq_life>0:
            if random.randint(0,400)==1:
                back_sound=random.choice(sounds.sound_manager.\
                        all_sounds['background_fire'])
                self.thread_lock.acquire()
                self.sound_queue.put((back_sound,0.5*SCREEN_SIZE[0]))
                self.thread_lock.release()

    def drawUnitCircle(self,mouse_event):
        for ii in self.all_troops.values():
            result=ii.click(mouse_event)
            if result:
                break


class Barrack(object):

    def __init__(self,scene):

        self.scene=scene
        circles,info=objects.object_images['greencircle']
        self.circle=generals.splitImage(circles,info)[-1]

        self.boxedges=generals.splitImage(*objects.object_images['boxedge'])
        self.level_info=self.scene.level_info
        

    #-----Create soldier----------
    def addTroop(self,slot,weapon_type):

        if weapon_type=='ammo':
            topleft=generals.grid2Window(slot,GRID_SIZE,TOPLEFT)
            #----Over write ammo number using level info------------
            ammo_load=self.level_info.player_ammo_dict[weapon_type]
            weapon_dict=weapons.WEAPON_DICT['ammo']
            weapon_dict['load']=ammo_load
            ammobox=AmmoBox(world=self.scene,topleft=topleft,speed=0,\
                    **weapon_dict)
            ammobox.slot=slot
            self.scene.money-=weapons.WEAPON_PRICES[weapon_type]
            self.scene.addAmmoBox(ammobox)
            self.scene.spots['defence'].remove(slot)

        else:
        
            random_name=readnames.pickRandom()
            topleft=generals.grid2Window(slot,GRID_SIZE,TOPLEFT)
            troop_dict=troops.TROOP_DICT[weapon_type]
            #----Over write ammo number using level info------------
            troop_dict['ammo']=self.level_info.player_ammo_dict[weapon_type]
            
            if weapon_type=='medi':
                soldier=MediDoctor(team=1,name=random_name,rank='soldier',weapon=None,\
                        world=self.scene,topleft=topleft,layer=1,\
                        **troop_dict)
            else:
                soldier=Soldier(team=1,name=random_name,rank='soldier',weapon=None,\
                        world=self.scene,topleft=topleft,layer=1,\
                        **troop_dict)

            soldier.path_finder=pathfinder_class2.PathFinder(\
                    self.scene.player_via_map)

            #----Create weapon--------------------------
            if weapon_type in ['grenade','artillery','mortar']:
                weapon=BombWeapon(world=self.scene,pos_center=soldier.pos_center,\
                        carrier=soldier,**weapons.WEAPON_DICT[weapon_type])
            else:
                weapon=Weapon(world=self.scene,pos_center=soldier.pos_center,carrier=soldier,\
                        **weapons.WEAPON_DICT[weapon_type])

            soldier.getWeapon(weapon)
            self.scene.addTroop(soldier)
            self.scene.all_names[soldier.team].append(soldier.name)
            self.scene.money-=weapons.WEAPON_PRICES[weapon_type]

            #----Take care of avaiable slot list--------------------------
            soldier.slot=slot
            if weapon_type != 'medi':
                self.scene.spots['defence'].remove(slot)


        
    def replaceCursor(self,weapon_type):
        if weapon_type is not None:

            size=2*weapons.WEAPON_DICT[weapon_type]['fire_range']

            self.circle_copy=self.circle.copy()
            self.circle_copy=pygame.transform.scale(self.circle_copy,(size,size))

            if weapon_type in ['grenade','mortar','artillery']:
                
                min_size=2*weapons.WEAPON_DICT[weapon_type]['min_fire_range']
                min_range_circle=self.circle.copy()
                min_range_circle=pygame.transform.scale(min_range_circle,\
                        (min_size,min_size))

                min_topleft=(int(size/2.-min_size/2.),(size/2.-min_size/2.))
                generals.chopCenter(self.circle_copy,min_range_circle,min_topleft)

            if weapon_type=='ammo':
                troop_image=weapons.AMMO['images'][0]   
            else:
                troop,info=troops.images['%ssoldier' %weapon_type]
                troop_image=generals.splitImage(troop,info)[0].convert_alpha()

            #troop_image=generals.setAlpha(troop_image,190,copy=True)
            troop_size=troop_image.get_size()

            self.circle_copy.blit(troop_image,dest=((size-troop_size[0])/2.,\
                    (size-troop_size[1])/2.))


    def drawCircleAndSlot(self,mouse_pos,surface=None):
        pygame.mouse.set_visible(False)
        size=self.circle_copy.get_size()
        topleft=(mouse_pos[0]-size[0]/2.,mouse_pos[1]-size[1]/2.)

        boxtopleft=self.highlightSlot(mouse_pos)

        if surface is None:
            self.scene.surface.blit(self.circle_copy,topleft)
            self.scene.surface.blit(self.boxedge,boxtopleft)
        else:
            surface.blit(self.circle_copy,topleft)
            surface.blit(self.boxedge,boxtopleft)

    def resetCursor(self):
        pygame.mouse.set_visible(True)

    def highlightSlot(self,mouse_pos):

        box=generals.window2Grid(mouse_pos,GRID_SIZE,TOPLEFT)
        if box in self.scene.spots['defence']:
            self.boxedge=self.boxedges[0]
        else:
            self.boxedge=self.boxedges[1]

        topleft=generals.grid2Window(box,GRID_SIZE,TOPLEFT)
        return topleft


class SoldierThread(threading.Thread):
    def __init__(self,queue,lock,surface):
        threading.Thread.__init__(self)
        self.queue=queue
        self.lock=lock
        self.clock=pygame.time.Clock()
        self.surface=surface
        self.stop=False
        '''
        #self._stop=threading.Event()
        def stop(self):
            self._stop.set()
        def stopped(self):
            return self._stop.isSet()
        '''
        #print 'soldier thread',self.getName(),'initialized'

    def run(self):
        while True and not self.stop:
            time_passed=self.clock.tick(30)
            self.lock.acquire()
            if not self.queue.empty():
                soldier=self.queue.get()
                soldier.update(time_passed,self.surface)
                self.queue.task_done()
                self.lock.release()
            else:
                self.lock.release()
            pygame.time.wait(30)


class EnemySpawn():

    def __init__(self,scene):
        self.scene=scene
        self.level_info=self.scene.level_info

        self.enemy_groups=self.level_info.enemy_groups
        self.intra_pause=self.level_info.intra_pause*parameters.DIFFICULTY_PAUSE_FACTOR[\
                self.scene.difficulty]
        self.inter_pause=self.level_info.inter_pause*parameters.DIFFICULTY_PAUSE_FACTOR[\
                self.scene.difficulty]

        self.spawn_spots=self.scene.spots['enemy_spawn']
        self.hq_spots=self.scene.spots['hq']

        self.intra_timer=0
        self.inter_timer=0

        self.enemy_groups2=[]   #all enemies
        for ii in self.enemy_groups:
            listii=[]      # ii for each enemy list
            for jj in ii:
                #----Open up each tuple to get a list of weapon types---
                # e.g. ('rifle',3)  ->   ['rifle',rifle',rifle']
                listjj=[jj[0],]*jj[1]  
                #----Append to enemy list of group ii-------
                listii+=listjj
            self.enemy_groups2.append(listii)

        #----Create a dict for all possible combinations of spawn spot ~ hq spot paths
        self.path_finder=pathfinder_class2.PathFinder(self.scene.via_map)
        self.paths={}
        for ii in self.spawn_spots:
            for jj in self.hq_spots:
                self.path_finder.start=ii
                self.path_finder.end=jj
                self.path_finder.findPath()
                self.paths[(ii,jj)]=self.path_finder.path

    def spawnAtRandom(self,time_passed):
        self.inter_timer+=time_passed
        self.intra_timer+=time_passed

        if self.inter_timer>=self.inter_pause:
            if len(self.enemy_groups2)==0:
                return None
            else:
                self.current_group=self.enemy_groups2[0]

                if self.intra_timer>=self.intra_pause:
                    if len(self.current_group)==0:
                        del self.enemy_groups2[0]
                        self.inter_timer=0
                        return None
                    else:
                        spot=random.choice(self.spawn_spots)
                        end=random.choice(self.hq_spots)
                        soldier=self.createSoldier(spot,end,self.current_group[0])
                        weapon=self.createWeapon(self.current_group[0],soldier)
                        soldier.getWeapon(weapon)
                        self.scene.addTroop(soldier)
                        self.scene.all_names[soldier.team].append(soldier.name)

                        self.intra_timer=0
                        del self.current_group[0]
                        return True



    def createSoldier(self,spot,end,weapon_type):

        #----Create enemy--------------------------
        path=self.paths[(spot,end)]
        random_name=readnames.pickRandom()
        enemy_pos=generals.grid2Window(spot,GRID_SIZE,TOPLEFT)

        #----Overwrite ammo using level info--------------------------
        ammo=int(self.level_info.enemy_ammo_dict[weapon_type]*\
                parameters.DIFFICULTY_ENEMY_AMMO_FACTOR[self.scene.difficulty])
        troop_dict=troops.TROOP_DICT[weapon_type]
        troop_dict['ammo']=ammo

        enemy=Soldier(team=2,name=random_name,rank='soldier',weapon=None,\
                world=self.scene,topleft=enemy_pos,layer=1,\
                **troop_dict)
                
        enemy.path_list=copy.copy(path)

        return enemy

        
    def createWeapon(self,weapon_type,soldier):

        #----Create weapon--------------------------
        if weapon_type in ['grenade','mortar','artillery']:
            weapon=BombWeapon(world=self.scene,pos_center=soldier.pos_center,\
                    carrier=soldier,**weapons.WEAPON_DICT[weapon_type])
        else:
            weapon=Weapon(world=self.scene,pos_center=soldier.pos_center,carrier=soldier,\
                    **weapons.WEAPON_DICT[weapon_type])

        return weapon

    def isVictory(self):
        win=len(self.enemy_groups2)==0 and\
                self.scene.hq_life>0 and\
                len(self.scene.team2)==0
        return win
