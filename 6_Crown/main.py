# Monkey Buster 2048 Tutorial Part 6 (See video on YouTube)
# Crown animation display
# This code animates a crown, usually when a high score has been achieved at end of game
# You will need to create a "Fonts" folder and place "debussy.ttf" in there. Try www.cooltext.com
# You will need to create a "Resources" folder and place 5 x .png images in there for your buttons
# You will also need a "Resources/crown.png" image to display the crown

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivy.clock import Clock

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
WHITE = (1, 1, 1)

BLUE = (0/255,149/255,200/255)
LIME = (142/255,184/255,14/255)
PINK = (197/255,2/255,104/255)
ORANGE = (254/255, 128/255, 1/255)
DARK_GREEN = (34/255,100/255,34/255)

# Game state constants
C_PLAYING_GAME = 2

# Explosion instructions
C_SCROLL_LEFT = 1
C_SCROLL_RIGHT = 2
C_SCROLL_UP = 3
C_SCROLL_DOWN = 4

MAX_CROWN_STEPS = 10

#_______________________________________________________________________________________________________________________

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click)

        # Set game variables
        self.set_game_variables()

        # Initialise triggers
        self.initialise_triggers()

        # Initialise and call main function
        self.game_main()

    # ___________________________________________________________________________________________________________________

    def back_click(self, window, key, *largs):
        if key == 27:
            #self.unschedule_all_triggers()
            #self.Game_menu()
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
        split_y = int(((((y2-y1-RECT_OFFSET*4)/9) * self.MATRIX_HEIGHT) - BORDERWIDTH_MATRIX*2)/self.MATRIX_HEIGHT)
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

        x1, y1, x2, y2 = self.BUTTON_RECT
        size = int((x2-x1-RECT_OFFSET*4)/5)
        self.BUTTON_1_RECT = x1, y1, x1 + size, y1 + size
        x1, y1, x2, y2 = self.BUTTON_1_RECT
        self.BUTTON_2_RECT = x2 + RECT_OFFSET, y1, x2 + RECT_OFFSET + size, y2
        x1, y1, x2, y2 = self.BUTTON_2_RECT
        self.BUTTON_3_RECT = x2 + RECT_OFFSET, y1, x2 + RECT_OFFSET + size, y2
        x1, y1, x2, y2 = self.BUTTON_3_RECT
        self.BUTTON_4_RECT = x2 + RECT_OFFSET, y1, x2 + RECT_OFFSET + size, y2
        x1, y1, x2, y2 = self.BUTTON_4_RECT
        self.BUTTON_5_RECT = x2 + RECT_OFFSET, y1, x2 + RECT_OFFSET + size, y2

        self.BANK_RECT = self.BUTTON_3_RECT

        # Determine resting place of crown image
        x1, y1, x2, y2 = self.MATRIX_RECT
        x1 += self.BLOCKSIZE
        x2 -= self.BLOCKSIZE
        y1 += self.BLOCKSIZE*4
        y2 = y1 + int((x2-x1)/2)
        self.CROWN_RECT = x1, y1, x2, y2

        return

    # __________________________________________________________________________________________________________________

    def initialise_triggers(self):

        # Triggers used in the game
        self.trigger1 = Clock.create_trigger(self.animate_crown_run, 0.05)

        return
    # ___________________________________________________________________________________________________________________

    def initialise_special_effects(self):

        return
    # __________________________________________________________________________________________________________________

    def game_main(self):

        self.current_screen = C_PLAYING_GAME

        # Initialise special effects
        self.initialise_special_effects()

        self.draw_canvas()

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

        x1, y1, x2, y2 = self.BUTTON_1_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_1.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        x1, y1, x2, y2 = self.BUTTON_2_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_2.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        x1, y1, x2, y2 = self.BUTTON_3_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/banana_bank.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        x1, y1, x2, y2 = self.BUTTON_4_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_3.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        x1, y1, x2, y2 = self.BUTTON_5_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_5.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

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

    #___________________________________________________________________________________________________________________

    def animate_crown_run(self, dt):

        self.draw_canvas()
        x1, y1, x2, y2 = self.CROWN_RECT
        increment = int(self.BLOCKSIZE/4)
        x1 -= increment*self.crown_index*2
        x2 += increment*self.crown_index*2
        y1 -= increment*self.crown_index
        y2 += increment*self.crown_index

        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/crown.png', pos=(x1, y1), size=(x2-x1, y2-y1))

        if self.crown_index > 0:
            self.crown_index -=1
        else:
            self.display_congratulations()

        return

    #___________________________________________________________________________________________________________________

    def display_congratulations(self):

        x1, y1, x2, y2 = self.CROWN_RECT
        y1 = y2
        y2 = y1 + int(self.BLOCKSIZE/2)
        fontsize = int(self.BLOCKSIZE/2)

        text = 'Congratulations!'
        with self.canvas:
            Color(rgb=WHITE)
            self.c_label = Label(text=text, halign="center", valign="bottom", size=(x2-x1, y2-y1),
                                 pos=(x1, y1), font_size=fontsize, font_name="Fonts/debussy.ttf")

        x1, y1, x2, y2 = self.CROWN_RECT
        y2 = y1
        y1 = y2 - int(self.BLOCKSIZE/2)
        fontsize = int(self.BLOCKSIZE/4)
        text = 'You made a top score!'
        with self.canvas:
            Color(rgb=WHITE)
            self.c_label2 = Label(text=text, halign="center", valign="bottom", size=(x2-x1, y2-y1),
                                  pos=(x1, y1), font_size=fontsize, font_name="Fonts/debussy.ttf")


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

        x, y = touch.pos
        if self.current_screen == C_PLAYING_GAME:

            if self.mouse_in_rect(x, y, self.BUTTON_1_RECT):
                self.crown_index = MAX_CROWN_STEPS
                if not (self.trigger1.is_triggered):
                    self.trigger1 = Clock.schedule_interval(self.animate_crown_run, 0.01)
            if self.mouse_in_rect(x, y, self.BUTTON_5_RECT):
                self.unschedule_all_triggers()
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
