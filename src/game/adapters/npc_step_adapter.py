from __future__ import annotations
from collections import deque
from typing import Deque, Optional, Tuple

Action = Tuple[int, int]  # (dx,dy)

class NpcStepAdapter:
    """
    Cola de pasos cardinales para el sprite.
    La vista la consulta en cada tick; el agente (o el bridge) empuja pasos.
    """
    def __init__(self) -> None:
        self._q: Deque[Action] = deque()

    def push_step(self, dx: int, dy: int) -> None:
        if abs(dx) + abs(dy) != 1:
            raise ValueError("Solo pasos cardinales de 1 celda.")
        self._q.append((dx, dy))

    def has_steps(self) -> bool:
        return bool(self._q)

    def try_pop(self) -> Optional[Action]:
        return self._q.popleft() if self._q else None