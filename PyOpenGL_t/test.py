import pygame 
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

colors = {'red':(1, 0, 0), 'green':(0, 1, 0), 'blue':(1, 0, 0), 'yellow':(1, 1, 0), 'white':(1,1,1),
            'cyan':(0,1, 1), 'magenta':(1,0,1)}


class Surface():
    def __init__(self, vertices, color=None):
        self.color = color
        if isinstance(self.color, str):
            self.color = colors[color]
        self.vertices = vertices


class Cube():
    def __init__(self, vertices=None, cmap=None):
        if cmap is None:
            cmap = (None, None, None, None, None, None)
        if vertices is None:
            self.vertices = (
                (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
            )
        self.edges = (
                (0, 1), (0, 3), (0, 4), (1, 2), (1, 5), (2, 3), (3, 6), (2, 7), (4, 6), (5, 7), (6, 7), (5, 7)
            )
        self.faces = (
            Surface((0, 1, 2, 3), cmap[0]),Surface((4, 5, 1, 0), cmap[1]), Surface((1, 5, 7, 2), cmap[2]),
            Surface((3, 2, 7, 6), cmap[3]), Surface((4, 0, 3, 6), cmap[4]), Surface((6, 7, 5, 4), cmap[5])
        )
    def draw(self):
        glBegin(GL_LINES)
        glColor3fv((0,0,0))
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        glEnable(GL_DEPTH_TEST)
        glBegin(GL_QUADS)
        for face in self.faces:
            if face.color is not None:
                glColor3fv(face.color)
                for vertex in face.vertices:
                    glVertex3fv(self.vertices[vertex])
        glEnd()


cmap = ('red', 'green', 'yellow', 'white', 'blue', 'magenta')

def main():
    pygame.init()
    height = 800
    width = 600
    display = (height, width)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, height/width, 0.1, 50.0)
    glTranslatef(0, 0, -10)

    while 1:
        glRotatef(1, 1, 1, 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        c = Cube(cmap=cmap)
        c.draw()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

