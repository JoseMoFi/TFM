from __future__ import annotations
import arcade
from .config import SCREEN_W, SCREEN_H
from .view import MainView
from .adapters.npc_step_adapter import NpcStepAdapter
from .messaging.world_bus import WorldBus
from .messaging.messages import WorldSnapshot, PROTOCOL_VERSION
import time

def bootstrap_world(npc_id: str = "npc_eldric"):
    step_adapter = NpcStepAdapter()
    bus = WorldBus()
    window = arcade.get_window()
    if not window:
        window = arcade.Window(SCREEN_W, SCREEN_H, "RPG Grid + Panadería")
    view = MainView(step_adapter=step_adapter)
    window.show_view(view)

    def build_snapshot() -> WorldSnapshot:
        areas = [{"name": "Bakery", "rect": [50, 50, 60, 60]}]
        nearby = []  # futuro: npcs/objetos cercanos
        return WorldSnapshot(
            version=PROTOCOL_VERSION,
            t_sim = time.perf_counter(),
            seq=int(time.perf_counter() * 1000),
            npc_id=npc_id,
            cell=(view.npc.cell_x, view.npc.cell_y),
            nearby=nearby,
            areas=areas,
            last_events=[],
        )

    bus.register_npc(npc_id, build_snapshot)
    return window, view, step_adapter, bus