import random
import intel
from generals import window2Grid
from generals import grid2Window
from startlevel import GRID_SIZE
from startlevel import TOPLEFT
import weapons

RANDOM_SHOUTs=[
        'Taking fire !!!',\
        'Fire at will.',\
        'GET THEM ALL !!!'\
        ]
DIFFICULTY_FIRE_CHANCE_FACTOR={
        'Come on':1+0.2,\
        'Low':1+0.1,\
        'Mid':1.,\
        'High':1-0.1,\
        'Are You Sure?':1+0.2\
        }

DIFFICULTY_FIRE_NUM_FACTOR={
        'Come on':1,\
        'Low':2,\
        'Mid':3,\
        'High':4,\
        'Are You Sure?':5\
        }

DIFFICULTY_AIM_PAUSE_FACTOR={
        'Come on':500,\
        'Low':450,\
        'Mid':400,\
        'High':300,\
        'Are You Sure?':200\
        }


class State():
    def __init__(self,name):
        self.name=name
    
    def do_actions(self,time):
        pass
    def check_conditions(self):
        pass
    def entry_actions(self):
        pass
    def exit_actions(self):
        pass


class StateMachine():

    def __init__(self,init_state):
        self.states={}
        self.active_state=init_state
        self.init_state=init_state

        self.addState(init_state)

    def addState(self,state):
        self.states[state.name]=state

    def think(self,time_passed):
        self.active_state.do_actions(time_passed)
        new_state_name=self.active_state.check_conditions()
        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self,new_state_name):
        if self.active_state is not None:
            self.active_state.exit_actions()

        self.active_state=self.states[new_state_name]
        self.active_state.entry_actions()

    @staticmethod
    def getRandomShout():
        return RANDOM_SHOUTs[random.randint(0,len(RANDOM_SHOUTs)-1)]


class MarchingState(State):

    def __init__(self,soldier):
        State.__init__(self,'marching')
        self.soldier=soldier

    def do_actions(self,time_passed):
        if self.soldier.path_list is not None:
            self.soldier.moveAlongPath(time_passed)

        else:
            return

    def entry_actions(self):
        pass

    def check_conditions(self):

        target=self.soldier.searchEnemey()
        #----Fire change according to difficulty------------
        chance=50*DIFFICULTY_FIRE_CHANCE_FACTOR[self.soldier.world.difficulty]

        if target is not None and self.soldier.ammo>0 and\
                random.randint(1,int(chance))==1:
            return 'firing'
        else:
            return None

class FiringState(State):
    def __init__(self,soldier):
        State.__init__(self,'firing')
        self.soldier=soldier

        self.fired_num=0
        self.timer=0
        self.current_speed=self.soldier.speed

    def do_actions(self,time_passed):
        self.timer+=time_passed
        self.soldier.moveAlongPath(time_passed)

        #----Fire after slowed down for n seconds--------------------------
        if self.soldier.ammo>0 and self.timer>=\
			DIFFICULTY_AIM_PAUSE_FACTOR[self.soldier.world.difficulty]:
            fired=self.soldier.fireAtWill(time_passed)
            if fired:
                self.fired_num+=1
        else:
            return

    def entry_actions(self):
        self.soldier._speed*=0.2

        #----Send defencing shout to intel center------------------
        intel_text='Enemy troop: '+StateMachine.getRandomShout()
        shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                priority=4,start=self.soldier.world.global_time_passed,\
                time=3000)
        self.soldier.world.intel_center.addNewIntel(shout_intel)

    def exit_actions(self):
        
        self.soldier._speed/=0.2
        self.fired_num=0
        self.timer=0

    def check_conditions(self):
        if self.soldier.ammo==0 or self.fired_num==\
                DIFFICULTY_FIRE_NUM_FACTOR[self.soldier.world.difficulty]:
            return 'marching'
        if self.soldier.searchEnemey() is None:
            return 'marching'
        else:
            return None


class DefencingState(State):

    def __init__(self,soldier):
        State.__init__(self,'defencing')
        self.soldier=soldier
        
    def do_actions(self,time_passed):
        if self.soldier.ammo>0:
            self.soldier.fireAtWill(time_passed)
            
    def entry_actions(self):
        #----Send defencing shout to intel center------------------
        intel_text=self.soldier.rank.capitalize()+' '+self.soldier.name+\
                ': '+StateMachine.getRandomShout()
        shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                priority=4,start=self.soldier.world.global_time_passed,\
                time=3000)
        self.soldier.world.intel_center.addNewIntel(shout_intel)

    def check_conditions(self):
        enemy=self.soldier.searchEnemey()
        if self.soldier.ammo==0:
            ammo=self.soldier.searchAmmo()
            if ammo is None:
                return None
            else:
                self.soldier.target_ammo=ammo
                return 'moveto_ammo'
        else:
            if enemy is not None and self.soldier.ammo>0:
                return 'defencing'
            else:
                return None

class StandByState(State):

    def __init__(self,soldier):
        State.__init__(self,'standby')
        self.soldier=soldier

    def do_actions(self,time_passed):
        #----Send standby shout to intel center------------------
        intel_text=self.soldier.rank.capitalize()+' '+self.soldier.name+\
                ' standing by.'
        shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                priority=4,start=self.soldier.world.global_time_passed,\
                time=3000)
        self.soldier.world.intel_center.addNewIntel(shout_intel)


    def check_conditions(self):
        enemy=self.soldier.searchEnemey()
        if self.soldier.ammo==0:
            ammo=self.soldier.searchAmmo()
            if ammo is None:
                return None
            else:
                self.soldier.target_ammo=ammo
                return 'moveto_ammo'
        else:
            if enemy is not None and self.soldier.ammo>0:
                return 'defencing'
            else:
                return None


class MediStandByState(State):

    def __init__(self,soldier):
        State.__init__(self,'medi_standby')
        self.soldier=soldier


    def do_actions(self,time_passed):
        if self.soldier.wound is None:
            #----Send standby shout to intel center------------------
            intel_text='Doctor '+self.soldier.name+\
                    ' standing by.'
        else: 
            #----Send standby shout to intel center------------------
            intel_text='Doctor '+self.soldier.name+\
                    ' coming!'
        shout_intel=intel.Intel(text=intel_text,intel_type='shout',\
                priority=4,start=self.soldier.world.global_time_passed,\
                time=3000)
        self.soldier.world.intel_center.addNewIntel(shout_intel)

    def check_conditions(self):
        self.wound=None
        wound=self.soldier.searchWound()

        if wound is not None and self.soldier.ammo>0:
            #----Switch to moveto--------------------------
            self.soldier.wound=wound

            if wound.life<=30:
                self.soldier.lock_check=True
            else:
                self.soldier.lock_check=False

	    if (self.soldier.pos_center-wound.pos_center).get_length()<=30:
	        return 'healing'
            else:
                return 'moveto_wound'
        else:
            return None


class MoveToWoundState(State):

    def __init__(self,soldier):
        State.__init__(self,'moveto_wound')
        self.soldier=soldier

    def entry_actions(self):
        self.soldier.path_finder.start=self.soldier.slot
        self.soldier.path_finder.end=self.soldier.wound.slot
        self.soldier.path_finder.findPath()
        self.soldier.path_list=self.soldier.path_finder.path
        self.soldier.ismoving=True

    def do_actions(self,time_passed):
        if self.soldier.path_list is not None:
            self.soldier.moveAlongPath(time_passed)

    def check_conditions(self):

        #----Stick to the current wound------------------
        if self.soldier.lock_check:
            #----Check wound still alive--------------------------
            if self.soldier.id in self.soldier.world.all_troops:

                #----Stop to heal when getting hereby--------------------------
                if (self.soldier.pos_center-self.soldier.wound.pos_center).\
                        get_length()<=30:
                    return 'healing'
                else:
                    return None
            else:
                return 'medi_standby'

        #----Check if there is a more wounded--------------------------
        elif self.soldier.lock_check==False:
            wound=self.soldier.searchWound()
            if wound is not None and self.soldier.wound.life-wound.life>=30:
                #self.soldier.wound=wound
                return 'medi_standby'
            else:
                #----Stop to heal when getting hereby--------------------------
                if (self.soldier.pos_center-self.soldier.wound.pos_center).\
                        get_length()<=30:
                    return 'healing'
                else:
                    return None

    def exit_actions(self):
        self.soldier.slot=window2Grid(self.soldier.topleft,GRID_SIZE,TOPLEFT)
        self.soldier.ismoving=False
	self.soldier.path_list=None


class HealingState(State):

    def __init__(self,soldier):
        State.__init__(self,'healing')
        self.soldier=soldier

    def entry_actions(self):
        self.soldier.ismoving=False

    def do_actions(self,time_passed):
        self.soldier.heal(time_passed)

    def check_conditions(self):
        #----Check wound still alive--------------------------
        if self.soldier.wound.id not in self.soldier.world.all_troops:
            return 'medi_standby'
        else:
            if self.soldier.wound.life<=30:
                self.soldier.lock_check=True
                return None
            elif self.soldier.wound.life>=60:
                self.soldier.lock_check=False
                return 'medi_standby'
    def exit_actions(self):
        self.soldier.wound=None


class MoveToAmmoState(State):

    def __init__(self,soldier):
        State.__init__(self,'moveto_ammo')
        self.soldier=soldier

    def entry_actions(self):
        self.soldier.path_finder.start=self.soldier.slot
        self.soldier.path_finder.end=self.soldier.target_ammo.slot
        self.soldier.path_finder.findPath()
        self.soldier.path_list=self.soldier.path_finder.path

    def do_actions(self,time_passed):
        if self.soldier.path_list is not None:
            self.soldier.moveAlongPath(time_passed)

    def check_conditions(self):
        #----Check ammo box still there--------------------------
        if self.soldier.target_ammo.id in self.soldier.world.ammoboxs:
            if (self.soldier.target_ammo.pos_center-self.soldier.pos_center).\
                    get_length() <=30:
                return 'recharge_ammo'
            else:
                return None
        else:
            return 'return_to_slot'

    def exit_actions(self):
        self.soldier.ismoving=False

class RechargeAmmoState(State):

    def __init__(self,soldier):
        State.__init__(self,'recharge_ammo')
        self.soldier=soldier

    def do_actions(self,time_passed):
        self.soldier.reload(time_passed)

    def check_conditions(self):
        if self.soldier.ammo==weapons.MAX_WEAPON_AMMO[self.soldier.weapon.weapon_type]:
            return 'return_to_slot'
        if self.soldier.target_ammo.load<=0:
            return 'return_to_slot'
        else:
            return None

    def exit_actions(self):
        self.soldier.target_ammo=None


class ReturnToSlotState(State):

    def __init__(self,soldier):
        State.__init__(self,'return_to_slot')
        self.soldier=soldier

    def entry_actions(self):
        self.soldier.path_finder.start=window2Grid(self.soldier.topleft,\
                GRID_SIZE,TOPLEFT)
        self.soldier.path_finder.end=self.soldier.slot
        self.soldier.path_finder.findPath()
        self.soldier.path_list=self.soldier.path_finder.path

        return

    def do_actions(self,time_passed):
        self.soldier.moveAlongPath(time_passed)

    def check_conditions(self):
        #dist=(self.soldier.topleft-grid2Window(self.soldier.slot,GRID_SIZE,TOPLEFT)).\
                #get_length()
        #if self.soldier.ismoving==False and dist<=0.1:
        if self.soldier.ismoving==False:
            return 'standby'
        else:
            return None

        






        
     

