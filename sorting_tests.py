from shapely import from_wkt
from shapely.geometry import MultiLineString, LineString
import math
import pandas as pd
from operator import itemgetter
wkt='MultiLineString ((661649.79104394 6635517.19294568, 664227.55918609 6635196.88195656),(664243.70611254 6635245.10146993, 661646.11600118 6635567.96471892),(664217.30864214 6635147.77912126, 661651.55405597 6635466.27027538))'
multiline = from_wkt(wkt)
segments=list(multiline.geoms)

class Bentley_Ottman:
    def __init__(self, segments):
        self.segments=[list(x.coords) for x in segments]
    def test(self):
        return self.segments
    def sweepingline(self, flipped, dir):
        flag=None
        sorted=None
        df = pd.DataFrame(flipped, columns=['line_p1', 'line_p2'])
        df['p1_x']=[df['line_p1'][i][0] for i in range(len(df))]
        df['p1_y']=[df['line_p1'][i][1] for i in range(len(df))]
        df['p2_x']=[df['line_p2'][i][0] for i in range(len(df))]
        df['p2_y']=[df['line_p2'][i][1] for i in range(len(df))]

        if dir>=45 and dir<135:
            flag='Ox_left'
            df.sort_values(by='p1_x', ascending=False, inplace=True)
        elif dir>=135 and dir<225:
            flag='Oy_down'
            df.sort_values(by='p1_y', ascending=False, inplace=True)
        elif dir>=225 and dir<315:
            flag='Ox_right'
            df.sort_values(by='p1_x', ascending=True, inplace=True)
        elif dir>=315 and (dir<45 or dir+360<405):
            flag='Oy_up'
            df.sort_values(by='p1_y', ascending=True, inplace=True)
        #print(df)
        df=df.reset_index(drop=True)
        sorted=[[df['line_p1'][i], df['line_p2'][i]] for i in range(len(df))]
        return sorted
    def flip_segments(self):
        base_geom=self.segments[0]
        geoms_slice=self.segments.copy()
        geoms_slice.remove(base_geom)
        l1=base_geom
        for geom_slice in geoms_slice:
            l2=geom_slice
            dx1, dy1 = l1[1][0]-l1[0][0], l1[1][1]-l1[0][1]
            dx2, dy2 = l2[1][0]-l2[0][0], l2[1][1]-l2[0][1]
            r1=math.atan2(dy1,dx1)
            r2=math.atan2(dy2,dx2)
            if dx1>0 and dy1>0:
                a1=r1
            elif dx1>0 and dy1<0:
                a1=360-r1
            elif dx1<0 and dy1>0:
                a1=180-r1
            elif dx1<0 and dy1<0:
                a1=r1-180
            
            if dx2>0 and dy2>0:
                a2=r2
            elif dx2>0 and dy2<0:
                a2=360-r2
            elif dx2<0 and dy2>0:
                a2=180-r2
            elif dx2<0 and dy2<0:
                a2=r2-180
            #print(a1, a2)
            if abs(a1-a2)>5:
                l2=[l2[1], l2[0]]
            geom_slice_index=geoms_slice.index(geom_slice)
            geoms_slice[geom_slice_index]=l2
        geoms_slice.append(base_geom)
        return geoms_slice, a2
def parallel_offsetting(lines, distance):
    offset_lines=[]
    if len(lines)%2==0:
        d=distance
        # CHECK FOR 4 LINES IN HALLWAY
        for i in range(len(lines), 1, -1):
            print(i)
            left=LineString(lines[i]).parallel_offset(distance=d*i, side='left')
            offset_lines.append(left)
        for i in range(1, len(lines)//2+1, 1):
            right=LineString(lines[i]).parallel_offset(distance=d*i, side='right')
            offset_lines.append(right)
    elif len(lines)%2!=0:
        d=distance
        for i in range(len(lines)//2):
            d=d*(i+1)
            print(lines[i], d)
            left=LineString(lines[i]).parallel_offset(distance=d, side='left')
            offset_lines.append(left)
        d=distance
        print(lines[len(lines)//2])
        middle=LineString(lines[len(lines)//2])
        offset_lines.append(middle)
        for i in range(len(lines)//2):
            d=d*(i+1)
            print(lines[len(lines)-i-1], d)
            right=LineString(lines[len(lines)-i-1]).parallel_offset(distance=d, side='right')
            offset_lines.append(right)
    return offset_lines
sweepingline=Bentley_Ottman(segments)
flipped, dir = sweepingline.flip_segments()
#print(dir)
sorted=sweepingline.sweepingline(flipped, dir)
print([LineString(sorted[i]) for i in range(len(sorted))])
print(parallel_offsetting(sorted, 100))

