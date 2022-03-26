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
        self.text = self.FONT.render(text, True, text_color)
        self.button_color = button_color
        self.text_position = (x + 5, y)
    
    def draw(self):
        pygame.draw.rect(self.window, self.button_color, self.rect)
        self.window.blit(self.text, self.text_position)


class Game:

    def __init__(self, maze: Maze, searcher: searchers.Searcher):
        self.maze = maze
        self.searcher = searcher
        self.window = None
        self.clock = None
        self.goal = None
        self.buttons = None
    
    def show(self):
        self._initialize()
        self._display()

    def _initialize(self):
        maze_width = self.maze.width * 20
        maze_height = self.maze.height * 20
        width = maze_width + 100 if maze_width > 500 else 600
        height = maze_height + 180 if maze_height > 420 else 600

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Maze')
        self.clock = pygame.time.Clock()

        self.buttons = [
            Button(self.window, (int(width/3), 50), (70, 30), 'SOLVE'),
            Button(self.window, (int(width/3) + 100, 50), (70, 30), 'RESET', pygame.Color(235, 64, 52), WHITE)
        ]
    
    def _display(self):
        run = True
        while run:
            self.window.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
            
            self._draw_buttons()
            self._draw_maze()

            pygame.display.update()
    
    def _draw_maze(self):
        y = 130

        for line in self.maze.grid:
            x = 50
            for tile in line:
                if tile == '#':
                    rect = pygame.Rect(x, y, 20, 20)
                    pygame.draw.rect(self.window, WHITE, rect)
                
                x += 20
            y += 20

    def _draw_buttons(self):
        for button in self.buttons:
            button.draw()

if __name__ == '__main__':
    s = searchers.DepthFirstSearcher()
    m = Maze('src/mazes/simple.txt')

    game = Game(m, s)
    game.show()