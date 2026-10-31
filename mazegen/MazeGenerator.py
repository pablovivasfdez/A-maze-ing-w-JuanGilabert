""" Generador de laberintos
Aquí está probablemente la parte más interesante.

Tenemos que garantizar:
    conectividad;
    paredes coherentes entre celdas vecinas;
    entrada y salida válidas;
    bordes exteriores cerrados;
    ausencia de áreas abiertas de 3×3;
    reproducibilidad mediante seed;
    modo PERFECT=True;
    modo PERFECT=False;
    patrón 42 cuando el tamaño lo permita.

Para PERFECT=True debe existir un único camino entre entrada y salida.(COMPROBAR CON Djikstra QUE SOLO HAY 1 RUTA ENTRE ENTRADA Y SALIDA, NO EN GENERAL)

Para PERFECT=False, en cambio, tenemos que generar un tablero jugable tipo Pac-Man con múltiples rutas y las condiciones específicas de las esquinas y centro.

Aquí tendremos que ser especialmente cuidadosos:
    no basta con implementar un algoritmo estándar de generación de laberintos y ya está. Hay restricciones adicionales del proyecto.

    ┌───────────────────────┐
    │    MazeGenerator      │
    ├───────────────────────┤
    │ generate()            │
    │ generate_perfect()    │
    │ generate_playable()   │
    └───────────┬───────────┘
                │
        ┌───────┴───────────┐
        │                   │
PERFECT=True         PERFECT=False
        │                   │
        ▼                   ▼
Perfect generator    Playable generator
        │                   │
        └─────────┬─────────┘
                  ▼
                Maze


Además, hay que preparar el paquete para poder construir un:
        mazegen-1.0.0-py3-none-any.whl o .tar.gz
y el repositorio debe contener todo lo necesario para volver a construirlo


PERFECT=True
Tenemos que generar un perfect maze, es decir, un laberinto con un único camino entre entrada y salida.
Aquí algoritmos como:
    Recursive Backtracker
    Prim
    Kruskal
son candidatos naturales.


PERFECT=False

Aquí no basta con generar un maze perfecto y quitar una pared.

El PDF exige:
    conectividad completa;
    las cuatro esquinas abiertas;
    centro abierto;
    al menos dos rutas independientes;
    pocos dead ends;
    que sea utilizable como tablero tipo Pac-Man.

Por eso diseñaría estos dos modos conscientemente, en vez de intentar que un único algoritmo haga todo.

Ejemplo:
    generator = MazeGenerator(
        width=20,
        height=15,
        seed=42
    )
    maze = generator.generate()
    solution = generator.solve()



            │
            ▼
          Maze
"""
class MazeGenerator:
    """Generate and manipulate mazes."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | None = None,
        perfect: bool = False,
    ) -> None:
        ...

    def generate(self) -> None:
        """Generate a new maze."""
        ...#TODO: Se usara MazeGenerator

    def generate_perfect() -> ...:
        ...
    
    def generate_playable() -> ...:
        ...
    
    def get_maze(self) -> ...:
        """Return the generated maze structure."""
        ...

    def solve(self, entry: ..., exit: ...) -> str:
        """Return a valid shortest path."""
        ...#TODO: Se usara MazeSolver


import random

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def ft_hunt(
        seen: set[tuple[int, int]], width: int, height: int,
        grid: list[list[int]], rng: random.Random) -> tuple[int, int] | None:
    for y in range(height):
        for x in range(width):
            if (x, y) in seen:
                continue
            dirs = neighbours((x, y), seen, width, height, True)
            if (dirs):
                carve((x, y), rng.choice(dirs), grid)
                return (x, y)
    return None


def inbounds(x: int, y: int, width: int, height: int) -> bool:
    return(0 <= x < width and 0 <= y < height)


def carve(position: tuple[int, int], d: str, grid: list[list[int]]) -> None:
    x, y = position
    dx, dy = DELTA[d]
    nx, ny = x + dx, y + dy
    grid[y][x] &= ~BIT[d]
    grid[ny][nx] &= ~BIT[OPPOSITE[d]]


def neighbours(
        position: tuple[int, int], seen: set[tuple[int, int]], width: int,
        height: int, visited: bool):
    x, y = position
    res = []
    for dir, (dx, dy) in DELTA.items():
        nx = x + dx
        ny = y + dy
        if (inbounds(nx, ny, width, height) and ((nx, ny) in seen) == visited):
            res.append(dir)
    return res
    

def search_square(x: int, y: int, grid: list[list[int]]) -> bool:
    for l in range(x, x + 2):
        for c in range(y, y + 2):
            if (grid[c][l] & BIT["E"] or grid[c][l] & BIT["S"]): return True
    return False


def makes_3_square(x: int, y: int, nx: int, ny: int, width: int, height: int, grid: list[list[int]], d: str) -> bool:
    min_x = max(0, min(x, nx) - 2)
    min_y = max(0, min(y, ny) - 2)
    max_x = min(width - 3, max(x ,nx))
    max_y = min(height - 3, max(y, ny))
    orig_val = grid[y][x]
    orig_nval = grid[ny][nx]
    grid[y][x] &= ~BIT[d]
    grid[ny][nx] &= ~BIT[OPPOSITE[d]]
    creates = False
    for sy in range(min_y, max_y + 1):
        for sx in range(min_x, max_x + 1):
            if not search_square(sx, sy, grid):
                reates = True
                break
        if creates: break
    grid[y][x] = orig_val
    grid[ny][nx] = orig_nval
    return creates


def hunt_and_kill(width: int, height: int, start: tuple[int, int], seed: int | None, perfect: bool) -> list[list[int]]:
    rng = random.Random(seed)
    grid = [[15] * width for _ in range(height)]
    seen = {start}
    x, y = start
    while True:
        dirs = neighbours((x, y), seen, width, height, False)
        if (dirs):
            d = rng.choice(dirs)
            carve((x, y), d, grid)
            dx, dy = DELTA[d]
            x, y = x + dx, y + dy
            seen.add((x, y))
        else:
            cell = ft_hunt(seen, width, height, grid, rng)
            if cell is None:
                break
            x, y = cell
            seen.add((x, y))
    if not (perfect):
        for cy in range(height):
            for cx in range(width):
                if (rng.random() < 0.15):
                    dirs = list(DELTA)
                    rng.shuffle(dirs)
                    for d in dirs:
                        dx, dy = DELTA[d]
                        nx, ny = cx + dx, cy + dy
                        if (inbounds(nx, ny, width, height) and (grid[cy][cx] & BIT[d]) and not makes_3_square(cx, cy, nx, ny, width, height, grid, d)):
                            grid[cy][cx] &= ~BIT[d]
                            grid[ny][nx] &= ~BIT[OPPOSITE[d]]
    return grid


from collections import deque
import random
#from core.MazeDirections import MazeDirection
# from core.MazeCell import MazeCell

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "E": "W", "S": "N", "W": "E"}
LOGO = []
DELTA = {"N" : (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
DECISION = [0, 1, 2]


def all_visited(x: int, y: int, visited: set[tuple[int, int]]) -> bool:
    dirs = list(DELTA)
    for d in dirs:
        dx, dy = DELTA[d]
        nx, ny = x + dx, y +dy
        if ((nx, ny) not in visited): return False
    return True


def search_square(x: int, y: int, grid: list[list[int]]) -> bool:
    for l in range(x, x + 2):
        for c in range(y, y + 2):
            if (grid[c][l] & BIT["E"] or grid[c][l] & BIT["S"]): return True
    return False


def makes_3_square(x: int, y: int, nx: int, ny: int, width: int, height: int, grid: list[list[int]]) -> bool:
    min_x = max(0, min(x, nx) - 2)
    min_y = max(0, min(y, ny) - 2)
    max_x = min(width - 3, max(x ,nx))
    max_y = min(height - 3, max(y, ny))

    for sy in range(min_y, max_y + 1):
        for sx in range(min_x, max_x + 1):
            if not search_square(sx, sy, grid): return True
    return False



def bfs(width: int, height: int, start: tuple[int, int], seed: int | None, perfect: bool) -> list[list[int]]:
    rng = random.Random(seed)
    queue = deque([start])
    visited = {start}
    grid = [[15] * width for _ in range(height)]
    while queue:
        dirs = list(DELTA)
        node = queue.pop()
        x, y = node
        rng.shuffle(dirs)
        visited.add(node)
        for d in dirs:
            dx, dy = DELTA[d]
            nx, ny = x + dx, y + dy
            if (all_visited(x, y, visited) and not perfect):
                if (rng.random() < 0.45 and not makes_3_square(x, y, nx, ny, width, height, grid)):
                    grid[y][x] &= ~BIT[d]
                    grid[ny][nx] &= ~BIT[OPPOSITE[d]]
                    continue
            if ((nx ,ny) in visited): continue
            if not (0 <= nx < width and 0 <= ny < height): continue
            if ((nx, ny) in LOGO):continue
            grid[y][x] &= ~BIT[d]
            grid[ny][nx] &= ~BIT[OPPOSITE[d]]
            queue.append((nx, ny))
            visited.add((nx, ny))
    return grid




 
