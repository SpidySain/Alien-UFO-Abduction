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
MAX_BOXES = 15 
SPAWN_INTERVAL = 8.0
last_spawn_time = 0

magic_boxes = []
box_counter = 0 

# Box types
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
    """Spawn a magic box near the UFO at its current height."""
    global box_counter
    

    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(20, 50)
    
    box_x = ufo_x + math.cos(angle) * distance
    box_y = ufo_y + math.sin(angle) * distance
    box_z = ufo_z  
    
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
        'life_time': 15.0 
    }
    
    magic_boxes.append(new_box)
    print(f"[Magic Box] Spawned {box_type} box (ID: {new_box['id']}) at ({box_x:.1f}, {box_y:.1f}, {box_z:.1f})")

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
        abduction.score += 10
    elif effect == "fake_abduction":
        pass

def check_collision(box):
    """Check if UFO is close enough to collect the box."""
    ufo_x, ufo_y, ufo_z = ufo_base.ufo_pos
    dx = box['x'] - ufo_x
    dy = box['y'] - ufo_y
    dz = box['z'] - ufo_z
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    return distance < 15.0

def update():
    """Update box logic every frame."""
    global magic_boxes, last_spawn_time
    
    current_time = time.time()
    
    if len(magic_boxes) < MAX_BOXES and (current_time - last_spawn_time) > SPAWN_INTERVAL:
        spawn_box()
        last_spawn_time = current_time
    
    # Update existing boxes
    for box in magic_boxes[:]:
        if box['collected']:
            continue
            
        # Check if box expired
        if (current_time - box['spawn_time']) > box['life_time']:
            magic_boxes.remove(box)
            print(f"[Magic Box] Box {box['id']} expired")
            continue
            
        # Check for collection
        if check_collision(box):
            box['collected'] = True
            apply_effect(box)
            magic_boxes.remove(box)
            print(f"[Magic Box] Box {box['id']} collected and removed")

def draw_box(box):
    """Draw a very colorful magic box with rainbow effects."""
    glPushMatrix()
    glTranslatef(box['x'], box['y'], box['z'])
    
    # Pulsing effect
    pulse = (math.sin(time.time() * 4 + box['id']) + 1) * 0.5
    scale = 1.0 + pulse * 0.3
    
    glScalef(scale, scale, scale)
    
    # Rainbow color cycling for extra vibrancy
    hue_shift = (time.time() * 0.5 + box['id'] * 0.2) % 1.0
    
    if box['type'] == "power_up":
        # Green power-up with rainbow glow
        glColor3f(0.0, 1.0, 0.0)  # Bright green base
    else:
        # Red trap with intense red
        glColor3f(1.0, 0.0, 0.0)  # Bright red base
    
    # Draw main cube
    glutSolidCube(MAGIC_BOX_SIZE)
    
    for i in range(3):
        glPushMatrix()
        glScalef(1.0 + i*0.1, 1.0 + i*0.1, 1.0 + i*0.1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(3 - i)
        if box['type'] == "power_up":
            # Green to cyan gradient
            glColor4f(0.0, 1.0 - i*0.3, 0.5 + i*0.1, 0.7 - i*0.2)
        else:
            # Red to orange gradient
            glColor4f(1.0, 0.5 - i*0.1, 0.0, 0.7 - i*0.2)
        glutSolidCube(MAGIC_BOX_SIZE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glPopMatrix()
    
    # Draw rotating symbol with bright color
    glPushMatrix()
    glRotatef(time.time() * 50, 0, 0, 1)  # Rotate symbol
    
    if box['type'] == "power_up":
        # Yellow plus sign
        glColor3f(1.0, 1.0, 0.0)  # Bright yellow
    else:
        # White exclamation mark
        glColor3f(1.0, 1.0, 1.0)  # Bright white
    
    if box['type'] == "power_up":
        glBegin(GL_QUADS)
        glVertex3f(-1, -0.5, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(1, -0.5, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(1, 0.5, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(-1, 0.5, MAGIC_BOX_SIZE/2 + 0.1)
        
        glVertex3f(-0.5, -1, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(0.5, -1, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(0.5, 1, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(-0.5, 1, MAGIC_BOX_SIZE/2 + 0.1)
        glEnd()
    else:
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -1, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(0.5, -1, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(0.5, 0.5, MAGIC_BOX_SIZE/2 + 0.1)
        glVertex3f(-0.5, 0.5, MAGIC_BOX_SIZE/2 + 0.1)
        glEnd()
        glTranslatef(0, -1.5, 0)
        glutSolidSphere(0.3, 6, 6)
    glPopMatrix()
    
    glPopMatrix()

def draw_boxes():
    """Draw all active magic boxes."""
    update() 
    
    for box in magic_boxes:
        if not box['collected']:
            draw_box(box)

def reset_boxes():
    """Clear all boxes (useful for game restart)."""
    global magic_boxes, last_spawn_time
    magic_boxes = []
    last_spawn_time = 0