from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time, random
import city
import ufo_base

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