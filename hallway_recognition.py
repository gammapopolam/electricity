from vector_algs_handler import get_direction
from shapely import intersects, relate, equals
from shapely.geometry import LineString, MultiLineString
import math

class HallwaySearch:
    def __init__(self, l1, l1_buff, l2, l2_buff, angle):
        self.l1=l1
        self.l2=l2
        self.l1_buff=l1_buff
        self.l2_buff=l2_buff
        self.flag1 = 'undefined'
        self.angle=angle
    def is_buffers_intersect(self):
        #if intersects(self.l1_buff, self.l2_buff)==True and self.l1_buff.intersection(self.l2_buff).area>(self.l2_buff.area/100*15): #!
        if intersects(self.l1_buff, self.l2_buff)==True and self.l1_buff.intersection(self.l2_buff).area>(self.l2_buff.area/100*15): #!
            return True
        else:
            return False
    def is_stream(self):
        #if self.angle_flag(self.l1, self.l2)=='hallway':
        #    return True
        if relate(self.l1, self.l2)=='FF1FF0102' and self.angle_flag(self.l1, self.l2)=='hallway':
            return True
        #elif relate(self.l1, self.l2)=='1F1F00102' and self.angle_flag(self.l1, self.l2)=='hallway':
        #    return True
        elif relate(self.l1, self.l2)=='FF1F0F102' and self.angle_flag(self.l1, self.l2)=='hallway':
            return True
        else:
            return False
        
    def solve(self):
        flag='undefined'
        if self.is_buffers_intersect()==False:
            flag='undefined'
        else:
            if self.is_stream()==True:
                flag='stream'
        return flag
    def angle_flag(self, l1, l2):
        flag='undefined'
        if l1.geom_type=='MultiLineString' and l2.geom_type=='MultiLineString':
            l1_geoms=list(l1.geoms)
            l2_geoms=list(l2.geoms)
            for geom in l1_geoms:
                l1=geom.coords
                for geom2 in l2_geoms:
                    l2=geom2.coords
                    m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                    m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                    angle_rad = abs(math.atan(m1) - math.atan(m2))
                    angle_deg = angle_rad*180/math.pi
                    #print('angle diff:', abs(angle_deg))
                    if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                        flag='hallway'
        elif l1.geom_type=='MultiLineString' and l2.geom_type=='LineString':
            l1_geoms=list(l1.geoms)
            l2=list(l2.coords)
            for geom in l1_geoms:
                l1=geom.coords
                m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                angle_rad = abs(math.atan(m1) - math.atan(m2))
                angle_deg = angle_rad*180/math.pi
                #print('angle diff:', abs(angle_deg))
                if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                    flag='hallway'
        elif l1.geom_type=='LineString' and l2.geom_type=='MultiLineString':
            l2_geoms=list(l2.geoms)
            l1=list(l1.coords)
            for geom in l2_geoms:
                l2=geom.coords
                m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                angle_rad = abs(math.atan(m1) - math.atan(m2))
                angle_deg = angle_rad*180/math.pi
                #print('angle diff:', abs(angle_deg))
                if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                    flag='hallway'
        else:
            l1=list(l1.coords)
            l2=list(l2.coords)
            m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
            m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
            angle_rad = abs(math.atan(m1) - math.atan(m2))
            angle_deg = angle_rad*180/math.pi
            #print('angle diff:', abs(angle_deg))
            if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                flag='hallway'
        return flag
    def angle_flag_new(self, l1, l2):
        if self.l1.geom_type=='LineString' and self.l2.geom_type=='LineString':
            a1=get_direction(list(self.l1.coords))
            a2=get_direction(list(self.l2.coords))
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag1='hallway'
        elif self.l1.geom_type=='LineString' and self.l2.geom_type=='MultiLineString':
            a1=get_direction(list(self.l1.coords))
            a2s=[]
            for geom in self.l2.geoms:
                a2i=get_direction(list(geom.coords))
                a2s.append(a2i)
            a2=max(a2s) #! 
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag1='hallway'
        elif self.l2.geom_type=='LineString' and self.l1.geom_type=='MultiLineString':
            a2=get_direction(list(self.l2.coords))
            a1s=[]
            for geom in self.l1.geoms:
                a1i=get_direction(list(geom.coords))
                a1s.append(a1i)
            a1=max(a1s) #! 
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag1='hallway'
        elif self.l1.geom_type=='MultiLineString' and self.l2.geom_type=='MultiLineString':
            a1s=[]
            for geom in self.l1.geoms:
                a1i=get_direction(list(geom.coords))
                a1s.append(a1i)
            a1=max(a1s) #! 
            a2s=[]
            for geom in self.l2.geoms:
                a2i=get_direction(list(geom.coords))
                a2s.append(a2i)
            a2=max(a2s) #! 
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag1='hallway'
        return self.flag1
    def to_multiline(self, flag):
        if flag=='stream':
            newgeom=[]
            if self.l1.geom_type=='MultiLineString':
                for l1_geom in self.l1.geoms:
                    if l1_geom not in newgeom:
                        newgeom.append(l1_geom)
                if self.l2.geom_type=='MultiLineString':
                    for l2_geom in self.l2.geoms:
                        if l2_geom not in newgeom:
                            newgeom.append(l2_geom)
                elif self.l2.geom_type=='LineString':
                    if self.l2 not in newgeom:
                        newgeom.append(self.l2)
                    
            elif self.l1.geom_type=='LineString':
                if self.l1 not in newgeom:
                    newgeom.append(self.l1)
                if self.l2.geom_type=='MultiLineString':
                    for l2_geom in self.l2.geoms:
                        if l2_geom not in newgeom:
                            newgeom.append(l2_geom)
                elif self.l2.geom_type=='LineString':
                    if self.l2 not in newgeom:
                        newgeom.append(self.l2)
        newgeom=list(set(newgeom))
        self.multil=MultiLineString(newgeom)
        return self.multil
