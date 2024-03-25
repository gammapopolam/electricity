from vector_algs_handler import get_direction
from shapely import intersects, relate, equals
from shapely.geometry import LineString, MultiLineString

class HallwaySearch:
    def __init__(self, l1, l1_buff, l2, l2_buff, angle):
        self.l1=l1
        self.l2=l2
        self.l1_buff=l1_buff
        self.l2_buff=l2_buff
        self.flag = 'undefined'
        self.angle=angle
    def is_buffers_intersect(self):
        if intersects(self.l1_buff, self.l2_buff)==True and self.l1_buff.intersection(self.l2_buff).area>(self.l2_buff.area/100*15): #!
            return True
        else:
            return False
    def is_stream(self):
        if relate(self.l1, self.l2)=='FF1FF0102' and self.angle_flag(self.l1, self.l2)=='hallway':
            return True
        #elif relate(self.l1, self.l2)=='1F1F00102' and self.angle_flag(self.l1, self.l2)=='hallway':
        #    return True
        elif relate(self.l1, self.l2)=='FF1F0F102' and self.angle_flag(self.l1, self.l2)=='hallway':
            return True
        else:
            return False
        
    def solve(self):
        if self.is_buffers_intersect()==False:
            self.flag='undefined'
        else:
            if self.is_stream()==True:
                self.flag='stream'
    def angle_flag(self):
        if self.l1.geom_type=='LineString' and self.l2.geom_type=='LineString':
            a1=get_direction(list(self.l1.coords))
            a2=get_direction(list(self.l2.coords))
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag='hallway'
        elif self.l1.geom_type=='LineString' and self.l2.geom_type=='MultiLineString':
            a1=get_direction(list(self.l1.coords))
            a2s=[]
            for geom in self.l2.geoms:
                a2i=get_direction(list(geom.coords))
                a2s.append(a2i)
            a2=max(a2s) #! 
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag='hallway'
        elif self.l2.geom_type=='LineString' and self.l1.geom_type=='MultiLineString':
            a2=get_direction(list(self.l2.coords))
            a1s=[]
            for geom in self.l1.geoms:
                a1i=get_direction(list(geom.coords))
                a1s.append(a1i)
            a1=max(a1s) #! 
            if abs(a1-a2)<self.angle or abs(a1-a2)>(180-self.angle):
                self.flag='hallway'
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
                self.flag='hallway'
    def to_multiline(self, flag):
        if flag=='stream':
            if self.l1.geom_type=='MultiLineString':
                if self.l2.geom_type=='MultiLineString':
                    self.multil=MultiLineString([*self.l1.geoms, *self.l2.geoms])
                elif self.l2.geom_type=='LineString':
                    self.multil=MultiLineString([*self.l1.geoms, self.l2])
            elif self.l1.geom_type=='LineString':
                if self.l2.geom_type=='MultiLineString':
                    self.multil=MultiLineString([self.l1, *self.l2.geoms])
                elif self.l2.geom_type=='LineString':
                    self.multil=MultiLineString([self.l1, self.l2])
        return self.multil
