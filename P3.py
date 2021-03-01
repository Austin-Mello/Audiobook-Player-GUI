#!/usr/bin/env python
"""
PagePointerAV.py
by A.Hornof (ajh) 2020

Shows a page from a book, and moves a pointer up and down to show the line
currently being read.
----------------------------------------
User input: <D> and <F> or <J> and <K>.
            <ESC> or <Q> to quit.
The system output is AV - both audio and visual.

Notes: The "_" in _variable indicates it is a private class variable.

Uses Python 3.7
----------------------------------------
Sources for ideas:
chimp.py by Pete Shiners from
https://www.pygame.org/docs/tut/ChimpLineByLine.html
eventlist.py from
https://www.pygame.org/docs/ref/examples.html#pygame.examples.eventlist.main
"""

# Import Modules
import os
import pygame # Currently using 1.9.6
import SoundObject # created by ajh, should accompany this file.
if not pygame.font: print ('Warning, fonts disabled')

# GLOBAL VARIABLES
# Data subdirectory.
DATA_DIR = "data"
# Sound file names.
S_FILE_FORWARD = "Forward.ogg"
S_FILE_CH2 = "NormanChapter2Audio.ogg"
S_FILE_NAVPROMPTS = "NavigationPrompts.ogg"

# ---------------------------------------------------------------------------- #
# load_image( ) - Load an image file. (Adapted from Pete Shinners)
# More error-checking could probably be done.

def load_image(name, colorkey=None):

    # Set up path to subdirectory
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, DATA_DIR)

    # Join the path and filename, cross-platform.
    fullname = os.path.join(data_dir, name)

    # Try to load the image. Exit gracefully if it fails.
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(pygame.get_error()))

    # Update the pixel format. This is important to do after loading a file.
    #   It improves rendering speed.
    image = image.convert()

    return image

# ---------------------------------------------------------------------------- #
# Arrow Class - Creates an arrow on the display.
# The arrow could also be drawn using an image-file of an arrow.
class Arrow(pygame.sprite.Sprite):

    def __init__(self, surface_in, initial_x_pos, initial_y_pos,
                 top_y, bottom_y, num_lines):

        # Pseudo-private member variables.
        self._surface = surface_in  # used internally for drawing
        self._x = initial_x_pos     # Current mouse x,y position.
        self._y = initial_y_pos
        self._top_y = top_y         # Top and bottom y position on screen
        self._bottom_y = bottom_y
        self._num_lines = num_lines # Number of lines to span.

        # y position with decimal, so rounding errors do not accumulate.
        self._y_with_decimal = initial_y_pos

        # compute the distance of each movement
        self._movement_distance = (self._bottom_y - self._top_y) / self._num_lines

    # Create a red arrow on the surface specified.
    def draw(self):
        pygame.draw.lines(self._surface, pygame.Color('red'),
                          False,  # first and last lines are not connnected.
                          [[self._x + 15, self._y - 15],  # the outside end of the top barb.
                           [self._x + 30, self._y],  # right (pointed) end
                           [self._x, self._y],  # left end
                           [self._x + 30, self._y],  # back to the right end
                           [self._x + 15, self._y + 15]],  # the outside end of the bottom barb.
                          10)  # width

    # Move the arrow UP one position.
    def move_up(self):
        # If you haven't hit the top
        if (self._y > self._top_y):
            # Calculate the new position without rounding, and then round it.
            self._y_with_decimal -= self._movement_distance
            self._y = round(self._y_with_decimal)

    # Move the arrow DOWN one position.
    def move_down(self):
        # If you haven't hit the bottom
        if (self._y < self._bottom_y):
            self._y_with_decimal += self._movement_distance
            self._y = round(self._y_with_decimal)

    # Toggle the arrow through the main menu
    def toggle_left(self):
        self._x = self._x - 400
    def toggle_right(self):
        self._x = self._x + 400

# ---------------------------------------------------------------------------- #
# Indicator Class - An indicator that a button has been pressed. The indicator
#   can be on or off. It is like an indicator light on a dashboard.
class Indicator:

    def __init__(self, surface_in, text_label, x_pos_in, y_pos_in):
        self._surface = surface_in  # used internally for drawing
        self._text_label = text_label
        self._x_pos = x_pos_in
        self._y_pos = y_pos_in
        self._text_color = pygame.Color('white')
        self._off_color  = pygame.Color('blue')
        self._on_color   = pygame.Color('red')
        self._Font = pygame.font.Font(None, 26) # Font size
        # Indicates how many more clock ticks the indicator will remain on.
        self._remaining_ON_ticks = 0 # Start with it off.
        self._ticks_in_flash = 2     # How many clock ticks to stay on for a "flash".

    # Flash the indicator by setting a number of main-loop ticks that must elapse.
    def flash(self):
        self._remaining_ON_ticks = self._ticks_in_flash

    # Draw the indicator.
    def draw(self):
        # If any "ON" clock ticks are remaining, draw it in the "ON" position.
        if self._remaining_ON_ticks > 0:
            self.draw_text(self._on_color)
            self._remaining_ON_ticks -= 1
        # Draw it in the "OFF" position.
        else:
            self.draw_text(self._off_color)

    # Render the text in the specified color.
    def draw_text(self, input_color):
        # Render the text.r
        text_img = self._Font.render(self._text_label, 1, self._text_color, input_color)
        # Add the text to the background.
        self._surface.blit(text_img, (self._x_pos, self._y_pos))

# ---------------------------------------------------------------------------- #
# KeyDisplay( ) creates a KeyDisplay class to show activated keys. It shows a
#   sequence of rectangles, used to indicate the button pressed.
class KeyDisplay(pygame.sprite.Sprite):

    # Create a key_display on the screen.
    def __init__(self, surface_in, x_pos_in, y_pos_in):
        self._surface = surface_in  # used internally for drawing
        self._x_pos = x_pos_in
        self._y_pos = y_pos_in
        self._y_offset = 30          # The vertical spacing between indicators.

        # Indicators
        self._UP_indicator = Indicator( self._surface, "UP", self._x_pos, self._y_pos )
        self._DOWN_indicator = Indicator( self._surface, "DOWN", self._x_pos,
                                          self._y_pos + self._y_offset)
        self._UP_indicator.draw()
        self._DOWN_indicator.draw()

    # Draw the keys.
    def draw(self):
        self._UP_indicator.draw()
        self._DOWN_indicator.draw()

    # Indicate that UP was pressed.
    def UP(self):
        self._UP_indicator.flash()

    # Indicate that DOWN was pressed.
    def DOWN(self):
        self._DOWN_indicator.flash()

# ---------------------------------------------------------------------------- #
class MainMenuKeys(pygame.sprite.Sprite):
    
    # Create a the main menu key_display on the screen.
    def __init__(self, surface_in, x_pos_in, y_pos_in):
        self._surface = surface_in  # used internally for drawing
        self._x_pos = x_pos_in
        self._y_pos = y_pos_in
        self._x_offset = 400          # The vertical spacing between indicators.

        # Indicators
        self._UP_indicator = Indicator( self._surface, "Book Reader", self._x_pos, self._y_pos )
        self._DOWN_indicator = Indicator( self._surface, "Headings and Topic Sentences", self._x_pos + self._x_offset,
                                          self._y_pos)
        """self._help_indicator = Indicator( seld._surface, "Book reader main menu.  Press space to start from your
                                        "bookmark, K to move forward through the menu, J to move backward through the menu,
                                        "and semicolon for help.", 350, 600)"""                         
        self._UP_indicator.draw()
        self._DOWN_indicator.draw()

    # Draw the keys.
    def draw(self):
        self._UP_indicator.draw()
        self._DOWN_indicator.draw()

    # Indicate that UP was pressed.
    def UP(self):
        self._UP_indicator.flash()

    # Indicate that DOWN was pressed.
    def DOWN(self):
        self._DOWN_indicator.flash()

# ---------------------------------------------------------------------------- #
def main():
# ---------------------------------------------------------------------------- #

    """
    This function is called when the program starts. it initializes everything it
    needs, then runs in a loop until the function returns.
    """

    # Initialize pygame.
    pygame.init()

    # ------------------------------------------------------------------------ #
    # Set up all the visual elements.

    # Set up the window.
    screen = pygame.display.set_mode((842, 1376), flags=pygame.RESIZABLE)
    pygame.display.set_caption("Audio Book")

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(pygame.Color('white'))

    # Prepare the image of the page. Add it to the background.
    page_1 = load_image("MainMenu.png")
    background.blit(page_1, (0,0))

    # Position the arrow on the screen and specify its movement range.
    # See the Arrow __init()__ for the argument list.
    arrow = Arrow(screen, 10, 506, 887, 887+368, 12)

    # Load the clock
    clock = pygame.time.Clock()

    # Create the indicator panel that shows when buttons are pressed.
    key_display = MainMenuKeys(screen, 50, 500) # (x,y) position

    # Draw everything.
    screen.blit(background, (0, 0))
    key_display.draw()
    pygame.display.flip()

    # ------------------------------------------------------------------------ #
    # Set up all the auditory elements.

    # Create the sounds.
    # Send in the data directory name, the sound file name, the start time,
    #   and the duration. Sometimes different sounds are in the same file.
    forward_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_FORWARD, 500, 750)
    backward_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_FORWARD, 1500, 750)
    chapter2_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_CH2, 0, 9999999)
    mmhelp1_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_NAVPROMPTS, 24000, 9000)
    mmhelp2_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_NAVPROMPTS, 12600, 10900)
    bookreader_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_NAVPROMPTS, 8000, 1500)
    headings_sound = SoundObject.SoundObject(DATA_DIR, S_FILE_NAVPROMPTS, 10000, 2100)

    # ------------------------------------------------------------------------ #

    # Variables used within Main Loop
    program_running = True
    playing = False
    selected = True
    # Main Loop

    while program_running:

        # Limits the while loop to a max of 60 clock-ticks per second.
        clock.tick(60)
        

        # Handle Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                program_running = False

            # Handle Keystroke Events
            elif event.type == pygame.KEYDOWN:

                # TODO: <SPACE> To select.
                

                # <;> To display help
                if event.key == pygame.K_SEMICOLON or event.key == pygame.K_a:
                    if selected == True:
                        background.blit(page_1, (0,0))
                        mmhelp1_sound.play()
                        font = pygame.font.Font(None, 16)
                        text = font.render("""Book reader main menu. Press space for Book Reader, K to move forward through the menu, J to move backward, L to quit, and semi-colon for help.""", 1, (10,10,10))
                        textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_width()/2)
                        background.blit(text, textpos)
                    else:
                        background.blit(page_1, (0,0))
                        mmhelp2_sound.play()
                        font = pygame.font.Font(None, 15)
                        text = font.render("""Book reader main menu. Press space for headings and topic sentences, K to move forward through the menu, J to move backward, L to quit, and semi-colon for help.""", 1, (10,10,10))
                        textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_width()/2)
                        background.blit(text, textpos)
                    
                # <J> To toggle selection
                if event.key == pygame.K_j or event.key == pygame.K_d:
                    if selected == True:
                        arrow.toggle_right()
                        headings_sound.play()
                        selected = False
                    else:
                        arrow.toggle_left()
                        bookreader_sound.play()
                        selected = True

                # <K> To toggle selection
                elif event.key == pygame.K_k or event.key == pygame.K_f:
                    if selected == True:
                        arrow.toggle_right()
                        headings_sound.play()
                        selected = False
                    else:
                        arrow.toggle_left()
                        bookreader_sound.play()
                        selected = True

                # <ESC> or <Q> quits
                elif event.key == pygame.K_l or event.key == pygame.K_s:
                    # Ideally, this would give a warning before quitting,
                    #   but that is not implemented yet.
                    program_running = False

        # Draw Everything
        screen.blit(background, (0, 0)) # Start with a fresh new background.
        key_display.draw()
        arrow.draw()
        pygame.display.flip()

        # Stop the sound that is playing when it is done.
        SoundObject.stop_when_done()

# Done
pygame.quit()


# this calls the 'main' function when this script is executed
if __name__ == "__main__":
    main()

