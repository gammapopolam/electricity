#%%
from sympy.solvers.solveset import linsolve
from shapely import intersects, relate, equals, box
from shapely.geometry import MultiLineString, LineString, MultiPoint, Point
import shapely
from sympy import *
import json
import geopandas as gpd
import matplotlib.pyplot as plt

from vector_algs_handler import *
#%%
class Equation:
    # Инициализация линии, состоящей из двух точек, как уравнение прямой
    def __init__(self, line):
        self.geom=line
        self.p1, self.p2 = list(line.coords)
        (x1, y1) = self.p1
        (x2, y2) = self.p2
        self.a=y1-y2
        self.b=x2-x1
        self.c=x1*y2-x2*y1
    def get_straight(self):
        x, y = symbols('x, y')
        return self.a*x+self.b*y+self.c

def flip_segments(line_current, line_next, first=False):
    #p1c, p2c - current line point 1/2
    #p1n, p2n - next line point 1/2
    p1c, p2c = list(line_current.coords)
    p1n, p2n = list(line_next.coords)
    d_2c1n = float(Point(p2c).distance(Point(p1n))) # расстояние от конца первого до начала второго, эталон
    d_1c2n = float(Point(p1c).distance(Point(p2n))) # расстояние от начала первого до конца второго
    d_1c1n = float(Point(p1c).distance(Point(p1n))) # расстояние от начала первого до начала второго
    d_2c2n = float(Point(p2c).distance(Point(p2n))) # расстояние от конца первого до конца второго
    a1 = get_direction(list(line_current.coords))
    a2 = get_direction(list(line_next.coords))
    if first:
        if d_1c2n<d_2c1n:
            line_current=LineString((p2c, p1c))
            line_next=LineString((p2n, p1n))
        if d_1c1n<d_2c1n:
            line_current=LineString((p2c, p1c))
        if d_2c2n<d_2c1n:
            line_next=LineString((p2n, p1n))
    else:
        # Случаи, когда не начало геометрии, а ход по линии 
        #print(a1-90, a2, a1+90)
        #print(a1, a2)
        if a2>360:
            a2=a2-360
        if (a1-90<a2 and a1+90>a2) and d_1c1n<d_1c2n:
            pass
        else:
            line_next=LineString((list(line_next.coords)[1], list(line_next.coords)[0]))
    return line_current, line_next
def segment_solver(line_current, line_next):
    # Если отрезки имеют пересечение, то новая геометрия - с общей вершиной в точке пересечения линий
    if line_current.intersects(line_next) or list(line_current.coords)[1]==list(line_next.coords)[0]:
        #print('segments intersect')
        p_int=line_current.intersection(line_next)
        #print(p_int)
        if p_int.geom_type=='Point':
            line_current=LineString((list(line_current.coords)[0], (p_int.x, p_int.y)))
            line_next=LineString(((p_int.x, p_int.y), list(line_next.coords)[1]))
            return (line_current, line_next)
    # Если отрезки не имеют пересечения, то новая геометрия - с общей вершиной в точке пересечения прямых продолжающих отрезки
    # Точка пересечения должна лежать в окне между ближашйими вершинами отрезков (cur - конца отрезка, next - начала отрезка)
    else:
        x, y = symbols('x, y')
        eq_cur=Equation(line_current)
        eq_next=Equation(line_next)
        p_int, =linsolve([eq_cur.get_straight(), eq_next.get_straight()], (x, y))
        bounds=MultiPoint((shapely.geometry.Point(eq_cur.p2), shapely.geometry.Point(eq_next.p1))).bounds
        test_distance1=float(shapely.geometry.Point(eq_cur.p2).distance(shapely.geometry.Point(eq_cur.p1)))
        test_distance2=float(shapely.geometry.Point(eq_cur.p2).distance(shapely.geometry.Point(eq_next.p1)))
        distance=max([test_distance1, test_distance2])
        bbox=box(*bounds).buffer(distance)
        #print(shapely.geometry.Point(p_int))
        #print(bbox)
        #print(shapely.geometry.Point(eq_cur.p2))
        #if shapely.geometry.Point(eq_cur.p2).within(bbox) and shapely.geometry.Point(p_int).within(bbox) and shapely.geometry.Point(eq_next.p1).within(bbox):
        if shapely.geometry.Point(p_int).within(bbox):
            #print('straightlines intersect')
            line_current=LineString((list(line_current.coords)[0], (p_int[0], p_int[1])))
            line_next=LineString(((p_int[0], p_int[1]), list(line_next.coords)[1]))
            return (line_current, line_next)
        else:
            return None
    '''
gdf=gpd.read_file('tests_offset_recover.gpkg')
uniq='00017'
gdf_origin=gdf[gdf['origin_id']==uniq]
gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
lines=list(gdf_origin.geometry)[:] # correct sort

origin_geom=[]
first=lines.pop(0)
line=lines.pop(0)
first, second=flip_segments(first, line, first=True)
origin_geom.append(list(first.coords)[0])
origin_geom.append(list(line.coords)[0])
origin_geom.append(list(line.coords)[1])
lines = list(filter(lambda x: (x.length>200), lines))
while len(lines)>2:
    line_current = LineString((origin_geom[-2], origin_geom[-1]))
    line_next=lines[0]
    line_current, line_next = flip_segments(line_current, line_next)
    solved=segment_solver(line_current, line_next)
    #print('current', line_current, line_next)
    line_current1 = LineString((origin_geom[-2], origin_geom[-1]))
    line_next1=lines[1]
    line_current1, line_next1 = flip_segments(line_current1, line_next1)
    solved_test1=segment_solver(line_current1, line_next1)
    #print('test', line_current1, line_next1)
    #print(origin_geom)
    if solved is not None:
        line_current, line_next = solved
        if solved_test1 is not None:
            line_current1, line_next1 = solved_test1

            p_test = list(line_current.coords)[0]
            p_int = list(line_next.coords)[0]
            p_int1 = list(line_next1.coords)[0]
            #print('test1', LineString((p_test, p_int)), LineString((p_test, p_int1)))
            if LineString((p_test, p_int)).length<LineString((p_test, p_int1)).length:
                #print('test false')
                origin_geom.pop()
                origin_geom.pop()
                lines.pop(0)
                if list(line_current.coords)[0] not in origin_geom:
                    origin_geom.append(list(line_current.coords)[0])
                if list(line_current.coords)[1] not in origin_geom:
                    origin_geom.append(list(line_current.coords)[1])
                if list(line_next.coords)[1] not in origin_geom:
                    origin_geom.append(list(line_next.coords)[1])
            else:
                #print('test true')
                #line_current, line_next = line_current1, line_next1
                origin_geom.pop()
                origin_geom.pop()
                lines.pop(0)
                lines.pop(0)
                if list(line_current1.coords)[0] not in origin_geom:
                    origin_geom.append(list(line_current1.coords)[0])
                if list(line_current1.coords)[1] not in origin_geom:
                    origin_geom.append(list(line_current1.coords)[1])
                if list(line_next1.coords)[1] not in origin_geom:
                    origin_geom.append(list(line_next1.coords)[1])
        else:
            origin_geom.pop()
            origin_geom.pop()
            lines.pop(0)
            if list(line_current.coords)[0] not in origin_geom:
                origin_geom.append(list(line_current.coords)[0])
            if list(line_current.coords)[1] not in origin_geom:
                origin_geom.append(list(line_current.coords)[1])
            if list(line_next.coords)[1] not in origin_geom:
                origin_geom.append(list(line_next.coords)[1])
    else:
        origin_geom.pop()
        continue
LineString(origin_geom)
# %%
print(LineString(origin_geom))

# %%'''