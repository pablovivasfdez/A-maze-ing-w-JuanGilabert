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
from collections import deque

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def ft_can_move(position: tuple[int, int]) -> bool:
    for dir in DELTA:
        dx, dy = DELTA[dir]
        


def ft_hunt(position: tuple[int, int], width: int, height: int) -> tuple[int, int]:
    x, y = position
    while y in range(height):
        for nx in range(width):
            if (ft_can_move((nx, y)))
                return ((nx, y))
        y = y + 1


def hunt_and_kill(width: int, height: int, start: tuple[int, int], seed: int | None) -> list[list[int]]:
    rng = random.Random(seed)
    grid = [[15] * width for _ in range(height)]
    queue = deque([start])
    seen = {start}
    x, y = queue.popleft()
    bool posibilidad = True
    while queue:
        if (posibilidad):
            x, y = queue.popleft()
        else:
            x, y = ft_hunt((x, y), width, height)
        posibilidad = False
        DELTA = rng.shuffle(DELTA)
        for dir in DELTA:
            dx, dy = DELTA[dir]
            nx, ny = x + dx, y + dy
            if ((nx, ny) not in seen):
                grid[y][x] &= ~BIT[dir]
                grid[ny][nx] &= ~BIT[OPPOSITE[dir]]
                seen.add((nx, ny))
                queue.append((nx, ny))
                posibilidad = True
                break
            else:
                continue
 
