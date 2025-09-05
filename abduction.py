from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time, random
import city
import ufo_base, ufo_beam

WIN_W, WIN_H = 1000, 800

humans = []
score = 0

# New: Dynamic spawning config
HUMANS_PER_CHUNK = 8
spawned_human_chunks = set()
rng = random.Random(123)

def chunk_key(x, z):
    cx = int(x // city.CHUNK_SIZE)
    cz = int(z // city.CHUNK_SIZE)
    return (cx, cz)

def spawn_humans_in_chunk(cx, cz):
    x_start = cx * city.CHUNK_SIZE
    z_start = cz * city.CHUNK_SIZE
    x_end = x_start + city.CHUNK_SIZE
    z_end = z_start + city.CHUNK_SIZE

    for _ in range(HUMANS_PER_CHUNK):
        x = rng.uniform(x_start, x_end)
        y = rng.uniform(z_start, z_end)
        humans.append({'x': x, 'y': y, 'lifted': 0.0, 'abducted': False})

def spawn_initial_humans():
    global humans, score, spawned_human_chunks
    humans = []
    score = 0
    spawned_human_chunks.clear()

    # Spawn in central chunks
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            spawn_humans_in_chunk(dx, dz)
            spawned_human_chunks.add((dx, dz))

def update_humans():
    for chunk_key in city.generated_chunks:
        if chunk_key not in spawned_human_chunks:
            cx, cz = chunk_key
            spawn_humans_in_chunk(cx, cz)
            spawned_human_chunks.add(chunk_key)

# Keep existing drawing code
def draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    """
    Draw 2D overlay text at window coords (0,0) bottom-left.
    Uses ufo_base.WIN_W / WIN_H so it adapts to window resize.
    """
    # Save enable states so we can restore them exactly
    depth_was = glIsEnabled(GL_DEPTH_TEST)
    light_was = glIsEnabled(GL_LIGHTING)
    tex_was   = glIsEnabled(GL_TEXTURE_2D)

    # Force overlay mode (always on top)
    if depth_was: glDisable(GL_DEPTH_TEST)
    if light_was: glDisable(GL_LIGHTING)
    if tex_was:   glDisable(GL_TEXTURE_2D)

    # Setup orthographic projection matching window coords
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, max(1, int(ufo_base.WIN_W)), 0, max(1, int(ufo_base.WIN_H)))

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Make sure the color is white (or whatever you want)
    glColor3f(1.0, 1.0, 1.0)

    # Draw text — raster pos uses the same coordinate system as the ortho above.
    # Note: y origin is bottom-left, so pass (WIN_H - margin) if you want top-left.
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))

    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    # Restore enable states
    if tex_was:   glEnable(GL_TEXTURE_2D)
    if light_was: glEnable(GL_LIGHTING)
    if depth_was: glEnable(GL_DEPTH_TEST)


def draw_human(h):
    glPushMatrix()
    glTranslatef(h['x'], h['y'], h['lifted'])
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
    update_humans()
    for h in humans:
        if not h['abducted']:
            draw_human(h)


def update_abductions(dt):
    """Update human abductions when beam is active."""
    if not ufo_beam.beam_active:
        return

    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    beam_angle = math.radians(ufo_beam.beam_angle_deg)
    abduction_speed = 140

    # Beam axis = pointing down (negative Z)
    axis = (0.0, 0.0, -1.0)

    for hmn in humans:
        if hmn['abducted']:
            continue

        # Vector from UFO to human (using current lifted height for z)
        dx = hmn['x'] - ufo_x
        dy = hmn['y'] - ufo_y
        dz = hmn['lifted'] - ufo_z  # human below UFO = negative

        if dz < 0:  # must be below UFO
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            if length == 0:
                continue

            # Normalize vector
            vx, vy, vz = dx/length, dy/length, dz/length

            # Dot product with axis (0,0,-1)
            dot = vx*axis[0] + vy*axis[1] + vz*axis[2]
            dot = max(-1.0, min(1.0, dot))  # clamp
            angle = math.acos(dot)

            if angle <= beam_angle:  # Inside cone
                target_height = ufo_z - 40.0
                hmn['lifted'] += abduction_speed * dt

                if hmn['lifted'] >= target_height:
                    hmn['lifted'] = target_height
                    hmn['abducted'] = True
                    global score
                    score += 1
