import pygame 
import numpy as np
from pygame.locals import *
from objloader import OBJ
from OpenGL.GL import *
from OpenGL.GLU import *
import time
from arduino import Handheld
from pyquaternion import Quaternion

colors = {'red':(1, 0, 0), 'green':(0, 1, 0), 'blue':(0, 0, 1), 'yellow':(1, 1, 0), 'white':(1,1,1),
            'cyan':(0,1, 1), 'magenta':(1,0,1)}

    
def parse_color(color):
    if isinstance(color, str):
        return colors[color]
    return color

def eulerAnglesToRotationMatrix(pitch, yaw, roll) :
    R_x = np.array([[1, 0, 0],
                    [0, np.cos(pitch), -np.sin(pitch)],
                    [0, np.sin(pitch), np.cos(pitch)]])
                    
    R_y = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                    [0, 1, 0],
                    [-np.sin(yaw), 0, np.cos(yaw)]])
                
    R_z = np.array([[np.cos(roll), -np.sin(roll), 0],
                    [np.sin(roll), np.cos(roll), 0],
                    [0, 0, 1]])

    R = np.dot(R_z, np.dot( R_y, R_x ))

    return R

def draw_obj(obj):
    t1 = time.time()
    obj.draw()
    t2 = time.time()
    print(t2-t1)
    glCallList(obj.gl_list)

def rotate(obj, pitch, yaw, roll):
    R = eulerAnglesToRotationMatrix(pitch, yaw, roll)
    obj.vertices = np.dot(obj.vertices, R)


def scale(obj, scale):
    obj.vertices = scale*obj.vertices


class Surface():
    def __init__(self, vertices=None, color=None):
        self.color = parse_color(color)
        if vertices is None:
            self.vertices = 5*np.array([[1, -1, 0], [1, 1, 0], [-1, 1, 0], [-1, -1, 0]])
        else:
            self.vertices = vertices 
        tmp = np.array(list(self.vertices))
        self.center = (np.sum(tmp[:,0]), np.sum(tmp[:,1]), np.sum(tmp[:,2]))
        self.basis = None
    
    def draw(self):
        glEnable(GL_DEPTH_TEST)
        glBegin(GL_QUADS)
        glColor3fv(self.color)
        for vertex in self.vertices:
            glVertex3fv(vertex)
        glEnd()
        self.draw_basis()
    
    def compute_basis(self, width=1):
        p1 = np.array(list(self.vertices[0]))
        p2 = np.array(list(self.vertices[1]))
        p3 = np.array(list(self.vertices[2]))
        v1 = p3 - p1
        v2 = p2 - p1
        v3 = np.cross(v1, v2)
        v2 = np.cross(v3, v1)
        x = Arrow(v1, self.center, color='red', width=width)
        y = Arrow(v2, self.center, color='green', width=width)
        z = Arrow(v3, self.center, color='blue', width=width)
        self.basis = (x, y, z)

    def add_basis(self, width=1):
        if self.basis is None:
            self.compute_basis(width)
        for b in self.basis:
            b.normalize()

    def draw_basis(self, width=1):
        self.add_basis(width)
        for b in self.basis:
            b.draw()

    def rotate(self, pitch, yaw, roll):
        R = eulerAnglesToRotationMatrix(pitch, yaw, roll)
        self.vertices = np.dot(self.vertices - self.center, R) + self.center
        for b in self.basis:
            b.rotate(R)

    def rotate_quaternion(self, quaternion):
        self.vertices = [quaternion.rotate(i) for i in self.vertices]
        for b in self.basis:
            b.rotate_quaternion(quaternion)

class Arrow():
    def __init__(self, vector, base, color=None, width=1):
        self.base = np.array(list(base))
        self.vector = np.array(list(vector))
        self.color = parse_color(color)
        self.width=width
    
    def draw(self):
        p1 = self.base 
        p2 = tuple(self.base + self.vector)
        glLineWidth(self.width)
        glBegin(GL_LINES)
        glColor3fv(self.color)
        glVertex3fv(p1)
        glVertex3fv(p2)
        glEnd()

    def normalize(self):
        self.vector = self.vector/np.linalg.norm(self.vector)

    def rotate(self, R):
        self.vector = np.dot(self.vector - self.base, R) + self.base

    def rotate_quaternion(self, quaternion):
        self.vector = quaternion.rotate(self.vector)

one_deg = np.pi/180

def main():
    pygame.init()
    height = 800
    width = 600
    display = (height, width)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, height/width, 0.1, 50.0)
    glTranslatef(0, 0, -20)
    glRotate(90, 1, 0,0)
    hheld = Handheld(baudrate=115200, port='/dev/ttyUSB0')
    x = []
    quat = None
    while 1:
        s = Surface(color='white', vertices=np.array([[1, -5, 0], [-1, -5, 0], [-1, 5, 0], [1, 5, 0]]))
        t = hheld.get_quaternion()
        
        # if len(t) == 3:
        #     x = t
        
        if len(t) == 4:
            quat = Quaternion(t[0], t[1], t[2], t[3])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        s.add_basis(5)
        # if len(x) == 3:
        #     s.rotate(x[0]*one_deg, x[1]*one_deg, x[2]*one_deg)
        #     s.rotate(x[0]*one_deg, x[1]*one_deg, x[2]*one_deg)
        
        if quat is not None:
            s.rotate_quaternion(quat)

        s.draw()
        print(x)
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

