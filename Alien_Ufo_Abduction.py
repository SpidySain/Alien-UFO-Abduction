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

# def draw_ground():
#     """Dark ground plane with grid lines"""
#     glDisable(GL_LIGHTING)
#     glBegin(GL_QUADS)
#     glColor3f(0.12, 0.14, 0.18)
#     s = GROUND_SIZE / 2
#     glVertex3f(-s, -s, 0)
#     glVertex3f(s, -s, 0)
#     glVertex3f(s, s, 0)
#     glVertex3f(-s, s, 0)
#     glEnd()

#     # Grid lines
#     glLineWidth(1)
#     glColor3f(0.25, 0.28, 0.33)
#     glBegin(GL_LINES)
#     step = 60
#     for x in range(-int(s), int(s) + 1, step):
#         glVertex3f(x, -s, 0)
#         glVertex3f(x, s, 0)
#     for y in range(-int(s), int(s) + 1, step):
#         glVertex3f(-s, y, 0)
#         glVertex3f(s, y, 0)
#     glEnd()
#     glEnable(GL_LIGHTING)


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

# def chunk_key(x, z):
#     cx = int(x // city.CHUNK_SIZE)
#     cz = int(z // city.CHUNK_SIZE)
#     return (cx, cz)

def spawn_humans_in_chunk(cx, cz):
    # x_start = cx #* city.CHUNK_SIZE
    # z_start = cz #* city.CHUNK_SIZE
    # x_end = x_start #+ city.CHUNK_SIZE
    # z_end = z_start #+ city.CHUNK_SIZE

    # for _ in range(HUMANS_PER_CHUNK):
    #     x = rng.uniform(x_start, x_end)
    #     y = rng.uniform(z_start, z_end)
    x_start, x_end = cx*100, cx*100 + 100
    z_start, z_end = cz*100, cz*100 + 100
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

# def update_humans():
#     for chunk_key in city.generated_chunks:
#         if chunk_key not in spawned_human_chunks:
#             cx, cz = chunk_key
#             spawn_humans_in_chunk(cx, cz)
#             spawned_human_chunks.add(chunk_key)

def update_human_movement(dt):
    """Update humans: wander randomly, but run from UFO if too close.
       If being abducted (lifted > 0), they stop moving unless dropped.
    """
    ufo_x, ufo_y, ufo_z = ufo_pos

    for h in humans:
        if h['abducted']:
            continue  # abducted humans don't move at all

        # --- Check if human is lifted ---
        if h['lifted'] > 0.0:
            # Compute distance from UFO
            dx = h['x'] - ufo_x
            dy = h['y'] - ufo_y
            dist = math.hypot(dx, dy)

            # Ground beam radius at UFO height
            h_beam = max(1.0, ufo_z)
            top_r = 6.0
            radius_ground = math.tan(math.radians(beam_angle_deg)) * h_beam + top_r

            if beam_active and dist <= radius_ground:
                # Still inside beam → freeze movement
                h['vx'] = 0.0
                h['vy'] = 0.0
            else:
                # Beam off OR UFO too far → fall down
                h['lifted'] = max(0.0, h['lifted'] - 60.0 * dt)
            continue

        # --- Normal movement when not lifted ---
        dx = h['x'] - ufo_x
        dy = h['y'] - ufo_y
        dist = math.hypot(dx, dy)

        if dist < 120:  # panic radius
            h['panic'] = True
            angle = math.atan2(dy, dx)  # away from UFO
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
        if speed > 1.0 and h['lifted'] == 0.0:  # only animate if moving on ground
            if h['panic']:
                h['walk_cycle'] += dt * speed * 0.35   # faster cycle in panic
            else:
                h['walk_cycle'] += dt * speed * 0.2    # normal walk
        # Do not reset walk_cycle — keeps pose when idle


        # Apply movement
        h['x'] += h['vx'] * dt
        h['y'] += h['vy'] * dt


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
    gluOrtho2D(0, max(1, int(WIN_W)), 0, max(1, int(WIN_H)))

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Make sure the color is white (or whatever you want)
    glColor3f(1.0, 1.0, 1.0)

    # Draw text — raster pos uses the same coordinate system as the ortho above.
 
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
    # Compute swing angle
    swing_amp = 25 if not h['panic'] else 50   # wider swing when panicking
    swing = math.sin(h['walk_cycle']) * swing_amp
    # --- Body ---
    glColor3f(0.8, 0.7, 0.6)  # skin tone for simplicity
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
    glRotatef(swing, 1, 0, 0)   # swing forward/back
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1)
    glPopMatrix()

    # Left arm
    glPushMatrix()
    glTranslatef(0, 0, 14)
    glRotatef(-90, 0, 1, 0)
    glRotatef(-swing, 1, 0, 0)  # opposite swing
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1)
    glPopMatrix()

    # --- Legs ---
    glPushMatrix()
    glTranslatef(-1.0, 0, 0)
    glRotatef(-swing, 1, 0, 0)  # opposite arm
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
    #update_humans()
    for h in humans:
        if not h['abducted']:
            draw_human(h)


def update_abductions(dt):
    """Update human abductions when beam is active."""
    global score
    if not beam_active:
        return

    ufo_x, ufo_y, ufo_z = ufo_pos
    beam_angle = math.radians(beam_angle_deg)
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

            if angle <= beam_angle:
                # Ground beam radius at UFO height
                h_beam = max(1.0, ufo_z)
                top_r = 6.0
                radius_ground = math.tan(math.radians(beam_angle_deg)) * h_beam + top_r

                dist_xy = math.hypot(dx, dy)

                # Only abduct if still within beam radius on the ground
                if dist_xy <= radius_ground:
                    target_height = ufo_z - 40.0
                    hmn['lifted'] += abduction_speed * dt

                    if hmn['lifted'] >= target_height:
                        hmn['lifted'] = target_height
                        hmn['abducted'] = True
                        score += 1





#-------------------------------------------------------------------------------------------------------
#                                     Main
#---------------------------------------------------------------------------------------------------------


keys_down = set()
last_time = None

def update(dt):
    # if menu.game_state != "playing":
    #     return
    global keys_down,ufo_yaw, ufo_pos, ufo_state, altitude_fly, cam_look, cam_pos, WIN_W, WIN_H, beam_cooldown
    # Ensure we modify the shared UFO state
    #pos = ufo_pos
    yaw = ufo_yaw

    can_move = (ufo_state != "landed")

    # Forward and right vectors
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

    # beam cooldown ticking
    update_beam(dt)

    
    # Abduction check
    update_abductions(dt)
    update_human_movement(dt)
    
    # Magic box beam collection
    # if beam_active:
    #     h = max(1.0, ufo_pos[2])
    #     top_r = 6.0
    #     radius_ground = math.tan(math.radians(ufo_beam.beam_angle_deg)) * h + top_r
    #     for box in magic_boxes[:]:
    #         if box['collected']:
    #             continue
    #         dx = box['x'] - pos[0]
    #         dy = box['y'] - pos[1]
    #         dist = math.hypot(dx, dy)
    #         if dist <= radius_ground:
    #             # Lift box upward gradually
    #             box['lifted'] += 60.0 * dt
    #             target_height = pos[2] - 6.0
    #             if box['lifted'] >= target_height:
    #                 box['lifted'] = target_height
    #                 box['collected'] = True
    #                 apply_effect(box)
    #                 # Remove collected box
    #                 if box in magic_box.magic_boxes:
    #                     magic_box.magic_boxes.remove(box)
    #                 print(f"[Magic Box] Box collected via beam!")

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

    # if menu.game_state == "playing":
        # draw your UFO world
    setup_camera()
    setup_lights()
        #city.draw_city()
    glEnable(GL_LIGHTING)
    draw_ufo()
    draw_humans()
    glDisable(GL_LIGHTING)
    draw_beam() 
    glEnable(GL_LIGHTING)
    #draw_boxes()


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
            f"Humans left={sum(1 for h in humans if not h['abducted'])} | "
            f"{beam_status} | B=beam | L=land/K=ascend"
        )

    draw_text_2d(12, WIN_H - 24, status, GLUT_BITMAP_HELVETICA_18)




    # else:
    #     menu.draw_menu()

    glutSwapBuffers()

    

def idle():
    glutPostRedisplay()

def on_key_down(key, x, y):
    global keys_down, ufo_state

    # ESC key → toggle menu/pause
    # if key == b'\x1b':
    #     if menu.game_state == "playing":
    #         menu.game_state = "menu"
    #     else:
    #         menu.game_state = "playing"

    # # If we are in menu mode, ignore other inputs
    # if menu.game_state != "playing":
    #     return

    # Add pressed key to active set
    keys_down.add(key)

    # Toggle UFO beam
    if key == b'b':
        try_toggle_beam()

    # Restart game instantly
    # if key == b'r':
        # menu.restart_game()

    # Landing and ascending
    if key == b'l' and ufo_state == "flying":
        ufo_state = "landing"
    if key == b'k' and ufo_state == "landed":
        ufo_state = "ascending"


def on_key_up(key, x, y):
    if key in keys_down: keys_down.remove(key)

# def on_mouse(button, state, x, y):
#     if menu.game_state in ["menu", "paused", "gameover"] and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
#         menu.handle_menu_click(x, y)


def main():
    # menu.restart_game()
    spawn_initial_humans()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIN_W, WIN_H)
    glutCreateWindow(b"Alien UFO Abduction ")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    #glutMouseFunc(on_mouse)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
