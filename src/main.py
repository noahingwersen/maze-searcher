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


class Game:
    START_COLOR = pygame.Color(255, 0, 0)
    GOAL_COLOR = pygame.Color(255, 255, 0)
    PROGRESS_COLOR = pygame.Color(0, 125, 255)
    PATH_COLOR = pygame.Color(0, 255, 0)

    def __init__(self, maze: Maze, searcher: searchers.Searcher):
        self.maze = maze
        self.searcher = searcher
        self.window = None
        self.solving = False
    
    def show(self):
        self._initialize()
        self._display()
    
    def reset(self):
        self.progress = []
        self.path = []
        self.start_position = None
        self.goal_position = None

        self.progress_queue = None
        self.path_queue = None
        self.thread = None
    
    def solve(self):
        if not self.solving:
            self.show_path = False

            if self.start_position and self.goal_position:
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

        self.maze_start_x = int((width - maze_width) / 2) if width == 600 else 50 
        self.maze_start_y = 130

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Maze')
        self.clock = pygame.time.Clock()

        self.buttons = [
            Button(self.window, (int(width/3), 50), (70, 30), 'SOLVE', pygame.Color(20, 92, 32), WHITE),
            Button(self.window, (int(width/3) + 100, 50), (70, 30), 'RESET', pygame.Color(235, 64, 52), WHITE)
        ]

        font = pygame.font.SysFont('ComicSans', 14)
        self.instructions = font.render(
            '*Click to mark the starting position, then click again to mark the goal location.',
            True,
            WHITE
        )
    
    def _draw_message(self):
        self.window.blit(self.instructions, (5, 5))
    
    def _display(self):
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
                
                # When user clicks the mouse, draw the start or goal position
                # depending on if they already exist
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()

                    # Add start/goal positions if inside maze
                    if self.start_position is None:
                        self.start_position = self._create_object(mouse_position)
                    else:
                        if self.goal_position is None:
                            self.goal_position = self._create_object(mouse_position)
                    
                    for button in self.buttons:
                        if button.rect.collidepoint(mouse_position):
                            self._button_clicked(button)
            
            self._draw()
            self.clock.tick(30)

            pygame.display.update()
    
    def _draw(self):
        self._draw_buttons()
        self._draw_maze()
        self._draw_message()
        self._draw_paths()
        self._draw_objects()
    
    def _create_object(self, position: tuple) -> tuple:
        if self._is_valid(position):
            # Set the objects position in terms of maze array position, not pixel location
            # These will be used by the solver
            return self._pixel_to_grid(position)

    def _is_valid(self, position: tuple) -> bool:
        # Check if the position is outside maze boundary or a wall
        if position[0] < self.maze_start_x or position[0] > self.maze_end_x:
            return False
        
        if position[1] < self.maze_start_y or position[1] > self.maze_end_y:
            return False
        
        grid_x, grid_y = self._pixel_to_grid(position)

        if self.maze.grid[grid_x][grid_y] == '#':
            return False
        
        # Position is valid at this point
        return True
    
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
    
    def _color_block(self, position: tuple, color: pygame.Color):
        x, y = self._grid_to_pixel(position)
        rect = pygame.Rect(x, y, 20, 20)
        pygame.draw.rect(self.window, color, rect)

    def _draw_buttons(self):
        for button in self.buttons:
            button.draw()
    
    def _button_clicked(self, button: Button):
        '''
        Determines event handler for the button that was clicked
        '''
        if button.name == 'RESET':
            self.reset()
        
        if button.name == 'SOLVE':
            self.solve()

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

if __name__ == '__main__':
    # s = searchers.DepthFirstSearcher()
    # s = searchers.BredthFirstSearcher()
    s = searchers.AStarSearcher()
    
    m = Maze('src/mazes/pacman.txt')
    game = Game(m, s)
    game.show()