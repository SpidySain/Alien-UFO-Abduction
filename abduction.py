
# abduction.py
# Step 3: humans + abduction + scoring

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time, random

WIN_W, WIN_H = 1000, 800

humans = []
HUMAN_COUNT = 12
score = 0

def spawn_humans(radius=500):
    global humans
    humans = []
    for i in range(HUMAN_COUNT):
        ang = random.random()*math.tau
        r = random.uniform(60, radius)
        x = math.cos(ang)*r
        y = math.sin(ang)*r
        humans.append(dict(x=x, y=y, z=0.0, lifted=0.0, abducted=False))

def draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_human(h):
    glPushMatrix()
    glTranslatef(h['x'], h['y'], h['z'] + h['lifted'])
    glColor3f(0.9, 0.8, 0.7)
    glPushMatrix()
    glTranslatef(0,0,6)
    gluCylinder(gluNewQuadric(), 2.0, 2.0, 12.0, 8, 1)
    glPopMatrix()
    glColor3f(0.95, 0.85, 0.7)
    glTranslatef(0,0,18)
    glutSolidSphere(3.5, 10, 10)
    glPopMatrix()

def draw_humans():
    for h in humans:
        if not h['abducted']:
            draw_human(h)
