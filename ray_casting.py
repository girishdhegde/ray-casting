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

    def draw(self, canvas, color=(255, 255, 255), ends=False):
        canvas = canvas.copy()
        if ends:
            canvas = self.pt1.draw(canvas)
            canvas = self.pt2.draw(canvas)
        cv2.line(canvas, (self.pt1.screen_pos[0], canvas.shape[0]-self.pt1.screen_pos[1]), 
                 (self.pt2.screen_pos[0], canvas.shape[0]-self.pt2.screen_pos[1]), color=color)
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
        self.end = point((int(2000*self.i), int(2000*self.j)),
                          origin=self.pos.origin)
        self.vec = vector(self.pos, self.end)

    def draw(self, canvas, color=(255, 255, 255), ends=True):
        canvas = canvas.copy()
        canvas = self.vec.draw(canvas, color, ends=ends)
        return canvas

    def cast(self, canvas, vectors=(), color=(255, 255, 255)):
        minDist = float('inf')
        end     = None
        canvas  = self.pos.draw(canvas, color=color)
        hit     = False
        for v in vectors:
            intr = v.intersects(self.vec)
            if intr:
                hit  = True
                dist = self.pos.distance(intr)
                if dist < minDist:
                    minDist = dist
                    end     = intr
        if hit:
            canvas = vector(self.pos, end).draw(canvas, color=color)
        return canvas

    def __str__(self):
        return f'ray at {self.pos.pos} and direction {self.dir} degree'


if __name__ == '__main__':
    canvas = np.ones((700, 1200, 3), dtype=np.uint8) * 0
    vectors = []
    for _ in range(15):
        p1 = point((np.random.randint(-600, 600), np.random.randint(-350, 350)), (600, 350))
        p2 = point((np.random.randint(-600, 600), np.random.randint(-350, 350)), (600, 350))
        v  = vector(p1, p2)
        vectors.append(v)
        canvas = v.draw(canvas, color=(0, 50, 255), ends=False)

    for j in range(-200, 200, 6):
        screen = canvas.copy()
        for angle in range(0, 360, 3):
            r      = ray(point((j, j), (600, 350)), dir=angle)
            screen = r.cast(screen, vectors, color=(255, 255, 255))
            # cv2.imshow('ray casting', screen)
            # cv2.waitKey(0)
        cv2.imshow('ray casting', screen)
        cv2.waitKey(100)
    cv2.destroyAllWindows()