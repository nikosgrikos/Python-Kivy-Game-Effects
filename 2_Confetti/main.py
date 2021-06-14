# Monkey Buster 2048 Tutorial Part 2 (See video on YouTube)
# Confetti flowing effect
# This code creates animates confetti flowing down the screen and fading into the background
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, Mesh
from kivy.clock import Clock
import random

# Set this to True if deploying on mobile phone
MOBILE = False
# Set this to True if deploying on MacOS
MACOS = False
# Set this to True if this is the deployed on a new phone!
MOBILE64 = True

# Size of screen to open
# Device 1: 720x1280 (Old Android)
# Device 2: 1440x2960 (Galaxy)
# Device 3: 768x1024 (Tablet)
if not(MOBILE):
    if MACOS:
        WINDOW_SIZE_X = 720*120/100  # Device 1: 120% of 720,  Device 2: 50% of 1440, Device 3: 150% of 768
        WINDOW_SIZE_Y = 1280*120/100 # Device 1: 120% of 1280, Device 2: 50% of 2960, Device 3: 150% of 1024
    else:
        WINDOW_SIZE_X = 720*60/100  # Device 1: 60% of 720,  Device 2: 25% of 1440, Device 3: 75% of 768
        WINDOW_SIZE_Y = 1280*60/100 # Device 1: 60% of 1280, Device 2: 25% of 2960, Device 3: 75% of 1024

    # Position of window for windows based platform
    if MACOS:
        Window.size = (WINDOW_SIZE_X/2, WINDOW_SIZE_Y/2)
    else:
        Window.size = (WINDOW_SIZE_X, WINDOW_SIZE_Y)

    Window.top = 32
    Window.left = 512
else:
    WINDOW_SIZE_X, WINDOW_SIZE_Y = Window.size

FULL_WINDOW_SIZE_X = WINDOW_SIZE_X
FULL_WINDOW_SIZE_Y = WINDOW_SIZE_Y

# Shorten the window if too wide
WINDOW_OFFSET_X = 0
if WINDOW_SIZE_X/WINDOW_SIZE_Y > 0.65:
    OLD_WINDOW_SIZE_X = WINDOW_SIZE_X
    WINDOW_SIZE_X = int(0.65*WINDOW_SIZE_Y)
    WINDOW_OFFSET_X = int((OLD_WINDOW_SIZE_X - WINDOW_SIZE_X)/2)

# This is the actual window the game is played on PC and mobile
WINDOW_RECT = WINDOW_OFFSET_X, 0, WINDOW_SIZE_X + WINDOW_OFFSET_X, WINDOW_SIZE_Y

# Offset position of the matrix
ORIGINAL_MATRIX_OFFSET_X = 20

# Pixel offset of matrix display, score display and next piece display (gap in between them)
RECT_OFFSET = int(WINDOW_SIZE_X / 45)

# Border width of each display in pixels
BORDERWIDTH_MATRIX = int(WINDOW_SIZE_X / 86) * 2

BACKGROUNDCOLOR = (15/255, 15/255, 20/255)
BORDERCOLOR = (140/255, 140/255, 140/255)
BACKGROUND_OPAQUE = (15/255, 15/255, 20/255, 0.5)
BLACK = (0, 0, 0)
RED = (1, 0, 0)

BLUE = (0/255,149/255,200/255)
LIME = (142/255,184/255,14/255)
PINK = (197/255,2/255,104/255)
ORANGE = (254/255, 128/255, 1/255)
DARK_GREEN = (34/255,100/255,34/255)

# Special effects variables
MAX_CONFETTI = 100

# Game state constants
C_PLAYING_GAME = 2
C_CONFETTI = 3

#_______________________________________________________________________________________________________________________

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click)

        # Set game variables
        self.set_game_variables()

        # Initialise special effects
        self.initialise_triggers()

        # Initialise special effects
        self.initialise_special_effects()

        # Initialise and call main function
        self.game_main()

    # ___________________________________________________________________________________________________________________

    def back_click(self, window, key, *largs):
        if key == 27:
            #self.unschedule_all_triggers()
            #self.current_screen = C_MENU
            return True

        return

    #___________________________________________________________________________________________________________________

    def set_game_variables(self):

        # Think of the screen as a matrix of 9 x 5
        # Row 1 - Score
        # Row 2-8 - Matrix for game play
        # Row 9 - Buttons
        self.MATRIX_WIDTH = 5
        self.MATRIX_HEIGHT = 7

        # Pixel offset of matrix from top and side of window
        offset_x = ORIGINAL_MATRIX_OFFSET_X

        # Determine the maximum size a block can be based on dimensions of window and matrix parameters
        x1, y1, x2, y2 = WINDOW_RECT
        split_y = int(((((y2-y1-RECT_OFFSET*4)/(self.MATRIX_HEIGHT+2)) * self.MATRIX_HEIGHT) - BORDERWIDTH_MATRIX*2)/self.MATRIX_HEIGHT)
        split_x = int((x2-x1-BORDERWIDTH_MATRIX*2-offset_x*2)/self.MATRIX_WIDTH)
        split = min(split_x, split_y)
        self.BLOCKSIZE = split

        matrix_rect_y = y1 + self.BLOCKSIZE + RECT_OFFSET*2

        # Adjust the starting Y coordinate of the matrix so that gaps between matrix and score are the same
        y = self.BLOCKSIZE * self.MATRIX_HEIGHT + BORDERWIDTH_MATRIX*2
        matrix_rect_y += int((y2-y-self.BLOCKSIZE*2-RECT_OFFSET*4)/2)

        # Adjust the starting X coordinate of the matrix
        x = self.BLOCKSIZE * self.MATRIX_WIDTH + BORDERWIDTH_MATRIX*2 + offset_x*2
        offset_x += int(x1/2) + int((x2-x)/2)

        # Determine exact pixel length endpoint of matrix
        matrix_rect_x = offset_x + BORDERWIDTH_MATRIX * 2 + self.BLOCKSIZE * self.MATRIX_WIDTH

        # Define the areas of the matrix
        self.MATRIX_RECT = (offset_x, matrix_rect_y, matrix_rect_x,
                            matrix_rect_y + BORDERWIDTH_MATRIX*2 + self.BLOCKSIZE*self.MATRIX_HEIGHT)

        x1, y1, x2, y2 = WINDOW_RECT
        self.SCORE_RECT = x1 + RECT_OFFSET, y2 - RECT_OFFSET - self.BLOCKSIZE, x2 - RECT_OFFSET, y2 - RECT_OFFSET
        self.BUTTON_RECT = x1 + RECT_OFFSET, y1 + RECT_OFFSET, x2 - RECT_OFFSET, y1 + RECT_OFFSET + self.BLOCKSIZE

        return

    # __________________________________________________________________________________________________________________

    def initialise_triggers(self):

        # Triggers used in the game
        self.trigger1 = Clock.create_trigger(self.special_effects_confetti_run, 0.01)

        return
    # __________________________________________________________________________________________________________________

    def game_main(self):

        self.current_screen = C_CONFETTI
        self.draw_canvas()
        self.special_effects_confetti()

        return

    # __________________________________________________________________________________________________________________

    def draw_canvas(self):

        # Clear the canvas
        self.canvas.clear()
        self.canvas.after.clear()

        # Draw the screen
        self.draw_score_section()
        self.draw_matrix_section()
        self.draw_button_section()

        return

    # ___________________________________________________________________________________________________________________

    def draw_score_section(self):

        self.display_rect(self.SCORE_RECT, border_width=1, color=BLUE)

        return

    # ___________________________________________________________________________________________________________________

    def draw_matrix_section(self):

        self.display_rect(self.MATRIX_RECT, border_width=BORDERWIDTH_MATRIX, color=BACKGROUNDCOLOR)

        # Draw a grid like pattern
        bw = 1
        x1, y1, x2, y2 = self.MATRIX_RECT
        x1 += BORDERWIDTH_MATRIX
        y1 += BORDERWIDTH_MATRIX
        x2 -= BORDERWIDTH_MATRIX
        y2 -= BORDERWIDTH_MATRIX

        for y in range(self.MATRIX_HEIGHT + 1):
            yy1 = y1 + y*self.BLOCKSIZE
            with self.canvas:
                Color(rgb=RED)
                Rectangle(pos=(x1, yy1), size=((x2 - x1), bw))

        for x in range(self.MATRIX_WIDTH + 1):
            xx1 = x1 + x*self.BLOCKSIZE
            with self.canvas:
                Color(rgb=RED)
                Rectangle(pos=(xx1, y1), size=(bw, (y2-y1)))

        return

    # ___________________________________________________________________________________________________________________

    def draw_button_section(self):

        self.display_rect(self.BUTTON_RECT, border_width=1, color=PINK)

        return

    # ___________________________________________________________________________________________________________________

    def display_rect(self, rect, border_width=None, color=None, y_offset=None):

        # Draw the provided rectangle with border
        x1, y1, x2, y2 = rect
        if y_offset:
            y1 -= y_offset
            y2 -= y_offset
        if border_width:
            bw = border_width
        else:
            bw = 1
        if not color:
            color = BACKGROUNDCOLOR
        with self.canvas:
            Color(rgb=BORDERCOLOR)
            Rectangle(pos=(x1, y1), size=(x2 - x1, y2 - y1))
            Color(rgb=color)
            Rectangle(pos=(x1 + bw, y1 + bw), size=((x2 - x1) - bw * 2, (y2 - y1) - bw * 2))

        return

    # ___________________________________________________________________________________________________________________

    def special_effects_confetti(self):

        # Remove explosion effects
        self.initialise_special_effects()

        for x in range(0, MAX_CONFETTI):
            self.special_effects_confetti_set(x)

        if not(self.trigger1.is_triggered):
            self.trigger1 = Clock.schedule_interval(self.special_effects_confetti_run, 0.05)

        return

    # ___________________________________________________________________________________________________________________

    def initialise_special_effects(self):

        blocks = MAX_CONFETTI
        self.blocks_position = [(None, None, None) for x in range(blocks)]
        self.blocks_colour = [(None, None, None, None) for x in range(blocks)]
        self.blocks_velocity = [(None, None) for x in range(blocks)]
        self.blocks_oscillation = [(None, None, None, None) for x in range(MAX_CONFETTI)]
        self.blocks_oscillation_increments = [(None, None, None, None) for x in range(MAX_CONFETTI)]

    # ___________________________________________________________________________________________________________________

    def special_effects_confetti_set(self, x):

        x1, y1, x2, y2 = self.MATRIX_RECT
        min_x = 0
        max_x = x2 - x1
        min_y = -self.BLOCKSIZE
        max_y = 0
        min_z = int(self.BLOCKSIZE/10)
        max_z = int(self.BLOCKSIZE/5)
        min_xv = -int(self.BLOCKSIZE/32)
        max_xv = int(self.BLOCKSIZE/16)
        min_yv = int(self.BLOCKSIZE/16)
        max_yv = int(self.BLOCKSIZE/8)
        min_osc = -2
        max_osc = 2

        i = random.randrange(min_x, max_x)
        j = random.randrange(min_y, max_y)
        k = random.randrange(min_z, max_z)
        self.blocks_position[x] = i, j, k

        k1 = random.randrange(255)
        k2 = random.randrange(255)
        k3 = random.randrange(255)
        self.blocks_colour[x] = k1 / 255, k2 / 255, k3 / 255, 0.5

        l = random.randrange(min_xv, max_xv)
        m = random.randrange(min_yv, max_yv)
        self.blocks_velocity[x] = l, m

        a, b, c, d, = 0, 0, 0, 0
        while a == 0:
            a = random.randrange(min_osc, max_osc)
            c = -a
        while b == 0:
            b = random.randrange(min_osc, max_osc)
            d = -b
        self.blocks_oscillation_increments[x] = a, b, c, d
        self.blocks_oscillation[x] = 0, 0, 0, 0

    # ___________________________________________________________________________________________________________________

    def special_effects_confetti_run(self, dt):

        self.draw_canvas()

        blocks = MAX_CONFETTI
        x1, y1, x2, y2 = WINDOW_RECT
        for x in range(0, blocks):
            v1, v2 = self.blocks_velocity[x]
            i, j, k = self.blocks_position[x]
            self.blocks_position[x] = i + v1, j + v2, k
            l, m, n, o = self.blocks_colour[x]
            l -= 2 / 255
            m -= 2 / 255
            n -= 2 / 255
            faded_count = 0
            if l < 15 / 255:
                l = 15 / 255
                faded_count += 1
            if m < 15 / 255:
                m = 15 / 255
                faded_count += 1
            if n < 20 / 255:
                n = 20 / 255
                faded_count += 1

            faded = (faded_count == 3)
            self.blocks_colour[x] = l, m, n, o

            colour = self.blocks_colour[x]
            x_pos, y_pos, x_size = self.blocks_position[x]
            x_pos += x1
            y_pos = y2 - y_pos
            y_size = x_size

            a, b, c, d = self.blocks_oscillation[x]
            e, f, g, h = self.blocks_oscillation_increments[x]
            a += e
            b += f
            c += g
            d += h
            if abs(a) >= x_size/4:
                e = -e
            if abs(b) >= x_size/4:
                f = -f
            if abs(c) >= x_size/4:
                g = -g
            if abs(d) >= x_size/4:
                h = -h
            self.blocks_oscillation[x] = a, b, c, d
            self.blocks_oscillation_increments[x] = e, f, g, h

            vertices = [x_pos + d, y_pos + c, 0, 0,
                        x_pos + x_size + d, y_pos + c, 0, 0,
                        x_pos + x_size + b, y_pos + y_size + a, 0, 0,
                        x_pos + b, y_pos + y_size + a, 0, 0,
                        x_pos + d, y_pos + c, 0, 0]

            indices = [0, 1, 2, 3, 0]

            with self.canvas:
                Color(rgba=colour)
                Mesh(colour=colour, vertices=vertices, indices=indices, mode='triangle_fan')

            if faded or x_pos < 0 or x_pos > FULL_WINDOW_SIZE_X or y_pos < 0:
                self.special_effects_confetti_set(x)

        return

    #___________________________________________________________________________________________________________________

    def mouse_in_rect(self, x, y, rect):

        x1, y1, x2, y2 = rect
        return x1 < x < x2 and y1 < y < y2

    #___________________________________________________________________________________________________________________

    def unschedule_all_triggers(self):

        if self.trigger1.is_triggered:
            Clock.unschedule(self.trigger1)

        return

    #___________________________________________________________________________________________________________________

    def on_touch_down(self, touch):

        if self.current_screen == C_CONFETTI:
            exit()

        return

    #___________________________________________________________________________________________________________________

    def on_touch_up(self, touch):

        return
    #___________________________________________________________________________________________________________________

    def on_touch_move(self, touch):

        return
#_______________________________________________________________________________________________________________________

class GameApp(App):
    def build(self):
        return Game()

if __name__ == "__main__":
    GameApp().run()
