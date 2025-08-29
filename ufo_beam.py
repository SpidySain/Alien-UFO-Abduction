
# ufo_beam.py
# Step 2: landing + beam

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time
import ufo_base

# WIN_W, WIN_H = 1000, 800
# ufo_pos = [0.0, 0.0, 60.0]
# ufo_yaw = 0.0
# ufo_speed = 140.0
# ufo_turn_speed = 100.0
# hover_amp = 6.0
# hover_speed = 2.0
last_time = None
keys_down = set()

beam_active = False
beam_cooldown = 3.0
beam_cooldown_left = 0.0
beam_angle_deg = 18.0

ufo_state = "flying"
altitude_fly = 60.0
altitude_land = 18.0

def draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, ufo_base.WIN_W, 0, ufo_base.WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in s: glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_beam():
    pos = ufo_base.ufo_pos
    yaw = ufo_base.ufo_yaw
    if not beam_active: return
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTranslatef(pos[0], pos[1], 0.0)
    h = max(1.0, pos[2])
    top_r = 6.0
    bottom_r = math.tan(math.radians(beam_angle_deg))*h + top_r
    glColor4f(1.0, 0.95, 0.4, 0.45)
    quad = gluNewQuadric()
    glTranslatef(0,0,0.1)
    glRotatef(yaw, 0,0,1)
    gluCylinder(quad, bottom_r, top_r, h-0.1, 24, 1)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()


def try_toggle_beam():
    global beam_active, beam_cooldown_left
    if beam_active:
        beam_active = False
        beam_cooldown_left = beam_cooldown
    else:
        if beam_cooldown_left == 0.0:
            beam_active = True

# def reshape(w, h):
#     global WIN_W, WIN_H, ASPECT
#     WIN_W, WIN_H = max(1,w), max(1,h)
#     ASPECT = WIN_W/float(WIN_H)
#     glViewport(0,0,WIN_W,WIN_H)