import sys
import random
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Global variables
ball_x = 400
ball_y = 50
ball_radius = 10
ball_dx = 2
ball_dy = 2

paddle_x = 350
paddle_y = 20
paddle_width = 100
paddle_height = 10

window_width = 800
window_height = 600

num_blocks_x = 10
num_blocks_y = 6
block_width = window_width // num_blocks_x
block_height = 30

blocks = [[1 for a in range(num_blocks_x)] for b in range(num_blocks_y)]  # 1 represents an active block, 0 represents a destroyed block ,,, (2D, NUM_BLOCKS_Y = COLUMN)

paddle_colors = [
   (0.0, 1.0, 0.0),  # Green
   (1.0, 0.0, 0.0),  # Red
   (0.0, 0.0, 1.0),  # Blue
   (1.0, 1.0, 0.0),  # Yellow
]

current_paddle_color = random.choice(paddle_colors)

game_over = False
is_paused = False
score = 0

def init():
   glutInit(sys.argv)
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(window_width, window_height)
   glutCreateWindow(b"DX-Ball")
   glutDisplayFunc(draw)
   glutKeyboardFunc(keyboard)
   glutTimerFunc(16, update, 0) #called the def update here , time,update,update e value pass korsi kina
                               #GLUT TIMER  schedules the update() function to be called repeatedly at the specified time interval, 16 miliseconds in this case
   glClearColor(0.0, 0.0, 0.0, 0.0)
   gluOrtho2D(0, window_width, 0, window_height)


def draw_circle(x, y, radius):
   num_segments = 100
   angle_increment = 2.0 * math.pi / num_segments      #calculate angle based on current iteration

   glBegin(GL_TRIANGLE_FAN)   #akta series of triangle draw korbe that shares a common central vertex, creating a filled circle

   for i in range(num_segments + 1):
       angle = i * angle_increment
       dx = radius * math.cos(angle) #horaizontal displacement
       dy = radius * math.sin(angle)  #vartical displacement
       glVertex2f(x + dx, y + dy)  #This function is called inside a loop to define the vertices for the circle's outline.

   glEnd()

def draw_rectangle(x, y, width, height, color):
   glColor3f(*color)
   glBegin(GL_QUADS)

   glVertex2f(x, y)    #This function is used to draw both the paddle and the blocks in the game.
   glVertex2f(x + width, y)
   glVertex2f(x + width, y + height)
   glVertex2f(x, y + height)
   glEnd()

   #why use glvertex2f?
   # => glVertex2f is responsible for specifying the position of vertices in the OpenGL coordinate system.
   # This is crucial for defining the shapes that are drawn on the screen, whether they are circles,
   # rectangles, or other geometric forms.

def draw_blocks():
   for i in range(num_blocks_y):                                #The patterns include the top row (i == 0), the bottom row (i == 5),
                                                                    # the leftmost column (j == 0), the rightmost column (j == 9),
                                                                    # and a group of blocks in the middle (1 < i < 4 and 3 <= j <= 6).
       for j in range(num_blocks_x):
           if blocks[i][j]:
               if i == 0 or i==5 or j==0 or j == 9 or (1<i<4 and 3<=j<=6):
                   draw_rectangle(j * block_width, window_height - (i + 1) * block_height, block_width, block_height, (0.5, 0.3, 1.7))
               else:
                   #glColor3f(1.0, 0.0, 0.0)
                   draw_rectangle(j * block_width, window_height - (i + 1) * block_height, block_width, block_height, (0.0, 0.0, 1.0))

def draw_text(x, y, text):
   glRasterPos2f(x, y)
   for char in text:
       glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_score():
   glColor3f(1.0, 1.0, 1.0)
   draw_text(window_width - 100, window_height - 30, f"Score: {score}")

def draw():
   global game_over

   glClear(GL_COLOR_BUFFER_BIT)

   # Draw the ball
   glColor3f(1.0, 1.0, 1.0)
   draw_circle(ball_x, ball_y, ball_radius)

   # Draw the paddle
   global current_paddle_color
   draw_rectangle(paddle_x, paddle_y, paddle_width, paddle_height, current_paddle_color)

   # Draw the blocks
   draw_blocks()

   # Draw the score
   draw_score()

   if game_over:
       glColor3f(1.0, 0.0, 0.0)
       draw_text(window_width // 2 - 50, window_height // 2, "Game Over")
       glutSwapBuffers()
       return

   glutSwapBuffers() #refresh rate of the screeen

def update(value):
   global ball_x, ball_y, ball_dx, ball_dy, game_over, score

   if game_over:
       return

   if not is_paused:
       # Update ball position
       if score>10 and score<=20:
           ball_x += ball_dx+ ball_dx//4
           ball_y += ball_dy+ ball_dy//4
       elif 20<score<=40:
           ball_x += ball_dx + ball_dx//2
           ball_y += ball_dy + ball_dy//2
       elif score>40:
           ball_x += ball_dx + ball_dx
           ball_y += ball_dy + ball_dy
       else:
           ball_x += ball_dx
           ball_y += ball_dy

       # Check for collisions with walls
       if ball_x + ball_radius > window_width or ball_x - ball_radius < 0: #1ST ONE RIGHT EDGE , 2ND E LEFT EDGE
           ball_dx *= -1                                                    #BOUNCE BACK THE BALL

       if ball_y + ball_radius > window_height: #ball hits the Bottom
           game_over = True
           ball_dy *= -1

       if ball_y - ball_radius < 0:
           ball_dy *= -1

       # Check for collision with the paddle
       if (
           ball_x >= paddle_x
           and ball_x <= paddle_x + paddle_width
           and ball_y - ball_radius <= paddle_y + paddle_height
       ):
           ball_dy *= -1
           change_paddle_color()

       # Check for collision with blocks
       hit_block_y = (window_height - ball_y) // block_height #row hit
       hit_block_x = ball_x // block_width                    #column hit
       if hit_block_y >= 0 and hit_block_y < num_blocks_y and hit_block_x >= 0 and hit_block_x < num_blocks_x and blocks[hit_block_y][hit_block_x]: #column, row, koyta active ase
           ball_dy *= -1
           blocks[hit_block_y][hit_block_x] = 0
           #global score
           score += 2

       # Check for game over condition
       if ball_y - ball_radius < 0:
           game_over = True

   glutPostRedisplay()  #triggering the redrawing of the screen using
   glutTimerFunc(16, update, 0)

def change_paddle_color():
   global current_paddle_color
   current_paddle_color = random.choice(paddle_colors)

def generate_random_points():
   glPushMatrix()
   glTranslatef(0, 0, 0)
   glColor3f(1.0, 1.0, 1.0)
   for _ in range(10):
       x = random.randint(0, window_width // 2)
       y = random.randint(window_height // 2, window_height)
       draw_circle(x, y, 3)
   glPopMatrix()

def keyboard(key, x, y):
   global paddle_x, is_paused

   if key == b'q':
       sys.exit(0)
   elif key == b'a' and paddle_x > 0:
       paddle_x -= 20
   elif key == b'd' and paddle_x + paddle_width < window_width:
       paddle_x += 20
   elif key == b'p':
       is_paused = not is_paused

if __name__ == "__main__":
   init()
   glutMainLoop()

