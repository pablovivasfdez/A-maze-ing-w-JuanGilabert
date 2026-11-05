from .MazeGenerator import MazeGenerator

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class HuntAndKill(MazeGenerator):

    def __init__(
            self, width: int, height: int, start: tuple[int, int],
            seed: int | None, perfect: bool, logo: list[tuple[int, int]]
            ) -> None:
        super().__init__(width, height, start, seed, perfect, logo)
        self.seen = {start} | set(logo)

    def ft_hunt(self) -> tuple[int, int] | None:
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.seen:
                    continue
                dirs = self.neighbours((x, y), True)
                if (dirs):
                    self.carve((x, y), self.rng.choice(dirs))
                    return (x, y)
        return None

    def inbounds(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and 0 <= y < self.height)

    def carve(self, position: tuple[int, int], d: str) -> None:
        x, y = position
        dx, dy = DELTA[d]
        nx, ny = x + dx, y + dy
        if ((nx, ny) in self.logo): return
        self.grid[y][x] &= ~BIT[d]
        self.grid[ny][nx] &= ~BIT[OPPOSITE[d]]

    def neighbours(self, position: tuple[int, int], visited: bool):
        x, y = position
        if ((x, y) in self.logo): return None
        res = []
        for dir, (dx, dy) in DELTA.items():
            nx = x + dx
            ny = y + dy
            if (self.inbounds(nx, ny) and ((nx, ny) in self.seen) == visited):
                res.append(dir)
        return res

    def _carve(self) -> None:
        x, y = self.start
        while True:
            dirs = self.neighbours((x, y), False)
            if (dirs):
                d = self.rng.choice(dirs)
                self.carve((x, y), d)
                dx, dy = DELTA[d]
                x, y = x + dx, y + dy
                self.seen.add((x, y))
            else:
                cell = self.ft_hunt()
                if cell is None:
                    break
                x, y = cell
                self.seen.add((x, y))

        if not (self.perfect):
            for cy in range(self.height):
                for cx in range(self.width):
                    if ((cx, cy) in self.logo): continue
                    if (self.rng.random() < 0.35):
                        dirs = list(DELTA)
                        d = self.rng.choice(dirs)
                        dx, dy = DELTA[d]
                        nx, ny = cx + dx, cy + dy
                        if ((nx, ny) in self.logo): continue
                        if (self.inbounds(nx, ny) and (self.grid[cy][cx] & BIT[d]) and not self.makes_3_square(cx, cy, nx, ny, d)):
                            self.grid[cy][cx] &= ~BIT[d]
                            self.grid[ny][nx] &= ~BIT[OPPOSITE[d]]
