"""
Solar System Simulation using OpenGL
A 3D interactive visualization of the solar system with textured planets and orbits.
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from PIL import Image
import time
import math

# Initialize GLUT for text rendering
glutInit()

# ---------------------------
# Global State Variables
# ---------------------------
start_time = time.time()
camera_distance = 30.0
camera_angle_x = 0.0
camera_angle_y = 0.0
last_mouse_x = 0
last_mouse_y = 0
mouse_pressed = False

# ---------------------------
# Window Setup
# ---------------------------
if not glfw.init():
    raise Exception("GLFW initialization failed")

window = glfw.create_window(1000, 800, "Solar System", None, None)
if not window:
    glfw.terminate()
    raise Exception("Window creation failed")

glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)

# Enable lighting
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# Set up light properties
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])
glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

# ---------------------------
# Mouse and Camera Controls
# ---------------------------
def mouse_button_callback(window, button, action, mods):
    """Handle mouse button press/release for camera rotation."""
    global mouse_pressed
    if button == glfw.MOUSE_BUTTON_LEFT:
        mouse_pressed = action == glfw.PRESS

def cursor_position_callback(window, xpos, ypos):
    """Handle mouse movement for camera rotation."""
    global last_mouse_x, last_mouse_y, camera_angle_x, camera_angle_y
    if mouse_pressed:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y
        camera_angle_x += dx * 0.3
        camera_angle_y += dy * 0.3
    last_mouse_x = xpos
    last_mouse_y = ypos

def scroll_callback(window, xoffset, yoffset):
    """Handle mouse scroll for camera zoom."""
    global camera_distance
    camera_distance -= yoffset * 2.0
    camera_distance = max(5.0, min(100.0, camera_distance))

# Register callbacks
glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.set_scroll_callback(window, scroll_callback)

# ---------------------------
# Helper Functions
# ---------------------------
def load_texture(path):
    """Load a texture from an image file."""
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.convert("RGB").tobytes()
    width, height = img.size
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return tex_id

def draw_orbit(radius):
    """Draw a circular orbit path."""
    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    for i in range(100):
        theta = 2 * np.pi * i / 100
        x = radius * np.cos(theta)
        z = radius * np.sin(theta)
        glVertex3f(x, 0, z)
    glEnd()

def draw_text(x, y, text):
    """Render text at specified 2D position."""
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(c))

def draw_skybox(texture, size=50):
    """Draw a textured skybox cube around the scene."""
    glBindTexture(GL_TEXTURE_2D, texture)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)

    # Front face
    glTexCoord2f(0, 0); glVertex3f(-size, -size, -size)
    glTexCoord2f(1, 0); glVertex3f(size, -size, -size)
    glTexCoord2f(1, 1); glVertex3f(size, size, -size)
    glTexCoord2f(0, 1); glVertex3f(-size, size, -size)

    # Back face
    glTexCoord2f(0, 0); glVertex3f(-size, -size, size)
    glTexCoord2f(1, 0); glVertex3f(size, -size, size)
    glTexCoord2f(1, 1); glVertex3f(size, size, size)
    glTexCoord2f(0, 1); glVertex3f(-size, size, size)

    # Left face
    glTexCoord2f(0, 0); glVertex3f(-size, -size, -size)
    glTexCoord2f(1, 0); glVertex3f(-size, -size, size)
    glTexCoord2f(1, 1); glVertex3f(-size, size, size)
    glTexCoord2f(0, 1); glVertex3f(-size, size, -size)

    # Right face
    glTexCoord2f(0, 0); glVertex3f(size, -size, -size)
    glTexCoord2f(1, 0); glVertex3f(size, -size, size)
    glTexCoord2f(1, 1); glVertex3f(size, size, size)
    glTexCoord2f(0, 1); glVertex3f(size, size, -size)

    # Top face
    glTexCoord2f(0, 0); glVertex3f(-size, size, -size)
    glTexCoord2f(1, 0); glVertex3f(size, size, -size)
    glTexCoord2f(1, 1); glVertex3f(size, size, size)
    glTexCoord2f(0, 1); glVertex3f(-size, size, size)

    # Bottom face
    glTexCoord2f(0, 0); glVertex3f(-size, -size, -size)
    glTexCoord2f(1, 0); glVertex3f(size, -size, -size)
    glTexCoord2f(1, 1); glVertex3f(size, -size, size)
    glTexCoord2f(0, 1); glVertex3f(-size, -size, size)

    glEnd()

def draw_ring(inner_radius, outer_radius, segments=128):
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        theta = 2 * np.pi * i / segments
        cos_t = np.cos(theta)
        sin_t = np.sin(theta)

        # Radial mapping (center → edge)
        glTexCoord2f(0, i / segments)
        glVertex3f(inner_radius * cos_t, inner_radius * sin_t, 0)

        glTexCoord2f(1, i / segments)
        glVertex3f(outer_radius * cos_t, outer_radius * sin_t, 0)
    glEnd()


def setup_camera():
    """Configure camera projection and view."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1000/800, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -camera_distance)
    glRotatef(camera_angle_y, 1, 0, 0)
    glRotatef(camera_angle_x, 0, 1, 0)

# ---------------------------
# Solar System Data
# ---------------------------
sun_radius = 1.5
sun_texture = load_texture("assets/sun.jpg")
sun_spin_angle = 0.0

saturn_ring_texture = load_texture("assets/saturn_rings.png")

# Planet data: name, radius, texture file, orbit radius, angular speed
planets_data = [
    ("Mercury", 0.1, "assets/mercury.jpg", 2.0, 4.15),
    ("Venus", 0.2, "assets/venus.jpg", 3.0, 1.62),
    ("Earth", 0.25, "assets/earth.jpg", 4.0, 1.0),
    ("Mars", 0.15, "assets/mars.jpg", 5.0, 0.53),
    ("Jupiter", 0.5, "assets/jupiter.jpg", 7.0, 0.084),
    ("Saturn", 0.45, "assets/saturn.jpg", 9.0, 0.034),
    ("Uranus", 0.35, "assets/uranus.jpg", 11.0, 0.011),
    ("Neptune", 0.35, "assets/neptune.jpg", 13.0, 0.006),
]

planets = []
for name, radius, tex_file, orbit, speed in planets_data:
    tex = load_texture(tex_file)
    planet_dict = {
        "name": name,
        "radius": radius,
        "texture": tex,
        "orbit": orbit,
        "speed": speed,
        "spin_angle": 0.0,
        "spin_speed": 0.05,
        "angle": 0.0
    }

    # Add rings to Saturn
    if name == "Saturn":
        planet_dict["has_rings"] = True
        planet_dict["ring_inner"] = radius * 1.2
        planet_dict["ring_outer"] = radius * 2.0
        # You can create a ring texture or use a color
        planet_dict["ring_texture"] = saturn_ring_texture  # Reuse Saturn texture, or load a separate ring texture
    else:
        planet_dict["has_rings"] = False

    planets.append(planet_dict)

background_texture = load_texture("assets/background.jpg")

# ---------------------------
# Main Rendering Loop
# ---------------------------
last_time = time.time()
quad = gluNewQuadric()
gluQuadricTexture(quad, GL_TRUE)

while not glfw.window_should_close(window):
    # Calculate delta time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Update planet and sun rotations
    sun_spin_angle += 0.01
    for p in planets:
        p["angle"] += p["speed"] * dt
        p["spin_angle"] += p["spin_speed"]

    # Calculate elapsed time in Earth years
    run_time = current_time - start_time
    earth_orbits = run_time / (2 * np.pi)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ---------------------------
    # Setup 3D Camera
    # ---------------------------
    setup_camera()

    # ---------------------------
    # Draw Background Skybox
    # ---------------------------
    glDepthMask(GL_FALSE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)  # Disable lighting for skybox

    glPushMatrix()
    glLoadIdentity()
    glRotatef(camera_angle_y, 1, 0, 0)
    glRotatef(camera_angle_x, 0, 1, 0)
    draw_skybox(background_texture)
    glPopMatrix()

    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    # ---------------------------
    # Set Light Position (at the Sun)
    # ---------------------------
    light_position = [0.0, 0.0, 0.0, 1.0]  # Positional light at origin (sun)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # ---------------------------
    # Draw Sun
    # ---------------------------
    # Disable lighting for the sun so it appears bright
    glDisable(GL_LIGHTING)
    glBindTexture(GL_TEXTURE_2D, sun_texture)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glRotatef(sun_spin_angle, 0, 0, 1)
    gluSphere(quad, sun_radius, 32, 32)
    glPopMatrix()
    # Re-enable lighting for planets
    glEnable(GL_LIGHTING)

    # ---------------------------
    # Draw Planets and Orbits
    # ---------------------------
    for p in planets:
        # Draw orbit line (disable lighting for white lines)
        glDisable(GL_LIGHTING)
        draw_orbit(p["orbit"])
        glEnable(GL_LIGHTING)

        # Calculate planet position
        x = p["orbit"] * math.cos(p["angle"])
        z = p["orbit"] * math.sin(p["angle"])

        # Draw planet
        glBindTexture(GL_TEXTURE_2D, p["texture"])
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(-90, 1, 0, 0)
        glRotatef(23.5, 0, 0, 1)  # Axial tilt
        if not p["name"] == "Saturn":
            glRotatef(p["spin_angle"], 0, 0, 1)
        gluSphere(quad, p["radius"], 32, 32)

        # Draw rings if planet has them (Saturn)
        if p.get("has_rings", False):
            glDisable(GL_CULL_FACE)
            glBindTexture(GL_TEXTURE_2D, saturn_ring_texture)

            # Offset rings slightly to avoid z-fighting with planet
            glTranslatef(0, 0.0001, 0)
            # Tilt rings with planet (Saturn ~26.7°)
            glRotatef(26.7, 1, 0, 0)
            draw_ring(p["ring_inner"], p["ring_outer"])


            glEnable(GL_TEXTURE_2D)
            glColor3f(1, 1, 1)  # Reset color

        glPopMatrix()

    # ---------------------------
    # Draw HUD (Years Counter)
    # ---------------------------
    glDisable(GL_LIGHTING)  # Disable lighting for HUD
    width, height = glfw.get_window_size(window)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    years_text = f"Years: {earth_orbits:.1f}"
    draw_text(width - 550, height * 0.85, years_text)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glfw.swap_buffers(window)
    glfw.poll_events()

# Cleanup
glfw.terminate()