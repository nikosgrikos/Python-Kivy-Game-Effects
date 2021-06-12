# Monkey Buster 2048 Tutorial Part 5 (See video on YouTube)
# Milestone achievement
# This code animates sun rays around an image and small sparkle images
# You will need to create a "Fonts" folder and place "debussy.ttf" in there. Try www.cooltext.com
# You will need to create a "Resources" folder and place 5 x .png images in there for your buttons
# You will need to create a "Beam" folder and place 8 x .png images in there for your rotated sun beam frames
# You will also need a "Resources/beam.png" image to display behind the tokens for shining effect
# You will also need a "Resources/sparkle.png" image to display sparkles
# You will also need a "Resources/Board_24.png" for your main achievement image (rename accordingly)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
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
WHITE = (1, 1, 1)

BLUE = (0/255,149/255,200/255)
LIME = (142/255,184/255,14/255)
PINK = (197/255,2/255,104/255)
ORANGE = (254/255, 128/255, 1/255)
DARK_GREEN = (34/255,100/255,34/255)

# Game state constants
C_PLAYING_GAME = 2
C_MILESTONE_BONUS_TOKENS = 3

# Sparkle instructions
C_ENLARGE = 1
C_CONTRACT = 2
C_REMOVE_SPARKLE = 3

BEAMFILE = ["beam_1.png", "beam_2.png",
            "beam_3.png", "beam_4.png",
            "beam_5.png", "beam_6.png",
            "beam_7.png", "beam_8.png"]

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

        self.MILESTONE_RECT = self.MATRIX_RECT

        return

    # __________________________________________________________________________________________________________________

    def initialise_triggers(self):

        # Triggers used in the game
        self.trigger1 = Clock.create_trigger(self.milestone_run, 0.05)

        return
    # ___________________________________________________________________________________________________________________

    def initialise_special_effects(self):

        self.sparkle_position = []
        self.beam_1_index = 0
        self.beam_2_index = len(BEAMFILE) - 1

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

    # __________________________________________________________________________________________________________________

    def milestone_run(self, dt):

        self.canvas.clear()
        self.canvas.after.clear()
        self.draw_canvas()

        self.display_rect(self.MILESTONE_RECT)
        x1, y1, x2, y2 = self.MILESTONE_RECT
        x1 += int(self.BLOCKSIZE*(3/2))
        x2 -= int(self.BLOCKSIZE*(3/2))
        y2 -= int(self.BLOCKSIZE*(3/2))
        y1 = y2 - (x2-x1)

        xx1 = x1 - int(self.BLOCKSIZE*(3/2))
        yy1 = y1 - int(self.BLOCKSIZE*(3/2))
        xx2 = x2 + int(self.BLOCKSIZE*(3/2))
        yy2 = y2 + int(self.BLOCKSIZE*(3/2))
        sourcefile = 'Beam/' + BEAMFILE[self.beam_1_index]
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source=sourcefile, pos=(xx1, yy1), size=(xx2-xx1, yy2-yy1))
        #sourcefile = 'Beam/' + BEAMFILE[self.beam_2_index]
        #with self.canvas:
        #    Color(rgb=WHITE)
        #    Rectangle(source=sourcefile, pos=(xx1, yy1), size=(xx2-xx1, yy2-yy1))

        self.beam_1_index += 1
        if self.beam_1_index == len(BEAMFILE) - 1:
            self.beam_1_index = 0
        self.beam_2_index -= 1
        if self.beam_2_index == 0:
            self.beam_2_index = len(BEAMFILE) - 1

        with self.canvas:
            Color(rgb=WHITE)
            sourcefile = 'Resources/Board_24.png'
            Rectangle(source=sourcefile, pos=(x1, y1), size=(x2-x1, y2-y1))

        self.sparkle(x1, y1, x2, y2)
        x1, y1, x2, y2 = self.MILESTONE_RECT
        y2 -= int((y2-y1)/2)
        fontsize = int(self.BLOCKSIZE/4)

        text = 'Congratulations!\nYou have reached the\nnext level!'
        with self.canvas:
            Color(rgb=WHITE)
            self.m_label = Label(text=text, halign="center", valign="bottom", size=(x2-x1, y2-y1),
                                 pos=(x1, y1), font_size=fontsize, font_name="Fonts/debussy.ttf")

        return

    # __________________________________________________________________________________________________________________

    def sparkle(self, x1, y1, x2, y2):

        min_sparkle_size = int(self.BLOCKSIZE / 10)
        max_sparkle_size = int(self.BLOCKSIZE / 2)
        sparkle_increment = int(self.BLOCKSIZE / 20)
        remove = False

        count = int(len(self.sparkle_position)/4)
        z = random.randrange(10)

        if count == 0 or z == 0:
            z = random.choice(['HORIZONTAL', 'VERTICAL'])
            if z == 'HORIZONTAL':
                x = random.randrange(x1, x2)
                y = random.choice([y1, y2])
            else:
                x = random.choice([x1, x2])
                y = random.randrange(y1, y2)
            self.sparkle_position.extend([x, y, min_sparkle_size, C_ENLARGE])
            count += 1


        count = int(len(self.sparkle_position)/4)
        for i in range(count):
            index = i*4
            x = self.sparkle_position[index]
            y = self.sparkle_position[index+1]
            size = self.sparkle_position[index+2]
            instruction = self.sparkle_position[index+3]

            half_size = int(size/2)
            xx1 = x-half_size
            yy1 = y-half_size
            xx2 = x+half_size
            yy2 = y+half_size
            with self.canvas:
                Color(rgb=WHITE)
                Rectangle(source='Resources/sparkle.png', pos=(xx1, yy1), size=(xx2-xx1, yy2-yy1))

            if instruction == C_ENLARGE:
                size += sparkle_increment
                if size > max_sparkle_size:
                    instruction = C_CONTRACT
            else:
                size -= sparkle_increment
                if size < min_sparkle_size:
                    instruction = C_REMOVE_SPARKLE
                    remove = True

            # Update sparkle position
            self.sparkle_position[index+2] = size
            self.sparkle_position[index+3] = instruction

        # Remove completed sparkles
        if remove:
            new_list = []
            points = int(len(self.sparkle_position) / 4)
            for k in range(points):
                index = k*4
                instruction = self.sparkle_position[index+3]
                if instruction != C_REMOVE_SPARKLE:
                    x = self.sparkle_position[index]
                    y = self.sparkle_position[index + 1]
                    size = self.sparkle_position[index + 2]
                    new_list.extend([x, y, size, instruction])
            self.sparkle_position = new_list

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
                if not (self.trigger1.is_triggered):
                    self.trigger1 = Clock.schedule_interval(self.milestone_run, 0.05)
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
