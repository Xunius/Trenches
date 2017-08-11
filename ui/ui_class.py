'''Classes for buttons and widgets.
'''

import pygame
from generals import Vector2, splitImage, topleft2Center, center2Topleft, setAlpha
from pygame.locals import Rect, USEREVENT
import numpy
import random
import cus_font

E_FONT=cus_font.E_FONT_PATH8




TIPS=[\
	'Tip: Sniper bullets penetrate.',\
	'Tip: Explosive weapons create areal damage.',\
	'Tip: Mortars and artilleries reach far, but not too near.',\
	'Tip: Do not throw bombs straight up.',\
	'Tip: Try to save your men as they tend to lose their targets when wounded.',\
	"Tip: Occasionally troop can not return to their duty after reloading. Yes that is a but.",
	'Tip: Promoted to a higher rank, soldiers get more skilled in terms of accuracy and speed.',\
	'Tip: Army doctors will try to save the most injured first.',\
	'Tip: A good strategy to maximize the power of bombs is to slow down the vanguards with rifle boys and throw your bombs into the crowd.',\
	"Tip: Watch out for your men's health and ammo status.",\
	'Tip: Drop ammo boxes next to your soldiers for them to reload when depleted of ammo.',\
	'Tip: Click on your soldiers to check their firing range. Do the same to the enemy troops.',\
	'Tip: There was a "Friend damage" flag control inside the code, yet I FORGOT to add this into the option panel!',\
	'Tip: Enemies get faster, more accurate and aggressive in a higher difficulty level.',\
	'Tip: Place your far-range troops further behind from the front line to protect them.',\
	'Tip: Pay attention to the alert to the up-coming attacks, they are in RED.'\
        ]


def wrapText(text,width,line_gap,font,font_color):
    '''Wrap text into multi-lines and render
    <width>: float, line width (in pixels) to wrap text.
    <line_gap>: float, line gap in fractions of font height.
    <font>: pygame font obj.
    '''

    lines=[]
    step=2
    n1=0

    while True:
        if n1>len(text)-1:
            break

        n2=n1+step
        while True:
            if n2>len(text)-1:
                break
            if len(lines)==0:
                tii=text[n1:n2]
            else:
                tii='  %s' %(text[n1:n2])  # add indention
            sii=font.render(tii,True,font_color)

            if sii.get_size()[0]<width:
                n2+=step
                continue
            else:
                n2-=step
                #n2-=1  # make room for '-'
                break

        if len(lines)==0:
            tii=text[n1:n2]
        else:
            tii='  %s' %(text[n1:n2])
        # Add - at end as continuation of word
        if tii[-1] not in [',', '.', '?', '!', ' ', '\n'] and n2<len(text)-1:
            tii+='-'
        lines.append(tii)
        n1=n2

    #-------------------Render texts-------------------
    text_surface=[]
    for tii in lines:
        sii=font.render(tii,True,font_color)
        text_surface.append(sii)

    #-----------------Combine surfaces-----------------
    line_height=text_surface[0].get_size()[1]
    surface=pygame.Surface((width,line_height*len(lines)+\
            len(lines)*line_gap*line_height)).convert_alpha()
    surface.fill((0,0,0,0))   # remove background color

    for ii,sii in enumerate(text_surface):
        if ii==0:
            surface.blit(sii,(0,0))
        else:
            surface.blit(sii,(0,ii*line_height+line_gap*line_height*ii))

    return surface,lines


class NumberBox(object):
    def __init__(self,image,topleft,value,text_topleft_shift=(0,0),\
            font=None,color=(255,255,255),font_size=25):

        self.image=image
        self.topleft=Vector2(topleft)
        self.text_topleft_shift=text_topleft_shift
        self.text_topleft=self.topleft+text_topleft_shift

        self.value=value
        self.color=color
        self.font_size=font_size

        self.size=self.image.get_size()

        #----Font--------------------------
        if font is None:
            self.font=pygame.font.Font(E_FONT,self.font_size)
        else:
            self.font=pygame.font.Font(font,self.font_size)

        self.blitText()

    @property
    def text_size(self):
        return self.text_surface.get_size()

    @property
    def text(self):
        return str(self.value)

    def blitText(self):
        self.text_surface=self.font.render(self.text,True,self.color)


    #----Auto shrink to fit in box--------------------------
    def autoShrink(self):
        while self.text_size[0] >= self.size[0]-self.text_topleft_shift[0] or\
                self.text_size[1] >= self.size[1]-self.text_topleft_shift[1]:

            self.font_size-=2
            self.font=pygame.font.Font(E_FONT,self.font_size)
            
            self.blitText()

            if self.font_size<=1:
                break

        self.text_topleft[1]=(self.size[1]-self.text_size[1])/2.+self.topleft[1]

    def update(self,value,surface):
        if value!=self.value:
            self.value=value
            self.blitText()
            self.autoShrink()

        surface.blit(self.image,self.topleft)
        surface.blit(self.text_surface,self.text_topleft)


class Button(object):

    def __init__(self,images,image_info,topleft,text='button',bid='button',
            active=True,font=None,font_color=(255,255,255),font_size=25):

        self.images=images
        self.image_info=image_info   #could be None if image is a single image.
        self.topleft=Vector2(*topleft)
        self.text=text               # text to show, unless is None 
        self.bid=bid                   # identifier
        self.active=active
        self.isdown=False
        self.font_color=font_color
        self.font_size=font_size
        if font is None:
            self.font=pygame.font.Font(E_FONT,self.font_size)
        else:
            self.font=pygame.font.Font(font,self.font_size)

        #----Window Rect area where button is valid----------------
        self.valid_area=None

        if self.image_info is not None:
            self.images=splitImage(images,image_info)

            if len(self.images)==1:
                self.image=self.images[0]
            else:
                #----Use the 1st image as button up, 2nd as button down,
                # 3rd as deactivated----
                self.selectFrame()
        else:
            self.image=images

        #self.size=self.image.get_size()
        self.pos_center=topleft2Center(topleft=self.topleft,size=self.size)
        self.rect=Rect(self.topleft[0],self.topleft[1],\
                self.size[0],self.size[1])

    @property
    def size(self):
        return self.image.get_size()

    def selectFrame(self):

        if self.active:
            if self.isdown:
                self.image=self.images[1]
            else:
                self.image=self.images[0]
        else:
            self.image=self.images[2]


    def draw(self,surface):
        self.selectFrame()
        surface.blit(self.image,self.topleft)

        if self.text is not None and len(self.text)>0:
            self.text_surface=self.font.render(self.text,True,self.font_color)
            self.text_size=self.text_surface.get_size()
    	    self.text_topleft=(self.pos_center[0]-0.5*self.text_size[0],\
			self.pos_center[1]-0.5*self.text_size[1])
            surface.blit(self.text_surface,self.text_topleft)


    def isOver(self,point):
        '''Check wether mouse is over button
        '''
        if self.valid_area is None:

            in_x=point[0]>=self.topleft[0] and\
                    point[0]<=self.topleft[0]+self.size[0]
            in_y=point[1]>=self.topleft[1] and\
                    point[1]<=self.topleft[1]+self.size[1]
        else:
            in_x=point[0]>=self.topleft[0] and\
                    point[0]<=self.topleft[0]+self.size[0] and\
                    point[0]>=self.valid_area[0] and\
                    point[0]<=self.valid_area[0]+self.valid_area[2]
            in_y=point[1]>=self.topleft[1] and\
                    point[1]<=self.topleft[1]+self.size[1] and\
                    point[1]>=self.valid_area[1] and\
                    point[1]<=self.valid_area[1]+self.valid_area[3]

        return in_x and in_y

    def down_actions(self):
        pass


    def up_actions(self):
        pass


    def actions(self,mouse_event,func=None):
        '''
        <mouse_event>:(mouse_event_type,button,point):
            <mouse_event_type>: 'mouse_down' or 'mouse_up'.
            <button>: button number, 1 for left, 2 for mid, 3 for right.
            <point>: mouse position
        '''

        mouse_event_type,button,point=mouse_event

        if self.active and self.isOver(point):
            if mouse_event_type=='mouse_down' and self.isdown is False:
                self.isdown=True
                self.selectFrame()
                self.down_actions()
            elif mouse_event_type=='mouse_up' and self.isdown:
                self.isdown=False
                self.selectFrame()
                self.up_actions()


class MenuButton(Button):
    def __init__(self,images,image_info,topleft,text='MENU',bid='menu',
            active=True,font_color=(255,255,255),font_size=20):
        Button.__init__(self,images,image_info,topleft,text=text,bid=bid,
                active=True,font_color=font_color,font_size=font_size)
        self.PAUSE_EVENT=None

    def up_actions(self):
        self.PAUSE_EVENT=USEREVENT
        pause_event=pygame.event.Event(self.PAUSE_EVENT,message='')
        pygame.event.post(pause_event)


class AddTroopButton(Button):

    def __init__(self,world,price,images,image_info,topleft,text,
            active=True,font_size=10):

        self.world=world
        self.price=price

        Button.__init__(self,images,image_info,topleft,text=text,bid=text,
                active=active,font_size=font_size)

        #-------Blit price text onto buttom surfaces-------
        self.price_surface=self.font.render('$'+str(self.price),True,(255,255,255))
        price_surface_size=self.price_surface.get_size()

        # Centered horizontally, buttom vertically
        self.price_surface_topleft=((self.size[0]-price_surface_size[0])*0.5,
                self.size[1]-price_surface_size[1])
        for ii in self.images:
            ii.blit(self.price_surface,dest=self.price_surface_topleft)


    @property
    def active(self):
        return self.world.money>=self.price
    @active.setter
    def active(self,value):
        self._active=value

    def down_actions(self):
        return self.bid
    def up_actions(self):
        return self.bid

    def actions(self,mouse_event,func=None):
        '''
        <mouse_event>:(mouse_event_type,button,point):
            <mouse_event_type>: 'mouse_down' or 'mouse_up'.
            <button>: button number, 1 for left, 2 for mid, 3 for right.
            <point>: mouse position

        Return the button'text if it is active and get pressed.
        Otherwise return None.
        '''

        mouse_event_type,button,point=mouse_event
        result=None

        if self.active and self.isOver(point):
            if mouse_event_type=='mouse_down' and self.isdown is False:
                self.isdown=True
                self.selectFrame()
                result=self.down_actions()
            elif mouse_event_type=='mouse_up' and self.isdown:
                self.isdown=False
                self.selectFrame()
                result=self.up_actions()
            return result
        else:
            return None


class RollText(Button):
    def __init__(self,images,image_info,topleft,text,color=(255,255,255),
            font=None,font_size=25):

        Button.__init__(self,images,image_info,topleft,text=text)

        self.rolling_speed=0.08    #pixels per millisecond
        self.font_size=font_size
        self.color=color
        self.edge=(5,5)

        #----Font--------------------------
        if font is None:
            self.font=pygame.font.Font(E_FONT,self.font_size)
        else:
            self.font=pygame.font.Font(font,self.font_size)

        #----Clip out a slightly small area of self.image to blit text surface
        self.text_blit_surface=self.image.subsurface(self.edge[0],self.edge[1],\
		self.size[0]-2.*self.edge[0],self.size[1]-2.*self.edge[1])
        self.default_text_topleft=Vector2(self.text_blit_surface.get_width()+1,\
            0.5*(self.text_blit_surface.get_height()-self.font.get_height()))

        self.text_topleft=self.default_text_topleft

        #----Update text--------------------------
        self.updateText(text)

        #----Active intel--------------------------
        self.active_intel=None
        self.shift=Vector2(-self.rolling_speed*30.,0)


    def updateText(self,text):

        self.text=text
        if text is not None:
            self.text_surface=self.font.render(self.text,True,self.color)
            self.text_size=self.text_surface.get_size()
    	    self.text_topleft=(self.default_text_topleft[0],\
                0.5*(self.text_blit_surface.get_height()-self.text_size[1]))

    def updateByIntel(self,intel):
        if intel is not None:
            if self.active_intel is not intel:
                self.color=intel.color
                self.font_size=intel.font_size
                self.font=pygame.font.Font(E_FONT,self.font_size)
                self.updateText(intel.text)
                self.rolling_speed=float(self.size[0]+self.text_size[0]+1)/\
                        intel.time   #intel.time in milliseconds
                #self.shift=Vector2(-self.rolling_speed*33,0)  #use 33milliseconds
    	        self.active_intel=intel
        else:
            self.text=None



    def draw(self,time_passed,surface):

        if self.text is not None:

            #----Roll from right to left--------------------------
            self.shift=Vector2(-self.rolling_speed*time_passed,0)
            self.text_topleft+=self.shift

            if self.text_topleft[0]<=-self.text_size[0]:
        	self.text_topleft=(self.default_text_topleft[0],\
				self.default_text_topleft[1])

            #--Necessary to create a copy of the blit surface every frame,
            # otherwise all frames will overlap with one another ---------------
            blit_surface_copy=self.text_blit_surface.copy()
            blit_surface_copy.blit(self.text_surface,dest=self.text_topleft)

            surface.blit(self.image,self.topleft)
            surface.blit(blit_surface_copy,self.topleft+self.edge)
        else:
            surface.blit(self.image,self.topleft)


class ScrollMenu():

    def __init__(self,image,topleft,left_scroll,right_scroll,\
            buttons,auto_scale=False):

        self.image=image
        self.topleft=Vector2(topleft)
        self.size=image.get_size()
        self.pos_center=topleft2Center(topleft=topleft,size=self.size)
        self.rect=Rect(self.topleft[0],self.topleft[1],self.size[0],\
                self.size[1])
        self.auto_scale=auto_scale

        #----Dict to store all buttons--------------------------
        self.buttons={}
        self.button_keys=[]
        for ii in buttons:
            self.buttons[ii.bid]=ii
            self.button_keys.append(ii.bid)
        self.button_pressed=None

        #----Automatically scale buttons according to self.image--------
        if self.auto_scale:
            for ii in self.buttons.values():
                ii.image=pygame.transform.scale(ii.image,(ii.size[0],
                    int(self.size[1])))

        #----Size of a single button--------------------------
        self.single_button_size=buttons[0].size

        #----Distance from the topleft corner of the 1st button to the topleft of
        # menu bar--------------------------
        self.edge=Vector2(4,self.size[1]*0.1)
        self.edge=Vector2(0,0)

        #----When too many buttons to display-------------------------
        if (self.edge[0]+self.single_button_size[0])*len(self.buttons)\
                >=self.size[0]:

            left_scroll_image,left_scroll_info=left_scroll

            #----Create scrolling buttons--------------------------
            self.left_scroll=Button(left_scroll_image,left_scroll_info,
                    self.topleft,text=None,bid='left')
            self.buttons['left']=self.left_scroll
            self.left_scroll.active=False

            right_scroll_image,right_scroll_info=right_scroll
            right_topleft=self.topleft+Vector2(self.size[0]-\
                    self.left_scroll.size[0],0)
            self.right_scroll=Button(right_scroll_image,right_scroll_info,\
                    right_topleft,text=None,bid='right')
            self.buttons['right']=self.right_scroll
            self.right_scroll.active=True

            self.scroll_speed=1.
        
        #----Set topleft positions for buttons--------------------------
        if 'left' in self.buttons.keys():

            left_start=self.topleft+(self.left_scroll.size[0],0)+\
                    self.edge

            self.button_blit_surface=self.image.subsurface(\
                    self.left_scroll.size[0],0,\
                    self.size[0]-2.*self.left_scroll.size[0],\
                    self.size[1])
            self.button_blit_surface_topleft=Vector2(self.topleft[0]+\
                    self.left_scroll.size[0],self.topleft[1])

            for ii in range(len(self.button_keys)):
                button=self.buttons[self.button_keys[ii]]
                button.topleft=left_start+\
                        Vector2(ii*(self.single_button_size[0]+self.edge[0]),0)
                button.valid_area=\
                    self.button_blit_surface.get_rect().move(*self.button_blit_surface_topleft)


        else:
            for ii in range(len(self.button_keys)):
                button=self.buttons[self.button_keys[ii]]
                button.topleft=self.topleft+self.edge+\
                        (ii*(self.single_button_size[0]+self.edge[0]),0)
                #button.number.topleft=button.topleft+(0.7*button.size[0],0.7*button.size[1])

            self.button_blit_surface=self.image.subsurface(Rect(0,0,\
                    self.size[0],self.size[1]))
            self.button_blit_surface_topleft=self.topleft

    def draw(self,surface):
        blit_surface=self.button_blit_surface.copy()

        for ii in self.buttons.values():
            #----Blit to the RELATIVE location wrt self.button_blit_surface_topleft
            ii.selectFrame()
            blit_surface.blit(ii.image,dest=ii.topleft-\
                    self.button_blit_surface_topleft)

        surface.blit(self.image,self.topleft)
        if 'left' in self.buttons.keys():
            self.buttons['left'].draw(surface)
            self.buttons['right'].draw(surface)
        surface.blit(blit_surface,self.button_blit_surface_topleft)

    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.bid
                break
        return buttonover

    def buttonAction(self,mouse_event,time_passed):

        mouse_event_type,button,point=mouse_event

        button=self.isOver(point)

        if button is not None:

            if mouse_event_type=='mouse_down':
                if button is 'left':
                    self.scrollButtons(time_passed,'left')
                elif button is 'right':
                    self.scrollButtons(time_passed,'right')
                else:
                    button_pressed=self.buttons[button].actions(mouse_event)
                    self.button_pressed=button_pressed
            elif mouse_event_type=='mouse_up':
                if button is not 'left' and button is not 'right':
                    if button==self.button_pressed:
                        button_pressed=self.buttons[button].actions(mouse_event)
                        self.button_pressed=None
                        return button_pressed
                    else:
                        if self.button_pressed is not None:
                            self.buttons[self.button_pressed].isdown=False
                            self.buttons[self.button_pressed].selectFrame()
                            self.button_pressed=None
                            return None

        else:
            if self.button_pressed is not None:
                self.buttons[self.button_pressed].isdown=False
                self.buttons[self.button_pressed].selectFrame()


    def scrollButtons(self,time_passed,direction):
        firstbutton=self.buttons[self.button_keys[0]]
        left_reference_point=self.topleft[0]+self.left_scroll.size[0]+self.edge[0]

        if firstbutton.topleft[0] >= left_reference_point:
            self.left_scroll.active=False
        else:
            self.left_scroll.active=True

        lastbutton=self.buttons[self.button_keys[-1]]
        right_reference_point=self.topleft[0]+self.size[0]-self.left_scroll.size[0]-\
                self.edge[0]-self.single_button_size[0]

        if lastbutton.topleft[0] <= right_reference_point:
            self.right_scroll.active=False
        else:
            self.right_scroll.active=True

        if direction=='left' and self.left_scroll.active:
            max_shift=left_reference_point-firstbutton.topleft[0]
            for ii in self.button_keys:
                button=self.buttons[ii]
                hori_shift=time_passed*self.scroll_speed
                button.topleft+=Vector2(min(hori_shift,max_shift),0)

        if direction=='right' and self.right_scroll.active:
            max_shift=lastbutton.topleft[0]-right_reference_point
            for ii in self.button_keys:
                button=self.buttons[ii]
                hori_shift=time_passed*self.scroll_speed
                button.topleft-=Vector2(min(hori_shift,max_shift),0)

        if firstbutton.topleft[0] >= left_reference_point:
            self.left_scroll.active=False
        else:
            self.left_scroll.active=True
        if lastbutton.topleft[0] <= right_reference_point:
            self.right_scroll.active=False
        else:
            self.right_scroll.active=True


class ResumeButton(Button):

    def __init__(self,image,image_info,topleft,text='RESUME',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='resume',active=active)

    def up_actions(self):
        self.parent.button_pressed='resume'


class OptionButton(Button):

    def __init__(self,image,image_info,topleft,text='OPTIONS',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='option',active=active)

    def up_actions(self):
        self.parent.button_pressed='option'


class ToMainButton(Button):

    def __init__(self,image,image_info,topleft,text='TO MAIN',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='tomain',active=active)

    def up_actions(self):
        self.parent.button_pressed='tomain'


class ExitButton(Button):

    def __init__(self,image,image_info,topleft,text='EXIT',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='exit',active=active)

    def up_actions(self):
        self.parent.button_pressed='exit'


class PauseScreen(object):

    def __init__(self,background,resume_button,option_button,\
            main_button,exit_button):

        self.background=background
        self.resume_button=resume_button
        self.option_button=option_button
        self.main_button=main_button
        self.exit_button=exit_button

        self.buttons={'RESUME':self.resume_button,\
                'OPTIONS':self.option_button,\
                'TO MAIN':self.main_button,\
                'EXIT':self.exit_button\
                }
        self.button_pressed=None
        self.event_num=None

        for ii in self.buttons.values():
            ii.parent=self


    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.text
                break
        return buttonover

    def buttonAction(self,mouse_event):

        mouse_event_type,button,point=mouse_event

        button=self.isOver(point)

        if button is not None:
            if mouse_event_type=='mouse_down':
                self.buttons[button].actions(mouse_event)
            elif mouse_event_type=='mouse_up':
                self.buttons[button].actions(mouse_event)

                #print 'button_pressed',self.button_pressed
                self.event_num=USEREVENT+1
                pause_event=pygame.event.Event(self.event_num)
                pygame.event.post(pause_event)


    def draw(self,surface):
        surface.blit(self.background,(0,0))
        for ii in self.buttons.values():
            ii.draw(surface)


class DragBar(object):
    '''Horizontal slide bar widget'''
    def __init__(self,bar_image,bar_topleft,
            left_black_image, left_green_image,
            right_black_image, right_green_image,
            mid_green_image, values):

        self.bar_image=bar_image
        self.bar_topleft=Vector2(bar_topleft)
        self.left_black_image=left_black_image
        self.left_green_image=left_green_image
        self.right_black_image=right_black_image
        self.right_green_image=right_green_image
        self.mid_green_image=mid_green_image
        self.values=values

        self.bar_size=Vector2(self.bar_image.get_size())
        self.button_size=self.mid_green_image.get_size()

        self.left_topleft=self.bar_topleft-(self.button_size[0]/2.,\
                (self.button_size[1]-self.bar_size[1])/2.)
        self.right_topleft=self.bar_topleft+(self.bar_size[0],0)-\
                (self.button_size[0]/2.,\
                (self.button_size[1]-self.bar_size[1])/2.)

        self.verti_center=self.bar_topleft[1]+0.5*self.bar_size[1]
        self.min=numpy.min(self.values)
        self.max=numpy.max(self.values)
        self.frac=0.5     # fractional position


    @property
    def button_topleft(self):
        return center2Topleft(center=self.button_pos,size=self.button_size)

    @property
    def button_pos(self):
        return Vector2(self.bar_topleft[0]+self.frac*self.bar_size[0],\
                self.verti_center)

    @property
    def active_button(self):
        if self.frac==0.:
            return self.left_green_image
        elif self.frac==1.:
            return self.right_green_image
        else:
            return self.mid_green_image


    def clickAction(self,mouse_event):
        mouse_event_type,button,point=mouse_event

        if mouse_event_type=='mouse_down' and button==1:
            if point[0]>=self.bar_topleft[0]-10 and\
                    point[0]<=self.bar_topleft[0]+self.bar_size[0]+10 and\
                    point[1]>=self.bar_topleft[1]-10 and \
                    point[1]<=self.bar_topleft[1]+self.bar_size[1]+10:
                if point[0]<=self.bar_topleft[0]:
                    self.frac=0.
                elif point[0]>=self.bar_topleft[0]+self.bar_size[0]:
                    self.frac=1.
                else:
                    self.frac=(point[0]-self.bar_topleft[0])/self.bar_size[0]

        return self.value


    @property
    def value(self):
        '''Get value from fractional position'''
        pass


    def draw(self,surface):
        surface.blit(self.bar_image,self.bar_topleft)
        surface.blit(self.left_black_image,self.left_topleft)
        surface.blit(self.right_black_image,self.right_topleft)
        surface.blit(self.active_button,self.button_topleft)


class ContinuousDragBar(DragBar):
    '''Continuous slide bar widget'''
    def __init__(self,bar_image,bar_topleft,
            left_black_image, left_green_image,
            right_black_image, right_green_image,
            mid_green_image, values=[0,1]):

        DragBar.__init__(self,bar_image,bar_topleft,
            left_black_image, left_green_image,
            right_black_image, right_green_image,
            mid_green_image, values=values)

        self.frac=0.5

    @property
    def value(self):
        value=self.frac*(self.max-self.min)+self.min
        return value


class OptionScreen(object):

    def __init__(self,background,music_volume_bar,effect_volume_bar,\
            checkbox,back_button):
        self.background=background
        self.effect_volume_bar=effect_volume_bar
        self.music_volume_bar=music_volume_bar
        self.checkbox=checkbox
        self.back_button=back_button

        self.buttons={'backtopause':self.back_button}
        self.music_volume_bar.parent=self
        self.effect_volume_bar.parent=self
        self.back_button.parent=self
        self.checkbox.parent=self

        self.music_volume=self.music_volume_bar.value
        self.effect_volume=self.effect_volume_bar.value

        self.event_num=USEREVENT+2

    @property
    def fullscreen(self):
        return self.checkbox.checked

    def draw(self,surface):
        surface.blit(self.background,(0,0))
        self.effect_volume_bar.draw(surface)
        self.music_volume_bar.draw(surface)
        self.checkbox.draw(surface)
        self.back_button.draw(surface)

    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.text
                break
        return buttonover

    def buttonAction(self,mouse_event):

        mouse_event_type,button,point=mouse_event

        self.music_volume=self.music_volume_bar.clickAction(mouse_event)
        self.effect_volume=self.effect_volume_bar.clickAction(mouse_event)
        self.checkbox.actions(mouse_event)
        self.back_button.actions(mouse_event)


class BackButton(Button):

    def __init__(self,image,image_info,topleft,text='BACK',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='back',active=active)

    def up_actions(self):
        event=pygame.event.Event(self.parent.event_num)
        pygame.event.post(event)


class CheckBox(object):

    def __init__(self,images,image_info,topleft,checked=False):
        self.images=images
        self.image_info=image_info
        self.topleft=Vector2(topleft)
        self.checked=checked

        self.images=splitImage(images,image_info)
        self.image=self.images[self.image_index]
        self.size=self.image.get_size()
        self.isdown=False

    @property
    def image_index(self):
        if self.checked:
            return 1
        else:
            return 0

    def draw(self,surface):
        surface.blit(self.image,self.topleft)

    def isOver(self,point):
        '''Check wether mouse is over button
        '''
        in_x=point[0]>=self.topleft[0] and\
                point[0]<=self.topleft[0]+self.size[0]
        in_y=point[1]>=self.topleft[1] and\
                point[1]<=self.topleft[1]+self.size[1]

        return in_x and in_y

    def down_actions(self):
        pass

    def up_actions(self):
        self.checked=not self.checked
        self.image=self.images[self.image_index]


    def actions(self,mouse_event):
        '''
        <mouse_event>:(mouse_event_type,button,point):
            <mouse_event_type>: 'mouse_down' or 'mouse_up'.
            <button>: button number, 1 for left, 2 for mid, 3 for right.
            <point>: mouse position
        '''
        mouse_event_type,button,point=mouse_event

        if self.isOver(point):
            if mouse_event_type=='mouse_down' and self.isdown is False:
                self.isdown=True
                self.down_actions()
            elif mouse_event_type=='mouse_up' and self.isdown:
                self.isdown=False
                self.up_actions()
        

class StartButton(Button):

    def __init__(self,image,image_info,topleft,text='START',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='start',active=active)

    def up_actions(self):
        self.parent.button_pressed='start'


class CreditButton(Button):

    def __init__(self,image,image_info,topleft,text='CREDIT',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='credit',active=active)

    def up_actions(self):
        self.parent.button_pressed='credit'


class ListBox(object):
    def __init__(self,bg_image,topleft,items,up_scroll,down_scroll,
            font=None,font_size=20,font_color=(255,255,255),
            margin=(20,10,10,20),auto_wrap=True):

        self.bg_image=bg_image
        self.topleft=Vector2(topleft)
        self.items=items
        self.up_scroll=up_scroll
        self.down_scroll=down_scroll
        self.font_size=font_size
        self.font_color=font_color
        self.margin=margin   # (top,left,right,buttom)
        self.auto_wrap=auto_wrap

        #----Font--------------------------
        if font is None:
            self.font=pygame.font.Font(E_FONT,self.font_size)
        else:
            self.font=pygame.font.Font(font,self.font_size)

        self.size=self.bg_image.get_size()
        self.verti_gap=8
        self.line_gap=0.5     # line gap when wrapping text into multi-lines
        self.text_topleft=self.topleft+Vector2(self.margin[1],self.margin[0])

        self.need_scroll=False              # need scroll buttons
        self.buttons=self.createButtons(self.size[0]-2*self.margin[2])

        if self.need_scroll:
            self.add_scroll()
            #-------------Re-compute text wrapping-------------
            self.buttons=self.createButtons(self.size[0]-2*self.margin[1]-
                    self.up_scroll_size[0])

            self.buttons['_up']=self.up_scroll_button
            self.buttons['_down']=self.down_scroll_button

        self.addBlitSurface()
        self.chosen_item=self.items[0]
        self.setButtonState()

    def setButtonState(self):
        '''Use down state for item selected, up state all others'''
        for kk,bii in self.buttons.items():
            if kk==self.chosen_item:
                bii.isdown=True
                bii.selectFrame()
            else:
                bii.isdown=False
                bii.selectFrame()


    def createButtons(self,width):
        '''Create a button for each item in the list
        <width>: float, width in pixels to wrap texts
        '''
        buttons={}
        topleft_last=self.text_topleft

        for ii,tii in enumerate(self.items):
            text_surface=self.font.render(tii,True,self.font_color)
            if text_surface.get_size()[0]>width:
                text_surface,_=wrapText(tii,width,self.line_gap,self.font,
                    self.font_color)
            sizeii=text_surface.get_size()

            button_img1=pygame.Surface(sizeii).convert_alpha()
            button_img1.fill((0,0,0,0))
            button_img1=setAlpha(button_img1,10,True) # transparent
            button_img1.blit(text_surface,(0,0))

            button_img2=pygame.Surface(sizeii)
            button_img2.fill((100,100,100,255))
            button_img2=setAlpha(button_img1,90,True) # highlight selected
            button_img2.blit(text_surface,(0,0))

            button_img=pygame.Surface((sizeii[0]*2,sizeii[1])).convert_alpha()
            button_img.fill((0,0,0,0))
            button_img.blit(button_img1,(0,0))
            button_img.blit(button_img2,(sizeii[0],0))

            img_info=['b',1,sizeii[1],2,sizeii[0]]

            if ii==0:
                topleftii=topleft_last
            else:
                topleftii=topleft_last+Vector2(0,self.verti_gap)

            if self.need_scroll is False and topleftii[1]+sizeii[1]>self.size[1]:
                self.need_scroll=True   # list box now has scrolls

            buttonii=Button(button_img,img_info,topleftii,
                    text=None,bid=tii)
            buttons[tii]=buttonii

            topleft_last=topleftii+Vector2(0,sizeii[1])

        return buttons


    def add_scroll(self):

        #--------------Create scroll buttons--------------
        up_scroll_image,up_scroll_info=self.up_scroll
        down_scroll_image,down_scroll_info=self.down_scroll

        self.up_scroll_size=[up_scroll_info[4],up_scroll_info[2]]

        self.up_scroll_button=Button(up_scroll_image,up_scroll_info,
                self.topleft+(self.size[0]-self.up_scroll_size[0],0),
                text=None,bid='_up',active=False)
        self.buttons['_up']=self.up_scroll_button

        down_topleft=self.topleft+self.size-self.up_scroll_size
        self.down_scroll_button=Button(down_scroll_image,down_scroll_info,
                down_topleft,
                text=None,bid='_down',active=True)
        self.buttons['_down']=self.down_scroll_button

        self.scroll_speed=1.

        return


    def addBlitSurface(self):
        '''A dummy rect area to blit possibly cropped button images'''
        if self.need_scroll:
            self.button_blit_surface=self.bg_image.subsurface(0,0,
                    self.size[0]-self.up_scroll_size[0],
                    self.size[1])

            for ii in self.items:
                btii=self.buttons[ii]
                btii.valid_area=self.button_blit_surface.get_rect().move(\
                        *self.topleft)
        else:
            self.button_blit_surface=self.bg_image.subsurface(0,0,self.size[0],
                    self.size[1])

        return


    def draw(self,surface):
        blit_surface=self.button_blit_surface.copy()

        for ii in self.items:
            bii=self.buttons[ii]
            #----Blit to the RELATIVE location wrt self.button_blit_surface_topleft
            bii.selectFrame()
            blit_surface.blit(bii.image,dest=bii.topleft-\
                    self.topleft)

        surface.blit(self.bg_image,self.topleft)
        if self.need_scroll:
            self.buttons['_up'].draw(surface)
            self.buttons['_down'].draw(surface)

        surface.blit(blit_surface,self.topleft)



    def isOver(self,point):
        buttonover=None

        for kk,bb in self.buttons.items():
            if bb.isOver(point):
                buttonover=bb.bid
                break
        return buttonover


    def buttonAction(self,mouse_event,time_passed):

        mouse_event_type,button,point=mouse_event
        button=self.isOver(point)

        if button is not None:
            if mouse_event_type=='mouse_down':
                if button in ['_up','_down']:
                    self.scrollButtons(time_passed,button)
                else:
                    self.buttons[button].actions(mouse_event)
            elif mouse_event_type=='mouse_up':
                if button not in ['_up','_down']:
                    self.buttons[button].actions(mouse_event)
                    self.chosen_item=button  # highlight selected item
                    self.setButtonState()
            return button


    def scrollButtons(self,time_passed,direction):
        firstbutton=self.buttons[self.items[0]]
        top_reference_point=self.topleft[1]+self.margin[0]

        if firstbutton.topleft[1] >= top_reference_point:
            self.up_scroll_button.active=False
        else:
            self.down_scroll_button.active=True

        lastbutton=self.buttons[self.items[-1]]
        buttom_reference_point=self.topleft[1]+self.size[1]-\
                self.margin[-1]-lastbutton.size[1]

        if lastbutton.topleft[1] <= buttom_reference_point:
            self.down_scroll_button.active=False
        else:
            self.down_scroll_button.active=True

        if direction=='_up' and self.up_scroll_button.active:
            max_shift=top_reference_point-firstbutton.topleft[1]
            for ii in self.items:
                button=self.buttons[ii]
                vert_shift=time_passed*self.scroll_speed
                button.topleft+=Vector2(0,min(vert_shift,max_shift))

        if direction=='_down' and self.down_scroll_button.active:
            max_shift=lastbutton.topleft[1]-buttom_reference_point
            for ii in self.items:
                button=self.buttons[ii]
                vert_shift=time_passed*self.scroll_speed
                button.topleft-=Vector2(0,min(vert_shift,max_shift))

        if firstbutton.topleft[1] >= top_reference_point:
            self.up_scroll_button.active=False
        else:
            self.up_scroll_button.active=True
        if lastbutton.topleft[1] <= buttom_reference_point:
            self.down_scroll_button.active=False
        else:
            self.down_scroll_button.active=True

        return


class TipBar(RollText):

    def __init__(self,images,image_info,topleft,color=(255,255,255),\
            font_size=20):
        text=self.getTip()
        RollText.__init__(self,images,image_info,topleft,text,color,
                font=E_FONT,font_size=font_size)

    @staticmethod
    def getTip():
        return random.choice(TIPS)

    def changeTip(self):
	self.updateText(self.getTip())


class DiscretDragBar(DragBar):
    '''Horizontal slide bar with discret values'''
    def __init__(self,bar_image,bar_topleft,
            left_black_image, left_green_image,
            right_black_image, right_green_image,
            mid_black_image, mid_green_image, levels):

        self.levels_keys=levels.keys()
        self.levels_keys.sort()
        self.mid_black_image=mid_black_image

        DragBar.__init__(self,bar_image,bar_topleft,
            left_black_image, left_green_image,
            right_black_image, right_green_image,
            mid_green_image, values=self.levels_keys)

        # e.g. level_dict={0:'low',1:'mid',2:'high'}
        self.level_dict=levels
        self.n_levels=len(levels)
        self.frac=0.5
        self.hori_gap=(self.right_topleft[0]-self.left_topleft[0])/\
            (self.n_levels-1)

        #----Font--------------------------
        self.font=pygame.font.Font(E_FONT,20)

    @property
    def value(self):
        # Snap fraction to discret levels
        fold=self.frac*self.bar_size[0]/self.hori_gap
        self.index=int(round(fold))
        res=self.level_dict[self.index]
        self.frac=self.index*self.hori_gap/self.bar_size[0]

        return res


    def draw(self,surface):
        super(DiscretDragBar,self).draw(surface)
        for ii in range(1,len(self.level_dict)-1):
            surface.blit(self.mid_black_image,self.left_topleft+\
                    ii*Vector2(self.hori_gap,0))
        surface.blit(self.active_button,self.button_topleft)

        text=self.font.render(self.value,True,(255,255,255))
        surface.blit(text,self.bar_topleft-(30+text.get_size()[0],0))


class BackButton2(Button):
    '''Back from credit screen to main screen'''
    def __init__(self,image,image_info,topleft,text='BACK',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='backtomain',active=active)

    def up_actions(self):
        self.parent.button_pressed=self.bid


class GoButton(Button):
    '''From mission selection screen into game scene'''
    def __init__(self,image,image_info,topleft,text='GO',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='go',active=active)

    def up_actions(self):
        self.parent.button_pressed=self.bid


class TextBox():

    def __init__(self,topleft,size,texts,up_scroll,down_scroll,\
            font_size=10,font_color=(255,255,255)):

        self.topleft=Vector2(topleft)
        self.size=size
        self.texts=texts
        self.up_scroll=up_scroll
        self.down_scroll=down_scroll
        self.font_size=font_size
        self.font_color=font_color

        self.surfaces=[]

        #----Font--------------------------
        self.font=pygame.font.Font(E_FONT,self.font_size)

        #--------------------Wrap texts--------------------
        self.texts=self.wrapText()
        self.blitText()

        self.edge=Vector2(7,0)
        self.single_button_size=self.surfaces[0].get_size()
        self.getPosition()
        

    def wrapText(self):
        lines=[]
        scroll_button_size=self.up_scroll[1][4]
        for tii in self.texts:
           _,linesii=wrapText(tii,self.size[0]-scroll_button_size-10,line_gap=1.,
                   font=self.font,font_color=self.font_color)
           lines.extend(linesii)
        return lines

    def getPosition(self):
        #----When too many buttons to display-------------------------
        self.buttons={}
        self.toplefts=[]
        if (self.edge[1]+self.single_button_size[1])*len(self.texts)\
                >=self.size[1]-5:

            up_scroll_image=self.up_scroll[0]
            up_scroll_info=self.up_scroll[1]

            #----Create scrolling buttons--------------------------
            self.up_scroll_button=Button(up_scroll_image,up_scroll_info,\
                    self.topleft+(self.size[0]-up_scroll_image.get_size()[0]/3.,0),\
                    text=None,bid='_up')
            self.buttons['_up']=self.up_scroll_button
            self.up_scroll_button.active=False

            down_scroll_image=self.down_scroll[0]
            down_scroll_info=self.down_scroll[1]

            down_topleft=self.up_scroll_button.topleft+(0,self.size[1]-down_scroll_image.get_size()[1])
            self.down_scroll_button=Button(down_scroll_image,down_scroll_info,\
                    down_topleft,text=None,bid='_down')
            self.buttons['_down']=self.down_scroll_button
            self.down_scroll_button.active=True

            self.scroll_speed=1.
        
        #----Set topleft positions for buttons--------------------------
        for ii in range(len(self.surfaces)):
            #surf=self.surfaces[ii]
            self.toplefts.append(self.topleft+self.edge+\
                    (0,ii*(self.single_button_size[1]+self.edge[1])))

        self.button_blit_surface=pygame.surface.Surface((\
                self.size[0],self.size[1]))
        self.button_blit_surface_topleft=self.topleft


    def draw(self,surface):
        blit_surface=self.button_blit_surface.copy()

        for ii in range(len(self.surfaces)):
            #----Blit to the RELATIVE location wrt self.button_blit_surface_topleft
            #ii.selectFrame()
            surfii=self.surfaces[ii]
            tpii=self.toplefts[ii]
            blit_surface.blit(surfii,dest=tpii-\
                    self.button_blit_surface_topleft)

        surface.blit(blit_surface,self.button_blit_surface_topleft)

        if '_up' in self.buttons.keys():
            self.buttons['_up'].draw(surface)
            self.buttons['_down'].draw(surface)

    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.bid
                break
        return buttonover


    def buttonAction(self,mouse_event,time_passed):

        mouse_event_type,button,point=mouse_event
        button=self.isOver(point)

        if button is not None:

            if mouse_event_type=='mouse_down':
                if button is '_up':
                    self.scrollButtons(time_passed,'_up')
                elif button is '_down':
                    self.scrollButtons(time_passed,'_down')
            elif mouse_event_type=='mouse_up':
                if button is not '_up' and button is not '_down':
                    pass


    def scrollButtons(self,time_passed,direction):
        tp0=self.toplefts[0]
        top_reference_point=self.topleft[1]+self.edge[1]

        if tp0[1] >= top_reference_point:
            self.up_scroll_button.active=False
        else:
            self.up_scroll_button.active=True

        tplast=self.toplefts[-1]
        bottom_reference_point=self.topleft[1]+self.size[1]-\
                2*self.edge[1]-self.single_button_size[1]

        if tplast[1] <= bottom_reference_point:
            self.down_scroll_button.active=False
        else:
            self.down_scroll_button.active=True

        if direction=='_up' and self.up_scroll_button.active:
            max_shift=top_reference_point-tp0[1]
            for ii in range(len(self.toplefts)):
                verti_shift=time_passed*self.scroll_speed
                self.toplefts[ii]+=Vector2(0,min(verti_shift,max_shift))

        if direction=='_down' and self.down_scroll_button.active:
            max_shift=tplast[1]-bottom_reference_point
            for ii in range(len(self.toplefts)):
                verti_shift=time_passed*self.scroll_speed
                self.toplefts[ii]-=Vector2(0,min(verti_shift,max_shift))

        tp0=self.toplefts[0]
        if tp0[1] >= top_reference_point:
            self.up_scroll_button.active=False
        else:
            self.up_scroll_button.active=True
        tplast=self.toplefts[-1]
        if tplast[1] <= bottom_reference_point:
            self.down_scroll_button.active=False
        else:
            self.down_scroll_button.active=True


    def blitText(self):
        for ii in self.texts:
            self.surfaces.append(self.font.render(ii,True,self.font_color))

    def changeContents(self,new_texts):
        self.texts=new_texts
        self.texts=self.wrapText()
        self.surfaces=[]
        self.blitText()
        self.getPosition()


class MissionScreen(object):
    def __init__(self,background,level_pack,list_box,tip_box,text_box,
            mini_map_background,difficulty_bar,back_button,next_button):

        self.background=background
        self.level_pack=level_pack
        self.list_box=list_box
        self.tip_box=tip_box
        self.text_box=text_box
        self.mini_map_background=mini_map_background
        self.difficulty_bar=difficulty_bar
        self.back_button=back_button
        self.next_button=next_button

        self.back_button.parent=self
        self.next_button.parent=self

        self.select_index=0
        self.select_level=self.level_pack[self.select_index]

        self.difficulty=self.difficulty_bar.value
        self.level_names=self.list_box.items

        self.button_pressed=None   #back or next
        self.passed_time=0
        self.event_num=None

        self.mini_map=pygame.transform.scale(self.select_level.minimap_image,\
                (180,130))
        self.mini_map_topleft=Vector2(450,100)



    def clickActions(self,mouse_event,time_passed):
        self.button_pressed=None

        select_item=self.list_box.buttonAction(mouse_event,time_passed)
        if select_item is not None:
            self.select_index=self.level_names.index(select_item)
            self.updateLevelInfo()

        self.text_box.buttonAction(mouse_event,time_passed)
        self.difficulty=self.difficulty_bar.clickAction(mouse_event)
        self.back_button.actions(mouse_event)
        self.next_button.actions(mouse_event)
        self.event_num=USEREVENT+1
        event=pygame.event.Event(self.event_num)
        pygame.event.post(event)

    def updateLevelInfo(self):
        #select_item=self.level_names[self.select_index]
        self.select_level=self.level_pack[self.select_index]
        self.text_box.changeContents(self.select_level.texts)
        self.mini_map=pygame.transform.scale(self.select_level.minimap_image,\
                (170,120))
        self.list_box.chosen_item=self.level_names[self.select_index]
        self.list_box.setButtonState()


    def draw(self,surface,time_passed):
        self.passed_time+=time_passed

        surface.blit(self.background,(0,0))
        self.list_box.draw(surface)
        self.tip_box.draw(time_passed,surface)

        self.mini_map_background.blit(self.mini_map,
            (0.5*(Vector2(self.mini_map_background.get_size())-\
                    self.mini_map.get_size())))

        surface.blit(self.mini_map_background,self.mini_map_topleft)

        self.text_box.draw(surface)
        self.difficulty_bar.draw(surface)
        self.back_button.draw(surface)
        self.next_button.draw(surface)

    def updateTip(self,time_passed):
        if self.passed_time>=25000:
            self.tip_box.changeTip()
	    self.passed_time=0


class RetryButton(Button):
    def __init__(self,image,image_info,topleft,text='RETRY',active=True):
        Button.__init__(self,image,image_info,topleft=topleft,text=text,
                bid='retry',active=active)

    def up_actions(self):
        self.parent.button_pressed=self.bid


class GameOverBox(object):

    def __init__(self,win_background,fail_background,topleft,
            retry_button,back_button,next_button):

        self.win_background=win_background
        self.fail_background=fail_background
        self.topleft=topleft
        self.retry_button=retry_button
        self.back_button=back_button
        self.next_button=next_button

        self.back_button.parent=self
        self.retry_button.parent=self
        self.next_button.parent=self

        self.button_pressed=None


    def chooseButton(self,win):
        if win:
            self.right_button=self.next_button
	    self.background=self.win_background
        else:
            self.right_button=self.retry_button
	    self.background=self.fail_background

    def draw(self,surface):
        surface.blit(self.background,self.topleft)
        self.back_button.draw(surface)
        self.right_button.draw(surface)

    def buttonAction(self,mouse_event):

        self.button_pressed=None
        self.back_button.actions(mouse_event)
        self.right_button.actions(mouse_event)

        return self.button_pressed


class MainScreen(object):

    def __init__(self,background,start_button,credit_button,\
            exit_button):

        self.background=background
        self.start_button=start_button
        self.credit_button=credit_button
        self.exit_button=exit_button

        self.buttons={'start':self.start_button,\
                'credit':self.credit_button,\
                'exit':self.exit_button\
                }

        self.button_pressed=None
        self.event_num=USEREVENT+3

        for ii in self.buttons.values():
            ii.parent=self


    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.bid
                break
        return buttonover

    def buttonAction(self,mouse_event):

        mouse_event_type,button,point=mouse_event

        button=self.isOver(point)

        if button is not None:
            if mouse_event_type=='mouse_down':
                self.buttons[button].actions(mouse_event)
            elif mouse_event_type=='mouse_up':
                self.buttons[button].actions(mouse_event)

                pause_event=pygame.event.Event(self.event_num)
                pygame.event.post(pause_event)


    def draw(self,surface):
        surface.blit(self.background,(0,0))
        for ii in self.buttons.values():
            ii.draw(surface)


class CreditScreen(object):

    def __init__(self,background,back_button):
        self.background=background
        self.back_button=back_button

        self.buttons={'backtomain':self.back_button}
        self.back_button.parent=self

        self.event_num=USEREVENT+4
        self.button_pressed=None

    def draw(self,surface):
        surface.blit(self.background,(0,0))
        self.back_button.draw(surface)

    def isOver(self,point):
        buttonover=None

        for ii in self.buttons.values():
            if ii.isOver(point):
                buttonover=ii.bid
                break
        return buttonover

    def buttonAction(self,mouse_event):
        self.button_pressed=None
        mouse_event_type,button,point=mouse_event
        self.back_button.actions(mouse_event)
        return self.button_pressed
