import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time
import math

# Window setup
if not glfw.init():
    raise Exception("GLFW can't be initialized")

window = glfw.create_window(1000, 800, "Solar System", None, None)
glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)

# Star (Sun)
sun_radius = 1.5

# Planet data: (name, radius, color RGB, orbit radius, orbit speed rad/s)
planets = [
    ("Mercury", 0.1, (0.5, 0.5, 0.5), 2.0, 4.15),
    ("Venus",   0.2, (1.0, 0.7, 0.0), 3.0, 1.62),
    ("Earth",   0.25, (0.0, 0.5, 1.0), 4.0, 1.0),
    ("Mars",    0.15, (1.0, 0.0, 0.0), 5.0, 0.53),
    ("Jupiter", 0.5, (1.0, 0.5, 0.0), 7.0, 0.084),
    ("Saturn",  0.45, (1.0, 1.0, 0.5), 9.0, 0.034),
    ("Uranus",  0.35, (0.5, 1.0, 1.0), 11.0, 0.011),
    ("Neptune", 0.35, (0.0, 0.0, 1.0), 13.0, 0.006),
]

# Track angles for each planet
angles = [0.0 for _ in planets]

last_time = time.time()

# Main loop
while not glfw.window_should_close(window):
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    # Update planet angles
    for i, (_, _, _, _, speed) in enumerate(planets):
        angles[i] += speed * dt

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1000/800, 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -25)  # camera pull back

    # Draw Sun
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)  # yellow
    gluSphere(gluNewQuadric(), sun_radius, 32, 32)
    glPopMatrix()

    # Draw planets
    for i, (name, radius, color, orbit_radius, _) in enumerate(planets):
        x = orbit_radius * math.cos(angles[i])
        z = orbit_radius * math.sin(angles[i])
        glPushMatrix()
        glColor3f(*color)
        glTranslatef(x, 0.0, z)
        gluSphere(gluNewQuadric(), radius, 32, 32)
        glPopMatrix()

    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
