from shapely import intersects, relate, equals
from shapely.geometry import MultiLineString, LineString
import math

def get_direction(l1):
    dx1, dy1 = l1[1][0]-l1[0][0], l1[1][1]-l1[0][1]
    r1=math.atan2(dy1,dx1)*180/math.pi
    if dx1>0 and dy1>0:
        a1=r1
    elif dx1<0 and dy1>0:
        a1=180-r1
    elif dx1<0 and dy1<0:
        a1=r1-180
    elif dx1>0 and dy1<0:
        a1=360-r1
    return a1

def area(q,p,r):
    return 1/2*(q[0]*p[1]-p[0]*q[1]+p[0]*r[1]-r[0]*p[1]+r[0]*q[1]-q[0]*r[1])

def side(p1, p3, p2):
    area123=area(p1,p3,p2)
    if area123==0:
        return 0
    elif area123<0:
        return -1 #справа
    elif area123>0:
        return 1 #слева
    
def line_side(line_cur, line_hall):
    p1, p2 = line_cur
    p3, p4 = line_hall
    #print(LineString((p1, p2)), LineString((p3, p4)))
    #if side(p1,p3,p2)>0 and side(p1,p4, p2)>0 and 
    if side(p1, p3, p2)>0 and side(p1, p4, p2)>0 and side(p3, p1, p4)<0 and side(p3, p2, p4)<0:
        return 1
    elif side(p1, p3, p2)<0 and side(p1, p4, p2)<0 and side(p3, p1, p4)>0 and side(p3, p2, p4)>0:
        return -1
    else:
        return 0