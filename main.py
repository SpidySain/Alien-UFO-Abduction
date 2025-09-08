from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import time, math

import ufo_base
import ufo_beam
import abduction
import city
import random
import magic_box
import menu
import enemies
import health

keys_down = set()
last_time = None

def update(dt):
    if menu.game_state != "playing":
        return
    global keys_down
    # Ensure we modify the shared UFO state
    pos = ufo_base.ufo_pos
    yaw = ufo_base.ufo_yaw

    can_move = (ufo_beam.ufo_state != "landed")

    # Forward and right vectors
    forward = [ math.cos(math.radians(yaw)), math.sin(math.radians(yaw)) ]
    right   = [ math.cos(math.radians(yaw+90)), math.sin(math.radians(yaw+90)) ]

    if can_move and b'w' in keys_down:
        pos[0] += forward[0]*ufo_base.ufo_speed*dt
        pos[1] += forward[1]*ufo_base.ufo_speed*dt
    if can_move and b's' in keys_down:
        pos[0] -= forward[0]*ufo_base.ufo_speed*dt
        pos[1] -= forward[1]*ufo_base.ufo_speed*dt
    if can_move and b'd' in keys_down:
        pos[0] -= right[0]*ufo_base.ufo_speed*0.7*dt
        pos[1] -= right[1]*ufo_base.ufo_speed*0.7*dt
    if can_move and b'a' in keys_down:
        pos[0] += right[0]*ufo_base.ufo_speed*0.7*dt
        pos[1] += right[1]*ufo_base.ufo_speed*0.7*dt
    if can_move and b'q' in keys_down:
        ufo_base.ufo_yaw += ufo_base.ufo_turn_speed*dt
    if can_move and b'e' in keys_down:
        ufo_base.ufo_yaw -= ufo_base.ufo_turn_speed*dt

    #landing/accending
    if ufo_beam.ufo_state == "flying" and b'l' in keys_down:
        ufo_beam.ufo_state = "landing"
    if ufo_beam.ufo_state == "landed" and b'k' in keys_down:
        ufo_beam.ufo_state = "ascending"

    if ufo_beam.ufo_state == "landing":
        pos[2] = max(ufo_beam.altitude_land, pos[2] - 40.0*dt)
        if abs(pos[2]-ufo_beam.altitude_land) < 0.5:
            pos[2] = ufo_beam.altitude_land
            ufo_beam.ufo_state = "landed"
    elif ufo_beam.ufo_state == "ascending":
        pos[2] = min(ufo_beam.altitude_fly, pos[2] + 40.0*dt)
        if abs(pos[2]-ufo_beam.altitude_fly) < 0.5:
            pos[2] = ufo_beam.altitude_fly
            ufo_beam.ufo_state = "flying"

    # Hover when flying
    if ufo_beam.ufo_state == "flying":
        t = time.time()
        pos[2] = ufo_beam.altitude_fly + math.sin(t*2*math.pi*ufo_base.hover_speed)*ufo_base.hover_amp

    # beam cooldown ticking
    ufo_beam.update_beam(dt)

    
    # Abduction check
    abduction.update_abductions(dt)
    abduction.update_human_movement(dt)

    glColor3f(1,0,0)
    glRasterPos2f(10, ufo_base.WIN_H - 30)
    for ch in f"Health: {enemies.ufo_health:.0f}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    
    # Magic box beam collection
    if ufo_beam.beam_active:
        h = max(1.0, pos[2])
        top_r = 6.0
        radius_ground = math.tan(math.radians(ufo_beam.beam_angle_deg)) * h + top_r
        for box in magic_box.magic_boxes[:]:
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
                    magic_box.apply_effect(box)
                    # Remove collected box
                    if box in magic_box.magic_boxes:
                        magic_box.magic_boxes.remove(box)
                    print(f"[Magic Box] Box collected via beam!")

     # Camera follow
    cam_offset = -220.0
    ufo_base.cam_pos[0] = pos[0] + math.cos(math.radians(ufo_base.ufo_yaw))*cam_offset
    ufo_base.cam_pos[1] = pos[1] + math.sin(math.radians(ufo_base.ufo_yaw))*cam_offset
    ufo_base.cam_pos[2] = 160.0
    ufo_base.cam_look[0], ufo_base.cam_look[1], ufo_base.cam_look[2] = pos[0], pos[1], 40.0

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
    ufo_base.WIN_W, ufo_base.WIN_H = max(1, w), max(1, h)
    ufo_base.ASPECT = ufo_base.WIN_W / float(ufo_base.WIN_H)
    glViewport(0, 0, ufo_base.WIN_W, ufo_base.WIN_H)

    # Clear screen
    glClearColor(0.05, 0.06, 0.09, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    if menu.game_state == "playing":
        # draw your UFO world
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
        enemies.draw_enemies() 
        health.draw_health_bar()


        # Beam status string
        if ufo_beam.beam_active:
            beam_status = f"Beam active: {ufo_beam.beam_timer:.1f}s"
        elif ufo_beam.beam_cooldown_left > 0:
            beam_status = f"Cooldown: {ufo_beam.beam_cooldown_left:.1f}s"
        else:
            beam_status = "Beam ready"

        # Final status text
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
    global keys_down

    # ESC key → toggle menu/pause
    if key == b'\x1b':
        if menu.game_state == "playing":
            menu.game_state = "menu"
        else:
            menu.game_state = "playing"

    # If we are in menu mode, ignore other inputs
    if menu.game_state != "playing":
        return

    # Add pressed key to active set
    keys_down.add(key)

    # Toggle UFO beam
    if key == b'b':
        ufo_beam.try_toggle_beam()

    # Restart game instantly
    if key == b'r':
        menu.restart_game()
        health.reset_health()    

    # Landing and ascending
    if key == b'l' and ufo_beam.ufo_state == "flying":
        ufo_beam.ufo_state = "landing"
    if key == b'k' and ufo_beam.ufo_state == "landed":
        ufo_beam.ufo_state = "ascending"


def on_key_up(key, x, y):
    if key in keys_down: keys_down.remove(key)

def on_mouse(button, state, x, y):
    if menu.game_state in ["menu", "paused", "gameover"] and button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        menu.handle_menu_click(x, y)


def main():
    menu.restart_game()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(ufo_base.WIN_W, ufo_base.WIN_H)
    glutCreateWindow(b"Alien UFO Abduction - Modular Version")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    glutMouseFunc(on_mouse)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
    
