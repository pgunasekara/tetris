import pyglet
from pyglet.window import key

import random
import sys

__module_name__ = 'tetris'
__module_description__ = 'a clone of tetris written in python'
__version__ = (0, 1, 0)
#Comments done by Pasindu Gunasekara for COMP SCI 3IO3

# these are the dimensions from the gameboy version
BOARD_WIDTH = 14
BOARD_HEIGHT = 20

#values to represent various types of spaces on the board
#0 - empty space on the board
#1 - space occupied by a block
#2 - active block
BLOCK_EMPTY = 0
BLOCK_FULL = 1
BLOCK_ACTIVE = 2
BLOCK_IMG_FILE = 'img/block.png'                                                #selects an image for a block to display

block = pyglet.image.load(BLOCK_IMG_FILE)                                       #loads the image into pyglet using any available image decoder
block_sprite = pyglet.sprite.Sprite(block)                                      #generates a pyglet sprite out of the image

BLOCK_WIDTH = block.width                                                       #gets the width dimension from the actual width of the block image previously loaded
BLOCK_HEIGHT = block.height                                                     #gets the width dimension from the actual width of the block image previously loaded

window = pyglet.window.Window(width=BOARD_WIDTH*BLOCK_WIDTH,
                              height=BOARD_HEIGHT*BLOCK_HEIGHT)                 #creates a new window with pylet using the width and height previous taken, along with accounting for the block size by multiplying by the block width or height

class Shape(object):
    """
    The shape class is used to build each shape that the user might encounter in a game of tetris.
    Performs various other operations on shapes, such as selecting, cloning, and rotating.
    """
    #Array of 6 different types of shapes that a user may recieve randomly at each iteration of the game.
    _shapes = [
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]],
        [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 1, 1, 0]],
        [[0, 0, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], [0, 1, 0, 0]],
        [[0, 0, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0]],
    ]
    
    def __init__(self, x=0, y=0):
        """
        x: x coordinate of the shape with a default value of 0 
        y: y coordinate of the shape with a default value of 0 
        """
        self.shape = random.choice(self._shapes)                                #Selects a random shape from the preset array of shapes
        self.shape = self.copy_shape()                                          #Sets the current shape of the object

        for i in range(random.choice(range(4))):
            self.rotate()                                                       #Select a random orientation for the shape

        self.x = x
        self.y = y

    def copy_shape(self):
        """
        Returns an array with the copy of the current shape selected for the object.
        """
        new_shape = []
        for row in self.shape:                                                  #iterates over each element in the array 'shape'
            new_shape.append(row[:])                                            #Appends each row of the original shape, to the copied shape
        return new_shape
    
    def clone(self):
        """
        Creates a object of the Shape class and copies the current shape to create a copy of itself.
        """
        cloned = Shape()                                                        #cloned: holds the new shape to be returned
        cloned.shape = self.copy_shape()                                        #the constructor selects a random shape, but a copy overwrites it
        cloned.x = self.x
        cloned.y = self.y
        return cloned
    
    def rotate(self):
        """
        Rotates the shape to change it's orientation when the shape is generated or when the user rotates it.
        """
        new_shape = self.copy_shape()                                           #new_shape: a temporary variable that holds a copy of the current shape in order to not overwrite it until the rotation is complete
        for j in range(0, 4):
            for i in range(0, 4):
                new_shape[i][j] = self.shape[4 - j - 1][i]                      #rotate the matrix holding the shape
        self.shape = new_shape                                                  #replaces the current shape with the new rotated shape

    @property
    def left_edge(self):
        """
        Tests if the shape is on a left edge, returns the coordinate of the left edge if found.
        """
        for x in range(0, 4):                                                   #Test points from left (0) to right(4)
            for y in range(0, 4):                                               #Test points from bottom (0) to top (3)
                if self.shape[y][x] == BLOCK_FULL:                              #if left edge is found
                    return x                                                    #If the left block is a full block, then return the x coordinate of the full block

    @property
    def right_edge(self):
        """
        Tests if the shape is on a right edge, returns coordinate if found.
        """
        for x in range(3, -1, -1):                                              #test x values 3, 2, 1, 0, going from right (3) to left (0)
            for y in range(0, 4):                                               #test y values from bottom (0) to top (3)
                if self.shape[y][x] == BLOCK_FULL:                              #if right edge is found
                    return x                                                    #return the x coordinate of the first right edge block found

    @property
    def bottom_edge(self):
        """
        Test if the shape in a bottom edge, returns the coordinate if found
        """
        for y in range(3, -1, -1):                                              #test x values 3, 2, 1, 0, going from right (3) to left (0)
            for x in range(0, 4):                                               #test y values from bottom (0) to top (3)
                if self.shape[y][x] == BLOCK_FULL:                              #if right edge is found
                    return y                                                    #return the y coordinate of the first bottom edge block found


class Board(pyglet.event.EventDispatcher):
    """
    The board class is used for the game board containing the shapes.
    Allows for various board operations, such as resetting the game, adding shapes, and collision detection.
    """
    #variables used to keep track of the current shape, the next shape, and the board matrix
    active_shape = None
    pending_shape = None
    board = None
    
    def __init__(self, width, height, block):
        """
        Initializes the board with the height, and width, and begins a new game.
        """
        self.width, self.height = width, height                                 #sets the height and width of the game board
        self.block = block                                                      #sets the block sprite for the board based on the image file loaded previously
        self.calculated_height = self.height * BLOCK_HEIGHT                     #the calculated height accounts for the height of the block, so that the window can display all blocks
        self.calculated_width = self.width * BLOCK_WIDTH                        #calculated width accounts for the width of the block
        self.reset()                                                            #clears the board, and starts a new game
    
    def reset(self):
        """
        Clears the board and starts a new game
        """
        self.board = []                                                         #sets the board to be an empty board
        for row in range(self.height):                                          #For each row in the board where the number of rows = height
            self.board.append([0] * self.width)                                 #Set each row to be an array of 0s
        
        self.pending_shape = Shape()                                            #get the next shape to add to the board (random)
        self.add_shape()                                                        #calls the add_shape method to add the new shape to the window

    def add_shape(self):
        """
        Adds a new shape to the window, and sets it as the current active shape
        """
        self.active_shape = self.pending_shape.clone()                          #sets the current active shape to be the preselected pending shape
        self.active_shape.x = self.width // 2 - self.active_shape.left_edge     #sets the shape to be in the middle of the x axis of the board
        self.active_shape.y = -1                                                #sets the y coordinate of the shape to be the top of the screen
        self.pending_shape = Shape()                                            #create a new random pending shape to send out next
        
        if self.is_collision():                                                 #checks if the blocks hit the top of the the window
            self.reset()                                                        #If so, the game ends, and resets
            self.dispatch_event('on_game_over')                                 #the on_game_over event will reset the game
    
    def rotate_shape(self):
        """
        Rotates the active shape
        """
        rotated_shape = self.active_shape.clone()                               #works on a copy of the active shape
        rotated_shape.rotate()                                                  #rotate once using the rotate method on Shape

        if rotated_shape.left_edge + rotated_shape.x < 0:
            rotated_shape.x = -rotated_shape.left_edge
        elif rotated_shape.right_edge + rotated_shape.x >= self.width:
            rotated_shape.x = self.width - rotated_shape.right_edge - 1
        
        if rotated_shape.bottom_edge + rotated_shape.y > self.height:
            return False
        
        if not self.is_collision(rotated_shape):                                #if no collision is detected on the rotated shape
            self.active_shape = rotated_shape                                   #set the new rotated shape to be the active shape
    
    def move_left(self):
        """
        Moves the active shape left if possible, and returns true. If it is not possible to move, then returns False.
        """
        self.active_shape.x -= 1                                                #moves the shape by 1 unit to the left
        if self.out_of_bounds() or self.is_collision():                         #checks if the move causes the shape to collide with another shape or go out of bounds
            self.active_shape.x += 1                                            #if there is a collision or it goes out of bounds, then reset the shape back to it's previous position
            return False                                                        #return false if it is not possible to move left
        return True                                                             #return true if it is possible to move left
    
    def move_right(self):
        """
        Moves the active shape right if possible, and returns true. If it is not possible to move, then returns False.
        """
        self.active_shape.x += 1                                                #moves the shape by 1 unit to the right
        if self.out_of_bounds() or self.is_collision():                         #checks if the move causes the shape to collide with another shape or go out of bounds
            self.active_shape.x -= 1                                            #if there is a collision or it goes out of bounds, then reset the shape back to it's previous position
            return False                                                        #return false if it is not possible to move right
        return True                                                             #return true if it is possible to move right
    
    def move_down(self):
        """
        Moves the active shape down if possible, and returns true. If it is not possible to move, then returns False.
        """
        self.active_shape.y += 1                                                #moves the shape by 1 unit down
        
        if self.check_bottom() or self.is_collision():                          #Checks if the new position of the shape causes the shape to hit to the bottom or cause a collision
            self.active_shape.y -= 1                                            #if so, reset back to the original position of the shape
            self.shape_to_board()                                               #add shape to permant location on the board
            self.add_shape()                                                    #add a new shape, as the current one has hit the bottom
            return False                                                        #return false because the move was not possible
        return True                                                             #return true because the move was possible
    
    def out_of_bounds(self, shape=None):
        """
        Checks if the shape has gone out of bounds on the two sides of the board
        """
        shape = shape or self.active_shape                                      #check the shape that gets passed in, or by default the currently selected shape
        if shape.x + shape.left_edge < 0:                                       #check for the shape going off the left side of the board
            return True                                                         #return true if it does
        elif shape.x + shape.right_edge >= self.width:                          #check for the shape going off the of the right side of the board
            return True                                                         #return true if it does
        return False                                                            #if the shape does not go out of the left and right bounds, then return false
    
    def check_bottom(self, shape=None):
        """
        Checks if the shape has hit the bottom of the board.
        """
        shape = shape or self.active_shape                                      #the shape to be checked if not passed in, will be the current shape for the board
        if shape.y + shape.bottom_edge >= self.height:                          #if the shape has hit the bottom, or goes lower than the bottom of the board
            return True                                                         #return true as the shape is at the bottom
        return False                                                            #return false as the shape has not hit the bottom
    
    def is_collision(self, shape=None):
        """
        Check if a shape has collide with other shapes that are transposed onto the board.
        """
        shape = shape or self.active_shape                                      #checks the current shape or a user specified shape
        for y in range(4):                                                      #range from the bottom of a shape (0) to the top (3)
            for x in range(4):                                                  #range from the left of a shape (0) to the right (3)
                if y + shape.y < 0:                                             #
                    continue                                                    #skip this iteration of the loop
                if shape.shape[y][x] and self.board[y + shape.y][x + shape.x]:  #if a point on the shape collides with a transposed shape on the board
                    return True                                                 #return true as there is a collision
        return False                                                            #return false as there is no collision detected
    
    def test_for_line(self):
        """
        Test is there is a full row, if so then the row can be removed
        """
        for y in range(self.height - 1, -1, -1):                                #loop from the top the of the board (self.height-1) to the bottom of the board (0)
            counter = 0                                                         #use a counter to keep track of how many blocks are encountered in each row
            for x in range(self.width):                                         #loop through each block in the current row
                if self.board[y][x] == BLOCK_FULL:                              #if there exists a block in that cell
                    counter += 1                                                #then increment the counter to indicate that there is a block in that cell
            if counter == self.width:                                           #check if the number of blocks within the row are equal to the number of cells in the row, if yes the row is full
                self.process_line(y)                                            #remove the current row, and move all lines above it down one line
                return True                                                     #return true as a line was found
        return False                                                            #return false as a line was not found after looping through all cells within the board
    
    def process_line(self, y_to_remove):
        """
        Removed a row based on the row value provided in the argument by moving all over rows above it it down by one unit.
        """
        for y in range(y_to_remove - 1, -1, -1):                                #loop from the the row to remove, and iterate down to 0
            for x in range(self.width):                                         #process each block within that row
                self.board[y + 1][x] = self.board[y][x]                         #overwrite the previous row
    
    def shape_to_board(self):
        # transpose onto board
        # while test for line, process & increase score
        for y in range(4):                                                      #loop through y coordinates in the shape, from bottom(0) to top(3)
            for x in range(4):                                                  #loop through y coordinates in the shape, from left(0) to right(3)
                dx = x + self.active_shape.x                                    #calculate the for where the x coordinate will lie on the board
                dy = y + self.active_shape.y                                    #calculate the for where the x coordinate will lie on the board
                if self.active_shape.shape[y][x] == BLOCK_FULL:                 #if the the current block is a filled block
                    self.board[dy][dx] = BLOCK_FULL                             #then transpose it onto the board
        
        lines_found = 0                                                         #checks the number of lines found on the board to keep track of the score
        while self.test_for_line():                                             #uses the line test function to find all lines and remove them
            lines_found += 1                                                    #when lines are found, increase the player score by 1
        
        if lines_found:                                                         #if the players score increased
            self.dispatch_event('on_lines', lines_found)                        #then update the score

    def move_piece(self, motion_state):
        """
        Defines a set of keyboard events to perform actions on the shape within the game.
        """
        if motion_state == key.MOTION_LEFT:                                     #listens for the left arrow key
            self.move_left()                                                    #move the shape left by one unit if possible
        elif motion_state == key.MOTION_RIGHT:                                  #listens for the right arrow key
            self.move_right()                                                   #move the shape right by one unit if possible
        elif motion_state == key.MOTION_UP:                                     #listens for the up arrow key
            self.rotate_shape()                                                 #rotate the shape clockwise by 90 degrees
        elif motion_state == key.MOTION_DOWN:                                   #listens for the down arrow key
            self.move_down()                                                    #move the shape down by one unit if possible
    
    def draw_game_board(self):
        """
        Draws the game board at each frame based on the values of the current board matrix.
        """
        for y, row in enumerate(board.board):                                   #loop over each row within the board
            for x, col in enumerate(row):                                       #loop ovr each column at each row to select each cell at y, x
                if col == BLOCK_FULL or col == BLOCK_ACTIVE:                    #check if the current column has an stationary block (FULL) or a moving block (ACTIVE)
                    self.draw_block(x, y)                                       #if a block exists, then draw the block on the screen using the x y coordinates provided by the loop
        
        for y in range(4):                                                      #
            for x in range(4):
                dx = x + self.active_shape.x
                dy = y + self.active_shape.y
                if self.active_shape.shape[y][x] == BLOCK_FULL:
                    self.draw_block(dx, dy)
    
    def draw_block(self, x, y):
        """
        Draws a block onto the screen using the blit method in pyglet
        """
        y += 1 # since calculated_height does not account for 0-based index
        self.block.blit(x * BLOCK_WIDTH, self.calculated_height - y * BLOCK_HEIGHT)


Board.register_event_type('on_lines')                                           #event listener to update score and increase difficulty
Board.register_event_type('on_game_over')                                       #event listener to check for a game over


class Game(object):
    """
    The game class puts together the other two classes, and contains functionality to run the game loop, handle keyboard events, and update the window title with the user score.
    """
    ticks = 0
    factor = 4
    frame_rate = 60.0                                                           #the game window will update 60 times a second for a framerate of 60fps
    
    is_paused = False
    
    def __init__(self, window_ref, board, starting_level=1):
        """
        Constructor: sets up the window, the board, and the callback functions
        """
        self.window_ref = window_ref                                            #sets the specifications for the window and creates it
        self.board = board                                                      #Sets the default game board
        self.starting_level = int(starting_level)                               #if the starting level is specified by the user, set it manually
        self.register_callbacks()                                               #register callback functions for
        self.reset()
    
    def register_callbacks(self):
        """ Sets up the callback functions for drawing, and keyboard """
        self.board.push_handlers(self)                                          #pushes event handlers onto the stack (drawing, and keyboard)
    
    def reset(self):
        """
        Resets the current game, but setting the start level back to the start level specified by the user, and reseting the score.
        """
        self.level = self.starting_level
        self.lines = 0
        self.score = 0
    
    def should_update(self):
        if self.is_paused:                                                      #check if the game is currently paused
            return False                                                        #if paused, don't update board
        
        self.ticks += 1
        if self.ticks >= (self.frame_rate - (self.level * self.factor)):
            self.ticks = 0
            return True
        return False
    
    def draw_handler(self):
        self.window_ref.clear()                                                 #Clears the screen
        self.board.draw_game_board()                                            #draws the game board, which can be called at every frame to animate the application
    
    def keyboard_handler(self, motion):
        self.board.move_piece(motion)                                           #sets up the keyboard handler, by passing the key values into the board keyboard function
    
    def on_lines(self, num_lines):
        """
        Sets the score and current level;
        """
        self.score += (num_lines * self.level)                                  #the score per line increases as the level increase
        self.lines += num_lines
        if self.lines / 10 > self.level:
            self.level = self.lines / 10                                        #Set the level one the user reaches level * 10 lines
    
    def on_game_over(self):
        self.reset()                                                            #reset the game on game overs
    
    def cycle(self):
        if self.should_update():                                                #cycles through the game as long as it is not paused
            self.board.move_down()                                              #start moving shapes down if the game is not paused
            self.update_caption()                                               #set the score in the window title at each frame
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused                                     #pause or unpause the game
    
    def update_caption(self):
        self.window_ref.set_caption('Tetris - %s lines [%s]' % (self.lines, self.score)) #sets the window title to be the number of lines and the current score


board = Board(BOARD_WIDTH, BOARD_HEIGHT, block)                                 #create a board with the specified height, width, and the block image

if len(sys.argv) > 1:
    starting_level = int(sys.argv[1])                                           #set a custom level if it is given by the user
else:
    starting_level = 1                                                          #if a custom level is not set, then start at level 1

game = Game(window, board, starting_level)                                      #start a new game using the board and specified starting level

@window.event
def on_draw():
    game.draw_handler()                              x                           #sets the draw handling event for pyglet

@window.event
def on_text_motion(motion):
    game.keyboard_handler(motion)                                               #sets the keyboard handling even for pyglet

@window.event
def on_key_press(key_pressed, mod):
    if key_pressed == key.P:
        game.toggle_pause()                                                     #pauses the game using the 'P' key

def update(dt):
    game.cycle()                                                                #runs an infinite game cycle

pyglet.clock.schedule_interval(update, 1 / game.frame_rate)
pyglet.app.run()
