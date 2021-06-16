# Monkey Buster Tutorial Part 4 (See video on YouTube)
# Fruit tokens going into token bank, also fruit tokens going to fruit credits
# This code animates fruit tokens moving towards the token bank and fruit credits
# You will need to create a "Fonts" folder and place "debussy.ttf" in there. Try www.cooltext.com
# You will need to create a "Resources" folder and place 5 x .png images in there for your buttons
# and another 5 x .png images in there for fruit tokens. Try "free clip art" in Google, but check licence.
# You will also need a "beam.png" image to display behind the tokens for shining effect

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
MACOS = True
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
PURPLE = (125/255,62/255,157/255)

# Game state constants
C_PLAYING_GAME = 2
C_MILESTONE_BONUS_TOKENS = 3

# Fruit instructions
C_MOVE_TO_MIDDLE = 1
C_MOVE_TO_FRUIT_BANK = 2
C_MOVE_TO_CREDITS = 3
C_REMOVE_FRUIT = 4
C_MOVE_TO_MIDDLE_THEN_CREDITS = 5

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

        x1, y1, x2, y2 = self.SCORE_RECT
        size = int(self.BLOCKSIZE/2)
        self.FRUIT_TOKENS_RECT = x2-size, y2-size, x2, y2

        return

    # __________________________________________________________________________________________________________________

    def initialise_triggers(self):

        # Triggers used in the game
        self.trigger1 = Clock.create_trigger(self.animate_fruits_run, 0.03)
        self.trigger2 = Clock.create_trigger(self.process_milestone_bonus_run, 0.03)
        self.trigger3 = Clock.create_trigger(self.process_milestone_bonus_move, 0.03)

        return
    # ___________________________________________________________________________________________________________________

    def initialise_special_effects(self):

        self.fruit_position = []
        self.fruit_bank = 0
        self.fruit_tokens = 0

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

        self.draw_fruit_tokens()

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

        self.draw_bank_button()

        x1, y1, x2, y2 = self.BUTTON_4_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_4.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        x1, y1, x2, y2 = self.BUTTON_5_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/button_5.png', pos=(x1, y1), size=(x2 - x1, y2 - y1))

        return

    # __________________________________________________________________________________________________________________

    def draw_bank_button(self):

        x1, y1, x2, y2 = self.BUTTON_3_RECT
        yy2 = y1 + int(self.BLOCKSIZE/5)
        fontsize = self.BLOCKSIZE/5
        text = str(self.fruit_bank)

        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source="Resources/banana_bank.png", size=(x2-x1, y2-y1), pos=(x1, y1))
            Color(rgb=PURPLE)
            Rectangle(size=(x2-x1, yy2-y1), pos=(x1, y1))

        with self.canvas:
            Color(rgb=BACKGROUNDCOLOR)
            self.bank_label = Label(text=text, halign="center", valign="bottom", size=(x2-x1, yy2-y1),
                                     pos=(x1, y1), font_size=fontsize, font_name="Fonts/debussy.ttf")

    # ___________________________________________________________________________________________________________________

    def draw_fruit_tokens(self):

        x1, y1, x2, y2 = self.FRUIT_TOKENS_RECT
        with self.canvas:
            Color(rgb=WHITE)
            Rectangle(source='Resources/fruit_5.png', pos=(x1, y1), size=(x2-x1, y2-y1))

        x1, y1, x2, y2 = self.FRUIT_TOKENS_RECT
        yy1 = y1 - int(self.BLOCKSIZE/5)
        yy2 = y1
        fontsize = self.BLOCKSIZE/5
        text = str(self.fruit_tokens)

        with self.canvas:
            Color(rgb=BLUE)
            Rectangle(size=(x2-x1, yy2-yy1), pos=(x1, yy1))

        with self.canvas:
            Color(rgb=BLUE)
            self.fruit_token_label = Label(text=text, halign="left", valign="bottom", size=(x2-x1, yy2-yy1),
                                            pos=(x1, yy1), font_size=fontsize, font_name="Fonts/debussy.ttf")

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

    def animate_fruits(self):

        x = random.randrange(0, self.MATRIX_WIDTH)
        y = random.randrange(0, self.MATRIX_HEIGHT)
        z = random.choice([1, 2, 3, 4, 5])
        self.animate_fruits_initialise(y, x, z)

        return
    #___________________________________________________________________________________________________________________

    def animate_fruits_initialise(self, y, x, number_of_fruits):

        x1, y1, x2, y2 = self.MATRIX_RECT
        x1 += self.BLOCKSIZE*x + int(self.BLOCKSIZE*(2/3))
        y1 += self.BLOCKSIZE*(self.MATRIX_HEIGHT-1-y) + int(self.BLOCKSIZE*(2/3))
        size = int(self.BLOCKSIZE/3)
        delay_steps = 0
        self.fruit_position.extend([y1, x1, size, C_MOVE_TO_MIDDLE, number_of_fruits, delay_steps])

        if not(self.trigger1.is_triggered):
            self.trigger1 = Clock.schedule_interval(self.animate_fruits_run, 0.01)

        return

    #___________________________________________________________________________________________________________________

    def animate_fruits_run(self, dt):

        self.draw_canvas()

        x1, y1, x2, y2 = self.MATRIX_RECT
        max_fruit_size = self.BLOCKSIZE*2
        min_fruit_size = int(self.BLOCKSIZE/10)

        middle_x1 = x1 + int((x2-x1)/2)
        middle_y1 = y1 + int((y2-y1)/2)

        remove = False
        points = int(len(self.fruit_position)/6)
        for i in range(points):
            index = i*6
            y = self.fruit_position[index]
            x = self.fruit_position[index+1]
            fruit_size = self.fruit_position[index+2]
            instruction = self.fruit_position[index+3]
            image = self.fruit_position[index+4]
            delay_steps = self.fruit_position[index+5]

            x1 = x
            y1 = y

            if MOBILE64:
                increment_x = int(self.BLOCKSIZE / 10)
                increment_y = int(self.BLOCKSIZE / 5)
                increment_z = int(self.BLOCKSIZE / 10)
            else:
                increment_x = int(self.BLOCKSIZE / 5)
                increment_y = int(self.BLOCKSIZE / 3)
                increment_z = int(self.BLOCKSIZE / 5)

            if instruction in (C_MOVE_TO_MIDDLE_THEN_CREDITS, C_MOVE_TO_CREDITS):
                increment_x *= 2
                increment_y *= 2

            # Beam coordinates
            xx1 = x1 - int(fruit_size / 2)
            yy1 = y1 - int(fruit_size / 2)
            xx2 = xx1 + 2 * fruit_size
            yy2 = yy1 + 2 * fruit_size

            if image == 1:
                sourcefile = 'Resources/fruit_1.png'
            elif image == 2:
                sourcefile = 'Resources/fruit_2.png'
            elif image == 3:
                sourcefile = 'Resources/fruit_3.png'
            elif image == 4:
                sourcefile = 'Resources/fruit_4.png'
            elif image >= 5:
                sourcefile = 'Resources/fruit_5.png'

            if instruction != C_REMOVE_FRUIT:
                with self.canvas:
                    Color(rgb=WHITE)
                    Rectangle(source='Resources/beam.png', pos=(xx1, yy1), size=(xx2 - xx1, yy2 - yy1))

                with self.canvas:
                    Color(rgb=WHITE)
                    Rectangle(source=sourcefile, pos=(x1, y1), size=(fruit_size, fruit_size))

            if delay_steps > 0:
                delay_steps -= 1

            elif instruction in (C_MOVE_TO_MIDDLE, C_MOVE_TO_MIDDLE_THEN_CREDITS):

                if instruction == C_MOVE_TO_MIDDLE:
                    m_x1 = middle_x1 - int(max_fruit_size/2)
                    m_y1 = middle_y1 - int(max_fruit_size/2)
                else:
                    m_x1 = middle_x1
                    m_y1 = middle_y1
                if x < m_x1 - increment_x:
                    x += increment_x
                if y < m_y1 - increment_y:
                    y += increment_y
                if x > m_x1 + increment_x:
                    x -= increment_x
                if y > m_y1 + increment_y:
                    y -= increment_y
                if instruction == C_MOVE_TO_MIDDLE:
                    if fruit_size < max_fruit_size:
                        fruit_size += increment_z
                # No change
                if x1 == x and y1 == y \
                        and (fruit_size >= max_fruit_size or instruction == C_MOVE_TO_MIDDLE_THEN_CREDITS):
                    if instruction == C_MOVE_TO_MIDDLE:
                        instruction = C_MOVE_TO_FRUIT_BANK
                    else:
                        instruction = C_MOVE_TO_CREDITS

            elif instruction == C_MOVE_TO_FRUIT_BANK:

                xx1, yy1, xx2, yy2 = self.BANK_RECT
                corner_x1 = xx1 + int((xx2-xx1)/2)
                corner_y1 = yy1 + int((yy2-yy1)/2)

                if x > corner_x1 + increment_x:
                    x -= increment_x
                if x < corner_x1 - increment_x:
                    x += increment_x
                if y > corner_y1 + increment_y:
                    y -= increment_y
                if fruit_size > min_fruit_size:
                    fruit_size -= increment_z
                if x1 == x and y1 == y and fruit_size <= min_fruit_size:
                    instruction = C_REMOVE_FRUIT
                    self.fruit_bank += image
                    remove = True

            elif instruction == C_MOVE_TO_CREDITS:

                xx1, yy1, xx2, yy2 = self.FRUIT_TOKENS_RECT
                corner_x1 = xx1
                corner_y1 = yy1

                if x <= corner_x1 - increment_x:
                    x += increment_x
                if y <= corner_y1 - increment_y:
                    y += increment_y
                if x1 == x and y1 == y:
                    instruction = C_REMOVE_FRUIT
                    self.fruit_tokens += image
                    remove = True

            self.fruit_position[index] = y
            self.fruit_position[index+1] = x
            self.fruit_position[index+2] = fruit_size
            self.fruit_position[index+3] = instruction
            self.fruit_position[index+4] = image
            self.fruit_position[index+5] = delay_steps

        # Remove items that have scrolled to the max
        if remove:
            new_list = []
            points = int(len(self.fruit_position) / 6)
            for k in range(points):
                index = k*6
                instruction = self.fruit_position[index+3]
                if instruction != C_REMOVE_FRUIT:
                    y = self.fruit_position[index]
                    x = self.fruit_position[index + 1]
                    fruit_size = self.fruit_position[index + 2]
                    image = self.fruit_position[index + 4]
                    delay_steps = self.fruit_position[index + 5]
                    new_list.extend([y, x, fruit_size, instruction, image, delay_steps])
            self.fruit_position = new_list

            if new_list == []:
                Clock.unschedule(self.trigger1)
                self.draw_canvas()
        return

    #___________________________________________________________________________________________________________________

    def process_milestone_bonus(self, number_of_fruits):

        self.current_screen = C_MILESTONE_BONUS_TOKENS
        self.delay_steps = 0
        self.milestone_number_of_fruits_left = number_of_fruits
        self.milestone_position = 6, 2
        self.draw_canvas()

        # Start trigger
        if not (self.trigger2.is_triggered):
            self.trigger2 = Clock.schedule_interval(self.process_milestone_bonus_run, 0.03)

        return

    # ___________________________________________________________________________________________________________________

    def process_milestone_bonus_run(self, dt):

        division, modular = divmod(self.milestone_number_of_fruits_left, 1) # in MB, this was , 3)
        if division > 0:
            number_of_fruits = 1 # In MB, this was = 3
        else:
            number_of_fruits = modular

        if self.milestone_number_of_fruits_left > 0:
            y, x = self.milestone_position
            x1, y1, x2, y2 = self.MATRIX_RECT
            x1 += self.BLOCKSIZE*x
            y1 += self.BLOCKSIZE*(self.MATRIX_HEIGHT-1-y)
            size = int(self.BLOCKSIZE/2)
            i = random.randrange(int(self.BLOCKSIZE/2))
            j = random.randrange(int(self.BLOCKSIZE/2))
            x1 += i
            y1 += j
            self.delay_steps += 1

            self.fruit_position.extend([y1, x1, size, C_MOVE_TO_MIDDLE_THEN_CREDITS, number_of_fruits, self.delay_steps])
            self.animate_fruits_run(dt=0)
            self.milestone_number_of_fruits_left -= number_of_fruits

        else:
            # End trigger
            Clock.unschedule(self.trigger2)

            # Start move bonus fruits trigger
            if not (self.trigger3.is_triggered):
                self.trigger3 = Clock.schedule_interval(self.process_milestone_bonus_move, 0.03)

        return

    # ___________________________________________________________________________________________________________________

    def process_milestone_bonus_move(self, dt):

        self.animate_fruits_run(dt=0)
        points = int(len(self.fruit_position)/6)
        if points == 0:
            Clock.unschedule(self.trigger3)
            self.current_screen = C_PLAYING_GAME
            self.draw_canvas()
        return

    #___________________________________________________________________________________________________________________

    def mouse_in_rect(self, x, y, rect):

        x1, y1, x2, y2 = rect
        return x1 < x < x2 and y1 < y < y2

    #___________________________________________________________________________________________________________________

    def unschedule_all_triggers(self):

        if self.trigger1.is_triggered:
            Clock.unschedule(self.trigger1)
        if self.trigger2.is_triggered:
            Clock.unschedule(self.trigger2)
        if self.trigger3.is_triggered:
            Clock.unschedule(self.trigger3)

        return

    #___________________________________________________________________________________________________________________

    def on_touch_down(self, touch):

        x, y = touch.pos
        if self.current_screen == C_PLAYING_GAME:

            if self.mouse_in_rect(x, y, self.BUTTON_1_RECT):
                self.animate_fruits()
            if self.mouse_in_rect(x, y, self.BUTTON_2_RECT):
                self.process_milestone_bonus(self.fruit_bank)
            if self.mouse_in_rect(x, y, self.BUTTON_5_RECT):
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
