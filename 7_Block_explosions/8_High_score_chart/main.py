# Monkey Buster 2048 Tutorial Part 8 (See video on YouTube)
# High score chart
# This code displays a high score chart, saves/updates a high score
# You will need to create a "Fonts" folder and place "strasua.ttf" in there. Try www.cooltext.com
# You will need to create a "Resources" folder and place 5 x .png images in there for your buttons
# You will set DB_URL1 = 'https://xxxxxxxxxxxxxxxxxxxxx-rtdb.europe-west1.firebasedatabase.app/.json'
# where xxxxxxxxxxxxxxxxxxxx is your project name in Firebase
# You will need to insert the line to write a template to the database once only, then remove the line from the code

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label

from global_scores import write_score_to_database, retrieve_top_x_scores_from_database, \
    retrieve_top_x_team_scores_from_database, get_score_from_database
from global_scores import write_template_to_database

# Set this to True if deploying on mobile phone
MOBILE = False
# Set this to True if deploying on MacOS
MACOS = False
# Set this to True if this is the deployed on a new phone!
MOBILE64 = True

# Size of screen to open
if not(MOBILE):
    if MACOS:
        WINDOW_SIZE_X = 72*12 # Try also is 1440/2
        WINDOW_SIZE_Y = 128*12 # Try also 2960/2
    else:
        WINDOW_SIZE_X = 72*6 # Try also 1440/4
        WINDOW_SIZE_Y = 128*6 # Try also 2960/4

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
C_DISPLAY_SCORES = 3

DB_URL1 = 'https://monkeyscores-default-rtdb.europe-west1.firebasedatabase.app/.json'

#_______________________________________________________________________________________________________________________

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click)

        # Set game variables
        self.set_game_variables()

        # Set game variables
        self.initialise_variables()

        # Initialise triggers
        self.initialise_triggers()

        # Initialise and call main function
        self.game_main()

    # ___________________________________________________________________________________________________________________

    def back_click(self, window, key, *largs):
        if key == 27:
            self.unschedule_all_triggers()
            self.Game_menu()
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

    def initialise_variables(self):

        self.hi_score_label = [None for x in range(30)]
        self.team_flag = False
        self.country = 'Greece'
        self.name = 'Fred'

        # Call this once only, then remove when you have the template record in Firebase realtime database
        #write_template_to_database(DB_URL1)

        return

    # __________________________________________________________________________________________________________________

    def initialise_triggers(self):


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

    def mouse_in_rect(self, x, y, rect):

        x1, y1, x2, y2 = rect
        return x1 < x < x2 and y1 < y < y2

    #___________________________________________________________________________________________________________________

    def unschedule_all_triggers(self):

        return

    #___________________________________________________________________________________________________________________

    def process_score(self, score):

        url = DB_URL1
        lowest_global_score = self.get_lowest_global_score()
        try:
            users_highest_score = get_score_from_database(url)
        except:
            users_highest_score = 0

        count = int(len(self.global_scores) / 3)
        if score > users_highest_score and ((score > lowest_global_score and lowest_global_score > 0)\
                or count < 100):
            try:
                write_score_to_database(url, self.country, score, self.name)
                success = True
            except:
                pass

        # Find score position in top 100
        self.global_rank = 0
        if success:
            count = int(len(self.global_scores)/3)
            for i in range(0, count):
                index = (i*3) + 2
                if score >= self.global_scores[index]:
                    self.global_rank = i + 1
                    break

        return success

    # ___________________________________________________________________________________________________________________

    def get_lowest_global_score(self):

        # This routine returns the lowest score on the database or if there are over 100
        # scores, then it will return the 100th lowest score, i.e. cutoff is at 100
        self.team_flag = False
        success = self.get_global_scores()
        lowest_global_score = 0
        if success:
            count = int(len(self.global_scores)/3)
            if count == 100:
                index = ((count-1)*3) + 2
                lowest_global_score = self.global_scores[index]

        return lowest_global_score

    #___________________________________________________________________________________________________________________

    def get_global_scores(self):

        # This routine returns a list of 100 global scores from the firebase realtime database
        # Format is country, name, score, so 100x3=300 elements
        # If team_flag is True, then scores are ordered by country of maximum 4 users
        self.global_scores_index = 0
        url = DB_URL1
        try:
            if self.team_flag:
                self.global_scores = retrieve_top_x_team_scores_from_database(url, 25, 100)
            else:
                self.global_scores = retrieve_top_x_scores_from_database(url, 100)
            self.max_scores = int(len(self.global_scores) / 3)
            success = True
        except:
            self.global_scores = []
            self.max_scores = 0
            success = False

        return success

    #___________________________________________________________________________________________________________________

    def display_scores(self):

        # Clear the canvas
        self.canvas.clear()
        self.canvas.after.clear()

        j = 0
        x1, y1, x2, y2 = self.MATRIX_RECT
        x1 += int(self.BLOCKSIZE/2)
        x2 -= int(self.BLOCKSIZE/2)
        BOX_LENGTH = int(((x2 - x1) - (5 * RECT_OFFSET)) / 4)
        fontsize = int(BOX_LENGTH / 5)

        if self.team_flag:
            namefontsize = int(BOX_LENGTH / 8)
        else:
            namefontsize = fontsize

        max = self.global_scores_index + 10
        if self.max_scores < max:
            max = self.max_scores

        for i in range(self.global_scores_index, max):
            index = i*3
            country = self.global_scores[index]
            name = self.global_scores[index+1]
            score = self.global_scores[index+2]

            x_pos = x1
            y_pos = y1 + (10-i+self.global_scores_index)*RECT_OFFSET + (9-i+self.global_scores_index)*int(BOX_LENGTH/2)
            x_size = BOX_LENGTH
            y_size = int(BOX_LENGTH/2)

            BOX_RECT = x_pos, y_pos, x_pos+x_size, y_pos+y_size
            bw = 1
            self.display_rect(BOX_RECT)

            with self.canvas:
                Color(WHITE)
                Rectangle(size=(x_size-bw*2, y_size-bw*2), pos=(x_pos+bw, y_pos+bw))

            x_end = x2 + fontsize - fontsize*5 - RECT_OFFSET
            x_pos = x_pos + x_size + RECT_OFFSET
            y_pos = y_pos + int(fontsize/3)
            text = name
            with self.canvas:
                self.hi_score_label[j] = Label(text=text, halign="left", valign="bottom", size=(x_end-x_pos,namefontsize*3),
                                               pos=(x_pos, y_pos), font_size=namefontsize, font_name="Fonts/strasua.ttf")
                self.hi_score_label[j].text_size = self.hi_score_label[j].size
            j += 1

            x_pos = x1 - RECT_OFFSET - fontsize*3
            text = str(i+1)
            with self.canvas:
                self.hi_score_label[j] = Label(text=text, halign="right", valign="bottom", size=(fontsize*3,fontsize*2),
                                               pos=(x_pos, y_pos), font_size=fontsize, font_name="Fonts/strasua.ttf")
                self.hi_score_label[j].text_size = self.hi_score_label[j].size
            j += 1

            x_pos = x2 + fontsize - fontsize*5
            text = str(score)
            with self.canvas:
                self.hi_score_label[j] = Label(text=text, halign="right", valign="bottom", size=(fontsize*5,fontsize*2),
                                               pos=(x_pos, y_pos), font_size=fontsize, font_name="Fonts/strasua.ttf")
                self.hi_score_label[j].text_size = self.hi_score_label[j].size
            j += 1

        return
    #___________________________________________________________________________________________________________________

    def on_touch_down(self, touch):

        x, y = touch.pos
        if self.current_screen == C_PLAYING_GAME:

            if self.mouse_in_rect(x, y, self.BUTTON_1_RECT):
                self.current_screen = C_DISPLAY_SCORES
                self.get_global_scores()
                self.display_scores()

            if self.mouse_in_rect(x, y, self.BUTTON_2_RECT):
                try:
                    url = DB_URL1
                    users_highest_score = get_score_from_database(url)
                except:
                    users_highest_score = 0
                self.process_score(users_highest_score+1)

            if self.mouse_in_rect(x, y, self.BUTTON_5_RECT):
                self.unschedule_all_triggers()
                exit()

        elif self.current_screen == C_DISPLAY_SCORES:
            self.current_screen = C_PLAYING_GAME
            self.draw_canvas()

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
