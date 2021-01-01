import numpy as np
import cv2

class point:
    def __init__(self, pos, origin=(0, 0)):
        self.pos = pos
        self.origin = origin
        self.screen_pos = (self.pos[0]+self.origin[0], self.pos[1]+self.origin[1])

    def draw(self, canvas, r=3, color=(255, 255, 255)):
        canvas = canvas.copy()
        cv2.circle(canvas, (self.screen_pos[0], canvas.shape[0]-self.screen_pos[1]), 
                   r, color=color, thickness=-1)
        return canvas
    
    def distance(self, other):
        assert isinstance(other, point), 'non point type detected'
        return np.sqrt((self.pos[0]-other.pos[0])**2 + (self.pos[1]-other.pos[1])**2) 
    

    
    def __add__(self, other):
        assert isinstance(other, point), 'non point type detected'
        return point((self.pos[0]+other.pos[0], self.pos[1]+other.pos[1]), self.origin) 
    
    def __sub__(self, other):
        assert isinstance(other, point), 'non point type detected'
        return point((self.pos[0]-other.pos[0], self.pos[1]-other.pos[1]), self.origin)
    
    def __mul__(self, other):
        assert isinstance(other, point), 'non point type detected'
        return point((self.pos[0]*other.pos[0], self.pos[1]*other.pos[1]), self.origin)

    def __str__(self):
        return f'point at {self.pos}'

class vector:
    def __init__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2

    def draw(self, canvas, color=(255, 255, 255), ends=False, t=1):
        canvas = canvas.copy()
        if ends:
            canvas = self.pt1.draw(canvas)
            canvas = self.pt2.draw(canvas)
        cv2.line(canvas, (self.pt1.screen_pos[0], canvas.shape[0]-self.pt1.screen_pos[1]), 
                 (self.pt2.screen_pos[0], canvas.shape[0]-self.pt2.screen_pos[1]), color=color, thickness=t)
        return canvas

    def intersects(self, other):
        assert isinstance(other, vector), 'non vector type detected'
        dif1 = self.pt1 - self.pt2
        dif2 = other.pt1 - other.pt2
        dif3 = self.pt1 - other.pt1
        dnm  =  dif1.pos[0] * dif2.pos[1] - dif1.pos[1] * dif2.pos[0]
        if dnm != 0:
            t    = (dif3.pos[0] * dif2.pos[1] - dif3.pos[1] * dif2.pos[0]) / dnm
            u    = -(dif1.pos[0] * dif3.pos[1] - dif1.pos[1] * dif3.pos[0]) / dnm
            if 0 <= t <= 1 and 0 <= u <= 1.0:
                px = self.pt1.pos[0] - t * dif1.pos[0]
                py = self.pt1.pos[1] - t * dif1.pos[1]
                return point((int(px), int(py)), origin=self.pt1.origin)
            else:
                return False
        else:
            return False

    def __add__(self, other):
        assert isinstance(other, vector), 'non vector type detected'
        return vector(self.pt1, other.pt2) 
    

    def __str__(self):
        return f'vector with start {self.pt1} and end {self.pt2}'

class ray:
    def __init__(self, pos, dir=0):
        self.pos = pos
        self.dir = dir
        self.i   = np.cos(np.deg2rad(self.dir))
        self.j   = np.sin(np.deg2rad(self.dir))
        self.end = point((int(1000*self.i), int(1000*self.j)),
                          origin=self.pos.origin)
        self.vec = vector(self.pos, self.end)

    def draw(self, canvas, color=(255, 255, 255), ends=True):
        canvas = canvas.copy()
        canvas = self.vec.draw(canvas, color, ends=ends)
        return canvas

    def cast(self, canvas, vectors=(), color=(255, 255, 255), angle=0):
        minDist = float('inf')
        end     = None
        canvas  = self.pos.draw(canvas, color=color)
        self.hit     = False
        for v in vectors:
            intr = v.intersects(self.vec)
            if intr:
                self.hit  = True
                dist = self.pos.distance(intr)
                dist = dist * np.cos(np.deg2rad(abs(angle)))
                if dist < minDist:
                    minDist = dist
                    end     = intr
        if self.hit:
            self.mdist = minDist
            canvas = vector(self.pos, end).draw(canvas, color=color)
        return canvas

    def __str__(self):
        return f'ray at {self.pos.pos} and direction {self.dir} degree'


class scene:
    def __init__(self, walls, size, origin=(0, 0), wall_h=None, wall_min=None, wall_clr=(255, 255, 255)):
        self.canvas = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        self.world  = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        self.walls  = [vector(point(wall[0], origin), point(wall[1], origin)) for wall in walls]
        self.origin = origin
        self.w_clr  = wall_clr
        
        if wall_h:
            self.wall_h = wall_h // 2
        else:
            self.wall_h = size[1] // 4
        if wall_min:
            self.wall_min = wall_min
        else:
            self.wall_min = size[1] // 16

        for v in self.walls:
            self.canvas = v.draw(self.canvas, color=wall_clr, ends=False, t=5)

        # floor and ceiling
        rows = self.world.shape[0]
        mid  = rows // 2
        for row in range(1, mid):
            clr = int(np.interp(row, [0, mid], [255, 0]))
            self.world[rows - 1 - row] = (0, 0, clr)
            self.world[row] = (clr, 0, 0)
        cv2.putText(self.world, 'By girish d hegde', (size[0]-130, size[1]-10),
                    fontFace=3, fontScale=0.4, color=(0, 50, 255))
        cv2.putText(self.canvas, 'use "a, s, d, w" to control agent', (10, 20),
                    fontFace=3, fontScale=0.4, color=(50, 50, 50))
    
    def draw(self, agent_pos=[(0, 0)], ray_clr=(0, 200, 255), delay=10, fov=360, facing=0, delta=2):
        for pos in agent_pos:
            screen = self.canvas.copy()
            for angle in range(facing-fov//2, facing+fov//2, delta):
                r      = ray(point(pos, self.origin), dir=angle)
                screen = r.cast(screen, self.walls, color=ray_clr)
            cv2.imshow('ray casting', screen)
            cv2.waitKey(delay)
        cv2.destroyAllWindows()
    
    def draw_wall(self, world, pos, dist, fov=360, delta=1):
        width = delta * world.shape[1] // fov
        col   = pos * width
        dist2 = dist**2
        shp2  = (world.shape[0])**2
        clr0  = int(np.interp(dist2, [0, shp2], [self.w_clr[0], 0]))
        clr1  = int(np.interp(dist2, [0, shp2], [self.w_clr[1], 0]))
        clr2  = int(np.interp(dist2, [0, shp2], [self.w_clr[2], 0]))
        hgt   = int(np.interp(dist, [0, world.shape[0]], [self.wall_h, self.wall_min]))
        cv2.rectangle(world, (col, world.shape[0]-self.origin[1]-hgt),
                      (col+width, world.shape[0]-self.origin[1]+hgt), 
                      color=(clr0, clr1, clr2), thickness=-1) 
             
    def render(self, agent_pos=[(0, 0)], ray_clr=(0, 200, 255), delay=10, fov=360, facing=0, delta=2):
        for pos in agent_pos:
            screen = self.canvas.copy()
            world  = self.world.copy()
            for p, angle in enumerate(range(facing+fov//2, facing-fov//2, -delta)):
                r      = ray(point(pos, self.origin), dir=angle)
                screen = r.cast(screen, self.walls, color=ray_clr, angle=angle-facing)
                if r.hit:
                    self.draw_wall(world, p, r.mdist, fov=fov, delta=delta)
            cv2.imshow('2D ray casting', screen)
            cv2.imshow('3D ray casting', world)

if __name__ == '__main__':   
    # walls = [[(-300,  175), ( 300,  175)],
    #          [(-300, -175), ( 300, -175)],
    #          [(-300, -175), (-300,  175)],
    #          [( 300, -175), ( 300,  175)],
    #          [(   0, -100), (   0,   80)],
    #          [(   0,   25), (-175,   25)],
    #          [( 150,    0), ( 175,    0)],
    #          [(  50,  100), ( 175,  100)],
    #          [( 175,    0), ( 175,  100)],
    #          [(-200, -175), (-100, -175)]]

    walls = [[(-300,  175), ( 300,  175)],
             [(-300, -175), ( 300, -175)],
             [(-300, -175), (-300,  175)],
             [( 300, -175), ( 300,  175)],

             [( -25,  100), (  25,  100)],
             [( -25,   50), (  25,   50)],
             [(  25,   50), (  25,  100)],
             [( -25,   50), ( -25,  100)],

             [( -25, -100), (  25, -100)],
             [( -25, -175), (  25, -175)],
             [(  25, -100), (  25, -175)],
             [( -25, -100), ( -25, -175)],

             [( 250, -100), ( 250,  100)],
             [( 150, -100), ( 250, -100)],
             [( 150,  100), ( 250,  100)],
             [( 150,    0), ( 150,  100)],
             [( 150,  -50), ( 150, -100)],

            [( -150,  -50), (-150, -175)],
            [( -150,  -50), (-250,  -50)],

            [( -300,   50), (-100,   50)]]

    scene1 = scene(walls, (600, 350), (300, 175))
    pos    = [[10, 0]]
    offset = 10
    off_f  = 10
    facing = 0
    fov    = 120

    while True:
        scene1.render(pos, delay=0, fov=fov, facing=facing, delta=1)
        key = cv2.waitKey()
        # esc
        if key == 27:
            break

        # 's' cursor - backward
        elif key == 115:
            pos[0][1] -= int(np.sin(np.deg2rad(facing)) * offset)
            pos[0][0] -= int(np.cos(np.deg2rad(facing)) * offset)
        # 'w' cursor - forward
        elif key == 119:
            pos[0][1] += int(np.sin(np.deg2rad(facing)) * offset)
            pos[0][0] += int(np.cos(np.deg2rad(facing)) * offset)

        # 'd' cursor - rotate right
        elif key == 100:
            facing -= off_f
        # 'a' cursor - rotate left
        elif key == 97:
            facing += off_f

        # '+'
        elif key == 43:
            fov += offset
        # '-'
        elif key == 45:
            fov -= offset

    cv2.destroyAllWindows()
