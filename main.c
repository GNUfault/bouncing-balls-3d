#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <GL/glu.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

#define NUM_BALLS 50
#define BALL_RADIUS 0.3f
#define BALL_SPEED 0.08f
#define PI 3.14159265359f

int WIDTH, HEIGHT;

typedef struct {
    float x, y, z;
    float dx, dy, dz;
    float hue, hue_speed;
    float r, g, b;
} Ball;

Ball balls[NUM_BALLS];

void hsv_to_rgb(float h, float s, float v, float* r, float* g, float* b) {
    int i = (int)(h * 6);
    float f = h * 6 - i;
    float p = v * (1 - s), q = v * (1 - f * s), t = v * (1 - (1 - f) * s);
    switch (i % 6) {
        case 0: *r = v, *g = t, *b = p; break;
        case 1: *r = q, *g = v, *b = p; break;
        case 2: *r = p, *g = v, *b = t; break;
        case 3: *r = p, *g = q, *b = v; break;
        case 4: *r = t, *g = p, *b = v; break;
        case 5: *r = v, *g = p, *b = q; break;
    }
}

void init_ball(Ball* b) {
    b->x = ((float)rand() / RAND_MAX - 0.5f) * 6.0f;
    b->y = ((float)rand() / RAND_MAX - 0.5f) * 6.0f;
    b->z = ((float)rand() / RAND_MAX - 0.5f) * 6.0f;
    float vx = ((float)rand() / RAND_MAX * 2 - 1);
    float vy = ((float)rand() / RAND_MAX * 2 - 1);
    float vz = ((float)rand() / RAND_MAX * 2 - 1);
    float mag = sqrtf(vx * vx + vy * vy + vz * vz);
    if (mag == 0.0f) { vx = 1.0f; vy = 0.0f; vz = 0.0f; mag = 1.0f; }
    b->dx = vx / mag * BALL_SPEED;
    b->dy = vy / mag * BALL_SPEED;
    b->dz = vz / mag * BALL_SPEED;
    b->hue = ((float)rand() / RAND_MAX);
    b->hue_speed = 0.005f + ((float)rand() / RAND_MAX) * 0.01f;
}

void update_ball(Ball* b, float x_bound, float y_bound, float z_bound) {
    b->x += b->dx; b->y += b->dy; b->z += b->dz;
    if (b->x + BALL_RADIUS > x_bound || b->x - BALL_RADIUS < -x_bound) b->dx *= -1;
    if (b->y + BALL_RADIUS > y_bound || b->y - BALL_RADIUS < -y_bound) b->dy *= -1;
    if (b->z + BALL_RADIUS > z_bound || b->z - BALL_RADIUS < -z_bound) b->dz *= -1;
    b->hue += b->hue_speed;
    if (b->hue > 1.0f) b->hue -= 1.0f;
    hsv_to_rgb(b->hue, 1.0f, 0.7f, &b->r, &b->g, &b->b);
}

void draw_sphere(float radius, int slices, int stacks) {
    for (int i = 0; i <= stacks; ++i) {
        float lat0 = PI * (-0.5f + (float)(i - 1) / stacks);
        float z0 = sinf(lat0) * radius;
        float zr0 = cosf(lat0) * radius;
        float lat1 = PI * (-0.5f + (float)i / stacks);
        float z1 = sinf(lat1) * radius;
        float zr1 = cosf(lat1) * radius;
        glBegin(GL_QUAD_STRIP);
        for (int j = 0; j <= slices; ++j) {
            float lng = 2 * PI * (float)(j - 1) / slices;
            float x = cosf(lng), y = sinf(lng);
            glNormal3f(x * zr0, y * zr0, z0);
            glVertex3f(x * zr0, y * zr0, z0);
            glNormal3f(x * zr1, y * zr1, z1);
            glVertex3f(x * zr1, y * zr1, z1);
        }
        glEnd();
    }
}

void setup_lighting() {
    glEnable(GL_LIGHTING);
    glEnable(GL_LIGHT0);
    float pos[]     = {2.0f, 5.0f, 5.0f, 1.0f};
    float ambient[] = {0.2f, 0.2f, 0.2f, 1.0f};
    float diffuse[] = {0.7f, 0.7f, 0.7f, 1.0f};
    float specular[]= {1.0f, 1.0f, 1.0f, 1.0f};
    glLightfv(GL_LIGHT0, GL_POSITION, pos);
    glLightfv(GL_LIGHT0, GL_AMBIENT,  ambient);
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  diffuse);
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular);
    glEnable(GL_COLOR_MATERIAL);
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular);
    glMaterialf(GL_FRONT, GL_SHININESS, 64.0f);
}

int main() {
    srand((unsigned int)time(NULL));
    if (!glfwInit()) return -1;
    GLFWmonitor* monitor = glfwGetPrimaryMonitor();
    const GLFWvidmode* mode = glfwGetVideoMode(monitor);
    WIDTH = mode->width;
    HEIGHT = mode->height;
    GLFWwindow* window = glfwCreateWindow(WIDTH, HEIGHT, "Bouncing Balls 3D", monitor, NULL);
    if (!window) return -1;
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);
    glewInit();
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_HIDDEN);
    glEnable(GL_DEPTH_TEST);
    glClearColor(0.05f, 0.05f, 0.1f, 1.0f);
    glMatrixMode(GL_PROJECTION);
    gluPerspective(55.0f, (float)WIDTH / HEIGHT, 0.1f, 100.0f);
    glMatrixMode(GL_MODELVIEW);
    setup_lighting();
    for (int i = 0; i < NUM_BALLS; i++) init_ball(&balls[i]);

    float fovy_rad = 55.0f * PI / 180.0f;
    float view_height = 10.0f * tanf(fovy_rad / 2.0f);
    float view_width  = view_height * ((float)WIDTH / HEIGHT);
    float scale = 0.65f;
    float x_bound = view_width * scale;
    float y_bound = view_height * scale;
    float z_bound = 6.0f * scale;

    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glLoadIdentity();
        gluLookAt(0, 0, -10, 0, 0, 0, 0, 1, 0);
        for (int i = 0; i < NUM_BALLS; i++) {
            update_ball(&balls[i], x_bound, y_bound, z_bound);
            glPushMatrix();
            glTranslatef(balls[i].x, balls[i].y, balls[i].z);
            glColor3f(balls[i].r, balls[i].g, balls[i].b);
            draw_sphere(BALL_RADIUS, 20, 20);
            glPopMatrix();
        }
        glfwSwapBuffers(window);
        glfwPollEvents();
        for (int key = GLFW_KEY_SPACE; key <= GLFW_KEY_LAST; key++) {
            if (glfwGetKey(window, key) == GLFW_PRESS) {
                glfwSetWindowShouldClose(window, GLFW_TRUE);
                break;
            }
        }
    }
    glfwTerminate();
    return 0;
}
