# menu.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import ufo_base, abduction, city, magic_box, ufo_beam

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
    gluOrtho2D(0, ufo_base.WIN_W, 0, ufo_base.WIN_H)

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
    abduction.spawn_initial_humans()
    city.init_city()
    magic_box.reset_boxes()
    ufo_base.ufo_pos[:] = [0.0, 0.0, 60.0]
    ufo_base.ufo_yaw = 0.0
    ufo_beam.ufo_state = "flying"
    ufo_beam.beam_active = False
    abduction.score = 0
    print("[Game] Restarted")

def handle_menu_click(x, y):
    global game_state
    y = ufo_base.WIN_H - y
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
