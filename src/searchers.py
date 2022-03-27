import queue
from typing import Tuple
from helpers import Stack, Queue, PriorityQueue

class Offset:
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Searcher:
    def solve(self, maze, start, goal):
        pass

    def _is_valid(self, maze, position) -> bool:
        x, y = position
        if x < 0 or x > len(maze):
            return False
        if y < 0 or y > len(maze[0]):
            return False
        
        if maze[x][y] == '#':
            return False
        
        return True

    def _get_path(self, end) -> list[tuple]:
        path = []
        position = end
        while position is not None:
            path.append(position)
            position = self.predecessors[position]
        
        path.reverse()

        return path

class DepthFirstSearcher(Searcher):
    def __init__(self):
        self.stack = Stack()
        self.predecessors = {}
    
    def solve(self, maze: list[list[str]], start: Tuple[int, int], goal: Tuple[int, int],
            progress_queue: queue.Queue = None, path_queue: queue.Queue = None):
        
        self.stack.push(start)
        self.predecessors[start] = None

        while not self.stack.is_empty():
            position = self.stack.pop()
            if progress_queue:
                progress_queue.put(position)

            if position == goal:
                path = self._get_path(goal)

                # Add path to queue for multithreading
                if path_queue:
                    for position in path:
                        path_queue.put(position)
                
                return path

            for direction in [Offset.UP, Offset.RIGHT, Offset.DOWN, Offset.LEFT]:
                neighbor = (position[0] + direction[0], position[1] + direction[1])

                if self._is_valid(maze, neighbor) and neighbor not in self.predecessors:
                    self.stack.push(neighbor)
                    self.predecessors[neighbor] = position

        return None


class BredthFirstSearcher(Searcher):
    
    def __init__(self):
        self.queue = Queue()
        self.predecessors = {}
    
    def solve(self, maze, start, goal, progress_queue = None, path_queue = None):
        self.queue.enqueue(start)
        self.predecessors[start] = None

        while not self.queue.is_empty():
            position = self.queue.dequeue()
            if progress_queue:
                progress_queue.put(position)

            if position == goal:
                path =  self._get_path(goal)
                if path_queue:
                    for position in path:
                        path_queue.put(position)
                
                return path
            
            for direction in [Offset.UP, Offset.RIGHT, Offset.DOWN, Offset.LEFT]:
                neighbor = (position[0] + direction[0], position[1] + direction[1])

                if self._is_valid(maze, neighbor) and neighbor not in self.predecessors:
                    self.queue.enqueue(neighbor)
                    self.predecessors[neighbor] = position

        return None


class AStarSearcher(Searcher):
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.predecessors = {}
        self.g_values = {}
    
    def solve(self, maze, start, goal, progress_queue, path_queue):
        self.queue.enqueue(start, self._get_distance(start, goal))
        self.predecessors[start] = None
        self.g_values[start] = 0

        while not self.queue.is_empty():
            position = self.queue.dequeue()
            if progress_queue:
                progress_queue.put(position)

            if position == goal:
                path = self._get_path(goal)
                if path_queue:
                    for position in path:
                        path_queue.put(position)
                
                return path
            
            for direction in [Offset.UP, Offset.RIGHT, Offset.DOWN, Offset.LEFT]:
                neighbor = (position[0] + direction[0], position[1] + direction[1])

                if self._is_valid(maze, neighbor) and neighbor not in self.predecessors:
                    g_value = self.g_values[position] + 1
                    h_value = self._get_distance(neighbor, goal)
                    f_value = g_value + h_value

                    self.queue.enqueue(neighbor, f_value)
                    self.predecessors[neighbor] = position
                    self.g_values[neighbor] = g_value
        
        return None

    def _get_distance(self, start, end):
        '''
        Returns the "Manhattan distance" between two locations
        '''
        x_dist = abs(end[0] - start[0])
        y_dist = abs(end[1] - start[1])
        
        return x_dist + y_dist 


if __name__ == '__main__':
    from maze import Maze
    m = Maze('src/mazes/simple.txt')
    s = DepthFirstSearcher()
    test = s.solve(m.grid, (14,1), (2, 10))
    stop = 'vreak'