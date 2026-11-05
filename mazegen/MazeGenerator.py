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
import random

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "E": "W", "S": "N", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


class MazeGenerator:

    def __init__(
            self, width: int, height: int, start: tuple[int, int],
            seed: int | None, perfect: bool, logo: list[tuple[int, int]]
            ) -> None:
        if start in logo:
            raise ValueError("The start point (ENTRY) can not be on the logo.")
        self.width = width
        self.height = height
        self.start = start
        self.perfect = perfect
        self.logo = logo
        self.rng = random.Random(seed)
        self.visited = {start}
        self.grid = [[15] * width for _ in range(height)]

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

    def _carve(self) -> None:
        raise NotImplementedError

    def generate(self) -> list[list[int]]:
        self._carve()
        return self.grid






 
