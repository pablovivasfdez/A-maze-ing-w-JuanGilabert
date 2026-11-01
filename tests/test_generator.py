"""
test_generator.py
│   ├── seed reproducible
│   ├── diferentes seeds
│   └── solución
"""


def test_reproducible_seed():
    pass


def test_diferents_seeds():
    pass


def test_solution():
    pass


def test_generator():
    test_reproducible_seed()
    test_diferents_seeds()
    test_solution()


if __name__ == "__main__":
    try:
        test_generator()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except BaseException as base_err:
        print(f"{base_err.__class__.__name__}: {base_err}\n")



"""Tests para los generadores de laberintos (hunt_and_kill y bfs).

Todos los tests se ejecutan contra cada generador de GENERATORS. Para
añadir otro algoritmo, importalo y anadelo al diccionario.

Ejecutar desde la raiz del proyecto:
    python tests/test_hunt_and_kill.py
o con pytest:
    python -m pytest tests/ -v
"""
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mazegen.hunt import hunt_and_kill  # noqa: E402
from mazegen.bfs import bfs as bfs_generator  # noqa: E402

GENERATORS = {
    "hunt_and_kill": hunt_and_kill,
    "bfs": bfs_generator,
}

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

SIZES = [(1, 1), (1, 5), (5, 1), (2, 2), (5, 5), (10, 7), (30, 20)]


def is_open(grid, x, y, d):
    """True si la celda (x, y) tiene el muro d abierto (bit a 0)."""
    return not (grid[y][x] & BIT[d])


def count_edges(grid, width, height):
    """Cuenta pasillos (cada uno una sola vez: solo mirando E y S)."""
    edges = 0
    for y in range(height):
        for x in range(width):
            if is_open(grid, x, y, "E"):
                edges += 1
            if is_open(grid, x, y, "S"):
                edges += 1
    return edges


def reachable(grid, width, height, start=(0, 0)):
    """BFS de referencia siguiendo solo muros abiertos."""
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and is_open(grid, x, y, d) and (nx, ny) not in seen):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def print_maze(grid, width, height):
    """Dibuja el laberinto en ASCII para inspeccionarlo a ojo."""
    out = ["+" + "---+" * width]
    for y in range(height):
        row, below = "|", "+"
        for x in range(width):
            row += "   " + ("|" if grid[y][x] & BIT["E"] else " ")
            below += ("---" if grid[y][x] & BIT["S"] else "   ") + "+"
        out += [row, below]
    print("\n".join(out))


def test_dimensions():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            # Añadido param perfect=True para tests base
            grid = gen(w, h, (0, 0), 42, True)
            assert len(grid) == h, f"{name} {w}x{h}: alto incorrecto"
            assert all(len(r) == w for r in grid), \
                f"{name} {w}x{h}: ancho incorrecto"


def test_cell_values_valid():
    for name, gen in GENERATORS.items():
        grid = gen(10, 10, (0, 0), 1, True)
        assert all(0 <= c <= 15 for row in grid for c in row), \
            f"{name}: valores fuera de 0-15"


def test_borders_closed():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            grid = gen(w, h, (0, 0), 7, True)
            for x in range(w):
                assert grid[0][x] & BIT["N"], f"{name} {w}x{h}: borde N abierto x={x}"
                assert grid[h - 1][x] & BIT["S"], f"{name} {w}x{h}: borde S abierto x={x}"
            for y in range(h):
                assert grid[y][0] & BIT["W"], f"{name} {w}x{h}: borde W abierto y={y}"
                assert grid[y][w - 1] & BIT["E"], f"{name} {w}x{h}: borde E abierto y={y}"


def test_walls_symmetric():
    """Si A tiene abierto el muro hacia B, B debe tenerlo abierto hacia A."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            for perfect_flag in [True, False]:
                grid = gen(w, h, (0, 0), 3, perfect_flag)
                for y in range(h):
                    for x in range(w):
                        for d, (dx, dy) in DELTA.items():
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                assert is_open(grid, x, y, d) == \
                                    is_open(grid, nx, ny, OPPOSITE[d]), \
                                    f"{name} {w}x{h} (perfect={perfect_flag}): muro incoherente ({x},{y}) {d}"


def test_all_cells_reachable():
    """Sin zonas aisladas: desde (0,0) se llega a todas las celdas en ambos modos."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            for seed in range(5):
                for perfect_flag in [True, False]:
                    grid = gen(w, h, (0, 0), seed, perfect_flag)
                    assert len(reachable(grid, w, h)) == w * h, \
                        f"{name} {w}x{h} seed={seed} perfect={perfect_flag}: hay celdas aisladas"


def test_perfect_and_imperfect_modes():
    """Verifica la cantidad de pasillos según el modo PERFECT."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            if w * h <= 4:  # Laberintos muy pequeños pueden no poder generar bucles
                continue
            for seed in range(5):
                # Modo PERFECT=True: debe ser un árbol sin ciclos
                grid_perf = gen(w, h, (0, 0), seed, True)
                assert count_edges(grid_perf, w, h) == w * h - 1, \
                    f"{name} {w}x{h} seed={seed}: PERFECT=True tiene ciclos o faltan pasillos"
                
                # Modo PERFECT=False: debe tener rutas alternativas (ciclos)
                grid_imperf = gen(w, h, (0, 0), seed, False)
                assert count_edges(grid_imperf, w, h) > w * h - 1, \
                    f"{name} {w}x{h} seed={seed}: PERFECT=False no generó rutas alternativas (ciclos)"


def test_no_closed_cells():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            if w * h == 1:
                continue
            # Comprobamos en ambos modos
            for perfect_flag in [True, False]:
                grid = gen(w, h, (0, 0), 5, perfect_flag)
                assert all(c != 15 for row in grid for c in row), \
                    f"{name} {w}x{h} perfect={perfect_flag}: hay celdas con los 4 muros"


def test_reproducible_same_seed():
    for name, gen in GENERATORS.items():
        assert gen(15, 15, (0, 0), 1234, True) == gen(15, 15, (0, 0), 1234, True), \
            f"{name}: misma seed, distinto laberinto (perfect=True)"
        assert gen(15, 15, (0, 0), 1234, False) == gen(15, 15, (0, 0), 1234, False), \
            f"{name}: misma seed, distinto laberinto (perfect=False)"


def test_different_seeds_differ():
    for name, gen in GENERATORS.items():
        assert gen(15, 15, (0, 0), 1, True) != gen(15, 15, (0, 0), 2, True), \
            f"{name}: seeds distintas, mismo laberinto (perfect=True)"


def test_start_not_in_corner():
    for name, gen in GENERATORS.items():
        for start in [(2, 3), (4, 4), (9, 6)]:
            grid = gen(10, 7, start, 11, True)
            assert len(reachable(grid, 10, 7, start)) == 70, \
                f"{name} start={start}: celdas aisladas"
            assert count_edges(grid, 10, 7) == 69, \
                f"{name} start={start}: no es perfecto"


def test_seed_none_works():
    for name, gen in GENERATORS.items():
        grid = gen(8, 8, (0, 0), None, True)
        assert len(reachable(grid, 8, 8)) == 64, f"{name}: seed=None falla"


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"OK    {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests pasados\n")
    
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    for gname, gen in GENERATORS.items():
        try:
            print(f"{gname} 8x5, seed {seed} (PERFECT=False):")
            print_maze(gen(20, 20, (0, 0), None , False), 20, 20)
        except Exception as e:  # noqa: BLE001
            print(f"  no se pudo generar: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)
