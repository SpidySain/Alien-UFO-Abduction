from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time
import ufo_base

last_time = None
keys_down = set()

# ---------------- Beam Config ----------------
beam_active = False
beam_cooldown = 5.0
beam_cooldown_left = 0.0

beam_duration = 10.0   # <-- Beam stays active for 10 seconds
beam_timer = 0.0       # countdown timer for active time
beam_angle_deg = 18.0

# ---------------- UFO States ----------------
ufo_state = "flying"
altitude_fly = 160
altitude_land = 18.0


def draw_beam():
    pos = ufo_base.ufo_pos
    yaw = ufo_base.ufo_yaw
    if not beam_active:
        return
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTranslatef(pos[0], pos[1], 0.0)
    h = max(1.0, pos[2])
    top_r = 6.0
    bottom_r = math.tan(math.radians(beam_angle_deg)) * h + top_r
    glColor4f(1.0, 0.95, 0.4, 0.45)
    quad = gluNewQuadric()
    glTranslatef(0, 0, 0.1)
    glRotatef(yaw, 0, 0, 1)
    gluCylinder(quad, bottom_r, top_r, h - 0.1, 24, 1)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()


def try_toggle_beam():
    """Activate beam if ready. Beam runs for beam_duration, then cooldown."""
    global beam_active, beam_cooldown_left, beam_timer
    if not beam_active and beam_cooldown_left == 0.0:
        beam_active = True
        beam_timer = beam_duration   # start countdown


def update_beam(dt):
    """Update beam timer and cooldown each frame."""
    global beam_active, beam_cooldown_left, beam_timer
    if beam_active:
        beam_timer -= dt
        if beam_timer <= 0:
            beam_active = False
            beam_cooldown_left = beam_cooldown
    elif beam_cooldown_left > 0:
        beam_cooldown_left = max(0.0, beam_cooldown_left - dt)
