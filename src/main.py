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
        self.window = pygame.display.set_mode((600, 600))
        pygame.display.set_caption('Maze')
        self.clock = pygame.time.Clock()

        self.buttons = [
            Button(self.window, (200, 60), (70, 30), 'SOLVE'),
            Button(self.window, (300, 60), (70, 30), 'RESET', pygame.Color(235, 64, 52), WHITE)
        ]

        self.maze_border = [
           # pygame.Rect()
        ]
    
    def _display(self):
        run = True
        while run:
            self.window.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
            
            self._draw_buttons()

            pygame.display.update()
    
    def _draw_maze(self):
        pass
    
    def _draw_buttons(self):
        for button in self.buttons:
            button.draw()

if __name__ == '__main__':
    s = searchers.DepthFirstSearcher()
    m = Maze('src/mazes/simple.txt')

    game = Game(m, s)
    game.show()