
# main.py
# Combines UFO base, beam, and abduction features

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import time, math

import ufo_base
import ufo_beam
import abduction

keys_down = set()
last_time = None

def update(dt):
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
    if can_move and b'a' in keys_down:
        pos[0] -= right[0]*ufo_base.ufo_speed*0.7*dt
        pos[1] -= right[1]*ufo_base.ufo_speed*0.7*dt
    if can_move and b'd' in keys_down:
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
    if ufo_beam.beam_cooldown_left > 0.0:
        ufo_beam.beam_cooldown_left = max(0.0, ufo_beam.beam_cooldown_left - dt)

    # Abduction check
    if ufo_beam.beam_active:
        h = max(1.0, pos[2])
        top_r = 6.0
        radius_ground = math.tan(math.radians(ufo_beam.beam_angle_deg))*h + top_r
        for hmn in abduction.humans:
            if hmn['abducted']: continue
            dx = hmn['x'] - pos[0]
            dy = hmn['y'] - pos[1]
            dist = math.hypot(dx, dy)
            if dist <= radius_ground * 0.75:
                target = max(0.0, pos[2]-6.0)
                hmn['lifted'] = min(target, hmn['lifted'] + 30.0*dt)
                if hmn['lifted'] >= target-0.1:
                    hmn['abducted'] = True
                    abduction.score += 1

     # Camera follow
    cam_offset = -220.0
    ufo_base.cam_pos[0] = pos[0] + math.cos(math.radians(ufo_base.ufo_yaw))*cam_offset
    ufo_base.cam_pos[1] = pos[1] + math.sin(math.radians(ufo_base.ufo_yaw))*cam_offset
    ufo_base.cam_pos[2] = 160.0
    ufo_base.cam_look[0], ufo_base.cam_look[1], ufo_base.cam_look[2] = pos[0], pos[1], 40.0

def display():
    global last_time
    now = time.time()
    if last_time is None: last_time = now
    dt = min(0.05, now-last_time)
    last_time = now
    update(dt)

    glClearColor(0.05,0.06,0.09,1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    ufo_base.setup_camera()
    ufo_base.setup_lights()
    ufo_base.draw_ground()
    ufo_base.draw_ufo()
    ufo_beam.draw_beam()
    abduction.draw_humans()

    
    status = f" Score={abduction.score} | Humans left={sum(1 for h in abduction.humans if not h['abducted'])} | B=beam (CD {ufo_beam.beam_cooldown_left:0.1f}s) | L=land/ascend"
    abduction.draw_text_2d(12, ufo_base.WIN_H-24, status, GLUT_BITMAP_HELVETICA_18)
    glutSwapBuffers()

def idle():
    glutPostRedisplay()

def on_key_down(key, x, y):
    keys_down.add(key)
    if key == b'\x1b':
        glutLeaveMainLoop()
    if key == b'b':
        ufo_beam.try_toggle_beam() 
    if key == b'r':
        abduction.spawn_humans()

def on_key_up(key, x, y):
    if key in keys_down: keys_down.remove(key)

def reshape(w,h):
    ufo_base.WIN_W, ufo_base.WIN_H = max(1,w), max(1,h)
    ufo_base.ASPECT = ufo_base.WIN_W/float(ufo_base.WIN_H)
    glViewport(0,0,ufo_base.WIN_W,ufo_base.WIN_H)

def main():
    abduction.spawn_humans()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(ufo_base.WIN_W, ufo_base.WIN_H)
    glutCreateWindow(b"Alien UFO Abduction - Modular Version")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(on_key_down)
    glutKeyboardUpFunc(on_key_up)
    glutReshapeFunc(reshape)
    glutMainLoop()

if __name__ == "__main__":
    main()
