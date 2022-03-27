# Maze Searcher

This application makes use of three different algorithms to find a path between a given start position and goal position.

![maze](https://user-images.githubusercontent.com/96736827/160293707-2691f83f-2e7d-41ce-a930-ae5f90f83cbc.png)

## Depth First Search (DFS)
This algorithm adds possible path positions to a stack architecture, which is a last in first out (LIFO) structure. This makes the search traverse long branches before doubling back to previous possibilities.

## Breadth First Search (BFS)
The breadth first search algorithm implements a queue architecture. This structure is denoted as first in first out (FIFO), which functions differently from the DFS algorithm. The search branches out evenly from the starting position, finding an efficient route but potentially taking longer to do so.

## A Star (A*)
Unlike the previous algorithms, the A* algorithms uses a simple heuristic to quickly find a path to the goal. Using a priority queue (highest priority out first), potential paths are ranked based on the distance to the goal
