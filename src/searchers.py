import queue
from typing import Tuple
from helpers import Stack, Queue, PriorityQueue

class Offset:
    '''
    Used to provide directions in terms of rows and columns with the top left being (0, 0)
    '''
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Searcher:
    '''
    Abstract class for searchers
    '''

    def _is_valid(self, maze, position) -> bool:
        '''
        Returns True if position is inside maze bounds and not a wall
        '''
        x, y = position
        if x < 0 or x > len(maze) - 1:
            return False
        if y < 0 or y > len(maze[0]) - 1:
            return False
        
        if maze[x][y] == '#':
            return False
        
        return True

    def _get_path(self, end) -> list[tuple]:
        '''
        Returns the path to a given end state by backtracing the predecessors
        '''
        path = []
        position = end
        while position is not None:
            path.append(position)
            position = self.predecessors[position]
        
        path.reverse()

        return path

class DepthFirstSearcher(Searcher):
    '''
    Searching algorithm that implements a Stack (LIFO)
    '''
    def __init__(self):
        self.stack = Stack()
        self.predecessors = {}
    
    def solve(self, maze, start, goal, progress_queue = None, path_queue = None):
        '''
        Find a path between a given start and goal point, if possible
        '''
        self.stack.push(start)
        self.predecessors[start] = None

        while not self.stack.is_empty():
            position = self.stack.pop()

            # Add position to queue for multithreading
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
    '''
    Searching algorithm that uses a Queue (FIFO)
    '''
    
    def __init__(self):
        self.queue = Queue()
        self.predecessors = {}
    
    def solve(self, maze, start, goal, progress_queue = None, path_queue = None):
        '''
        Find a path between a given start and goal point, if possible
        '''
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
    '''
    Searching algorithm that uses a PriorityQueue with priority based on heuristics
    '''
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.predecessors = {}
        self.g_values = {}
    
    def solve(self, maze, start, goal, progress_queue, path_queue):
        '''
        Find a path between a given start and goal point, if possible
        '''
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
