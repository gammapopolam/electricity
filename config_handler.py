import math
def config(scale):
    Tgraph=0.02*scale/100 # 5m for 25000
    print(f'Tgraph: {Tgraph}')
    default_hallway_offset=100 # расстояние между нитками коридора
    offset = (default_hallway_offset*Tgraph/4) # 125m for 25000
    buffer = (default_hallway_offset*2*Tgraph/4)
    default_angle=3 # 3deg for 25000
    angle=math.ceil(math.sqrt(default_angle*Tgraph/2))
    return offset, buffer, angle