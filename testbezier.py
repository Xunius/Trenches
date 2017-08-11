import numpy

#from gameobjects.vector2 import Vector2
#import matplotlib.pyplot as plt


def GetBezierCurve(start,end,height,steps):
    x0,y0=start
    x2,y2=end

    if x0==x2:
        xs=[x0,]*steps
        y_step=float(y2-y0)/steps
        ys=[ii*y_step for ii in range(1,steps+1)]

    else:

        theta=numpy.arctan2(-(y2-y0),x2-x0)
        cos_theta=numpy.cos(theta)
        if y2>y0:
            cos_theta=-numpy.abs(cos_theta)
        elif y2<y0:
            cos_theta=numpy.abs(cos_theta)
        else:
            cos_theta=0.

        cos_theta/=2.
        #print 'cos',cos_theta

        l=0.5*numpy.abs(x2-x0)*cos_theta
        x1=0.5*(x0+x2)+l

        #x1=0.5*((1-cos_theta)*x0+(1+cos_theta)*x2)
        #print 'x1',x1

        y1=height+(y2-y0)*(x1-x0)/(x2-x0)
        #print 'y1',y1

        xs=[]
        ys=[]
        for ii in range(1,steps+1):
            tt=float(ii)/steps
            xii=(1-tt)**2*x0+2*tt*(1-tt)*x1+tt**2*x2
            yii=(1-tt)**2*y0+2*tt*(1-tt)*y1+tt**2*y2
            xs.append(xii)
            ys.append(yii)

    return zip(xs,ys)


def getParabol(start,end,height,steps):

    x1,y1=start
    x2,y2=end

    if x1==x2:
        delta_y=float(y2-y1)/steps
        xs=[x1,]*steps
        ys=[y1+delta_y*ii for ii in range(1,steps+1)]

        return zip(xs,ys)

    else:

        a=4.*height/(x1-x2)**2
        #print 'a',a
        b=-4.*height*(x1+x2)/(x1-x2)**2
        #print 'b',b
        c=y1+4.*height*x1*x2/(x1-x2)**2
        #print 'c',c

        shift=float(y1-y2)/(x2-x1)

        xs=[]
        ys=[]
        ys2=[]

        delta_x=float(x2-x1)/steps
        for ii in range(1,steps+1):
            x=delta_x*ii+x1
            #print 'x',x
            y=a*x**2+b*x+c
            #ys2.append(y)
            y-=shift*(x-x1)
            #print 'y',y
            xs.append(x)
            ys.append(y)


        #return xs,ys
        return zip(xs,ys)
        #return (xs,ys),(xs,ys2)


'''
p0=Vector2(0,0)
p2=Vector2(15,4)

heading=(p2-p0).get_normalized()
theta=numpy.arctan2(-heading[1],heading[0])/numpy.pi*180
print 'heading',self.heading
print 'theta',theta

cos_theta=numpy.cos(theta/180.*numpy.pi)
print 'cos',cos_theta

x1=
theta=numpy.arctan2(p2[1]-p0[1],p2[0]-p0[0])/numpy.pi*180
printnumpy arctan2numpy arctan2 'theta',theta
cos_theta=numpy.cos(theta/180.*numpy.pi)
print 'cos',cos_theta
cos_theta/=3.

if p2[1]-p0[1]>0:
    cos_theta=numpy.abs(cos_theta)
elif p2[1]-p0[1]<0:
    cos_theta=-numpy.abs(cos_theta)
elif p2[1]==p0[1]:
    cos_theta=0


x1=0.5*((1-cos_theta)*p0[0]+(1+cos_theta)*p2[0])
print 'x1',x1

H=5.

y1=H+(p2[1]-p0[1])*(x1-p0[0])/(p2[0]-p0[0])


xs=[]
ys=[]
for ii in range(101):
    tt=ii/100.
    #xii=p0[0]+ii*(p2[0]-p[0])/100.
    xii=(1-tt)**2*p0[0]+2*tt*(1-tt)*x1+tt**2*p2[0]

    yii=(1-tt)**2*p0[1]+2*tt*(1-tt)*y1+tt**2*p2[1]
    xs.append(xii)
    ys.append(yii)

p0=(170.,410.)
p2=(10.,300.9)
#xs,ys=GetBezierCurve(p0,p2,5.,100)
#xs,ys=getParabol(p0,p2,5.,100)
aa,bb=getParabol(p0,p2,45.,100)

plt.plot(aa[0],aa[1],'r:')
plt.plot(bb[0],bb[1],'b-')
plt.axis('equal')
plt.show()
    
'''







