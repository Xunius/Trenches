'''A simple 2-D path searching algrithm.
Wrapped in a class.

Update time: 2013-12-22 22:23:44:
    Now added a <cut_corner> option to allow diagonal movement
    (cutting a corner). 
'''

import numpy
#import time
import copy
#import matplotlib.pyplot as plt


class PathFinder(object):
    
    def __init__(self,ori_map,start=(0,0),end=(1,1),cut_corner=False,\
            include_start=False,plot=False):
        '''Find a path from <start> to <end> on a 2D map <ori_map>.

        <ori_map>: 2D matrix defining a map of 0s and 1s, 1s for viable\
                places and 0 for non-viables;
        <start>: starting point;
        <end>: target point;
        <cut_corner>: bool, allow corner-cutting diagonal move or not.
        <plot>: plot out map or not.

        Return <path_list>: a list of coordinate tuples linking <start> and\
                <end>. The order is reversed so that the 1st point is <end>
                and last is <start>. If no path is found, return None.
        '''

        self.ori_map=ori_map
        self.start=start
        self.end=end
        self.cut_corner=cut_corner
        self.include_start=include_start
        self.plot=plot

        #--------Initial check of <start> and <end>-----------------
        if self.ori_map[self.end]==0 or self.ori_map[self.start]==0:
            #raise 'wrong settings of start or end.'
            self.path=None


        #-----3 by 3 search box-----------------
        self.search_box=numpy.array([[1.4,1,1.4],\
                [1,0,1],\
                [1.4,1,1.4]])

        if self.cut_corner==False:
            self.search_box_mask=numpy.array([[True,False,True],\
                    [False,False,False],\
                    [True,False,True]])


    def findPath(self):

        if self.start==self.end:
            self.path=[self.start,]
            return

        #-------distance map----------------
        # default everything to 9999, replace each with actual distance.
        self.distance_map=self.ori_map*9999
        if self.plot:
            self.distance_map[self.start]=0.1
        else:
            self.distance_map[self.start]=0
        #set the start to 0.1 is simply make it non zero, because zeros will be masked out
        #so that they will appear black in the plot, just for the purpose of displaying.

        coorlist=[self.start,]
        #print 'self.start',self.start
        newlist,finish=self.regionGrow(coorlist)

        while finish is False:
            newlist,finish=self.regionGrow(newlist)
            if len(newlist)==0:
                break

        #-----mask out non-viable areas---------------
        self.distance_map=numpy.ma.masked_equal(self.distance_map,0)

        #-----Check if path exists between <start> and <end>--------
        if finish is False:
            self.path=None
            return None

        #-----Find out path and return list-------------
        path=self.minPath()

        #--------Plot if needed--------------
        if self.plot:

            self.distance_map=numpy.where(self.distance_map==9999,0,self.distance_map)

            for coor in path:
                self.distance_map[coor]=9999

            plt.imshow(self.distance_map)
            plt.show()


        self.path=path

        return



    def modifySearchBox(self,index,search_box,size):

        search_box2=copy.copy(search_box)
        x,y=index
        w,h=size

        x_start=0
        y_start=0
        x_end=3
        y_end=3

        if x==0:
            x_start=1
        if y==0:
            y_start=1
        if x==w-1:
            x_end=2
        if y==h-1:
            y_end=2

        return search_box2[x_start:x_end,y_start:y_end]



    #--------------Region grow function----------------------------
    def regionGrow(self,coorlist):
        '''Expanding search and calculate distances for all viable points.

        <coorlist>: a list of coordinate tuples to expand out from.
        <distance_map>: 2D matrix containing distances of each point to
                        the starting point. Default to 9999.
        <search_box>: search element matrix. Default to a 3 by 3 array:

                    | 1.4     1     1.4|
                    |  1      0      1 |
                    | 1.4     1     1.4|

                      If search goes to corners or edges, truncate to approiate
                      form. E.g. the top left corner:

                    | 0       1 |
                    | 1      1.4|

        <end>: end point in tuple, used to check search finish.

        Return <newcoorlist>: a new list of coordinate tuples for the next\
                round of expansion.
                <finish>: bool, found the end point or not.
        '''

        newcoorlist=[]
        len_x,len_y=self.distance_map.shape

        for coor in coorlist:
            x,y=coor

            #-------calculate distances from a centre box to surrouding 8 boxes-
            distance_box=self.distance_map[max(x-1,0):min(x+2,len_x),\
                    max(y-1,0):min(y+2,len_y)]
            centre_box=numpy.ones(distance_box.shape)*self.distance_map[x,y]
            search_box2=self.modifySearchBox((x,y),self.search_box,self.distance_map.shape)

            #---New boxes to search/check, none 0: viable points; 9999: not
            # checked yet
            indices=numpy.where((distance_box!=0) & (distance_box==9999))
            indices=zip(indices[0]+max(0,x-1),indices[1]+max(0,y-1))

            #---Update distances-----------------------
            self.distance_map[max(x-1,0):min(x+2,len_x),\
                max(y-1,0):min(y+2,len_y)]=numpy.minimum(\
                centre_box+search_box2,distance_box)


            #----New coordinates to be expanded---------------
            for ii in indices:
                if ii in newcoorlist:
                    continue
                else:
                    newcoorlist.append(ii)
                if ii==self.end:
                    return newcoorlist,True


        return newcoorlist,False



    #--------Shortest local index----------------
    def minIndex(self,coor):
        '''Convert the index of minimum of a ub-matrix to the index\
                of the global matrix. 

        <coor>: the coordinate tuple defining a point of <distance_map>;
        <distance_map>: matrix from which global index is found.

        Return: <global_min_index>
        '''

        x,y=coor
        len_x,len_y=self.distance_map.shape

        local_box=self.distance_map[max(x-1,0):min(x+2,len_x),\
                max(y-1,0):min(y+2,len_y)]

        if self.cut_corner==False:
            mask=self.modifySearchBox((x,y),self.search_box_mask,self.distance_map.shape)
            local_box=numpy.ma.masked_array(local_box,mask=mask)

        local_min_index=numpy.unravel_index(local_box.argmin(),local_box.shape)
        global_min_index=(local_min_index[0]+max(0,x-1),\
                local_min_index[1]+max(y-1,0))

        return global_min_index


    #---------Global path indices-----------------
    def minPath(self):
        '''Work out a path from starting to target point on a map.

        <start>,<end>: starting and target point;
        <distance_map>: map defining viable areas and obstacles.

        Return: <path_list>: a list of coordinate tuples.
        '''

        path_list=[self.end,]
        num=1

        newindex=self.minIndex(self.end)
        path_list.append(newindex)

        while True:
            newindex=self.minIndex(newindex)
            num+=1
            if newindex==path_list[-1]: 
                path_list.append(newindex)
                break
            if newindex==self.start:
                path_list.append(newindex)
                break
            if num>10000:
                break
            path_list.append(newindex)

        path_list.reverse()
        
        if self.include_start is False:
            del path_list[0]

        return path_list




if __name__=='__main__':

    """
    size=(60,60)
    map=numpy.ones(size)
    map[20:30,0:50]=0
    map[30:52,38:50]=0
    map[46:50,24:42]=0
    start=(10,20)
    end=(32,32)
    '''
    size=(600,500)
    map=numpy.ones(size)
    map[200:230,0:400]=0
    map[230:520,350:400]=0
    map[460:500,240:420]=0
    start=(40,35)
    end=(380,300)
    '''

    start_time=time.clock()
    start_time2=time.time()

    pathfinder=PathFinder(map,start,end,cut_corner=False,include_start=False,plot=True)
    pathfinder.findPath()
    end_time=time.clock()
    #print 'time used',end_time-start_time
    #print 'time used by time()',time.time()-start_time2
    #print pathfinder.path
    """









