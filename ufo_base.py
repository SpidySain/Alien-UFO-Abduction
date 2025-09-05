# ufo_base.py
# Step 1: UFO model, ground, camera, movement

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time

# ---------------- Window / Camera ----------------
WIN_W, WIN_H = 1000, 800
ASPECT = WIN_W / WIN_H

fovY = 90
cam_pos = [0.0, -300.0, 160.0]
cam_look = [0.0, 0.0, 40.0]

# ---------------- Ground ----------------
GROUND_SIZE = 1200

# ---------------- UFO ----------------
ufo_pos = [0.0, 0.0, 60.0]
ufo_yaw = 0.0
ufo_speed = 140.0
ufo_turn_speed = 100.0
hover_amp = 6.0
hover_speed = 2.0

def draw_ground():
    """Dark ground plane with grid lines"""
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.14, 0.18)
    s = GROUND_SIZE / 2
    glVertex3f(-s, -s, 0)
    glVertex3f(s, -s, 0)
    glVertex3f(s, s, 0)
    glVertex3f(-s, s, 0)
    glEnd()

    # Grid lines
    glLineWidth(1)
    glColor3f(0.25, 0.28, 0.33)
    glBegin(GL_LINES)
    step = 60
    for x in range(-int(s), int(s) + 1, step):
        glVertex3f(x, -s, 0)
        glVertex3f(x, s, 0)
    for y in range(-int(s), int(s) + 1, step):
        glVertex3f(-s, y, 0)
        glVertex3f(s, y, 0)
    glEnd()
    glEnable(GL_LIGHTING)


# ---------------- UFO Model ----------------
# ---------------- UFO Model ----------------
def draw_ufo_opaque():
    """Draw only opaque parts: base, rim, dome"""
    glPushMatrix()
    glTranslatef(*ufo_pos)
    glRotatef(ufo_yaw, 0, 0, 1)
    glRotatef((time.time() * 30) % 360, 0, 0, 1)  # gentle spin

    # Base body (squashed sphere)
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.75)  # metallic gray
    glScalef(1.6, 1.6, 0.25)
    glutSolidSphere(30, 28, 18)
    glPopMatrix()

    # Rim (torus ring)
    glColor3f(0.85, 0.85, 0.9)
    glutSolidTorus(5, 35, 24, 32)

    # Dome (cockpit glass)
    glPushMatrix()
    glTranslatef(0, 0, 18)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.55, 0.75, 0.95, 0.4)  # <-- 40% opacity
    glutSolidSphere(16, 20, 16)
    glDisable(GL_BLEND)

    glPopMatrix()

    # Bottom lights (red-orange glow)
    for angle in range(0, 360, 60):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(20, 0, -6)
        glColor3f(1.0, 0.3, 0.2)
        glutSolidSphere(2.5, 12, 12)
        glPopMatrix()

    glPopMatrix()


def draw_ufo_windows():
    glPushMatrix()

    # Disable lighting so windows glow
    glDisable(GL_LIGHTING)

    # Enable transparency blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    # Force windows to render on top of the dome
    glDepthMask(GL_FALSE)   # <-- Ignore depth test for writing
    glDisable(GL_DEPTH_TEST)

    for angle in range(0, 360, 45):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(36, 0, 5)
        glColor4f(0.2, 0.8, 1.0, 0.8)  # Cyan windows, 80% opacity
        glutSolidSphere(3, 16, 16)
        glPopMatrix()

    # Restore depth state
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    glPopMatrix()



def draw_ufo():
    draw_ufo_opaque()      # Body + dome
    draw_ufo_windows()     # Windows (always last)


# ---------------- Lighting ----------------
def setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, -300.0, 500.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.15, 0.15, 0.15, 1.0))

    # allow glColor to affect materials
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # shiny highlights
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)


# ---------------- Camera ----------------
def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, ASPECT, 0.1, 5000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        cam_pos[0], cam_pos[1], cam_pos[2],
        cam_look[0], cam_look[1], cam_look[2],
        0, 0, 1
    )
