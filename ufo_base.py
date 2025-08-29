
# ufo_base.py
# Step 1: UFO model, ground, camera, movement

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time

WIN_W, WIN_H = 1000, 800
ASPECT = WIN_W / WIN_H

fovY = 90
cam_pos = [0.0, -300.0, 160.0]
cam_look = [0.0, 0.0, 40.0]

GROUND_SIZE = 1200

ufo_pos = [0.0, 0.0, 60.0]
ufo_yaw = 0.0
ufo_speed = 140.0
ufo_turn_speed = 100.0
hover_amp = 6.0
hover_speed = 2.0

def draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    # white text in screen coords
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_ground():
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.14, 0.18)  # dark tiles
    s = GROUND_SIZE/2
    glVertex3f(-s, -s, 0)
    glVertex3f( s, -s, 0)
    glVertex3f( s,  s, 0)
    glVertex3f(-s,  s, 0)
    glEnd()

    # grid lines
    glLineWidth(1)
    glColor3f(0.25, 0.28, 0.33)
    glBegin(GL_LINES)
    step = 60
    for x in range(-int(s), int(s)+1, step):
        glVertex3f(x, -s, 0); glVertex3f(x, s, 0)
    for y in range(-int(s), int(s)+1, step):
        glVertex3f(-s, y, 0); glVertex3f(s, y, 0)
    glEnd()

def draw_ufo():
    glPushMatrix()
    glTranslatef(*ufo_pos)
    glRotatef(ufo_yaw, 0,0,1)

    # gentle spin for style
    glRotatef((time.time()*30)%360, 0,0,1)

    # Base disk
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.75)
    glScalef(1.6, 1.6, 0.25)
    glutSolidSphere(30, 28, 18)
    glPopMatrix()

    # Rim (torus)
    glColor3f(0.85, 0.85, 0.9)
    glutSolidTorus(5, 35, 24, 32)

    # Dome
    glPushMatrix()
    glTranslatef(0,0,18)
    glColor3f(0.55, 0.75, 0.95)
    glutSolidSphere(16, 20, 16)
    glPopMatrix()

    glPopMatrix()

def setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, -300.0, 500.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9,0.9,0.9,1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR,(0.5,0.5,0.5,1.0))

def setup_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(fovY, ASPECT, 0.1, 5000.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
              cam_look[0], cam_look[1], cam_look[2],
              0,0,1)
