from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Any

PROTOCOL_VERSION = "1.0"

EventKind = Literal["time_tick", "zone_alert", "npc_interaction", "world_change"]

@dataclass(frozen=True)
class WorldSnapshot:
    """Estado del mundo para el NPC (JSON-friendly y versionado)."""
    version: str
    t_sim: float
    seq: int
    npc_id: str
    cell: tuple[int, int]
    nearby: list[dict]       # [{kind, id, cell, meta?}]
    areas: list[dict]        # [{name, rect:[x1,y1,x2,y2], walkable:bool?}]
    last_events: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class WorldEvent:
    """Evento push importante (interrupt)."""
    version: str
    t_sim: float
    seq: int
    event_id: str
    kind: EventKind
    payload: dict[str, Any]
    priority: int = 0  # 0 normal, 1 alto, 2 crítico
