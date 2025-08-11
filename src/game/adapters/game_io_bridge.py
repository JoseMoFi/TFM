from __future__ import annotations
import time
from typing import Callable, Optional, Tuple

from ..messaging.world_bus import WorldBus
from ..messaging.messages import WorldSnapshot, WorldEvent, PROTOCOL_VERSION
from ..adapters.npc_step_adapter import NpcStepAdapter

class GameIOBridge:
    """
    Puente usado por NPCAgent (SPADE-BDI) para hablar con el mundo Arcade.
    Cumple con lo que ya usas en tu agente:
      - move_to_cell(x,y, npc_id=...)
    Añade pull/push de estado/eventos:
      - request_snapshot(npc_id) -> WorldSnapshot
      - try_get_event(npc_id, timeout=...) -> WorldEvent|None
    """
    def __init__(self, npc_id: str, world_bus: WorldBus, step_adapter: NpcStepAdapter):
        self.npc_id = npc_id
        self.bus = world_bus
        self.steps = step_adapter

    # ---- API esperada por NPCAgent (.move) ----
    def move_to_cell(self, x: int, y: int, npc_id: Optional[str] = None) -> None:
        # Por simplicidad: descomponemos en pasos 4-dir. Aquí podrías meter A* si quieres.
        # OJO: Esto genera una ruta rectilínea (primero X, luego Y).
        if npc_id and npc_id != self.npc_id:
            return
        # Se encolan muchos pasos; considera rate limit o A* si la distancia es grande.
        # Aquí asumimos que el sprite empieza en su celda actual; la vista consumirá poco a poco.
        # Si quieres pathfinding real, lo añadimos en otra iteración.
        from ..view_state import get_current_cell  # util local para leer celda actual
        cx, cy = get_current_cell()
        dx = 1 if x > cx else -1
        while cx != x:
            self.steps.push_step(dx, 0)
            cx += dx
        dy = 1 if y > cy else -1
        while cy != y:
            self.steps.push_step(0, dy)
            cy += dy

    # ---- Estado/Evento (pull/push) ----
    def request_snapshot(self) -> WorldSnapshot:
        return self.bus.request_snapshot(self.npc_id)

    def try_get_event(self, timeout: float = 0.0) -> Optional[WorldEvent]:
        return self.bus.try_get_event(self.npc_id, timeout=timeout)

    # ---- Para que el mundo notifique eventos al NPC ----
    def publish_event(self, ev: WorldEvent) -> None:
        self.bus.publish_event(self.npc_id, ev)
