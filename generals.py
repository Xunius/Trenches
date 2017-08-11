'''General purpose functions.
'''
import pygame
from pygame.locals import Rect
import os
import math



#--------------2D vector computations--------------
class Vector2(tuple):
    '''2D vector computations

    pygame's functions often requires a coordinate as tuples, therefore
    Vector2 is subclassed from tuple type.
    '''
    def __new__(typ,*data):
        if len(data)==2:
            x,y=data
        else:
            x,y=data[0][0],data[0][1]
        n=tuple.__new__(typ,(float(x),float(y)))
        n._x=float(x)
        n._y=float(y)
        return n

    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y
    @x.setter
    def x(self,v):
        self._x=float(v)
    @y.setter
    def y(self,v):
        self._y=float(v)

    def __neg__(self):
        newvec=Vector2(-self._x, -self._y)
        return newvec

    def __add__(self,v):
        if isinstance(v,Vector2):
            newvec=Vector2(self._x+v.x, self._y+v.y)
        elif type(v) is list or type(v) is tuple:
            newvec=Vector2(self._x+v[0], self._y+v[1])
        return newvec

    def __radd__(self,v):
        return self.__add__(v)

    def __sub__(self,v):
        if isinstance(v,Vector2):
            newvec=Vector2(self._x-v.x, self._y-v.y)
        elif type(v) is list or type(v) is tuple:
            newvec=Vector2(self._x-v[0], self._y-v[1])
        return newvec

    def __rsub__(self,v):
        if isinstance(v,Vector2):
            newvec=Vector2(v.x-self._x, v.y-self._y)
        elif type(v) is list or type(v) is tuple:
            newvec=Vector2(v[0]-self._x, v[1]-self._y)
        return newvec

    def __mul__(self,v):
        if isinstance(v,Vector2):
            res=self._x*v.x+self._y*v.y
        elif type(v) is list or type(v) is tuple:
            res=self._x*v[0]+self._y*v[1]
        else:
            res=Vector2(self._x*v, self._y*v)
        return res

    def __rmul__(self,v):
        return self.__mul__(v)

    def __div__(self,v):
        v=float(v)
        return Vector2(self._x/v, self._y/v)
            
    def get_length(self):
        return math.sqrt(self._x**2+self._y**2)

    def get_normalized(self):
        l=self.get_length()
        return Vector2(self._x/l, self._y/l)

    def normalize(self):
        l=self.get_length()
        self._x=float(self._x/l)
        self._y=float(self._y/l)
        return self

    def __str__(self):
        return 'vector = (%f, %f)' %(self.x,self.y)

    def __repr__(self):
        return 'vector = (%f, %f)' %(self.x,self.y)

    def __getitem__(self,i):
        if i==0:
            return self._x
        elif i==1:
            return self._y
        else:
            raise Exception("Index out of range")

    def __setitem__(self,i,v):
        if i==0:
            self._x=v
        elif i==1:
            self._y=v
        else:
            raise Exception("Index out of range")


#------Interpret image file names----------
def interpName(filename):
    '''Interpret image file names

    '''

    name,ext=os.path.splitext(filename)

    #----Start with 'image'--------------------------
    name2=name.split('_')
    if name2[0] not in ['ani','image']:
        raise Exception("File name not recognized")
    image_name=name2[1]
    n_row,height,n_column,width=name2[2].split('x')

    return image_name,int(n_row),int(height),int(n_column),int(width)


#------Scale image to target size----------
def scaleImage(image,image_info):
    '''Scale image to target size

    '''
    return pygame.transform.scale(image,(image_info[3]*image_info[4],\
            image_info[1]*image_info[2]))

    
#------Translate from window coordinate to a mesh grid coordination---
def window2Grid(window_loc,grid_reso,topleft=(0,0),via_map=None,verbose=True):
    '''Translate from window coordinate to a mesh grid coordination,
    according to given grid size (grid_reso). And return viability if
    an accessiable map is given.

    <window_loc>: coordinate pair of the background space: (x,y). Note
                  that the origin (0,0) is top left corner, and x is
                  the horizontal direciton, which corresponds to the
                  column number.
    <grid_reso>: tuple of grid size pair: (w,h). w: horizontal width
                 of the grid box, h: vertical height of the box.
    <via_map>: 2D viability map, which has same size grid boxes as
               <grid_reso>.

    Return <grid_loc>: (row,column), row for row number, column for
    column number.

    If <via_map>: given, also return a boolean variable representing
    whether <grid_loc> is a viable grid box or not.

    row=y/h
    column=x/w
    '''

    window_loc=Vector2(*window_loc)
    topleft=Vector2(*topleft)
    window_loc-=topleft

    x,y=window_loc
    w,h=grid_reso

    row=int(y)/int(h)
    column=int(x)/int(w)

    if via_map is not None:
        if via_map[row,column]==1:
            viable=True
        else:
            viable=False

    if via_map is None:
        return (row,column)
    else:
        return ((row,column),viable)


#------Translate from grid coordinate to window coordinate---
def grid2Window(grid_pos,reso,topleft=(0,0),verbose=True):
    '''Convert from grid coordinate to window coordiante.

    <grid_pos>: tuple of grid coordianate: (row_index, column_index)
    <reso>: tuple of grid resolution: (width,height)

    Return <window_pos>: Window coordinate.
    '''
    return Vector2((grid_pos[1]*reso[0]+topleft[0],\
        grid_pos[0]*reso[1]+topleft[1]))




#--------Get topleft coordinate give center--------
def center2Topleft(rect=None,center=None,size=None):
    if rect is not None:
        return Vector2(rect[0],rect[1])
    if rect is None and center is not None and size is not None:
        return Vector2(center[0]-size[0]/2.,center[1]-size[1]/2.)


#--------Get center coordinate give topleft--------
def topleft2Center(rect=None,topleft=None,size=None):
    if rect is not None:
        return Vector2(rect[0]+rect[2]/2.,rect[1]+rect[3]/2.)
    if rect is None and topleft is not None and size is not None:
        return Vector2(topleft[0]+size[0]/2.,topleft[1]+size[1]/2.)


#-------Split frames from a composite image-------
def splitImage(image,image_info):
    '''
    <image>: image obj, have multiple frames in a row or column
    <image_info>: tuple: (image_name,n_row,height,n_column,width)
    '''
    image_name,n_row,height,n_column,width=image_info

    if n_row==1 and n_column==1:
        return [image,]

    elif n_row==1 and n_column!=1:
        return [image.subsurface(Rect(ii*width,0,width,height))\
                for ii in xrange(n_column)]

    elif n_row!=1 and n_column==1:
        return [image.subsurface(Rect(0,ii*height,width,height))\
                for ii in xrange(n_row)]


#------Prepare farewell text.----------
def prepareEndingText(scene,win):
    '''Prepare farewell text.

    '''

    if win:
        text='                    Victory !                           '
    else:
        text='                    Battle lost  .....                  '

    #----------Get dead names---------------
    team1_dead=scene.dead_names[1]
    team2_dead=scene.dead_names[2]
    dead_names=team1_dead+team2_dead

    dead_text='                     People that died in this battle:              '
    for ii in dead_names:
        if ii == dead_names[-1]:
            dead_text+=ii+'.                     '
        else:
            dead_text+=ii+',   '

    text+=dead_text
    text+='                Thanks for playing this game.                           '

    return text


#-----------Set surface transparency-----------
def setAlpha(surface,alpha,copy=True):
    '''
    <alpha>: int, 0-255.
    '''
    if copy:
        surface_copy=surface.copy().convert_alpha()
        array=pygame.surfarray.pixels_alpha(surface_copy)
        array[:]=alpha
        del array  # unlock surface by removing pixel array
        return surface_copy
    else:
        array=pygame.surfarray.pixels_alpha(surface)
        array[:]=alpha
        del array



def chopCenter(bg_surface,chop_surface,topleft):
    '''Chop <chop_surface> from a background surface <bg_surface>,
    starting from <topleft> wrt the topleft corner of <bg_surface>

    '''
    chop_array=pygame.surfarray.pixels_alpha(chop_surface)
    chop_array=chop_array.copy()
    bg_array=pygame.surfarray.pixels_alpha(bg_surface)
    chop_size=chop_array.shape

    tl_x,tl_y=map(int,topleft)
    bg_array[tl_x:tl_x+chop_size[0],\
             tl_y:tl_y+chop_size[1]]-=chop_array
    bg_array=None  # unlock surface
    chop_array=None  # unlock surface



#------------Turn surface to gray scale------------
def grayscale(img):
    arr = pygame.surfarray.array3d(img)
    arr=arr.dot([0.298,0.587,0.114])[:,:,None].repeat(3,axis=2)
    return pygame.surfarray.make_surface(arr)





'''
def stereoVolume(x,screen_width,global_volume):

    right_volume=float(x/screen_width)
    left_volume=(1.0-right_volume)*global_volume
    right_volume*=global_volume

    return (left_volume,right_volume)
'''
