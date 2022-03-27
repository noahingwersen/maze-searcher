import threading
import queue
import pygame
import searchers
from maze import Maze
pygame.init()

WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

class Button:
    FONT = pygame.font.SysFont('ComicSans', 12)

    def __init__(self, window: pygame.Surface, position: tuple,
            size: tuple, text: str, button_color: pygame.Color = WHITE, text_color: pygame.Color = BLACK):
        x, y = position
        width, height = size
        self.rect = pygame.Rect(x, y, width, height)
        self.window = window
        self.name = text
        self.text = self.FONT.render(text, True, text_color)
        self.button_color = button_color
        self.text_position = (x + 5, y)
    
    def draw(self):
        pygame.draw.rect(self.window, self.button_color, self.rect)
        self.window.blit(self.text, self.text_position)
    
    def set_text(self, text: str, color: pygame.Color):
        self.text = self.FONT.render(text, True, color)


class Game:
    # Color options for various components
    SELECTED_SEARCHER_COLOR = pygame.Color(117, 32, 21)
    START_COLOR = pygame.Color(255, 0, 0)
    GOAL_COLOR = pygame.Color(255, 255, 0)
    PROGRESS_COLOR = pygame.Color(0, 125, 255)
    PATH_COLOR = pygame.Color(0, 255, 0)

    def __init__(self, maze: Maze):
        self.maze = maze
        self.window = None
    
    def show(self):
        '''
        Display the maze solver GUI
        '''
        self._initialize()
        self._display()
    
    def reset(self):
        '''
        Clears the variables used for solving
        '''
        self.progress = []
        self.path = []
        self.start_position = None
        self.goal_position = None

        self.progress_queue = None
        self.path_queue = None
        self.thread = None
    
    def solve(self):
        '''
        Find a path to the goal using the selected searcher (if possible)
        '''
        if not self.solving:
            self._set_searcher()
            self.show_path = False

            if self.start_position and self.goal_position:
                # Pass solving to another thread, use a queue to communicate between solver thread and main thread
                self.progress_queue = queue.Queue()
                self.path_queue = queue.Queue()
                solve_args = (
                    self.maze.grid,
                    self.start_position,
                    self.goal_position,
                    self.progress_queue,
                    self.path_queue
                )

                self.thread = threading.Thread(target = self.searcher.solve, args=solve_args, daemon=True)
                self.solving = True
                self.thread.start()

    def _initialize(self):
        '''
        Initializes GUI and variables, only runs once.
        '''
        self.solving = False

        # Adjust the size of the window for larger mazes. Min size is (600, 600)
        maze_width = self.maze.width * 20
        maze_height = self.maze.height * 20
        width = maze_width + 100 if maze_width > 500 else 600
        height = maze_height + 180 if maze_height > 420 else 600

        self.start_position = None
        self.goal_position = None
        self.progress_queue = None
        self.path_queue = None
        self.thread = None
        
        self.progress = []
        self.path = []
        self.show_path = False

        # Top left corner of the maze. It will be centered if the maze is less than 600 px
        self.maze_start_x = int((width - maze_width) / 2) if width == 600 else 50 
        self.maze_start_y = 130

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Maze')
        self.clock = pygame.time.Clock()

        # Default to DFS searcher
        self.searcher = searchers.DepthFirstSearcher()
        self.searcher_type = 'DFS'

        self.buttons = [
            Button(self.window, (50, 50), (70, 30), 'SOLVE', pygame.Color(20, 92, 32), WHITE),
            Button(self.window, (150, 50), (70, 30), 'RESET', pygame.Color(235, 64, 52), WHITE),
            Button(self.window, (width - 120, 50), (70, 30), 'A*'),
            Button(self.window, (width - 220, 50), (70, 30), 'BFS'),
            Button(self.window, (width - 320, 50), (70, 30), 'DFS', self.SELECTED_SEARCHER_COLOR, WHITE)
        ]

        font = pygame.font.SysFont('ComicSans', 14)
        self.instructions = font.render(
            '*Click to mark the starting position, then click again to mark the goal location.',
            True,
            WHITE
        )
    
    def _display(self):
        '''
        Main event loop
        '''
        run = True
        while run:
            self.window.fill(BLACK)

            # Incrementally add search progress with any frame tick so it doesn't overwhelm the user
            if self.progress_queue:
                if len(self.progress) != len(self.progress_queue.queue):
                    next_spot = next(tile for tile in self.progress_queue.queue if tile not in self.progress)
                    self.progress.append(next_spot)
                else:
                    self.show_path = True

            # Add the final path when the thread is complete
            if self.thread and not self.thread.is_alive():
                if self.solving and self.path_queue:
                    for tile in self.path_queue.queue:
                        self.path.append(tile)
                    
                    self.solving = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()

                    # Add start/goal positions if inside maze
                    if self._is_valid(mouse_position):
                        if self.start_position is None:
                            self.start_position = self._pixel_to_grid(mouse_position)
                        else:
                            if self.goal_position is None:
                                self.goal_position = self._pixel_to_grid(mouse_position)
                    
                    # Check if any buttons were clicked
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_position):
                            self._button_clicked(button)
            
            self._draw()
            self.clock.tick(30)

            pygame.display.update()

    ### Drawing Options ###

    def _draw(self):
        self._draw_buttons()
        self._draw_maze()
        self._draw_message()
        self._draw_paths()
        self._draw_objects()

    def _draw_buttons(self):
        for button in self.buttons:
            button.draw()

    def _draw_maze(self):
        y = self.maze_start_y

        for line in self.maze.grid:
            x = self.maze_start_x
            for tile in line:
                if tile == '#':
                    rect = pygame.Rect(x, y, 20, 20)
                    pygame.draw.rect(self.window, WHITE, rect)
                
                x += 20
            y += 20
        
        self.maze_end_x = x
        self.maze_end_y = y
    
    def _draw_message(self):
        self.window.blit(self.instructions, (5, 5))

    def _draw_paths(self):
        for tile in self.progress:
            self._color_block(tile, self.PROGRESS_COLOR)
        
        if self.show_path:
            for tile in self.path:
                self._color_block(tile, self.PATH_COLOR)

    def _draw_objects(self):
        if self.start_position:
            self._draw_circle(self.start_position, self.START_COLOR)
        
        if self.goal_position:
            self._draw_circle(self.goal_position, self.GOAL_COLOR)

    def _draw_circle(self, position, color):
            pixel = self._grid_to_pixel(position)
            center = (pixel[0] + 10, pixel[1] + 10)
            pygame.draw.circle(self.window, color, center, 10)

    def _color_block(self, position: tuple, color: pygame.Color):
        x, y = self._grid_to_pixel(position)
        rect = pygame.Rect(x, y, 20, 20)
        pygame.draw.rect(self.window, color, rect)
    

    ### Helper Functions ###

    def _is_valid(self, position: tuple) -> bool:
        '''
        Returns True if a position is within the maze boundaries and not a wall
        '''
        if position[0] < self.maze_start_x or position[0] > self.maze_end_x:
            return False
        
        if position[1] < self.maze_start_y or position[1] > self.maze_end_y:
            return False
        
        grid_x, grid_y = self._pixel_to_grid(position)

        if self.maze.grid[grid_x][grid_y] == '#':
            return False
        
        # Position is valid at this point
        return True
    
    def _set_searcher(self):
        '''
        Instantiates a new searcher of the selected type
        '''
        if self.searcher_type == 'DFS':
            self.searcher = searchers.DepthFirstSearcher()
        elif self.searcher_type == 'BFS':
            self.searcher = searchers.BredthFirstSearcher()
        elif self.searcher_type == 'A*':
            self.searcher = searchers.AStarSearcher()

    def _select_searcher(self, type: str):
        '''
        Set the searcher type and mark the appropriate button
        '''
        searcher_buttons = [button for button in self.buttons if button.name in ['DFS', 'BFS', 'A*']]
        for button in searcher_buttons:
            if button.name == type:
                button.set_text(button.name, WHITE)
                button.button_color = self.SELECTED_SEARCHER_COLOR
            else:
                # Reset any other searcher button options
                button.set_text(button.name, BLACK)
                button.button_color = WHITE
        
        self.searcher_type = type

    def _pixel_to_grid(self, pixels):
        '''
        Converts pixel location to grid indices
        '''
        x = int((pixels[1] - self.maze_start_y) / 20)
        y = int((pixels[0] - self.maze_start_x) / 20)

        return (x, y)

    def _grid_to_pixel(self, grid):
        '''
        Converts grid indices to pixel location
        '''
        x = grid[1] * 20 + self.maze_start_x
        y = grid[0] * 20 + self.maze_start_y

        return (x, y)
    

    ### Event Handlers ###

    def _button_clicked(self, button: Button):
        '''
        Determines event handler for the button that was clicked
        '''
        if button.name == 'RESET':
            self.reset()
        
        if button.name == 'SOLVE':
            self.solve()
        
        if button.name == 'DFS':
            self._select_searcher('DFS')
        
        if button.name == 'BFS':
            self._select_searcher('BFS')
        
        if button.name == 'A*':
            self._select_searcher('A*')

if __name__ == '__main__':  
    m = Maze('src/mazes/pacman.txt')
    game = Game(m)
    game.show()
