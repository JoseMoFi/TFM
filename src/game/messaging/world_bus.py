from __future__ import annotations
import threading
from queue import PriorityQueue, Empty
from typing import Callable, Optional, Dict, Tuple
from .messages import WorldSnapshot, WorldEvent

class WorldBus:
    """
    Mediador in-process y thread-safe:
      - Pull: el NPC pide snapshots (builder por NPC).
      - Push: el mundo publica eventos por NPC (cola prioritaria).
    """
    def __init__(self) -> None:
        self._snapshot_builders: Dict[str, Callable[[], WorldSnapshot]] = {}
        self._event_queues: Dict[str, "PriorityQueue[Tuple[int, int, WorldEvent]]"] = {}
        self._lock = threading.RLock()
        self._seq = 0

    def register_npc(self, npc_id: str, snapshot_builder: Callable[[], WorldSnapshot]) -> None:
        with self._lock:
            self._snapshot_builders[npc_id] = snapshot_builder
            self._event_queues[npc_id] = PriorityQueue()

    def unregister_npc(self, npc_id: str) -> None:
        with self._lock:
            self._snapshot_builders.pop(npc_id, None)
            self._event_queues.pop(npc_id, None)

    # Pull
    def request_snapshot(self, npc_id: str) -> WorldSnapshot:
        with self._lock:
            builder = self._snapshot_builders.get(npc_id)
            if not builder:
                raise KeyError(f"NPC '{npc_id}' no registrado")
        return builder()

    # Push
    def publish_event(self, npc_id: str, ev: WorldEvent) -> None:
        with self._lock:
            q = self._event_queues.get(npc_id)
            if not q:
                return
            self._seq += 1
            q.put((-ev.priority, self._seq, ev))

    def try_get_event(self, npc_id: str, timeout: float = 0.0) -> Optional[WorldEvent]:
        q = self._event_queues.get(npc_id)
        if not q:
            return None
        try:
            _, _, ev = q.get(timeout=timeout)
            return ev
        except Empty:
            return None
