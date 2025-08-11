from __future__ import annotations
from collections import deque
from typing import Callable, Deque, Optional

# Nota: No importamos tu NPC Agent para no romper dependencias aquí.
# Este adaptador expone un puerto genérico que el BDI puede usar.
# Puedes inyectar funciones/callbacks desde agents.npc_agent en runtime.

Action = tuple[int, int]  # (dx, dy) con |dx|+|dy| = 1

class NpcBDIAdapter:
    """
    Cola de acciones atómicas (pasos en rejilla) empujadas por el BDI.
    - El BDI 'push' acciones (dx, dy).
    - El loop del juego hace 'pop' cuando el sprite está libre.
    - Callbacks opcionales para eventos (p.ej., al llegar a celda).
    """

    def __init__(self) -> None:
        self._queue: Deque[Action] = deque()
        self.on_dequeue: Optional[Callable[[Action], None]] = None
        self.on_idle: Optional[Callable[[], None]] = None
        self.on_step_done: Optional[Callable[[], None]] = None

    def push_action(self, dx: int, dy: int) -> None:
        if abs(dx) + abs(dy) != 1:
            raise ValueError("Solo se permiten pasos cardinales de 1 celda.")
        self._queue.append((dx, dy))

    def has_actions(self) -> bool:
        return len(self._queue) > 0

    def try_dequeue(self) -> Optional[Action]:
        if self._queue:
            act = self._queue.popleft()
            if self.on_dequeue:
                self.on_dequeue(act)
            return act
        if self.on_idle:
            self.on_idle()
        return None

    def notify_step_done(self) -> None:
        if self.on_step_done:
            self.on_step_done()
