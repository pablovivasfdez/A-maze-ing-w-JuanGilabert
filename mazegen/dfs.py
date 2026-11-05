from .MazeGenerator import MazeGenerator
import random
#from core.MazeDirections import MazeDirection
# from core.MazeCell import MazeCell

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "E": "W", "S": "N", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class DFS(MazeGenerator):

    def all_visited(self, x: int, y: int) -> bool:
        dirs = list(DELTA)
        for d in dirs:
            dx, dy = DELTA[d]
            nx, ny = x + dx, y + dy
            if not (0 <= nx < self.width and 0 <= ny < self.height): continue
            if (nx, ny) in self.logo: continue
            if ((nx, ny) not in self.visited): return False
        return True

    def _carve(self) -> None:
        self.stack = [self.start]
        while self.stack:
            x, y = self.stack[-1]
            dirs = list(DELTA)
            self.rng.shuffle(dirs)
            for d in dirs:
                dx, dy = DELTA[d]
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height): continue
                if ((nx, ny) in self.logo): continue
                if (self.all_visited(x, y) and not self.perfect):
                    if (self.grid[y][x] & BIT[d]
                            and self.rng.random() < 0.15
                            and not self.makes_3_square(x, y, nx, ny, d)):
                        self.grid[y][x] &= ~BIT[d]
                        self.grid[ny][nx] &= ~BIT[OPPOSITE[d]]
                        continue
                if ((nx, ny) in self.visited): continue
                self.grid[y][x] &= ~BIT[d]
                self.grid[ny][nx] &= ~BIT[OPPOSITE[d]]
                self.visited.add((nx, ny))
                self.stack.append((nx, ny))
                break
            else:
                self.stack.pop()  # backtrack
