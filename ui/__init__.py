'''Define classes for GUI elements.
'''
import pygame
import ui_class
import generals
import weapons
import os
import cus_font
from Trenches import SCREEN_SIZE, __version__

E_FONT=cus_font.E_FONT_PATH8

PATH=os.path.dirname(os.path.realpath(__file__))

#-------------------Some colors-------------------
C_DARKGREEN=(57,61,56)
C_DARKRED=(108,8,24)
C_LIGHTGREEN=(95,103,94)
C_LIGHTGREENHIGHLIGHT=(195,197,199)
C_LIGHTGREENSHADOW=(57,61,56)
C_GOLD=(218,230,35)
C_RED=(244,77,74)
C_DARKGREY_TRANS=(20,40,30,200)
C_DARKGREEN_TRANS=(90,100,95,200)


IMAGE_FILE_NAMES={

#------------------Scroll buttons------------------
'LEFT_SCROLL_FILE'       : 'image_leftscroll_1x40x3x20.png',
'RIGHT_SCROLL_FILE'      : 'image_rightscroll_1x40x3x20.png',
'UP_SCROLL_FILE'         : 'image_upscroll_1x30x3x30.png',
'DOWN_SCROLL_FILE'       : 'image_downscroll_1x30x3x30.png',

#---------------------Buttons---------------------
'PLAQUE_BUTTON_FILE'     : 'image_plaquebutton_2x40x1x160.png',
'CHECKBOX_FILE'          : 'image_checkbox_1x20x2x20.png',

#---------------------Drag bar---------------------
'DRAG_BAR_FILE'          : 'image_scrollbar_1x21x1x202.png',
'LEFT_BLACKBUTTON_FILE'  : 'image_buttonblackleft_1x40x1x40.png',
'RIGHT_BLACKBUTTON_FILE' : 'image_buttonblackright_1x40x1x40.png',
'MID_BLACKBUTTON_FILE'   : 'image_buttonblackmid_1x40x1x40.png',
'MID_GREENBUTTON_FILE'   : 'image_buttongreenmid_1x40x1x40.png',
'LEFT_GREENBUTTON_FILE'  : 'image_buttongreenleft_1x40x1x40.png',
'RIGHT_GREENBUTTON_FILE' : 'image_buttongreenright_1x40x1x40.png',

#----Main screen--------------------------
'MAIN_SCREEN_FILE'       : 'image_mainpixel_1x600x1x800.png',
'MAIN_SCREENNOMENU_FILE' : 'image_mainpixelnomenu_1x600x1x800.png',
'METAL_FRAME_FILE'       : 'image_metalframe_1x600x1x800.png'
}




def loadCommonAssets():
    '''Load and create assets.
    This function will be called upon module loading.
    '''
    def scale(assets,key,newsize):
        img,info=assets[key]
        img=pygame.transform.scale(img,newsize)
        info=[key,1,newsize[1],1,newsize[0]]
        assets[key]=[img,info]
        return assets

    assets={}

    for kk,vv in IMAGE_FILE_NAMES.items():
        abpath=os.path.join(PATH,vv)
        img=pygame.image.load(abpath).convert_alpha()
        img_info=generals.interpName(vv)
        keyname=kk[:-5].lower()
        assets[keyname]=[img,img_info]

    assets=scale(assets,'main_screen',SCREEN_SIZE)
    assets=scale(assets,'main_screennomenu',SCREEN_SIZE)
    assets=scale(assets,'metal_frame',SCREEN_SIZE)

    #---------Create a dimmed background image---------
    bg_image=assets['main_screennomenu'][0].copy()
    metalframe_image=assets['metal_frame'][0].copy()

    #----------------Turn image to grey----------------
    bg_image=generals.grayscale(bg_image)
    bg_image=generals.setAlpha(bg_image,30)

    bg_image.blit(metalframe_image,(0,0))
    image_info=['dim_background',1,SCREEN_SIZE[1],1,SCREEN_SIZE[0]]
    assets['dim_background']=[bg_image,image_info]

    return assets


ASSETS=loadCommonAssets()


#----------Create frame and button images----------
def createPlainFrame(size,border_width=2,
        border_color=(0,0,0),fill_color=(255,255,255)):
    '''Create a box surface with a border line of given width'''

    width,height=size
    surface=pygame.Surface((width,height)).convert_alpha()
    surface.fill(border_color)
    # rect=(topleft_x, topleft_y, w, h)
    surface.fill(fill_color,rect=(border_width,border_width,
        width-border_width*2,height-border_width*2))

    return surface


def createReliefFrame(size,border_width=3,
        fill_color=(150,150,150),highlight_color=(190,190,190),
        shadow_color=(10,10,10),reverse_light=False):
    '''Create a box surface with 3d relief effect

    <reverse_light>: put highlight at bottom-right sides, and shadow at
                     top-left sides. Used to create button-down effect.
    '''

    width,height=size
    surface=pygame.Surface((width,height))
    surface.fill(fill_color)

    if reverse_light:
        highlight_color,shadow_color=shadow_color,highlight_color

    #------------Make hightlight and shadow------------
    array=pygame.surfarray.pixels3d(surface)
    for ii in range(border_width):
        array[ii,:-(ii+1),:]=highlight_color
        array[:-(ii+1),ii,:]=highlight_color
        array[-(ii+1),(ii+1):,:]=shadow_color
        array[(ii+1):,-(ii+1),:]=shadow_color

    del array
    return surface


def createPlainFrameWithTitlebar(size,text='title bar',border_width=2,
        font=None,font_size=25,font_color=(255,255,255),
        border_color=(0,0,0),fill_color=(255,255,255),titlebar_color=(100,100,100)):
    '''Create a box surface with a title bar at top, and a border line at edges.
    '''

    width,height=size
    surface=createPlainFrame(size,border_width=border_width,
            border_color=border_color,fill_color=fill_color).convert_alpha()

    if font is None:
        font=pygame.font.Font(E_FONT,font_size)
    else:
        font=pygame.font.Font(font,font_size)

    text_surface=font.render(text,True,font_color)
    text_size=text_surface.get_size()
    text_topleft=(0.5*(size[0]-text_size[0]), border_width+5)

    title_size=(width-2*border_width, border_width+text_size[1]+5)
    surface.fill(titlebar_color,(border_width,border_width,title_size[0],title_size[1]))
    surface.blit(text_surface,text_topleft)

    return surface


def createButtonImages(size,n_states=3,border_width=3,image=None,
        fill_color=C_LIGHTGREEN, highlight_color=C_LIGHTGREENHIGHLIGHT,
        shadow_color=C_LIGHTGREENSHADOW):
    '''Create images for button with relief effect.

    <size>: (width,height), size of button image.
    <n_states>: int, 2 or 3. 2 for 2-state button: up and down.
                3 for 3-state button: up, down and de-activated.
    <image>: surface or None. If not None, surface image blit onto button
             face.
    Meanings of color arguments see createReliefFrame().

    Return <button_image>: surface of button images aligned in following manner:

        ________________
        | up   |  down |         2-state botton
        ----------------
        ___________________________
        | up   |  down | inactive |        3-state botton
        ---------------------------
            <button_image_info>: list, ['string_name', n_row, height, 
                                         n_column, width]
    '''

    button_image1=createReliefFrame(size, border_width=3,
            fill_color=C_LIGHTGREEN,highlight_color=C_LIGHTGREENHIGHLIGHT,
            shadow_color=C_LIGHTGREENSHADOW)
    button_image2=createReliefFrame(size, border_width=3,
            fill_color=C_LIGHTGREEN,highlight_color=C_LIGHTGREENHIGHLIGHT,
            shadow_color=C_LIGHTGREENSHADOW,reverse_light=True)

    button_image=pygame.Surface((size[0]*n_states,size[1]))
    button_image.blit(button_image1,(0,0))
    button_image.blit(button_image2,(size[0],0))

    #---------Blit image onto button if given---------
    if image is not None:
        if image.get_size()!=size:
            image=pygame.transform.scale(image,size)
        button_image.blit(image,(0,0))
        button_image.blit(image,(size[0],0))

    if n_states==3:
        button_image.blit(button_image1,(size[0]*2,0))
        button_image.blit(image,(size[0]*2,0))

        grey_tile=pygame.Surface(size).convert_alpha()
        grey_tile.fill((100,100,100,220))
        button_image.blit(grey_tile,(size[0]*2,0))

    image_info=['button',1,size[1],n_states,size[0]]

    return button_image, image_info



#----Game screen interface--------------------------
def createMenuButton():

    #------------Create surfaces for button------------
    menu_button_image,menu_button_image_info=createButtonImages((60,40),
            n_states=2,border_width=3)

    menu_button=ui_class.MenuButton(menu_button_image,menu_button_image_info,\
            (0,0),'menu',font_size=15)
    return menu_button


def createScrollMenu(scene,level):

    scrollbar_image=pygame.Surface((220,40))
    scrollbar_image.fill(C_LIGHTGREEN)

    left_scroll_image,left_scroll_info=ASSETS['left_scroll']
    left_scroll_image=generals.scaleImage(left_scroll_image,left_scroll_info)

    right_scroll_image,right_scroll_info=ASSETS['right_scroll']
    right_scroll_image=generals.scaleImage(right_scroll_image,right_scroll_info)

    weapon_buttons=[]

    #------------Create buttons for weapons------------
    button_size=(40,40)

    for ii in level.weapons_in_level:
        #-----------------Read icon images-----------------
        file_name='image_'+ii+'icon_1x60x1x60.png'
        abpath=os.path.join(PATH,file_name)
        weapon_icon=pygame.image.load(abpath).convert_alpha()

        button_imageii,image_info=createButtonImages(button_size,n_states=3,
                image=weapon_icon)

        #------------------Create button------------------
        buttonii=ui_class.AddTroopButton(world=scene,
                price=weapons.WEAPON_PRICES[ii],
                images=button_imageii,
                image_info=image_info,
                topleft=(0,0),
                text=ii,
                active=True)
        weapon_buttons.append(buttonii)

    scroll_bar=ui_class.ScrollMenu(scrollbar_image,(60,0),\
            (left_scroll_image,left_scroll_info),\
            (right_scroll_image,right_scroll_info),\
            weapon_buttons,\
            auto_scale=True)

    return scroll_bar


def createIntelBar():

    surface=pygame.Surface((360,40))
    pygame.draw.rect(surface,C_DARKRED,(0,0,360,40),10)
    pygame.draw.rect(surface,C_LIGHTGREEN,(5,5,360-10,40-10),0)
    intel_bar=ui_class.RollText(surface,None,(280,0),'',font_size=25)

    return intel_bar


def createMoneyBar():

    surface=pygame.Surface((90,40))  # (w,h)
    pygame.draw.rect(surface,C_DARKGREEN,(0,0,90,40),10)   
    pygame.draw.rect(surface,C_LIGHTGREEN,(5,5,90-10,40-10),0)

    font=pygame.font.Font(E_FONT,22)
    dolarsign=font.render('$ ',True,C_GOLD)
    surface.blit(dolarsign,dest=(5,40/2-dolarsign.get_size()[1]/2))

    #----Money window--------------------------
    money_bar=ui_class.NumberBox(surface,(640,0),value=0,\
            text_topleft_shift=(30,0),font_size=45)

    return money_bar


def createHqBar():

    surface=pygame.Surface((70,40))
    pygame.draw.rect(surface,C_DARKGREEN,(0,0,70,40),10)   
    pygame.draw.rect(surface,C_LIGHTGREEN,(5,5,70-10,40-10),0)

    font=pygame.font.Font(E_FONT,22)
    hqtext=font.render('HQ ',True,C_RED)
    surface.blit(hqtext,dest=(5,40/2-hqtext.get_size()[1]/2))

    #----Hq life window--------------------------
    hq_bar=ui_class.NumberBox(surface,(730,0),value=1,\
            text_topleft_shift=(40,0),font_size=35)

    return hq_bar



#----Pause menu interface--------------------------
def createResumeButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.ResumeButton(button_image,image_info,text='RESUME',
            topleft=topleft)
    return button


def createOptionButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.OptionButton(button_image,image_info,text='OPTIONS',
            topleft=topleft)
    return button


def createToMainButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.ToMainButton(button_image,image_info,text='TO MAIN',
            topleft=topleft)
    return button


def createExitButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.ExitButton(button_image,image_info,text='EXIT',
            topleft=topleft)
    return button


def createPauseScreen():

    bg_image_ori,_=ASSETS['dim_background']
    bg_image=bg_image_ori.copy()

    #--------------Create box with title--------------
    frame=createPlainFrameWithTitlebar((400,400),text='GAME PAUSED',
            border_width=3,font_size=40,font_color=(255,255,255),
            fill_color=C_DARKGREY_TRANS,titlebar_color=C_DARKGREEN_TRANS)
    bg_image.blit(frame,(0.5*(bg_image.get_size()[0]-400),
        0.5*(bg_image.get_size()[1]-400)))

    #------------------Create buttons------------------
    resume=createResumeButton((330,170))
    option=createOptionButton((330,220))
    tomain=createToMainButton((330,270))
    exit=createExitButton((330,340))

    return ui_class.PauseScreen(bg_image,resume,option,tomain,exit)




#----Option menu interface--------------------------
def createDragBar(topleft):

    #----------------Get drag bar image----------------
    bar_image,_=ASSETS['drag_bar']
    bar_image=pygame.transform.scale(bar_image,(250,10))

    #----------------Get button images----------------
    def getButton(name):
        img,_=ASSETS[name]
        img=pygame.transform.scale(img,(20,20))
        return img

    buttons=['left_blackbutton', 'left_greenbutton', 
             'mid_blackbutton', 'mid_greenbutton',
             'right_blackbutton', 'right_greenbutton']

    left_black,left_green,mid_black,mid_green,right_black,right_green=\
            map(getButton,buttons)

    dragbar=ui_class.ContinuousDragBar(bar_image,bar_topleft=topleft,
            left_black_image=left_black, left_green_image=left_green,
            right_black_image=right_black, right_green_image=right_green,
            mid_green_image=mid_green, values=[0,1])

    return dragbar


def createBackButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.BackButton(button_image,image_info,topleft=topleft)

    return button


def createCheckBox(topleft):

    button_image,info=ASSETS['checkbox']
    button_image=generals.scaleImage(button_image,info)

    checkbox=ui_class.CheckBox(button_image,info,topleft=topleft)
    return checkbox


def createOptionScreen():

    bg_image_ori,_=ASSETS['dim_background']
    bg_image=bg_image_ori.copy()

    #--------------Create box with title--------------
    frame=createPlainFrameWithTitlebar((400,400),text='OPTIONS',
            border_width=3,font_size=40,font_color=(255,255,255),
            fill_color=C_DARKGREY_TRANS,titlebar_color=C_DARKGREEN_TRANS)
    bg_image.blit(frame,(0.5*(bg_image.get_size()[0]-400),
        0.5*(bg_image.get_size()[1]-400)))

    font=pygame.font.Font(E_FONT,20)
    music_text=font.render('MUSIC VOLUME',True,(255,255,255))
    sound_text=font.render('SOUND VOLUME',True,(255,255,255))
    fullscreen_text=font.render('FULLSCREEN',True,(255,255,255))

    #--------------Musice volume control--------------
    bg_image.blit(music_text,(270,180))
    music_volume_bar=createDragBar((276,210))

    #---------------Sound volume control---------------
    bg_image.blit(sound_text,(270,250))
    effect_volume_bar=createDragBar((276,280))

    #----------------Fullscreen control----------------
    bg_image.blit(fullscreen_text,(270,320))
    checkbox=createCheckBox((440,320))

    #-------------------Back button-------------------
    back_button=createBackButton((330,380))

    return ui_class.OptionScreen(bg_image,music_volume_bar,\
            effect_volume_bar,checkbox,back_button)




#----Mission selection menu interface--------------------------
def createBackButton2(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.BackButton2(button_image,image_info,
            topleft=topleft)

    return button


def createGoButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.GoButton(button_image,image_info,
            topleft=topleft,text='NEXT')

    return button


def createDifficultyBar(topleft):

    levels={0:'Come on',\
            1:'Low',\
            2:'Mid',\
            3:'High',\
            4:'Are You Sure?'}

    #----------------Get drag bar image----------------
    bar_image,_=ASSETS['drag_bar']
    bar_image=pygame.transform.scale(bar_image,(130,10))

    #----------------Get button images----------------
    def getButton(name):
        img,_=ASSETS[name]
        img=pygame.transform.scale(img,(20,20))
        return img

    buttons=['left_blackbutton', 'left_greenbutton', 
             'mid_blackbutton', 'mid_greenbutton',
             'right_blackbutton', 'right_greenbutton']

    left_black,left_green,mid_black,mid_green,right_black,right_green=\
            map(getButton,buttons)

    diff_bar=ui_class.DiscretDragBar(bar_image,topleft,
            left_black, left_green,
            right_black, right_green,
            mid_black, mid_green, levels)

    return diff_bar


def createMissionScreen(level_pack):

    #--------------Get background image--------------
    bg_image_ori,_=ASSETS['dim_background']
    background=bg_image_ori.copy().convert()

    #background=generals.setAlpha(background,20)
    background.set_alpha(20)

    blackbox=pygame.Surface((440,480)).convert()
    blackbox.fill((0,0,0))
    blackbox.set_alpha(150)
    background.blit(blackbox,(320,30))

    #---------------Scroll button images---------------
    up_scroll_image,up_scroll_info=ASSETS['up_scroll']
    down_scroll_image,down_scroll_info=ASSETS['down_scroll']

    #---------------Create tip box image---------------
    tip_box_image=createPlainFrame((400,40),border_color=C_LIGHTGREEN,
            fill_color=C_DARKGREEN)
    tip_box=ui_class.TipBar(tip_box_image,None,(350,40),\
        font_size=15)
    
    #--------------Create text box bar --------------
    text_box=ui_class.TextBox(topleft=(350,270),size=(400,150),
                texts=level_pack[0].texts,
                up_scroll=(up_scroll_image,up_scroll_info),
                down_scroll=(down_scroll_image,down_scroll_info),
                font_size=16,
                font_color=(255,255,255))

    #---------------Create difficult bar---------------
    diff_text=pygame.font.Font(E_FONT,20).render('DIFFICULTY',True,(255,255,255))
    background.blit(diff_text,(450,450))
    difficulty_bar=createDifficultyBar((540,480))

    #------------------Create buttons------------------
    back_button=createBackButton2((80,520))
    next_button=createGoButton((570,520))

    #-----------------Create list box-----------------
    list_box_image=createPlainFrameWithTitlebar((227,440),text='MISSIONS',
            border_width=2,font_size=30,font_color=(255,255,255),
            fill_color=C_LIGHTGREEN,titlebar_color=C_DARKGREEN)

    entries=[]

    for ii in level_pack:
        entries.append('* %s' %(ii.title))

    list_box=ui_class.ListBox(list_box_image,(60,40),
            entries,(up_scroll_image,up_scroll_info),
            (down_scroll_image,down_scroll_info),font_size=15,
            margin=(50,10,10,20))

    #------------------Create minimap------------------
    minimap_background=pygame.Surface((200,150)).convert_alpha()

    #-----------Create mission select screen-----------
    mission_screen=ui_class.MissionScreen(background,level_pack,
            list_box,tip_box,text_box,
            minimap_background,
            difficulty_bar,back_button,next_button)

    return mission_screen



#---------------Game over interface---------------
def createRetrybutton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.RetryButton(button_image,image_info,text='RETRY',
            topleft=topleft)
    return button


def createGameOver():

    boxsize=(400,300)

    #-----------Create dialogue box for win-----------
    win_screen_image=createPlainFrame(boxsize,border_width=2,
            fill_color=C_DARKGREEN_TRANS)
    win_text1=pygame.font.Font(E_FONT,40).render('MISSION',True,(255,255,255))
    win_text2=pygame.font.Font(E_FONT,40).render('COMPLETE',True,(255,255,255))

    t_left=int(0.5*(boxsize[0]-win_text1.get_size()[0]))
    win_screen_image.blit(win_text1,(t_left,20))
    t_left=int(0.5*(boxsize[0]-win_text2.get_size()[0]))
    win_screen_image.blit(win_text2,(t_left,20+win_text1.get_size()[1]+5))

    #-----------Create dialogue box for fail-----------
    fail_screen_image=createPlainFrame(boxsize,border_width=2,
            fill_color=C_DARKGREEN_TRANS)
    fail_text1=pygame.font.Font(E_FONT,40).render('MISSION',True,(255,255,255))
    fail_text2=pygame.font.Font(E_FONT,40).render('Failed',True,(255,255,255))

    t_left=int(0.5*(boxsize[0]-fail_text1.get_size()[0]))
    fail_screen_image.blit(fail_text1,(t_left,20))
    t_left=int(0.5*(boxsize[0]-fail_text2.get_size()[0]))
    fail_screen_image.blit(fail_text2,(t_left,20+win_text1.get_size()[1]+5))

    retry_button=createRetrybutton((420,400))
    back_button=createBackButton2((230,400))
    next_button=createGoButton((420,400))

    topleft=0.5*(generals.Vector2(SCREEN_SIZE)-win_screen_image.get_size())
    gameover_box=ui_class.GameOverBox(win_screen_image,fail_screen_image,
		topleft,retry_button,back_button,next_button)

    return gameover_box

    

#--------------Main screen interface--------------
def createStartButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    buttonii=ui_class.StartButton(button_image,image_info,
            topleft=topleft)
    return buttonii


def createCreditButton(topleft):

    button_image,image_info=ASSETS['plaque_button']
    button=ui_class.CreditButton(button_image,image_info,
            topleft=topleft)
    return button


def createCreditScreen():

    bg_image_ori,_=ASSETS['dim_background']
    bg_image=bg_image_ori.copy()

    #--------------Create box with title--------------
    frame=createPlainFrameWithTitlebar((400,430),text='CREDITS',
            border_width=3,font_size=40,font_color=(255,255,255),
            fill_color=C_DARKGREY_TRANS,titlebar_color=C_DARKGREEN_TRANS)
    bg_image.blit(frame,(0.5*(bg_image.get_size()[0]-400),
        0.5*(bg_image.get_size()[1]-450)))

    font=pygame.font.Font(E_FONT,15)
    texts=[
            'Programe:',
            '    G.X.',
            'Art Work:',
            '    G.X., Chenyu',
            'Animations:',
            '    G.X.',
            'Story:',
            '    G.X., Feng WEI',
            'Music & sound:',
            '    Yisell.com, 66RPG.com',
            'Font:',
            '    Jason Kottke',
            '    (http:///www.kottke.org)'
            ]

    topleft_0=(230,140)
    v_gap=20

    for ii,tii in enumerate(texts):
        text_surfaceii=font.render(tii,True,(255,255,255))
        bg_image.blit(text_surfaceii,topleft_0+generals.Vector2(0,v_gap*ii))

    back_button=createBackButton2((100,510))
    credit_screen=ui_class.CreditScreen(bg_image,back_button)

    return credit_screen


#-----------Create main screen interface-----------
def createMainScreen():

    background,_=ASSETS['main_screen']

    start_button=createStartButton((425,320))
    credit_button=createCreditButton((425,370))
    exit_button=createExitButton((425,440))

    #---------------Blit version number---------------
    font=pygame.font.Font(E_FONT,20)
    text_surface=font.render(__version__,True,(255,255,255))
    background.blit(text_surface,generals.Vector2(SCREEN_SIZE)-\
            text_surface.get_size()-generals.Vector2(10,10))

    main_screen=ui_class.MainScreen(background,start_button,credit_button,\
            exit_button)

    return main_screen





