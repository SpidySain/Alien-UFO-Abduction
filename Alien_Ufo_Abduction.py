from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import time, math, random
from types import SimpleNamespace

# --------------------------------------------------------------------
# Namespaces to mirror your original modules
# --------------------------------------------------------------------
ufo_base  = SimpleNamespace()
ufo_beam  = SimpleNamespace()
abduction = SimpleNamespace()
city      = SimpleNamespace()
magic_box = SimpleNamespace()
menu      = SimpleNamespace()
meno      = menu  # alias as requested

# ====================================================================
# 1) ufo_base
# ====================================================================
ufo_base.WIN_W, ufo_base.WIN_H = 1000, 800
ufo_base.ASPECT = ufo_base.WIN_W / ufo_base.WIN_H

ufo_base.fovY = 90
ufo_base.cam_pos  = [0.0, -300.0, 160.0]
ufo_base.cam_look = [0.0, 0.0, 40.0]

ufo_base.GROUND_SIZE = 1200

ufo_base.ufo_pos = [0.0, 0.0, 60.0]
ufo_base.ufo_yaw = 0.0
ufo_base.ufo_speed = 140.0
ufo_base.ufo_turn_speed = 100.0
ufo_base.hover_amp = 6.0
ufo_base.hover_speed = 2.0

def _ub_draw_ground():
    glDisable(GL_LIGHTING)
    glBegin(GL_QUADS)
    glColor3f(0.12, 0.14, 0.18)
    s = ufo_base.GROUND_SIZE / 2
    glVertex3f(-s, -s, 0); glVertex3f(s, -s, 0)
    glVertex3f(s,  s, 0);  glVertex3f(-s, s, 0)
    glEnd()

    glLineWidth(1)
    glColor3f(0.25, 0.28, 0.33)
    glBegin(GL_LINES)
    step = 60
    for x in range(-int(s), int(s)+1, step):
        glVertex3f(x, -s, 0); glVertex3f(x, s, 0)
    for y in range(-int(s), int(s)+1, step):
        glVertex3f(-s, y, 0); glVertex3f(s, y, 0)
    glEnd()
    glEnable(GL_LIGHTING)
ufo_base.draw_ground = _ub_draw_ground

def _ub_draw_ufo_opaque():
    glPushMatrix()
    glTranslatef(*ufo_base.ufo_pos)
    glRotatef(ufo_base.ufo_yaw, 0, 0, 1)
    glRotatef((time.time() * 30) % 360, 0, 0, 1)

    glPushMatrix()
    glColor3f(0.7, 0.7, 0.75)
    glScalef(1.6, 1.6, 0.25)
    glutSolidSphere(30, 28, 18)
    glPopMatrix()

    glColor3f(0.85, 0.85, 0.9)
    glutSolidTorus(5, 35, 24, 32)

    glPushMatrix()
    glTranslatef(0, 0, 18)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.55, 0.75, 0.95, 0.4)
    glutSolidSphere(16, 20, 16)
    glDisable(GL_BLEND)
    glPopMatrix()

    for angle in range(0, 360, 60):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(20, 0, -6)
        glColor3f(1.0, 0.3, 0.2)
        glutSolidSphere(2.5, 12, 12)
        glPopMatrix()

    glPopMatrix()

def _ub_draw_ufo_windows():
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)
    glDisable(GL_DEPTH_TEST)

    for angle in range(0, 360, 45):
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(36, 0, 5)
        glColor4f(0.2, 0.8, 1.0, 0.2)
        glutSolidSphere(3, 16, 16)
        glPopMatrix()

    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def _ub_draw_ufo():
    _ub_draw_ufo_opaque()
    _ub_draw_ufo_windows()
ufo_base.draw_ufo = _ub_draw_ufo

def _ub_setup_lights():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, -300.0, 500.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  (0.9, 0.9, 0.9, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.6, 0.6, 0.6, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT,  (0.15, 0.15, 0.15, 1.0))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)
ufo_base.setup_lights = _ub_setup_lights

def _ub_setup_camera():
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(ufo_base.fovY, ufo_base.ASPECT, 0.1, 5000.0)
    glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    gluLookAt(
        ufo_base.cam_pos[0],  ufo_base.cam_pos[1],  ufo_base.cam_pos[2],
        ufo_base.cam_look[0], ufo_base.cam_look[1], ufo_base.cam_look[2],
        0, 0, 1
    )
ufo_base.setup_camera = _ub_setup_camera

# ====================================================================
# 2) ufo_beam
# ====================================================================
ufo_beam.beam_active = False
ufo_beam.beam_cooldown = 5.0
ufo_beam.beam_cooldown_left = 0.0
ufo_beam.beam_duration = 10.0
ufo_beam.beam_timer = 0.0
ufo_beam.beam_angle_deg = 18.0

ufo_beam.ufo_state = "flying"
ufo_beam.altitude_fly = 160.0
ufo_beam.altitude_land = 18.0

def _ubm_draw_beam():
    if not ufo_beam.beam_active:
        return
    pos = ufo_base.ufo_pos
    yaw = ufo_base.ufo_yaw
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTranslatef(pos[0], pos[1], 0.0)
    h = max(1.0, pos[2])
    top_r = 6.0
    bottom_r = math.tan(math.radians(ufo_beam.beam_angle_deg)) * h + top_r
    glColor4f(1.0, 0.95, 0.4, 0.45)
    quad = gluNewQuadric()
    glTranslatef(0, 0, 0.1)
    glRotatef(yaw, 0, 0, 1)
    gluCylinder(quad, bottom_r, top_r, h - 0.1, 24, 1)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()
ufo_beam.draw_beam = _ubm_draw_beam

def _ubm_try_toggle_beam():
    if not ufo_beam.beam_active and ufo_beam.beam_cooldown_left == 0.0:
        ufo_beam.beam_active = True
        ufo_beam.beam_timer = ufo_beam.beam_duration
ufo_beam.try_toggle_beam = _ubm_try_toggle_beam

def _ubm_update_beam(dt: float):
    if ufo_beam.beam_active:
        ufo_beam.beam_timer -= dt
        if ufo_beam.beam_timer <= 0:
            ufo_beam.beam_active = False
            ufo_beam.beam_cooldown_left = ufo_beam.beam_cooldown
    elif ufo_beam.beam_cooldown_left > 0:
        ufo_beam.beam_cooldown_left = max(0.0, ufo_beam.beam_cooldown_left - dt)
ufo_beam.update_beam = _ubm_update_beam

# ====================================================================
# 3) abduction
# ====================================================================
abduction.humans = []
abduction.score = 0
abduction.HUMANS_PER_CHUNK = 8
abduction.spawned_human_chunks = set()
abduction.rng = random.Random(123)

def _abd_chunk_key(x, z):
    cx = int(x // city.CHUNK_SIZE)   # city defined later; resolved at runtime
    cz = int(z // city.CHUNK_SIZE)
    return (cx, cz)
abduction.chunk_key = _abd_chunk_key

def _abd_spawn_humans_in_chunk(cx, cz):
    x_start = cx * city.CHUNK_SIZE
    z_start = cz * city.CHUNK_SIZE
    x_end = x_start + city.CHUNK_SIZE
    z_end = z_start + city.CHUNK_SIZE
    for _ in range(abduction.HUMANS_PER_CHUNK):
        x = abduction.rng.uniform(x_start, x_end)
        y = abduction.rng.uniform(z_start, z_end)
        abduction.humans.append({
            'x': x, 'y': y, 'lifted': 0.0, 'abducted': False,
            'vx': abduction.rng.uniform(-20, 20),
            'vy': abduction.rng.uniform(-20, 20),
            'dir_change_time': abduction.rng.uniform(2, 5),
            'panic': False
        })
abduction.spawn_humans_in_chunk = _abd_spawn_humans_in_chunk

def _abd_spawn_initial_humans():
    abduction.humans = []
    abduction.score = 0
    abduction.spawned_human_chunks.clear()
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            abduction.spawn_humans_in_chunk(dx, dz)
            abduction.spawned_human_chunks.add((dx, dz))
abduction.spawn_initial_humans = _abd_spawn_initial_humans

def _abd_update_humans():
    for ch_key in city.generated_chunks:
        if ch_key not in abduction.spawned_human_chunks:
            cx, cz = ch_key
            abduction.spawn_humans_in_chunk(cx, cz)
            abduction.spawned_human_chunks.add(ch_key)
abduction.update_humans = _abd_update_humans

def _abd_update_human_movement(dt):
    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    for h in abduction.humans:
        if h['abducted']:
            continue
        if h['lifted'] > 0.0:
            h['vx'] = 0.0; h['vy'] = 0.0
            continue
        dx = h['x'] - ufo_x; dy = h['y'] - ufo_y
        dist = math.sqrt(dx*dx + dy*dy)
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
                angle = abduction.rng.uniform(0, 2 * math.pi)
                speed = abduction.rng.uniform(10, 25)
                h['vx'] = math.cos(angle) * speed
                h['vy'] = math.sin(angle) * speed
                h['dir_change_time'] = abduction.rng.uniform(2, 5)
        h['x'] += h['vx'] * dt
        h['y'] += h['vy'] * dt
abduction.update_human_movement = _abd_update_human_movement

def _abd_draw_text_2d(x, y, s, font=GLUT_BITMAP_HELVETICA_18):
    depth_was = glIsEnabled(GL_DEPTH_TEST)
    light_was = glIsEnabled(GL_LIGHTING)
    tex_was   = glIsEnabled(GL_TEXTURE_2D)
    if depth_was: glDisable(GL_DEPTH_TEST)
    if light_was: glDisable(GL_LIGHTING)
    if tex_was:   glDisable(GL_TEXTURE_2D)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, max(1, int(ufo_base.WIN_W)), 0, max(1, int(ufo_base.WIN_H)))
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    if tex_was:   glEnable(GL_TEXTURE_2D)
    if light_was: glEnable(GL_LIGHTING)
    if depth_was: glEnable(GL_DEPTH_TEST)
abduction.draw_text_2d = _abd_draw_text_2d

def _abd_draw_human(h):
    glPushMatrix()
    glTranslatef(h['x'], h['y'], h['lifted'])
    glColor3f(0.8, 0.7, 0.6)
    glPushMatrix(); glTranslatef(0, 0, 6)
    gluCylinder(gluNewQuadric(), 2.0, 2.0, 12.0, 8, 1); glPopMatrix()
    glColor3f(0.95, 0.85, 0.7)
    glPushMatrix(); glTranslatef(0, 0, 20)
    glutSolidSphere(3.5, 12, 12); glPopMatrix()
    glColor3f(0.8, 0.7, 0.6)
    glPushMatrix(); glTranslatef(0, 0, 14); glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1); glPopMatrix()
    glPushMatrix(); glTranslatef(0, 0, 14); glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 0.8, 0.8, 8.0, 8, 1); glPopMatrix()
    glPushMatrix(); glTranslatef(-1.0, 0, 0)
    gluCylinder(gluNewQuadric(), 1.0, 1.0, 6.0, 8, 1); glPopMatrix()
    glPushMatrix(); glTranslatef(1.0, 0, 0)
    gluCylinder(gluNewQuadric(), 1.0, 1.0, 6.0, 8, 1); glPopMatrix()
    glPopMatrix()

def _abd_draw_humans():
    abduction.update_humans()
    for h in abduction.humans:
        if not h['abducted']:
            _abd_draw_human(h)
abduction.draw_humans = _abd_draw_humans

def _abd_update_abductions(dt):
    if not ufo_beam.beam_active:
        return
    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    beam_angle = math.radians(ufo_beam.beam_angle_deg)
    abduction_speed = 140
    axis = (0.0, 0.0, -1.0)
    for hmn in abduction.humans:
        if hmn['abducted']:
            continue
        dx = hmn['x'] - ufo_x
        dy = hmn['y'] - ufo_y
        dz = hmn['lifted'] - ufo_z
        if dz < 0:
            length = math.sqrt(dx*dx + dy*dy + dz*dz)
            if length == 0: continue
            vx, vy, vz = dx/length, dy/length, dz/length
            dot = max(-1.0, min(1.0, vx*axis[0] + vy*axis[1] + vz*axis[2]))
            angle = math.acos(dot)
            if angle <= beam_angle:
                target_height = ufo_z - 40.0
                hmn['lifted'] += abduction_speed * dt
                if hmn['lifted'] >= target_height:
                    hmn['lifted'] = target_height
                    hmn['abducted'] = True
                    abduction.score += 1
abduction.update_abductions = _abd_update_abductions
def display():
    global _last_time
    now = time.time()
    if _last_time is None:
        _last_time = now
    dt = min(0.05, now - _last_time)
    _last_time = now
    update(dt)

    w = glutGet(GLUT_WINDOW_WIDTH); h = glutGet(GLUT_WINDOW_HEIGHT)
    ufo_base.WIN_W, ufo_base.WIN_H = max(1, w), max(1, h)
    ufo_base.ASPECT = ufo_base.WIN_W / float(ufo_base.WIN_H)
    glViewport(0, 0, ufo_base.WIN_W, ufo_base.WIN_H)

    glClearColor(0.05, 0.06, 0.09, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if menu.game_state == "playing":
        ufo_base.setup_camera()
        ufo_base.setup_lights()
        city.draw_city()
        glEnable(GL_LIGHTING)
        ufo_base.draw_ufo()
        abduction.draw_humans()
        glDisable(GL_LIGHTING)
        ufo_beam.draw_beam()
        glEnable(GL_LIGHTING)
        magic_box.draw_boxes()

        if ufo_beam.beam_active:
            beam_status = f"Beam active: {ufo_beam.beam_timer:.1f}s"
        elif ufo_beam.beam_cooldown_left > 0:
            beam_status = f"Cooldown: {ufo_beam.beam_cooldown_left:.1f}s"
        else:
            beam_status = "Beam ready"

        status = (
            f"Score={abduction.score} | "
            f"Humans left={sum(1 for h in abduction.humans if not h['abducted'])} | "
            f"{beam_status} | B=beam | L=land/K=ascend"
        )
        abduction.draw_text_2d(12, ufo_base.WIN_H - 24, status, GLUT_BITMAP_HELVETICA_18)
    else:
        menu.draw_menu()

    glutSwapBuffers()

def idle():
    glutPostRedisplay()

def on_key_down(key, x, y):
    if key == b'\x1b':
        menu.game_state = "menu" if menu.game_state == "playing" else "playing"
    if menu.game_state != "playing":
        return
    keys_down.add(key)
    if key == b'b':
        ufo_beam.try_toggle_beam()
    if key == b'r':
        menu.restart_game()
    if key == b'l' and ufo_beam.ufo_state == "flying":
        ufo_beam.ufo_state = "landing"
    if key == b'k' and ufo_beam.ufo_state == "landed":
        ufo_beam.ufo_state = "ascending"

def on_key_up(key, x, y):
    if key in keys_down:
        keys_down.remove(key)

def on_mouse(button, state, x, y):
    if menu.game_state in ["menu", "paused", "gameover"] and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        menu.handle_menu_click(x, y)

def main():
    menu.restart_game()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(ufo_base.WIN_W, ufo_base.WIN_H)
    glutCreateWindow(b"Alien UFO Abduction - Single File (Ordered)")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    glutMouseFunc(on_mouse)
    glutMainLoop()

if __name__ == "__main__":
    main()
