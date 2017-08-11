'''Process mask layer of scene map.

Regrid the mask layer and get the accessible map.

e.g. Design the accessible map of a game scene by filling obstacls with
black and leaving the viable areas with white. This mask layer is
640*400 in size, and the grid of the game is set to 20*20, therefore
the accessible map is 32*20. This map is get by averaging every 20*20
grid boxes of the original 640*400 image.
'''




import numpy
#import matplotlib.pyplot as plt


COLOR_CODES={'enemy_spawn':[255,0,0],\
            'hq':[0,0,255],\
            'defence':[0,0,0],\
            'viable':[255,255,255]\
            }


#---Regrid the mask layer by averaging grid boxes---------
def regrid(image,reso,verbose=True):
    '''Regrid the mask layer by averaging grid boxes.

    <image>: image obj read by Image.open(). 
    <reso>: tuple of resolution.
    '''

    delta_x,delta_y=reso
    try:
        size=image.size
        size=image.shape
    except:
        size=image.get_size()

    contract=3

    image_array=numpy.array(image)

    if image_array.shape[-1]==4:
        image_array=image_array[:,:,:3]

    # Note that the 0th dimension is width and 1st one the height.
    new_array=numpy.zeros((size[1]/delta_y,size[0]/delta_x,3))

    for ii in range(new_array.shape[0]):
        for jj in range(new_array.shape[1]):
            box=image_array[contract+jj*delta_y:jj*delta_y+delta_y-contract,\
                    ii*delta_x+contract:ii*delta_x+delta_x-contract,:]
            box=numpy.mean(box,axis=0)
            box=numpy.mean(box,axis=0)
            new_array[ii,jj]=box

    return new_array



#------Header description here.----------
def viaimage2Viamap(via_image,via_value=COLOR_CODES['viable'],\
        block_value=[0,0,0],verbose=True):
    '''Translate regrided viable image to a 2D via map.

    <via_image>: the numpy.ndarray of viability image regrided to 
                 the game world resolution. It is a 3D array with its
                 3rd dimention being the RGB color channels.
    <via_value>: tuple of the color representing viable grid boxes. 
                 E.g. (255,255,255) (white) being viable grids.
    <block_value>: tuple of the color representing non-viable grids.
                   E.g. (0,0,0) (black) being non-viable grids.

    Return <via_map>: a map of 0s and 1s with 1s being the viable
    grids and 0s the non-viable ones.

    '''

    '''
    via_map=numpy.zeros(via_image.shape[:2])
    via_map=numpy.where((via_image[:,:,0]==via_value[0]) &\
            (via_image[:,:,1]==via_value[1]) &\
            (via_image[:,:,2]==via_value[2]) ,1,via_map)
    via_map=numpy.where((via_image[:,:,0]==block_value[0]) &\
            (via_image[:,:,1]==block_value[1]) &\
            (via_image[:,:,2]==block_value[2]) ,0,via_map)
    '''
    via_map=numpy.ones(via_image.shape[:2])
    via_map=numpy.where((via_image[:,:,0]==block_value[0]) &\
            (via_image[:,:,1]==block_value[1]) &\
            (via_image[:,:,2]==block_value[2]) ,0,via_map)

    return via_map


#------Read spots locations from mask map----------
def readSpots(mask_map,color_codes=COLOR_CODES,verbose=True):
    '''Read spots locations from mask map

    mask_map
    '''

    spots={}
    mask_map=numpy.array(mask_map)
    if mask_map.shape[-1]==4:
        mask_map=mask_map[:,:,:3]

    for ii in color_codes.keys():
        index=numpy.where((mask_map[:,:,0]==color_codes[ii][0]) & \
                (mask_map[:,:,1]==color_codes[ii][1]) &\
                (mask_map[:,:,2]==color_codes[ii][2]))
        index=zip(index[0],index[1])
        #print 'index',index
        '''
        if len(index)>1:
            raise()
        if len(index)==1:
            spots[ii]=index[0]
        else:
            spots[ii]=index
        '''
        spots[ii]=index

    return spots







#----Main--------------------------
if __name__=='__main__':


    """
    file='test.png'
    image=Image.open(file)

    start_time=time.clock()
    start_time2=time.time()

    sharp=regrid(image,(20,20))

    end_time=time.clock()
    #print 'time used',end_time-start_time
    #print 'time used by time()',time.time()-start_time2

    #--Note: this is not displayed quite well due to matplotlib
    # issue, not the data itself.

    via_map=viaimage2Viamap(sharp)
    plt.imshow(via_map)
    plt.show()
    """




