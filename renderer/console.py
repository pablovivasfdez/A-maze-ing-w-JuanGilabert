"""
console.py podría convertirlo a ANSI:
    ansi_wall = hex_to_ansi(palette.wall)

mientras que mlx.py podría convertirlo a RGB:
    rgb_wall = hex_to_rgb(palette.wall)

"""
from core.maze import Maze
from core.MazeDirections import Direction, DELTAS
from enum import Enum


class Style(Enum):
    WALL = "#"
    FLOOR = "."
    LOGO = "L"
    START = "S"
    END = "E"

def write_matrix(maze: Maze) -> list[list[str]]:

    lines, columns = maze.height * 2 + 1, maze.width * 2 + 1
    grid = [["#" for _ in range(columns)] for _ in range(lines)]

    for i in range(maze.height):
        for j in range(maze.width):
            grid[2 * i +1][2 * j + 1] = "."
            if (maze.is_fully_surrounded(j, i)):
                grid[2 * i + 1][2 * j + 1] = Style.LOGO
            else:
                for dir in Direction:
                    if (not maze.has_wall(j, i, dir)):
                        dx, dy = DELTAS[dir]
                        grid[2 * i + 1 + dy][2 * j + 1 + dx] = Style.FLOOR
    return grid


