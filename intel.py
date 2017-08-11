'''Class for intel and intel center
'''
import numpy
import random

# Max time postpone (ms) for intel of different priorities
MAX_POSTPONE_TIME={1:0,\
        2:2000,\
        3:2000,\
        4:1000\
        }

# Description wordings for incoming enemy
# key: enemy number range, value: list of descriptive words
ENEMY_NUM_DESCRIPTION={\
        (1,6):['A team of','Several','A fireteam of'],\
        (6,11):['A squard of','A crew of','Several'],\
        (11,21):['A section of','A combat group','More than 10','A big group of'],\
        (21,41):['A platoon of','A troop of','Tens of','A larget group of'],\
        (41,250):['A company of','A squadron of']\
        }


class Intel(object):
    def __init__(self,text,intel_type,priority,start,time,color=(255,255,255),\
            font_size=20,repeat=1):

        self._text=text
        self.intel_type=intel_type
        self.priority=priority
        self.time=time
        self.start=start
        self.end=self.start+self.time
        self.color=color
        self.font_size=font_size
        self.repeat=repeat

    @property
    def max_postpone(self):
        return MAX_POSTPONE_TIME[self.priority]

    @property
    def text(self):
        return self._text+'   '


class IntelCenter(object):
    def __init__(self,world,enemysprawn):

        self.world=world
        self.enemysprawn=enemysprawn
        self.new_intels=[]
        self.time_table={}
        self.active_intel=None

        self.getTopPrioIntels()
        self.current_point=0


    @property
    def global_timer(self):
        return self.world.global_time_passed

    @staticmethod
    def getRandomDiscription(number):
        for kk,vv in ENEMY_NUM_DESCRIPTION.items():
            if number >= kk[0] and number <=kk[1]:
                return vv[random.randint(0,len(vv)-1)]


    def getTopPrioIntels(self):

        for ii in range(len(self.enemysprawn.enemy_groups2)):
            number=len(self.enemysprawn.enemy_groups2[ii])
            start=ii*(self.enemysprawn.inter_pause+\
                    self.enemysprawn.intra_pause*(number-1))
            length=self.enemysprawn.inter_pause*0.8
            end=start+length
            #print 'start',start
            #print 'end',end
            random_discrip=IntelCenter.getRandomDiscription(number)
	    if ii==len(self.enemysprawn.enemy_groups2)-1:
		text='Final wave coming'
	    else:
		if random_discrip[0]=='A':
	            text='Warning.  '+random_discrip+' enemies is coming.'
		else:
	            text='Warning.  '+random_discrip+' enemies are coming.'

            intel=Intel(text=text,intel_type='enemy_intel',priority=1,\
                    start=start,time=length,color=(255,100,100),font_size=25)
            self.time_table[(start,end)]=intel



    def update(self):

        #----Remove expired intels and Update active intel-----
        for ii in self.time_table.keys():
            if self.global_timer > ii[1]:
                del self.time_table[ii]

        self.active_intel=None
        for ii in self.time_table.keys():
            if  (ii[1]-self.global_timer)*(self.global_timer-ii[0])>=0:
                self.active_intel=self.time_table[ii]
                break
        
        #----Get all intels--------------------------
        all_intels=self.new_intels+self.time_table.values()
        self.new_intels=[]

        #----Empty time table--------------------------
        if self.active_intel is not None:
            self.time_table={(self.active_intel.start,self.active_intel.end):\
                    self.active_intel}
            all_intels.remove(self.active_intel)
        else:
            self.time_table={}

        #----Sort by priority--------------------------
        prios=[ii.priority for ii in all_intels]
        prio_index=numpy.argsort(prios)
        sorted_intels=[all_intels[ii] for ii in prio_index]

        #----Refresh time table--------------------------
        for intel in sorted_intels:
            self.reArrange(intel)


    def addNewIntel(self,intel):
        self.new_intels.append(intel)

    def reArrange(self,intel):
        start=intel.start
        end=intel.end

        if self.checkTimeTable(start,end):
            self.time_table[(start,end)]=intel
        else:
            new_time_slot=self.postpone(intel)
            if new_time_slot is not None:
                self.time_table[new_time_slot]=intel


    def checkTimeTable(self,start,end):
        '''Check time table and return bool, if True,
        could fit in (start,end) into time table.
        '''
        for kk in self.time_table.keys():

            if (kk[1]-start)*(start-kk[0])>=0 or\
                    (kk[1]-end)*(end-kk[0])>=0:
                return False
            if (end-kk[1])*(kk[1]-start)>=0 or\
                    (end-kk[0])*(kk[0]-start)>=0:
                return False
            else:
                continue
        return True


    def postpone(self,intel):
        post_timestep=100
        start=intel.start
        end=intel.end

        while True:
            start+=post_timestep
            end+=post_timestep
            if self.checkTimeTable(start,end):
                intel.start=start
                intel.end=end
                return (start,end)
            else:
                #----Maximum delay--------------------------
                if start-intel.start>=intel.max_postpone:
                    return None
                else:
                    continue
