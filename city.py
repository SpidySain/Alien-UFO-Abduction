from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import ufo_beam 
import ufo_base 

# Parameter
CHUNK_SIZE = 200 
BUILDINGS_PER_CHUNK = 15 
TREES_PER_CHUNK = 10     

# Track generated chunks to avoid duplicates
generated_chunks = set()
buildings = []
trees = []

# Random generator seed (can be fixed for consistency)
rng = random.Random(42)

def chunk_key(x, z):
    """Get the chunk grid coordinate for a world position."""
    cx = int(x // CHUNK_SIZE)
    cz = int(z // CHUNK_SIZE)
    return (cx, cz)

def generate_chunk(cx, cz):
    """Generate buildings and trees in a given chunk."""
    global buildings, trees

    x_start = cx * CHUNK_SIZE
    z_start = cz * CHUNK_SIZE
    x_end = x_start + CHUNK_SIZE
    z_end = z_start + CHUNK_SIZE

    # Generate random buildings
    for _ in range(BUILDINGS_PER_CHUNK):
        bx = rng.uniform(x_start, x_end)
        bz = rng.uniform(z_start, z_end)
        w = rng.randint(20, 40)
        d = rng.randint(20, 40)
        h = rng.randint(20, int(ufo_beam.altitude_fly - 35))
        buildings.append((bx, bz, w, d, h))

    # Generate random trees
    for _ in range(TREES_PER_CHUNK):
        tx = rng.uniform(x_start, x_end)
        tz = rng.uniform(z_start, z_end)
        trees.append((tx, tz))

def init_city():
    """Initialize the starting city area around (0,0)."""
    global generated_chunks, buildings, trees
    buildings = []
    trees = []
    generated_chunks.clear()

    # Pre-generate central area
    center_range = 2
    for dx in range(-center_range, center_range + 1):
        for dz in range(-center_range, center_range + 1):
            generate_chunk(dx, dz)
            generated_chunks.add((dx, dz))

def update_city():
    """Add new chunks based on UFO position."""
    global generated_chunks

    ufo_x = ufo_base.ufo_pos[0]
    ufo_z = ufo_base.ufo_pos[1]

    # Determine current chunk
    center_cx = int(ufo_x // CHUNK_SIZE)
    center_cz = int(ufo_z // CHUNK_SIZE)

    radius = 3

    # Generate nearby chunks if not already done
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            cx = center_cx + dx
            cz = center_cz + dz
            if (cx, cz) not in generated_chunks:
                generate_chunk(cx, cz)
                generated_chunks.add((cx, cz))

def draw_ground():
    """Draw infinite ground with repeating grid."""
    glColor3f(0.12, 0.14, 0.18)
    glBegin(GL_QUADS)
    s = 10000
    glVertex3f(-s, -s, 0)
    glVertex3f( s, -s, 0)
    glVertex3f( s,  s, 0)
    glVertex3f(-s,  s, 0)
    glEnd()

    # Grid lines
    glLineWidth(1)
    glColor3f(0.25, 0.28, 0.33)
    glBegin(GL_LINES)
    step = 60
    for x in range(-s, s + 1, step):
        glVertex3f(x, -s, 0)
        glVertex3f(x, s, 0)
    for z in range(-s, s + 1, step):
        glVertex3f(-s, z, 0)
        glVertex3f(s, z, 0)
    glEnd()

def draw_buildings():
    glColor3f(0.5, 0.5, 0.7)
    for (x, y, w, d, h) in buildings:
        glPushMatrix()
        glTranslatef(x, y, h / 2)
        glScalef(w, d, h)
        glutSolidCube(1.0)
        glPopMatrix()

def draw_trees():
    for (x, y) in trees:
        # Trunk
        glColor3f(0.55, 0.27, 0.07)
        glPushMatrix()
        glTranslatef(x, y, 5)
        glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 2, 2, 10, 8, 8)
        glPopMatrix()

        # Leaves
        glColor3f(0.0, 0.6, 0.0)
        glPushMatrix()
        glTranslatef(x, y, 15)
        glutSolidSphere(6, 12, 12)
        glPopMatrix()

def draw_city():
    """Main draw function — updates city then renders."""
    update_city()
    draw_ground()
    draw_buildings()
    draw_trees()