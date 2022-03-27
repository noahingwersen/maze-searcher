'''
This file contains custom classes for the structures commonly used in the search algorithms
'''
from collections import deque
import heapq

class Stack:
    '''
    A stack follows 'Last In First Out' (LIFO) structure. The items stored in the stack are meant to be interacted with through the push and pop methods.
    '''

    def __init__(self):
        self._items = []
    
    def push(self, item):
        self._items.append(item)
    
    def pop(self):
        return self._items.pop(-1)
    
    def is_empty(self):
        return not self._items
    
    def size(self):
        return len(self._items)

    def __str__(self):
        return str(self._items)

class Queue:
    '''
    A queue follows 'First In First Out' (FIFO) structure.
    '''

    def __init__(self):
        self._items = deque([])
    
    def enqueue(self, item):
        self._items.append(item)
    
    def dequeue(self):
        return self._items.popleft()
    
    def is_empty(self):
        return not self._items
    
    def size(self):
        return len(self._items)

    def __str__(self):
        return str(self._items)

class PriorityQueue:
    '''
    A priority queue ensures that the item with the highest priority is at the top of the queue
    '''

    def __init__(self):
        self._items = []
    
    def enqueue(self, item, priority):
        heapq.heappush(self._items, (priority, item))
    
    def dequeue(self):
        # Return just the item, not the priority
        return heapq.heappop(self._items)[1]
    
    def is_empty(self):
        return not self._items
    
    def size(self):
        return len(self._items)
    
    def __str__(self):
        return str(self._items)
