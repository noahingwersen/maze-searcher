class Maze:

    def __init__(self, maze_file: str):
        self.grid = self._load(maze_file)
        self.height = len(self.grid)
        self.width = len(self.grid[0])

    def _load(self, file: str):
        try:
            with open(file, 'r') as f:
                maze = []
                for line in f.readlines():
                    maze.append(line.strip('\n'))
            
            return maze

        except FileNotFoundError:
            print('Unable to find the specified maze file')
            raise SystemExit
    
if __name__ == '__main__':
    m = Maze('src/mazes/simple.txt')