from sympy.solvers.solveset import linsolve
from shapely import intersects, relate, equals
from shapely.geometry import MultiLineString, LineString
from sympy import *
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

def segment_solver(line_current, line_next):
    # Если отрезки имеют пересечение, то новая геометрия - с общей вершиной в точке пересечения линий
    if line_current.intersects(line_next):
        p_int=line_current.intersection(line_next)
        line_current=LineString((list(line_current)[0], (p_int.x, p_int.y)))
        line_next=LineString(((p_int.x, p_int.y), list(line_next)[1]))
        return (line_current, line_next)
    # Если отрезки не имеют пересечения, то новая геометрия - с общей вершиной в точке пересечения прямых продолжающих отрезки
    # Точка пересечения должна лежать в окне между ближашйими вершинами отрезков (cur - конца отрезка, next - начала отрезка)
    else:
        x, y = symbols('x, y')
        eq_cur=Equation(line_current)
        eq_next=Equation(line_next)
        p_int, =linsolve([eq_cur.get_straight(), eq_next.get_straight()], (x, y))
        dx1=abs(eq_cur.p2[0]-p_int[0])
        dx2=abs(eq_next.p1[0]-p_int[0])
        dy1=abs(eq_cur.p2[1]-p_int[1])
        dy2=abs(eq_next.p1[1]-p_int[1])
        dx=abs(eq_cur.p2[0]-eq_next.p1[0])
        dy=abs(eq_cur.p2[1]-eq_next.p1[1])
        if dx1<dx*2 and dx2<dx*2 and dy1<dy*2 and dy2<dy*2 and dx!=dy:
            line_current=LineString((list(line_current)[0], (p_int.x, p_int.y)))
            line_next=LineString(((p_int.x, p_int.y), list(line_next)[1]))
            return (line_current, line_next)
        else:
            return None