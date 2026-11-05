import random

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class HuntAndKill:

    def __init__(
            self, width: int, height: int, start: tuple[int, int],
            seed: int | None, perfect: bool, logo: list[tuple[int, int]]
            ) -> None:
        if start in logo:
            raise ValueError("El punto de entrada (ENTRY) no puede estar dentro del logo.")
        self.width = width
        self.height = height
        self.start = start
        self.perfect = perfect
        self.logo = logo
        self.rng = random.Random(seed)
        self.grid = [[15] * width for _ in range(height)]
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

    def search_square(self, x: int, y: int) -> bool:
        for l in range(x, x + 2):
            for c in range(y, y + 2):
                if (self.grid[c][l] & BIT["E"] or self.grid[c][l] & BIT["S"]): return True
        return False

    def makes_3_square(self, x: int, y: int, nx: int, ny: int, d: str) -> bool:
        min_x = max(0, min(x, nx) - 2)
        min_y = max(0, min(y, ny) - 2)
        max_x = min(self.width - 3, max(x, nx))
        max_y = min(self.height - 3, max(y, ny))
        orig_val = self.grid[y][x]
        orig_nval = self.grid[ny][nx]
        self.grid[y][x] &= ~BIT[d]
        self.grid[ny][nx] &= ~BIT[OPPOSITE[d]]
        creates = False
        for sy in range(min_y, max_y + 1):
            for sx in range(min_x, max_x + 1):
                if not self.search_square(sx, sy):
                    creates = True
                    break
            if creates: break
        self.grid[y][x] = orig_val
        self.grid[ny][nx] = orig_nval
        return creates

    def generate(self) -> list[list[int]]:
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

        # 3 anidados, igual se puede hacer a la vez que se genera o quitar el tercer for cogiendo solamente una direccion
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
        return self.grid
