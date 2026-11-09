from __future__ import annotations
import random

from .model import CARDINAL_DIRECTIONS, Direction, Maze, MazeError
WallCandidate = tuple[int, int, Direction]
Neighbor = tuple[Direction, tuple[int, int]]
SUPPORTED_ALGORITHMS: tuple[str, ...] = ("dfs", "hunt_and_kill")

class BaseAlgorithm:
    def __init__(self, maze: Maze, rng: random.Random, start: tuple[int, int] | None) -> None:
        self.maze = Maze
        self.rng = rng
        self.start = start
        self.visited: set[tuple[int, int]] = set()

    
    def _remove_dead_ends(maze: Maze, rng: random.Random) -> None:
        for _ in range(3):
            dead_ends = maze.real_dead_end_cells()
            if not dead_ends:
                return
            rng.shuffle(dead_ends)
            progress = False
            for x, y in dead_ends:
                if len(maze.open_neighbors(x, y)) != 1:
                    continue
                directions = list(CARDINAL_DIRECTIONS)
                rng.shuffle(directions)
                for direction in directions:
                    neighbor = maze.get_neighbor(x, y, direction)
                    if neighbor is None:
                        continue
                    if neighbor in maze.pattern42_cells:
                        continue
                    if not maze.has_wall(x, y, direction):
                        continue
                    if not maze.open_wall(x, y, direction):
                        continue
                    if maze.has_open_3x3():
                        maze.close_wall(x, y, direction)
                        continue
                    progress = True
                    break
            if not progress:
                return
    
    def _wall_candidates(maze: Maze) -> list[WallCandidate]:
        candidates: list[WallCandidate] = []
        for x, y in maze.non_pattern_cells():
            for direction in (Direction.EAST, Direction.SOUTH):
                neighbor = maze.get_neighbor(x, y, direction)
                if neighbor is None:
                    continue
                if neighbor in maze.pattern42_cells:
                    continue
                if not maze.has_wall(x, y, direction):
                    continue
                candidates.append((x, y, direction))
        return candidates

    def _add_one_cycle(maze: Maze, rng: random.Random) -> bool:
        #ns xq falla
        candidates = _wall_candidates(maze)
        rng.shuffle(candidates)
        for x, y, direction in candidates:
            if not maze.open_wall(x, y, direction):
                continue
            if maze.has_open_3x3():
                maze.close_wall(x, y, direction)
                continue
            return True
        return False

    def braid(
        maze: Maze,
        rng: random.Random,
        target_loops: int = 3,
    ) -> list[str]:
        """Turn a perfect maze into a playable board.

        Dead ends are removed when possible and independent cycles are added
        until ``target_loops`` is reached.  Every modification is rejected if
        it would create an open ``3x3`` area.

        Returns:
            Warnings about constraints that could not be satisfied.
        """
        warnings: list[str] = []
        _remove_dead_ends(maze, rng)
        loops = maze.count_loops()
        attempts = 0
        max_attempts = max(4, len(maze.non_pattern_cells()))
        while loops < target_loops and attempts < max_attempts:
            attempts += 1
            if not _add_one_cycle(maze, rng):
                break
            loops = maze.count_loops()

        if loops < 2:
            warnings.append(
                "No se pudieron crear al menos dos rutas independientes; "
                "el tablero es demasiado pequeño."
            )
        dead_ends = len(maze.real_dead_end_cells())
        if dead_ends > 2:
            warnings.append(
                f"Quedan {dead_ends} callejones sin salida; el máximo "
                "recomendado es 2."
            )
        return warnings


    def _resolve_start(
        maze: Maze,
        start: tuple[int, int] | None,
    ) -> tuple[int, int]:
        candidate = maze.entry if start is None else start
        if (
            maze.is_inside(*candidate)
            and candidate not in maze.pattern42_cells
        ):
            return candidate
        cells = maze.non_pattern_cells()
        if not cells:
            raise MazeError(
                "No hay celdas libres para generar el laberinto."
            )
        return cells[0]
            

class DFS():

    def _carve(self) -> None:
        """Generador DFS del usuario con rotura de muros al retroceder (15%)."""
        current = self._resolve_start(self.maze, self.start)
        visited: set[tuple[int, int]] = {current}
        stack: list[tuple[int, int]] = [current]
        
        while stack:
            x, y = stack[-1]
            directions = list(CARDINAL_DIRECTIONS)
            self.rng.shuffle(directions)
            
            moved = False
            for direction in directions:
                neighbor = self.maze.get_neighbor(x, y, direction)

                #Nose si hace falta comprobar estas.
                # Saltamos bordes o celdas del logo
                if neighbor is None or neighbor in self.maze.pattern42_cells:
                    continue

                # Si el vecino ya está visitado, lo ignoramos para avanzar
                if neighbor in visited:
                    continue
                    
                # Avance normal del DFS
                self.maze.open_wall(x, y, direction)
                visited.add(neighbor)
                stack.append(neighbor)
                moved = True
                break
                
            if not moved:
                stack.pop() # Backtrack


class HuntAndKill(BaseAlgorithm):

    def _unvisited_neighbors(self, position: tuple[int, int]) -> list[Neighbor]:
        x, y = position
        result: list[Neighbor] = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.maze.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.maze.pattern42_cells:
                continue
            if neighbor in self.visited:
                continue
            result.append((direction, neighbor))
        return result

    def _visited_neighbors(self, position: tuple[int, int]) -> list[Neighbor]:
        x, y = position
        result: list[Neighbor] = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.maze.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.maze.pattern42_cells:
                continue
            if neighbor in self.visited:
                result.append((direction, neighbor))
        return result

    def _hunt(self) -> tuple[int, int] | None:
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                position = (x, y)
                if position in self.visited:
                    continue
                if position in self.maze.pattern42_cells:
                    continue
                candidates = self._visited_neighbors(position)
                if not candidates:
                    continue
                direction, _ = self.rng.choice(candidates)
                self.maze.open_wall(x, y, direction)
                self.visited.add(position)
                return position
        return None


    def carve(self) -> None:
        """Carve a perfect maze with the hunt-and-kill algorithm."""
        #mas chequeo de quue start es posible y no esta en el logo y que si hay mas espacio aparte del logo
        current = self._resolve_start(self.maze, self.start)

        visited: set[tuple[int, int]] = {current}
        while True:
            candidates = self._unvisited_neighbors(current)
            if candidates:
                direction, neighbor = self.rng.choice(candidates)
                self.maze.open_wall(current[0], current[1], direction)
                visited.add(neighbor)
                current = neighbor
                continue
            hunted = self._hunt()
            if hunted is None:
                return
            current = hunted

class AlgorithmFactory:
    @classmethod
    def get_algorithm(cls, maze: Maze, algorithm: str, rng: random.Random, start: tuple[int, int] | None) -> BaseAlgorithm:
        if algorithm == "dfs":
            return DFS(maze, rng, start)
        if algorithm == "hunt_and_kill":
            return HuntAndKill(maze, rng, start)
        raise MazeError(
            f"Algoritmo desconocido: {algorithm!r}. "
            f"Use uno de: {', '.join(SUPPORTED_ALGORITHMS)}."
        )
