from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import math
import time
import ufo_base
import ufo_beam
import abduction

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
    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    
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
    effect = box['effect']
    box_type = "Power-up" if box['type'] == "power_up" else "Trap"
    effect_name = effect.replace('_', ' ').title()
    print(f"[Magic Box] Collected: {box_type} - {effect_name}")
    
    if effect == "beam_wider":
        ufo_beam.beam_angle_deg = min(45.0, ufo_beam.beam_angle_deg + 5.0)
    elif effect == "beam_narrow":
        ufo_beam.beam_angle_deg = max(5.0, ufo_beam.beam_angle_deg - 5.0)
    elif effect == "beam_stronger":
        pass
    elif effect == "beam_slower":
        pass
    elif effect == "cooldown_reset":
        ufo_beam.beam_cooldown_left = 0.0
    elif effect == "cooldown_extend":
        ufo_beam.beam_cooldown_left += 5.0
    elif effect == "score_bonus":
        abduction.score += 15
    elif effect == "fake_abduction":
        pass

def update():
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
    update() 
    
    for box in magic_boxes:
        if not box['collected']:
            draw_box(box)

def reset_boxes():
    """Clear all boxes (useful for game restart)."""
    global magic_boxes, last_spawn_time, box_counter
    magic_boxes = []
    last_spawn_time = 0
    box_counter = 0