from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import math, time, random

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



# ---------------- UFO Model ----------------

def draw_ufo_opaque():
    glPushMatrix()
    glTranslatef(*ufo_pos)
    glRotatef(ufo_yaw, 0, 0, 1)
    glRotatef((time.time() * 30) % 360, 0, 0, 1)  

    # Base body (
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.75)  
    glScalef(1.6, 1.6, 0.25)
    glutSolidSphere(30, 28, 18)
    glPopMatrix()

    # Rim 
    glColor3f(0.85, 0.85, 0.9)
    glutSolidTorus(5, 35, 24, 32)

    # Dome 
    glPushMatrix()
    glTranslatef(0, 0, 18)
    glColor4f(0.55, 0.75, 0.95, 0.4)  
    glutSolidSphere(16, 20, 16)
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
    glDepthMask(GL_FALSE)   
    glDisable(GL_DEPTH_TEST)
    # Restore depth state
    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    glPopMatrix()



def draw_ufo():
    draw_ufo_opaque()      
    draw_ufo_windows()     


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


# -------------------------------------------------------------------------------------------------------------------------
#                                                   BEAM
# -------------------------------------------------------------------------------------------------------------------------


last_time = None
keys_down = set()

# ---------------- Beam Config ----------------
beam_active = False
beam_cooldown = 5.0
beam_cooldown_left = 0.0

beam_duration = 10.0   
beam_timer = 0.0      
beam_angle_deg = 18.0

# ---------------- UFO States ----------------
ufo_state = "flying"
altitude_fly = 160
altitude_land = 18.0


def draw_beam():
    pos = ufo_pos
    yaw = ufo_yaw
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
        beam_timer = beam_duration  
    else:
        beam_active= not beam_active

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


# -------------------------------------------------------------------------------------------------------------------------
#                                                   ABDUCTION
# -------------------------------------------------------------------------------------------------------------------------



humans = []
score = 0

# New: Dynamic spawning config
HUMANS_PER_CHUNK = 8
spawned_human_chunks = set()
rng = random.Random(123)

def chunk_key(x, z):
    cx = int(x // CHUNK_SIZE)
    cz = int(z // CHUNK_SIZE)
    return (cx, cz)

def spawn_humans_in_chunk(cx, cz):
    x_start = cx * CHUNK_SIZE
    z_start = cz * CHUNK_SIZE
    x_end = x_start + CHUNK_SIZE
    z_end = z_start + CHUNK_SIZE

    for _ in range(HUMANS_PER_CHUNK):
        x = rng.uniform(x_start, x_end)
        y = rng.uniform(z_start, z_end)

        humans.append({
            'x': x,
            'y': y,
            'lifted': 0.0,
            'abducted': False,
            'vx': rng.uniform(-20, 20),
            'vy': rng.uniform(-20, 20),
            'dir_change_time': rng.uniform(2, 5),
            'panic': False,
            'walk_cycle': 0.0   
        })


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
    for chunk_key in generated_chunks:
        if chunk_key not in spawned_human_chunks:
            cx, cz = chunk_key
            spawn_humans_in_chunk(cx, cz)
            spawned_human_chunks.add(chunk_key)

def update_human_movement(dt):

    ufo_x, ufo_y, ufo_z = ufo_pos

    for h in humans:
        if h['abducted']:
            continue  

        # --- Check if human is lifted ---
        if h['lifted'] > 0.0:
            
            dx = h['x'] - ufo_x
            dy = h['y'] - ufo_y
            dist = math.hypot(dx, dy)

           
            h_beam = max(1.0, ufo_z)
            top_r = 6.0
            radius_ground = math.tan(math.radians(beam_angle_deg)) * h_beam + top_r

            if beam_active and dist <= radius_ground:
               
                h['vx'] = 0.0
                h['vy'] = 0.0
            else:
                
                h['lifted'] = max(0.0, h['lifted'] - 60.0 * dt)
            continue

    
        dx = h['x'] - ufo_x
        dy = h['y'] - ufo_y
        dist = math.hypot(dx, dy)

        if dist < 120:  
            h['panic'] = True
            angle = math.atan2(dy, dx)  
            speed = 50.0
            h['vx'] = math.cos(angle) * speed
            h['vy'] = math.sin(angle) * speed
        else:
            h['panic'] = False
            h['dir_change_time'] -= dt
            if h['dir_change_time'] <= 0:
                angle = rng.uniform(0, 2 * math.pi)
                speed = rng.uniform(10, 25)
                h['vx'] = math.cos(angle) * speed
                h['vy'] = math.sin(angle) * speed
                h['dir_change_time'] = rng.uniform(2, 5)


        speed = math.hypot(h['vx'], h['vy'])
        if speed > 1.0 and h['lifted'] == 0.0:  
            if h['panic']:
                h['walk_cycle'] += dt * speed * 0.35   
            else:
                h['walk_cycle'] += dt * speed * 0.2

        h['x'] += h['vx'] * dt
        h['y'] += h['vy'] * dt



def draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
   
    depth_was = glIsEnabled(GL_DEPTH_TEST)
    light_was = glIsEnabled(GL_LIGHTING)
    tex_was   = glIsEnabled(GL_TEXTURE_2D)

  
    if depth_was: glDisable(GL_DEPTH_TEST)
    if light_was: glDisable(GL_LIGHTING)
    if tex_was:   glDisable(GL_TEXTURE_2D)

 
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, max(1, int(WIN_W)), 0, max(1, int(WIN_H)))

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

 
    glColor3f(1.0, 1.0, 1.0)

    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))


    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    if tex_was:   glEnable(GL_TEXTURE_2D)
    if light_was: glEnable(GL_LIGHTING)
    if depth_was: glEnable(GL_DEPTH_TEST)


def draw_human(h):
    glPushMatrix()
    glTranslatef(h['x'], h['y'], h['lifted'])
    
    swing_amp = 25 if not h['panic'] else 50   
    swing = math.sin(h['walk_cycle']) * swing_amp
    # --- Body ---
    glColor3f(0.8, 0.7, 0.6)  
    glPushMatrix()
    glTranslatef(0, 0, 6)
    gluCylinder(gluNewQuadric(), 2.0, 2.0, 12.0, 8, 1)  # torso
    glPopMatrix()

    # --- Head ---
    glColor3f(0.95, 0.85, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glutSolidSphere(3.5, 12, 12)
    glPopMatrix()

    # --- Arms ---
    glColor3f(0.8, 0.7, 0.6)
    # Right arm
    glPushMatrix()
    glTranslatef(0, 0, 14)
    glRotatef(90, 0, 1, 0)
    glRotatef(swing, 1, 0, 0)   
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(0, 0, 14)
    glRotatef(-90, 0, 1, 0)
    glRotatef(-swing, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1)
    glPopMatrix()

    # --- Legs ---
    glPushMatrix()
    glTranslatef(-1.0, 0, 0)
    glRotatef(-swing, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 1.0, 1.0, 6.0, 8, 1)
    glPopMatrix()

    # Right leg
    glPushMatrix()
    glTranslatef(1.0, 0, 0)
    glRotatef(swing, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 1.0, 1.0, 6.0, 8, 1)
    glPopMatrix()

    glPopMatrix() 


def draw_humans():
    update_humans()
    for h in humans:
        if not h['abducted']:
            draw_human(h)


def update_abductions(dt):

    global score
    if not beam_active:
        return

    ufo_x, ufo_y, ufo_z = ufo_pos
    beam_angle = math.radians(beam_angle_deg)
    abduction_speed = 140

    axis = (0.0, 0.0, -1.0)
    for hmn in humans:
        if hmn['abducted']:
            continue

       
        dx = hmn['x'] - ufo_x
        dy = hmn['y'] - ufo_y
        dz = hmn['lifted'] - ufo_z  

        if dz < 0:  
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            if length == 0:
                continue

          
            vx, vy, vz = dx/length, dy/length, dz/length

          
            dot = vx*axis[0] + vy*axis[1] + vz*axis[2]
            dot = max(-1.0, min(1.0, dot)) 
            angle = math.acos(dot)

            if angle <= beam_angle:
             
                h_beam = max(1.0, ufo_z)
                top_r = 6.0
                radius_ground = math.tan(math.radians(beam_angle_deg)) * h_beam + top_r

                dist_xy = math.hypot(dx, dy)     
                if dist_xy <= radius_ground:
                    target_height = ufo_z - 40.0
                    hmn['lifted'] += abduction_speed * dt

                    if hmn['lifted'] >= target_height:
                        hmn['lifted'] = target_height
                        hmn['abducted'] = True
                        score += 1


###############################################

# Parameter
CHUNK_SIZE = 200 
BUILDINGS_PER_CHUNK = 15 
TREES_PER_CHUNK = 10     

# Track generated chunks to avoid duplicates
generated_chunks = set()
buildings = []
trees = []
MAX_BUILDING_HEIGHT=80
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
        h = rng.randint(20, MAX_BUILDING_HEIGHT)
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

    ufo_x = ufo_pos[0]
    ufo_z = ufo_pos[1]

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

######################################################



MAGIC_BOX_SIZE = 8.0
MAX_BOXES = 25 
SPAWN_INTERVAL = 10.0
last_spawn_time = 0

magic_boxes = []
box_counter = 0 

POWER_UPS = [
    "beam_wider",
    "beam_stronger",
    "cooldown_reset",
    "score_bonus"
]

TRAPS = [
    "beam_narrow",     
    "beam_slower",     
    "cooldown_extend", 
    "fake_abduction"   
]

def spawn_box():
    """Spawn a magic box on the ground surface."""
    global box_counter
    ufo_x, ufo_y, ufo_z = ufo_pos
    
    # Spawn box on ground in a ring around the UFO (30-80 units away)
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(30, 80)
    
    box_x = ufo_x + math.cos(angle) * distance
    box_y = ufo_y + math.sin(angle) * distance
    box_z = 4.0
    
    # 70% chance of power-up, 30% trap
    if random.random() < 0.7:
        box_type = "power_up"
        effect = random.choice(POWER_UPS)
    else:
        box_type = "trap"
        effect = random.choice(TRAPS)
    
    box_counter += 1
    new_box = {
        'id': box_counter,
        'x': box_x,
        'y': box_y,
        'z': box_z,
        'type': box_type,
        'effect': effect,
        'collected': False,
        'spawn_time': time.time(),
        'life_time': 25.0,
        'lifted': 0.0  
    }
    
    magic_boxes.append(new_box)
    print(f"[Magic Box] Spawned {box_type} box (ID: {new_box['id']}) at ({box_x:.1f}, {box_y:.1f})")

def apply_effect(box):
    """Apply the effect of the collected box."""
    global beam_angle_deg, beam_cooldown_left, score
    effect = box['effect']
    box_type = "Power-up" if box['type'] == "power_up" else "Trap"
    effect_name = effect.replace('_', ' ').title()
    print(f"[Magic Box] Collected: {box_type} - {effect_name}")
    
    if effect == "beam_wider":
        beam_angle_deg = min(45.0, beam_angle_deg + 5.0)
    elif effect == "beam_narrow":
        beam_angle_deg = max(5.0, beam_angle_deg - 5.0)
    elif effect == "beam_stronger":
        pass
    elif effect == "beam_slower":
        pass
    elif effect == "cooldown_reset":
        beam_cooldown_left = 0.0
    elif effect == "cooldown_extend":
        beam_cooldown_left += 5.0
    elif effect == "score_bonus":
        score += 15
    elif effect == "fake_abduction":
        pass

def update_boxes():
    """Update box logic every frame."""
    global magic_boxes, last_spawn_time
    
    current_time = time.time()
    
    # Spawn new box periodically
    if len(magic_boxes) < MAX_BOXES and (current_time - last_spawn_time) > SPAWN_INTERVAL:
        spawn_box()
        last_spawn_time = current_time
    
    # Update existing boxes
    for box in magic_boxes[:]:
        if box['collected']:
            continue
            
        if (current_time - box['spawn_time']) > box['life_time']:
            magic_boxes.remove(box)
            print(f"[Magic Box] Box {box['id']} expired")
            continue

def draw_box(box):
    """Draw a colorful magic box on the ground."""
    glPushMatrix()
    glTranslatef(box['x'], box['y'], box['z'] + box['lifted'])
    
    # Pulsing effect
    pulse = (math.sin(time.time() * 3 + box['id']) + 1) * 0.5
    scale = 1.0 + pulse * 0.2
    
    glScalef(scale, scale, scale)
    if box['type'] == "power_up":
        glColor3f(0.0, 0.9, 0.0) 
    else:
        glColor3f(0.9, 0.0, 0.0) 
    
    # Draw main cube
    glutSolidCube(MAGIC_BOX_SIZE)
    
    # Draw wireframe outline for visibility
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(2.0)
    if box['type'] == "power_up":
        glColor3f(0.7, 1.0, 0.7)
    else:
        glColor3f(1.0, 0.7, 0.7)
    glutSolidCube(MAGIC_BOX_SIZE + 1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Draw symbol on top
    glTranslatef(0, 0, MAGIC_BOX_SIZE/2 + 1.0)
    if box['type'] == "power_up":
        # Plus sign for power-up
        glColor3f(1.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(-2, -0.5, 0)
        glVertex3f(2, -0.5, 0)
        glVertex3f(2, 0.5, 0)
        glVertex3f(-2, 0.5, 0)
        glVertex3f(-0.5, -2, 0)
        glVertex3f(0.5, -2, 0)
        glVertex3f(0.5, 2, 0)
        glVertex3f(-0.5, 2, 0)
        glEnd()
    else:
        # Exclamation mark for trap
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -2, 0)
        glVertex3f(0.5, -2, 0)
        glVertex3f(0.5, 1, 0)
        glVertex3f(-0.5, 1, 0)
        glEnd()
        glTranslatef(0, -2.5, 0)
        glutSolidSphere(0.5, 6, 6)
    
    glPopMatrix()

def draw_boxes():
    """Draw all active magic boxes."""
    update_boxes() 
    
    for box in magic_boxes:
        if not box['collected']:
            draw_box(box)

def reset_boxes():
    """Clear all boxes (useful for game restart)."""
    global magic_boxes, last_spawn_time, box_counter
    magic_boxes = []
    last_spawn_time = 0
    box_counter = 0

#################################################

# ====================================================================================================
#                                      ENEMIES + HEALTH SYSTEM
# ====================================================================================================

# --------- UFO Health ----------
ufo_max_health = 100
ufo_health = 100.0

def reset_ufo_health():
    global ufo_health
    ufo_health = float(ufo_max_health)

def damage_ufo(amount: float):
    global ufo_health
    ufo_health = max(0.0, ufo_health - float(amount))

def check_game_over():
    global game_state
    if ufo_health <= 0.0 and game_state == "playing":
        print("[Game] UFO destroyed — Game Over")
        game_state = "gameover"

def draw_ufo_healthbar():
    """Battery-like health bar above UFO. Billboarded & depth-safe."""
    glPushMatrix()
    glTranslatef(ufo_pos[0], ufo_pos[1], ufo_pos[2] + 36.0)
    # face the camera around Z
    ang = math.degrees(math.atan2(cam_pos[1]-ufo_pos[1], cam_pos[0]-ufo_pos[0]))
    glRotatef(ang, 0, 0, 1)
    glScalef(1.8, 1.8, 1.0)

    depth_was = glIsEnabled(GL_DEPTH_TEST)
    light_was = glIsEnabled(GL_LIGHTING)
    if depth_was: glDisable(GL_DEPTH_TEST)
    if light_was: glDisable(GL_LIGHTING)

    width = 38.0; height = 10.0; cap_w = 4.0
    seg_count = 5; seg_gap = 0.8
    inner_w = width - 4.0; inner_h = height - 4.0
    seg_w = (inner_w - (seg_count - 1) * seg_gap) / seg_count

    glLineWidth(2.0)
    glColor3f(0.98, 0.98, 0.98)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-width/2, -height/2, 0)
    glVertex3f(width/2, -height/2, 0)
    glVertex3f(width/2, height/2, 0)
    glVertex3f(-width/2, height/2, 0)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(width/2, -height/4, 0)
    glVertex3f(width/2 + cap_w, -height/4, 0)
    glVertex3f(width/2 + cap_w, height/4, 0)
    glVertex3f(width/2, height/4, 0)
    glEnd()

    frac = max(0.0, min(1.0, ufo_health / ufo_max_health))
    lit_segments = int(frac * seg_count + 1e-6)
    def seg_col():
        if frac > 0.6: return (0.2, 0.9, 0.2)
        if frac > 0.3: return (0.95, 0.8, 0.1)
        return (0.95, 0.2, 0.1)

    start_x = -inner_w/2
    for i in range(seg_count):
        x0 = start_x + i * (seg_w + seg_gap)
        x1 = x0 + seg_w
        y0 = -inner_h/2; y1 = inner_h/2
        glColor3f(*(seg_col() if i < lit_segments else (0.25,0.25,0.25)))
        glBegin(GL_QUADS)
        glVertex3f(x0, y0, 0.1); glVertex3f(x1, y0, 0.1)
        glVertex3f(x1, y1, 0.1); glVertex3f(x0, y1, 0.1)
        glEnd()

    if light_was: glEnable(GL_LIGHTING)
    if depth_was: glEnable(GL_DEPTH_TEST)
    glPopMatrix()

# --------- Enemies / Projectiles ----------
enemies = []       # dict: type, x,y,z, weapon, next_fire, fire_interval, rockets_left
projectiles = []   # dict: type, x,y,z, vx,vy,vz, damage, radius, spawn, ttl, smoke
MAX_ENEMIES = 14
ENEMY_SPAWN_INTERVAL = 8.0
_last_enemy_spawn_time = 0.0

# Barrel offsets for visuals
SOLDIER_BARREL_FORWARD = 2.4
SOLDIER_BARREL_LEN     = 3.5
SOLDIER_BARREL_Z       = 7.0

TANK_BARREL_FORWARD = 3.4
TANK_BARREL_LEN     = 5.0
TANK_BARREL_Z       = 4.2

def reset_enemies_and_projectiles():
    global enemies, projectiles, _last_enemy_spawn_time
    enemies = []
    projectiles = []
    _last_enemy_spawn_time = time.time()

def spawn_enemy():
    """Spawn soldier (gun/rocket) or tank (rocket)."""
    ufx, ufy, _ = ufo_pos
    angle = random.uniform(0, 2*math.pi)
    dist = random.uniform(140, 320)
    ex = ufx + math.cos(angle)*dist
    ey = ufy + math.sin(angle)*dist

    etype = random.choice(["soldier", "tank", "soldier"])
    if etype == "soldier":
        weapon = random.choice(["gun", "rocket"])
        if weapon == "gun":
            fire_interval = random.uniform(0.6, 1.0); rockets_left = 0
        else:
            fire_interval = random.uniform(2.8, 3.6); rockets_left = random.randint(2, 4)
    else:
        weapon = "rocket"
        fire_interval = random.uniform(2.4, 3.0); rockets_left = random.randint(4, 6)

    enemies.append({
        'type': etype,
        'x': ex, 'y': ey, 'z': 0.0,
        'weapon': weapon,
        'next_fire': time.time() + random.uniform(0.5, 1.2),
        'fire_interval': fire_interval,
        'rockets_left': rockets_left
    })
    print(f"[Enemy] Spawned {etype} with {weapon} at ({ex:.1f},{ey:.1f})")

def update_enemy_spawning(dt):
    global _last_enemy_spawn_time
    now = time.time()
    if len(enemies) < MAX_ENEMIES and (now - _last_enemy_spawn_time) >= ENEMY_SPAWN_INTERVAL:
        for _ in range(random.randint(1, 2)):
            if len(enemies) < MAX_ENEMIES:
                spawn_enemy()
        _last_enemy_spawn_time = now

def _aim_vector(from_pos, to_pos):
    vx = to_pos[0] - from_pos[0]
    vy = to_pos[1] - from_pos[1]
    vz = to_pos[2] - from_pos[2]
    L = math.sqrt(vx*vx + vy*vy + vz*vz)
    if L == 0: return (0.0, 0.0, 0.0)
    return (vx/L, vy/L, vz/L)

def enemy_fire(enemy):
    """Projectiles start at barrel tip and head to UFO."""
    global projectiles
    ufx, ufy, ufz = ufo_pos

    if enemy['type'] == "soldier":
        ang = math.atan2(ufy - enemy['y'], ufx - enemy['x'])
        tip_x = enemy['x'] + math.cos(ang) * (SOLDIER_BARREL_FORWARD + SOLDIER_BARREL_LEN)
        tip_y = enemy['y'] + math.sin(ang) * (SOLDIER_BARREL_FORWARD + SOLDIER_BARREL_LEN)
        tip_z = SOLDIER_BARREL_Z
    else:
        ang = math.atan2(ufy - enemy['y'], ufx - enemy['x'])
        tip_x = enemy['x'] + math.cos(ang) * (TANK_BARREL_FORWARD + TANK_BARREL_LEN)
        tip_y = enemy['y'] + math.sin(ang) * (TANK_BARREL_FORWARD + TANK_BARREL_LEN)
        tip_z = TANK_BARREL_Z

    source = (tip_x, tip_y, tip_z)
    target = (ufx, ufy, ufz - 5.0)  # body center-ish
    dirx, diry, dirz = _aim_vector(source, target)

    if enemy['weapon'] == "gun":
        speed = 340.0; damage = 5.0; radius = 1.2; ttl = 3.0; ptype = "bullet"; smoke = False
    else:
        if enemy['rockets_left'] <= 0: return
        enemy['rockets_left'] -= 1
        speed = 190.0; damage = 20.0; radius = 2.6; ttl = 6.0; ptype = "rocket"; smoke = True

    projectiles.append({
        'type': ptype,
        'x': source[0], 'y': source[1], 'z': source[2],
        'vx': dirx*speed, 'vy': diry*speed, 'vz': dirz*speed,
        'damage': damage, 'radius': radius,
        'spawn': time.time(), 'ttl': ttl, 'smoke': smoke
    })

def update_enemies(dt):
    now = time.time()
    for e in enemies:
        if now >= e['next_fire']:
            enemy_fire(e)
            e['next_fire'] = now + e['fire_interval'] + random.uniform(-0.15, 0.25)

def update_projectiles(dt):
    """Move projectiles, collide with UFO and apply damage."""
    global projectiles
    center = (ufo_pos[0], ufo_pos[1], ufo_pos[2]-6.0)
    ufo_radius = 28.0
    now = time.time()
    new_list = []
    for p in projectiles:
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        p['z'] += p['vz'] * dt
        if (now - p['spawn']) > p['ttl']: continue
        if p['z'] < 0.0: continue

        dx = p['x'] - center[0]; dy = p['y'] - center[1]; dz = p['z'] - center[2]
        if (dx*dx + dy*dy + dz*dz) <= (ufo_radius + p['radius'])**2:
            damage_ufo(p['damage'])
            continue
        new_list.append(p)
    projectiles = new_list

def draw_enemies():
    """Soldiers carry visible guns; tanks show turret & barrel oriented at UFO."""
    for e in enemies:
        glPushMatrix()
        glTranslatef(e['x'], e['y'], 0.0)
        if e['type'] == "soldier":
            glColor3f(0.15, 0.5, 0.2)
            glPushMatrix(); glTranslatef(-0.6, 0, 0); gluCylinder(gluNewQuadric(), 0.6, 0.6, 5.0, 8, 1); glPopMatrix()
            glPushMatrix(); glTranslatef( 0.6, 0, 0); gluCylinder(gluNewQuadric(), 0.6, 0.6, 5.0, 8, 1); glPopMatrix()
            glPushMatrix(); glTranslatef(0, 0, 5.0); glScalef(2.0, 1.4, 3.0); glColor3f(0.2, 0.6, 0.25); glutSolidCube(2.0); glPopMatrix()
            glColor3f(0.9, 0.8, 0.7)
            glPushMatrix(); glTranslatef(0, 0, 9.8); glutSolidSphere(1.2, 12, 12); glPopMatrix()
            glColor3f(0.15, 0.15, 0.17)
            glPushMatrix()
            ang = math.degrees(math.atan2(ufo_pos[1]-e['y'], ufo_pos[0]-e['x']))
            glRotatef(ang, 0, 0, 1)
            glTranslatef(SOLDIER_BARREL_FORWARD, 0, SOLDIER_BARREL_Z)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 0.3, 0.3, SOLDIER_BARREL_LEN, 8, 1)
            glPopMatrix()
        else:
            glColor3f(0.25, 0.35, 0.45)
            glPushMatrix(); glTranslatef(0, 0, 2.0); glScalef(8.0, 6.0, 2.5); glutSolidCube(2.0); glPopMatrix()
            glColor3f(0.2, 0.25, 0.3)
            glPushMatrix(); glTranslatef(0, 0, 4.0); glutSolidSphere(2.2, 10, 10); glPopMatrix()
            glColor3f(0.1, 0.1, 0.12)
            glPushMatrix()
            ang = math.degrees(math.atan2(ufo_pos[1]-e['y'], ufo_pos[0]-e['x']))
            glRotatef(ang, 0, 0, 1)
            glTranslatef(TANK_BARREL_FORWARD, 0, TANK_BARREL_Z)
            glRotatef(-90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 0.5, 0.5, TANK_BARREL_LEN, 10, 1)
            glPopMatrix()
        glPopMatrix()

def draw_projectiles():
    lit = glIsEnabled(GL_LIGHTING)
    if lit: glDisable(GL_LIGHTING)
    for p in projectiles:
        glPushMatrix()
        glTranslatef(p['x'], p['y'], p['z'])
        if p['type'] == "bullet":
            glColor3f(1.0, 0.95, 0.2)
            glutSolidSphere(0.9, 12, 12)
        else:
            glColor3f(1.0, 0.4, 0.1)
            yaw = math.degrees(math.atan2(p['vy'], p['vx']))
            pitch = -math.degrees(math.atan2(p['vz'], math.hypot(p['vx'], p['vy'])))
            glRotatef(yaw, 0, 0, 1)
            glRotatef(pitch, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 0.7, 0.0, 3.4, 12, 1)
            glColor4f(1.0, 0.6, 0.2, 0.6)
            glutSolidSphere(1.0, 10, 10)
        glPopMatrix()
    if lit: glEnable(GL_LIGHTING)

#################################################

# menu.py

# ------------------ MENU STATE ------------------
game_state = "menu"   # menu | playing | paused | gameover

menu_buttons = [
    {"label": "Play",  "x": 400, "y": 500, "w": 200, "h": 50, "action": "resume"},
    {"label": "Restart", "x": 400, "y": 420, "w": 200, "h": 50, "action": "restart"},
    {"label": "Exit",    "x": 400, "y": 340, "w": 200, "h": 50, "action": "exit"},
]

# ------------------ DRAWING ------------------
def draw_text(x, y, text):
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

def draw_button(btn):
    # Background rectangle
    glColor3f(0.2, 0.2, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(btn["x"], btn["y"])
    glVertex2f(btn["x"] + btn["w"], btn["y"])
    glVertex2f(btn["x"] + btn["w"], btn["y"] + btn["h"])
    glVertex2f(btn["x"], btn["y"] + btn["h"])
    glEnd()

    # Label
    glColor3f(1, 1, 1)
    draw_text(btn["x"] + 60, btn["y"] + 20, btn["label"])

def draw_menu():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIN_W, 0, WIN_H)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)   # <-- IMPORTANT: draw always on top

    for btn in menu_buttons:
        draw_button(btn)

    glEnable(GL_DEPTH_TEST)    # restore
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# ------------------ LOGIC ------------------
def restart_game():
    global ufo_yaw, ufo_state, beam_active, score
    spawn_initial_humans()
    init_city()
    reset_boxes()
    ufo_pos[:] = [0.0, 0.0, 60.0]
    ufo_yaw = 0.0
    ufo_state = "flying"
    beam_active = False
    score = 0
    print("[Game] Restarted")
    # --- Added for enemies/health ---
    reset_enemies_and_projectiles()
    reset_ufo_health()

def handle_menu_click(x, y):
    global game_state
    y = WIN_H - y
    for btn in menu_buttons:
        if (btn["x"] <= x <= btn["x"] + btn["w"] and
            btn["y"] <= y <= btn["y"] + btn["h"]):
            if btn["action"] == "resume":
                game_state = "playing"
            elif btn["action"] == "restart":
                restart_game()
                game_state = "playing"
            elif btn["action"] == "exit":
                glutLeaveMainLoop()



#-------------------------------------------------------------------------------------------------------
#                                     Main
#---------------------------------------------------------------------------------------------------------

keys_down = set()
last_time = None

def update(dt):
    if game_state != "playing":
         return
    global keys_down,ufo_yaw, ufo_pos, ufo_state, altitude_fly, cam_look, cam_pos, WIN_W, WIN_H, beam_cooldown
    pos = ufo_pos
    yaw = ufo_yaw

    can_move = (ufo_state != "landed")

    forward = [ math.cos(math.radians(yaw)), math.sin(math.radians(yaw)) ]
    right   = [ math.cos(math.radians(yaw+90)), math.sin(math.radians(yaw+90)) ]

    if can_move and b'w' in keys_down:
        ufo_pos[0] += forward[0]*ufo_speed*dt
        ufo_pos[1] += forward[1]*ufo_speed*dt
    if can_move and b's' in keys_down:
        ufo_pos[0] -= forward[0]*ufo_speed*dt
        ufo_pos[1] -= forward[1]*ufo_speed*dt
    if can_move and b'd' in keys_down:
        ufo_pos[0] -= right[0]*ufo_speed*0.7*dt
        ufo_pos[1] -= right[1]*ufo_speed*0.7*dt
    if can_move and b'a' in keys_down:
        ufo_pos[0] += right[0]*ufo_speed*0.7*dt
        ufo_pos[1] += right[1]*ufo_speed*0.7*dt
    if can_move and b'q' in keys_down:
        ufo_yaw += ufo_turn_speed*dt
    if can_move and b'e' in keys_down:
        ufo_yaw -= ufo_turn_speed*dt

    #landing/accending
    if ufo_state == "flying" and b'l' in keys_down:
        ufo_state = "landing"
    if ufo_state == "landed" and b'k' in keys_down:
        ufo_state = "ascending"

    if ufo_state == "landing":
        ufo_pos[2] = max(altitude_land, ufo_pos[2] - 40.0*dt)
        if abs(ufo_pos[2]-altitude_land) < 0.5:
            ufo_pos[2] = altitude_land
            ufo_state = "landed"
    elif ufo_state == "ascending":
        ufo_pos[2] = min(altitude_fly, ufo_pos[2] + 40.0*dt)
        if abs(ufo_pos[2]-altitude_fly) < 0.5:
            ufo_pos[2] = altitude_fly
            ufo_state = "flying"

    # Hover when flying
    if ufo_state == "flying":
        t = time.time()
        ufo_pos[2] = altitude_fly + math.sin(t*2*math.pi*hover_speed)*hover_amp

   
    update_beam(dt)

    
    # Abduction check
    update_abductions(dt)
    update_human_movement(dt)
    
    # Magic box beam collection
    if beam_active:
        h = max(1.0, ufo_pos[2])
        top_r = 6.0
        radius_ground = math.tan(math.radians(beam_angle_deg)) * h + top_r
        for box in magic_boxes[:]:
            if box['collected']:
                continue
            dx = box['x'] - pos[0]
            dy = box['y'] - pos[1]
            dist = math.hypot(dx, dy)
            if dist <= radius_ground:
                # Lift box upward gradually
                box['lifted'] += 60.0 * dt
                target_height = pos[2] - 6.0
                if box['lifted'] >= target_height:
                    box['lifted'] = target_height
                    box['collected'] = True
                    apply_effect(box)
                    # Remove collected box
                    if box in magic_boxes:
                        magic_boxes.remove(box)
                    print(f"[Magic Box] Box collected via beam!")

    # --- Enemies & projectiles ---
    update_enemy_spawning(dt)
    update_enemies(dt)
    update_projectiles(dt)
    check_game_over()

     # Camera follow
    cam_offset = -220.0
    cam_pos[0] = ufo_pos[0] + math.cos(math.radians(ufo_yaw))*cam_offset
    cam_pos[1] = ufo_pos[1] + math.sin(math.radians(ufo_yaw))*cam_offset
    cam_pos[2] = 160.0
    cam_look[0], cam_look[1], cam_look[2] = ufo_pos[0], ufo_pos[1], 40.0

def display():
    global last_time
    now = time.time()
    if last_time is None: 
        last_time = now
    dt = min(0.05, now - last_time)
    last_time = now
    update(dt)

    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)

    glViewport(0, 0, WIN_W, WIN_H)

    # Clear screen
    glClearColor(0.05, 0.06, 0.09, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if game_state == "playing":
        # draw your UFO world
        setup_camera()
        setup_lights()
        draw_city()
        glEnable(GL_LIGHTING)
        draw_ufo()
        draw_ufo_healthbar()      # <<< added
        draw_humans()
        draw_enemies()            # <<< added
        glDisable(GL_LIGHTING)
        draw_beam() 
        draw_projectiles()        # <<< added
        glEnable(GL_LIGHTING)
        draw_boxes()


        # Beam status string
        if beam_active:
            beam_status = f"Beam active: {beam_timer:.1f}s"
        elif beam_cooldown_left > 0:
            beam_status = f"Cooldown: {beam_cooldown_left:.1f}s"
        else:
            beam_status = "Beam ready"

     # Final status text
        status = (
            f"Score={score} | "
            f"HP={int(ufo_health)}/{ufo_max_health} | "  # <<< added
            f"Humans left={sum(1 for h in humans if not h['abducted'])} | "
            f"{beam_status} | B=beam | L=land/K=ascend"
            )

        draw_text_2d(12, WIN_H - 24, status, GLUT_BITMAP_HELVETICA_18)


    else:
        draw_menu()

    glutSwapBuffers()

    

def idle():
    glutPostRedisplay()

def on_key_down(key, x, y):
    global keys_down, ufo_state, game_state

    # ESC key → toggle menu/pause
    if key == b'\x1b':
        if game_state == "playing":
            game_state = "menu"
        else:
            game_state = "playing"

    # If we are in menu mode, ignore other inputs
    if game_state != "playing":
        return

    # Add pressed key to active set
    keys_down.add(key)

    # Toggle UFO beam
    if key == b'b':
        try_toggle_beam()

    #Restart game instantly
    if key == b'r':
        restart_game()

    #Landing and ascending
    if key == b'l' and ufo_state == "flying":
        ufo_state = "landing"
    if key == b'k' and ufo_state == "landed":
        ufo_state = "ascending"


def on_key_up(key, x, y):
    if key in keys_down: keys_down.remove(key)

def on_mouse(button, state, x, y):
    if game_state in ["menu", "paused", "gameover"] and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        handle_menu_click(x, y)


def main():
    restart_game()
    spawn_initial_humans()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Alien UFO Abduction ")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    glutMouseFunc(on_mouse)
    
    glutMainLoop()

if __name__ == "__main__":
    main()