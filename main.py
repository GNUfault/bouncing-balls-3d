# bouncing-balls-3d - Bouncing Balls in 3D made with Pygame in Python
# Copyright (C) 2025  Connor Thomson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import colorsys

pygame.init()

screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h

pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL | FULLSCREEN)

actual_screen_info = pygame.display.Info()
WIDTH, HEIGHT = actual_screen_info.current_w, actual_screen_info.current_h

pygame.mouse.set_visible(False)

CAMERA_DISTANCE_FROM_ORIGIN = 10.0
FOV_Y = 55.0

half_fovy_rad = math.radians(FOV_Y / 2)
screen_edge_y_bound = CAMERA_DISTANCE_FROM_ORIGIN * math.tan(half_fovy_rad)
screen_edge_x_bound = screen_edge_y_bound * (WIDTH / HEIGHT)

REDUCTION_FACTOR = 0.55

X_BOUND = screen_edge_x_bound * REDUCTION_FACTOR
Y_BOUND = screen_edge_y_bound * REDUCTION_FACTOR

Z_PLAYFIELD_HALF_DEPTH = 5.0 
Z_BOUND_NEAR = -Z_PLAYFIELD_HALF_DEPTH
Z_BOUND_FAR = Z_PLAYFIELD_HALF_DEPTH

MAX_VELOCITY_COMPONENT = 0.08
MIN_INITIAL_VELOCITY_COMPONENT = 0.02

class Ball:
    def __init__(self, radius, initial_pos, initial_vel):
        self.radius = radius
        self.x, self.y, self.z = initial_pos
        self.dx, self.dy, self.dz = initial_vel
        
        self.hue = random.uniform(0, 1.0)
        self.hue_speed = random.uniform(0.005, 0.015)

    def update_position(self, x_bound, y_bound, z_bound_near, z_bound_far):
        self.x += self.dx
        self.y += self.dy
        self.z += self.dz

        if self.x + self.radius > x_bound:
            self.x = x_bound - self.radius
            self.dx *= -1
        elif self.x - self.radius < -x_bound:
            self.x = -x_bound + self.radius
            self.dx *= -1

        if self.y + self.radius > y_bound:
            self.y = y_bound - self.radius
            self.dy *= -1
        elif self.y - self.radius < -y_bound:
            self.y = -y_bound + self.radius
            self.dy *= -1

        if self.z + self.radius > z_bound_far:
            self.z = z_bound_far - self.radius
            self.dz *= -1
        elif self.z - self.radius < z_bound_near:
            self.z = z_bound_near + self.radius
            self.dz *= -1
            
    def update_color(self):
        self.hue += self.hue_speed
        if self.hue > 1.0:
            self.hue -= 1.0 

        self.current_color = colorsys.hls_to_rgb(self.hue, 0.7, 1.0)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3fv(self.current_color)

        sphere = gluNewQuadric()
        gluSphere(sphere, self.radius, 32, 32)
        gluDeleteQuadric(sphere)

        glPopMatrix()

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)

    glLightfv(GL_LIGHT0, GL_POSITION, (0, 10, 10, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))

    glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialfv(GL_FRONT, GL_SHININESS, 100.0)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, (WIDTH / HEIGHT), 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, -CAMERA_DISTANCE_FROM_ORIGIN,
              0, 0, 0,
              0, 1, 0)

init_opengl()

BALL_RADIUS = 0.5
NUM_BALLS = 10 
balls = []

for i in range(NUM_BALLS):
    initial_pos = (random.uniform(-X_BOUND + BALL_RADIUS, X_BOUND - BALL_RADIUS),
                   random.uniform(-Y_BOUND + BALL_RADIUS, Y_BOUND - BALL_RADIUS),
                   random.uniform(Z_BOUND_NEAR + BALL_RADIUS, Z_BOUND_FAR - BALL_RADIUS))
    
    initial_vel = (random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT),
                   random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT),
                   random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT))
    
    if abs(initial_vel[0]) < MIN_INITIAL_VELOCITY_COMPONENT: initial_vel = (MIN_INITIAL_VELOCITY_COMPONENT * random.choice([-1,1]), initial_vel[1], initial_vel[2])
    if abs(initial_vel[1]) < MIN_INITIAL_VELOCITY_COMPONENT: initial_vel = (initial_vel[0], MIN_INITIAL_VELOCITY_COMPONENT * random.choice([-1,1]), initial_vel[2])
    if abs(initial_vel[2]) < MIN_INITIAL_VELOCITY_COMPONENT: initial_vel = (initial_vel[0], initial_vel[1], MIN_INITIAL_VELOCITY_COMPONENT * random.choice([-1,1]))

    balls.append(Ball(BALL_RADIUS, initial_pos, initial_vel))

CLOCK = pygame.time.Clock()
FPS = 60

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN: 
            running = False

    for ball in balls:
        ball.update_position(X_BOUND, Y_BOUND, Z_BOUND_NEAR, Z_BOUND_FAR)
        ball.update_color()

    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball1 = balls[i]
            ball2 = balls[j]

            dx = ball2.x - ball1.x
            dy = ball2.y - ball1.y
            dz = ball2.z - ball1.z
            distance_squared = dx*dx + dy*dy + dz*dz
            
            min_distance = ball1.radius + ball2.radius
            min_distance_squared = min_distance * min_distance

            if distance_squared < min_distance_squared:
                distance = math.sqrt(distance_squared)
                overlap = min_distance - distance

                if distance == 0:
                    nx, ny, nz = random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)
                    norm_mag = math.sqrt(nx*nx + ny*ny + nz*nz)
                    if norm_mag > 0:
                        nx, ny, nz = nx/norm_mag, ny/norm_mag, nz/norm_mag
                    else:
                        nx, ny, nz = 1, 0, 0
                else:
                    nx, ny, nz = dx / distance, dy / distance, dz / distance

                ball1.x -= nx * overlap / 2
                ball1.y -= ny * overlap / 2
                ball1.z -= nz * overlap / 2

                ball2.x += nx * overlap / 2
                ball2.y += ny * overlap / 2
                ball2.z += nz * overlap / 2

                ball1.dx = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)
                ball1.dy = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)
                ball1.dz = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)
                
                ball2.dx = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)
                ball2.dy = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)
                ball2.dz = random.uniform(-MAX_VELOCITY_COMPONENT, MAX_VELOCITY_COMPONENT)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    gluLookAt(0, 0, -CAMERA_DISTANCE_FROM_ORIGIN,
              0, 0, 0,
              0, 1, 0)

    for ball in balls:
        ball.draw()

    pygame.display.flip()

    CLOCK.tick(FPS)

pygame.quit()
sys.exit()
